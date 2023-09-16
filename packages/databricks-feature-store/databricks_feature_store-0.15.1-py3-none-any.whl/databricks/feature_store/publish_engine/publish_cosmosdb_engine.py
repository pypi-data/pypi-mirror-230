import abc
from typing import List, Optional
from urllib.parse import urlparse

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from azure.cosmos.offer import ThroughputProperties
from pyspark.sql import SparkSession
from pyspark.sql.types import DateType, StructType, TimestampType

from databricks.feature_store.online_store_spec import AzureCosmosDBSpec
from databricks.feature_store.utils.cosmosdb_utils import (
    AUTO_SCALE_MAX_THROUGHPUT,
    CONTAINER_INDEXING_POLICY,
    PRIMARY_KEY_PROPERTY_NAME_VALUE,
    generate_cosmosdb_id,
    generate_cosmosdb_primary_key,
    generate_cosmosdb_safe_data_types,
    is_serverless_throughput_offer_error,
)


class PublishCosmosDBEngine(abc.ABC):
    def __init__(
        self, online_store_spec: AzureCosmosDBSpec, spark_session: SparkSession
    ):
        self.spark_session = spark_session
        self.account_uri = online_store_spec.account_uri
        self.authorization_key = (
            online_store_spec._lookup_authorization_key_with_write_permissions()
        )
        self.database_name = online_store_spec.database_name
        self.container_name = online_store_spec.container_name
        self._initialize_cosmosdb_client()

    def _initialize_cosmosdb_client(self):
        """
        Initialize Cosmos DB client and set the configs required to create and write to Cosmos DB containers.
        """
        self.cosmos_client = CosmosClient(self.account_uri, self.authorization_key)
        # Configurations used by the Spark writer to write to Cosmos DB. See example usage and config documentation:
        # https://github.com/Azure/azure-sdk-for-java/blob/main/sdk/cosmos/azure-cosmos-spark_3_2-12/docs/quick-start.md
        # https://github.com/Azure/azure-sdk-for-java/blob/main/sdk/cosmos/azure-cosmos-spark_3_2-12/docs/configuration-reference.md
        self.cosmosdb_spark_writer_options = {
            "spark.cosmos.accountEndpoint": self.account_uri,
            "spark.cosmos.accountKey": self.authorization_key,
            "spark.cosmos.database": self.database_name,
            "spark.cosmos.container": self.container_name,
            # We explicitly enforce the default value "ItemOverwrite" to guarantee upsert behavior.
            "spark.cosmos.write.strategy": "ItemOverwrite",
        }

    def _validate_timestamp_keys(self, schema: StructType, timestamp_keys: List[str]):
        # Check: We only support a single timestamp key in Cosmos DB.
        # TODO: ML-19665 add similar check in backend RPC validation.
        # TODO (ML-22021): move this validation to FeatureStoreClient.publish
        if len(timestamp_keys) > 1:
            raise ValueError(
                "Only one timestamp key is supported in Cosmos DB online store."
            )

        # The backend validates that the timestamp key is of Date, Timestamp type. The validation is duplicated
        # here in this client version to allow for the introduction of integer timestamp keys in future clients,
        # as the current Cosmos DB data model is not compatible with integer timestamp keys.
        if timestamp_keys and not type(schema[timestamp_keys[0]].dataType) in [
            DateType,
            TimestampType,
        ]:
            raise ValueError(
                "The timestamp key for Cosmos DB must be of either Date or Timestamp type."
            )

    def close(self):
        """
        Performs any close operations on the Cosmos DB connections. Cosmos DB connections are
        stateless http connections and hence does not need to be closed.
        :return:
        """
        pass

    def database_and_container_exist(self) -> bool:
        """
        Cosmos DB client is conservative in validation and does not check that (database, container) exists.
        Calling _get_properties forces the validation that both exist.
        """
        try:
            container_client = self.cosmos_client.get_database_client(
                self.database_name
            ).get_container_client(self.container_name)
            container_client._get_properties()
            return True
        except CosmosResourceNotFoundError:
            return False

    def get_cloud_provider_unique_id(self) -> Optional[str]:
        """
        Generate the expected container URI: https://{databaseaccount}.documents.azure.com/dbs/{db}/colls/{coll}
        https://docs.microsoft.com/en-us/rest/api/cosmos-db/cosmosdb-resource-uri-syntax-for-rest
        Returns the container URI if both the database and container exist, otherwise None.
        """
        if self.database_and_container_exist():
            # If the database and container exist, the account URI is expected to be well formed as below:
            # https://{databaseaccount}.documents.azure.com:443/, where port 443 and path "/" are optional.
            # Extract {databaseaccount}.documents.azure.com, dropping port and path if present.
            base_uri = urlparse(self.account_uri).hostname

            # Cosmos DB expectes the database account name to be lowercase, so we force that here to avoid generating
            # an unexpected container URI as the CosmosClient treats the URI in a case-insensitive manner.
            # https://docs.microsoft.com/en-us/azure/cosmos-db/sql/create-cosmosdb-resources-portal

            # Database and container name are case sensitive and should be used as-is
            return f"https://{base_uri.lower()}/dbs/{self.database_name}/colls/{self.container_name}"
        else:
            return None

    def create_empty_table(
        self,
        schema: StructType,
        primary_keys: List[str],
        timestamp_keys: List[str],
    ) -> str:
        """
        This method should handle creating the correct online table schema and state.
        (e.g. combining PKs, dropping the timestamp key, enabling ttl)
        """
        self._validate_timestamp_keys(schema, timestamp_keys)

        # All validations should be done prior to database or container creation.
        # If this method is called, then either the database or container did not exist.
        self.cosmos_client.create_database_if_not_exists(self.database_name)

        create_provisioned_table_error = None
        try:
            self.cosmos_client.get_database_client(
                self.database_name
            ).create_container_if_not_exists(
                self.container_name,
                PartitionKey(path=f"/{PRIMARY_KEY_PROPERTY_NAME_VALUE}"),
                indexing_policy=CONTAINER_INDEXING_POLICY,
                offer_throughput=ThroughputProperties(
                    auto_scale_max_throughput=AUTO_SCALE_MAX_THROUGHPUT
                ),
            )
        except Exception as e:
            # Store the exception and conditionally handle it in the finally block to avoid raising nested exceptions.
            # Nested exceptions are surfaced in order they were raised, which results in: 1. a verbose traceback,
            # 2. the Databricks Notebook UI displaying only the first exception message in the cell output.
            create_provisioned_table_error = e
        finally:
            # Creating containers with throughput offers (used for provisioned accounts) throws for serverless accounts.
            # If an exception is thrown for this reason, attempt to create a container without throughput.
            # Otherwise, re-raise the original error.
            if create_provisioned_table_error:
                if is_serverless_throughput_offer_error(create_provisioned_table_error):
                    self.cosmos_client.get_database_client(
                        self.database_name
                    ).create_container_if_not_exists(
                        self.container_name,
                        PartitionKey(path=f"/{PRIMARY_KEY_PROPERTY_NAME_VALUE}"),
                        indexing_policy=CONTAINER_INDEXING_POLICY,
                    )
                else:
                    raise create_provisioned_table_error

        # re-fetch the container URI now that the container is guaranteed to exist.
        return self.get_cloud_provider_unique_id()

    def write_table(
        self,
        df,
        schema: StructType,
        primary_keys: List[str],
        timestamp_keys: List[str],
    ):
        """
        This method should handle writing the correct online table schema.
        (e.g. combining PKs, writing online-safe data types, generating ttl)
        """
        self._validate_timestamp_keys(schema, timestamp_keys)

        # Write the DataFrame to Cosmos DB. All validations should be done prior.
        # Convert df to online-safe data types, generate the concatenated primary key and id columns
        df = generate_cosmosdb_safe_data_types(df)
        df = generate_cosmosdb_primary_key(df, primary_keys)

        # Window mode publish should use the timestamp key as the id property to enable range lookups.
        ts_col = timestamp_keys[0] if self.is_timeseries_window_publish else None
        df = generate_cosmosdb_id(df, column_for_id=ts_col)

        df.write.format("cosmos.oltp").options(
            **self.cosmosdb_spark_writer_options
        ).mode("APPEND").save()

    def generate_df_with_ttl_if_required(self, df, timestamp_keys: List[str]):
        """
        Convert the timestamp column to a TTL column expected by Cosmos DB.

        Currently is a no-op as TTL is not supported.
        """
        return df

    @property
    def is_timeseries_window_publish(self):
        """
        Determine if this publish engine will publish a window of a time series dataframe.
        This is currently equivalent to if TTL is defined in the online store spec.

        Currently returns False as TTL is not supported.
        """
        return False

    @property
    def table_name(self) -> str:
        """Table equivalent of this publish engine."""
        return self.container_name

    def drop_table(self):
        """
        Drops/deletes table from CosmosDB account
        """
        database_client = self.cosmos_client.get_database_client(self.database_name)
        # will raise CosmosResourceNotFoundError if container resource has already been deleted
        # delete operation happens synchronously here
        database_client.delete_container(self.container_name)
