""" Defines the SparkClient class and some utilities used by this class. """

import logging
from typing import List, Optional

import sqlparse
from mlflow.pyfunc import spark_udf
from pyspark import TaskContext
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, count, lit
from pyspark.sql.types import StructType
from pyspark.sql.utils import AnalysisException

from databricks.feature_store.utils.utils import (
    sanitize_identifier,
    sanitize_identifiers,
    sanitize_multi_level_name,
)

try:
    # PySparkException is the base class for all pyspark exceptions from v3.4.0.
    from pyspark.errors import PySparkException
except ImportError:
    # Before pyspark-3.4.0, CapturedException is the base class.
    from pyspark.sql.utils import CapturedException as PySparkException

_logger = logging.getLogger(__name__)


class SparkClient:
    """
    Wraps the details of interacting with the Spark behind an API.
    This class is used by the FeatureStoreClient.

    The Spark client should be reserved for low-level Spark operations and not contain any business logic
    that is unrelated to Spark (for example, calling the catalog backend).  If you need additional
    business logic, consider using SparkClientHelper instead.

    The idea behind this layer of abstraction is that the FeatureStoreClient may later
    be changed to create tables, set properties, etc using a RESTful client talking to
    a feature catalog service.
    """

    STREAMING_ZORDER_INTERVAL = 5000

    def __init__(self):
        """
        Constructs a SparkClient that reads and writes tables from the specified
        database_name.
        """
        # TaskContext.get() is None on Spark drivers. This is the same check performed by
        # SparkContext._assert_on_driver(), which is called by SparkSession.getOrCreate().
        self._on_spark_driver = TaskContext.get() is None

        # Initialize a SparkSession only if on the driver.
        # _internal_spark should not be accessed directly, but through the _spark property.
        self._internal_spark = (
            SparkSession.builder.appName("feature_store.spark_client").getOrCreate()
            if self._on_spark_driver
            else None
        )

    @property
    def _spark(self):
        """
        Property method to return the initialized SparkSession.
        Throws outside of the Spark driver as the SparkSession is not initialized.
        """
        if not self._on_spark_driver:
            raise ValueError(
                "Spark operations are not enabled outside of the driver node."
            )
        return self._internal_spark

    def get_current_catalog(self):
        """
        Get current set catalog in the spark context.
        """
        try:
            df = self._spark.sql("SELECT CURRENT_CATALOG()").collect()
            return df[0][0]
        except Exception as e:
            return None

    def get_current_database(self):
        """
        Get current set database in the spark context.
        """
        try:
            df = self._spark.sql("SELECT CURRENT_DATABASE()").collect()
            return df[0][0]
        except Exception as e:
            return None

    def catalog_exists(self, catalog_name):
        """
        Determines whether a catalog exists.
        """
        try:
            df = self._spark.sql(
                f"DESCRIBE CATALOG {sanitize_identifier(catalog_name)}"
            )
            return not df.isEmpty()
        except AnalysisException:
            return False

    def database_exists(self, catalog_name, database_name):
        """
        Determines whether a database exists in this catalog.
        """
        try:
            df = self._spark.sql(
                f"DESCRIBE SCHEMA {sanitize_identifier(catalog_name)}.{sanitize_identifier(database_name)}"
            )
            return not df.isEmpty()
        except AnalysisException:
            return False

    def table_exists(self, full_table_name):
        """
        Determines whether a table exists in this database.
        """
        try:
            df = self._spark.sql(
                f"DESCRIBE TABLE {sanitize_multi_level_name(full_table_name)}"
            )
            return not df.isEmpty()
        except AnalysisException:
            return False

    def get_delta_table_object(self, full_table_name):
        from delta.tables import DeltaTable

        return DeltaTable.forName(
            self._spark, sanitize_multi_level_name(full_table_name)
        )

    def is_delta_table(self, full_table_name):
        try:
            self.get_delta_table_object(full_table_name)
            return True
        except AnalysisException:
            return False

    def get_partition_columns_for_delta_table(self, full_table_name):
        """
        Caller is responsible to check the table is Delta table
        """
        table = self.get_delta_table_object(full_table_name)
        try:
            partitonColumnMetadataId = "partitionColumns"
            detail_dict = (
                table.detail()
                .select(partitonColumnMetadataId)
                .collect()[0]
                .asDict(True)
            )
            return detail_dict.get(partitonColumnMetadataId, [])
        except Exception:
            return []

    def has_generated_columns(self, qualified_table_name):
        """
        Determines whether an existing table contains generated columns.
        Return True if the query failed so that we reject register table.
        """
        try:
            result = self._spark.sql(
                f"SHOW CREATE TABLE {sanitize_multi_level_name(qualified_table_name)}"
            ).collect()[0]
            schema_dict = result.asDict(True)
            for value in schema_dict.values():
                if "GENERATED ALWAYS AS" in value.upper():
                    return True
            return False
        except PySparkException:
            return True

    def get_delta_table_path(self, qualified_table_name):
        """
        Expects Delta table. Returns the DBFS path to the Delta table.
        Use as documented here : https://docs.delta.io/latest/delta-utility.html#detail-schema
        """
        try:
            results = (
                self._spark.sql(
                    f"DESCRIBE DETAIL {sanitize_multi_level_name(qualified_table_name)}"
                )
                .limit(1)
                .collect()
            )
            paths = [row["location"] for row in results]
            if len(paths) == 0:
                return None
            return paths[0]
        # All pyspark exceptions inherit PySparkException
        # If the query failed for whatever reason we should return None here
        except PySparkException:
            return None

    @staticmethod
    def _dbfs_path_to_table_format(path):
        # Expected DBFS path for delta table "database_name.table_name" is
        # "dbfs:/path/to/files/database_name.db/table_name"
        #
        # If input path does not match this signature, return original path
        if not path.lower().startswith("dbfs:/"):
            return path
        # split by "/" and isolate the leaf file and parent db directory
        split_path = path.split("/")
        if len(split_path) < 2:
            return path
        db_path, table_name = split_path[-2:]
        if not db_path.lower().endswith(".db"):
            return path
        # Isolate database name and verify that "database_name.table_name" <--> input path
        db_name = db_path[:-3]  # everything before the last ".db" prefix
        return f"{db_name}.{table_name}"

    # TODO(zero.qu): find proper way to get the exact database name and table name of a delta table
    # Currently we extract the database name and table name of a delta table by parsing the
    # data source path. However, the path may not give sufficient information if the user uses
    # external blob storage like S3 to store the delta table. We should fix the logic here with
    # proper exception handling.
    def convert_to_table_format(self, path):
        data_source = self._dbfs_path_to_table_format(path)
        # case-sensitive comparison since DBFS supports case-sensitive files
        if self.get_delta_table_path(data_source) != path:
            return path
        return data_source

    def get_feature_table_schema(self, feature_table_name):
        feature_table = self.get_delta_table_object(feature_table_name)
        return feature_table.toDF().schema

    def createDataFrame(self, data, schema) -> DataFrame:
        return self._spark.createDataFrame(data, schema)

    def empty_df(self, schema) -> DataFrame:
        return self.createDataFrame([], schema)

    def create_table(
        self,
        qualified_table_name: str,
        schema: StructType,
        partition_columns: Optional[List[str]] = None,
        path: Optional[str] = None,
        comment: Optional[str] = None,
    ):
        """
        Creates a Delta table in the metastore.
        Will throw if schema contains duplicate columns.
        """
        df = self.empty_df(schema)
        writer = (
            df.write.partitionBy(*partition_columns) if partition_columns else df.write
        )
        if path:
            writer = writer.option("path", path)
        if comment is not None:  # Note: comment can be an empty string
            writer = writer.option("comment", comment)
        writer.format("delta").saveAsTable(
            sanitize_multi_level_name(qualified_table_name)
        )

    def delete_empty_table(self, qualified_table_name):
        """
        Drops a table from the metastore only if it is empty.
        """
        if not SparkClient._df_is_empty_optimized(
            self._spark.read.table(sanitize_multi_level_name(qualified_table_name))
        ):
            raise ValueError(
                f"Attempted to delete non-empty table {qualified_table_name}."
            )
        self.delete_table(qualified_table_name)

    # This should be used VERY VERY carefully as it will delete the entire delta table
    def delete_table(self, qualified_table_name):
        """
        Drops a table from the metastore.
        """
        self._spark.sql(
            f"DROP TABLE IF EXISTS {sanitize_multi_level_name(qualified_table_name)}"
        )

    def read_table(
        self, qualified_table_name, as_of_delta_timestamp=None, streaming=False
    ):
        """
        Reads a Delta table, optionally as of some timestamp.
        """
        if streaming and as_of_delta_timestamp:
            raise ValueError(
                "Internal error: as_of_delta_timestamp cannot be specified when"
                " streaming=True."
            )

        base_reader = (
            # By default, Structured Streaming only handles append operations. Because
            # we have a notion of primary keys, most offline feature store operations
            # are not appends. For example, FeatureStoreClient.write_table(mode=MERGE)
            # will issue a MERGE operation.
            # In order to propagate the non-append operations to the
            # readStream, we set ignoreChanges to "true".
            # For more information,
            # see https://docs.databricks.com/delta/delta-streaming.html#ignore-updates-and-deletes
            self._spark.readStream.format("delta").option("ignoreChanges", "true")
            if streaming
            else self._spark.read.format("delta")
        )

        if as_of_delta_timestamp:
            return base_reader.option("timestampAsOf", as_of_delta_timestamp).table(
                sanitize_multi_level_name(qualified_table_name)
            )
        else:
            return base_reader.table(sanitize_multi_level_name(qualified_table_name))

    def df_violates_pk_constraint(self, df, keys):
        count_column_name = "databricks__internal__row_counter"
        df_aggregated = (
            df.groupBy(*keys)
            .agg(count(lit(1)).alias(count_column_name))
            .filter(f"{count_column_name} > 1")
        )
        return not SparkClient._df_is_empty_optimized(df_aggregated)

    def write_table(
        self,
        qualified_table_name,
        primary_keys,
        timestamp_keys,
        df,
        mode,
        checkpoint_location=None,
        trigger=None,
    ):
        """
        Write features.

        :return: If ``df.isStreaming``, returns a PySpark :class:`StreamingQuery <pyspark.sql.streaming.StreamingQuery>`. :obj:`None` otherwise.
        """

        if mode not in ["overwrite", "merge"]:
            raise ValueError(f"Unsupported mode '{mode}'.")

        keys = primary_keys + timestamp_keys
        zorder_keys = primary_keys[0:2] + timestamp_keys if timestamp_keys else []

        if not df.isStreaming:
            # Verify that input dataframe has unique rows per pk combination
            if self.df_violates_pk_constraint(df, keys):
                raise ValueError(
                    f"Non-unique rows detected in input dataframe for key combination {keys}."
                )

        if df.isStreaming:
            if trigger is None:
                raise ValueError("``trigger`` must be set when df.isStreaming")
            if mode == "overwrite":
                raise TypeError(
                    "API not supported for streaming DataFrame in 'overwrite' mode."
                )
            return self._merge_streaming_df_into_delta_table(
                qualified_table_name,
                primary_keys,
                timestamp_keys,
                zorder_keys,
                df,
                trigger,
                checkpoint_location,
            )
        else:
            if mode == "overwrite":
                self._write_to_delta_table(
                    qualified_table_name, timestamp_keys, df, "overwrite"
                )
            else:
                self._merge_df_into_delta_table(
                    qualified_table_name, primary_keys, timestamp_keys, df
                )
            if zorder_keys:
                self._zorder_delta_table(qualified_table_name, zorder_keys)
            return None

    def get_predict_udf(self, model_uri, result_type=None):
        kwargs = {"result_type": result_type} if result_type else {}
        return spark_udf(self._spark, model_uri, **kwargs)

    def get_table_comment(self, delta_table_name):
        """
        Get a table's comment. Returns None if the table does not have comment.
        """
        comment = (
            self._spark.sql(
                f"DESCRIBE TABLE EXTENDED {sanitize_multi_level_name(delta_table_name)}"
            )
            .where(col("col_name") == "Comment")
            .select("data_type")
            .head()
        )
        if comment is None:
            return None
        return comment[0]

    def set_table_comment(self, delta_table_name, comment):
        """
        Set a table's comment. If comment is None, the table's comment will be removed.
        """
        if comment is None:
            self._spark.sql(
                f"COMMENT ON TABLE {sanitize_multi_level_name(delta_table_name)} IS NULL"
            )
        else:
            # comments can have \ and ', which can break the sql statement below, so escape them.
            escaped_comment = comment.replace("\\", "\\\\").replace("'", "\\'")
            self._spark.sql(
                f"COMMENT ON TABLE {sanitize_multi_level_name(delta_table_name)} IS '{escaped_comment}'"
            )

    @staticmethod
    def _get_pk_from_identifier(identifier: sqlparse.sql.Identifier) -> str:
        primary_key = str(identifier)
        # remove timeseries key definition from primary key
        if primary_key.endswith(" TIMESERIES"):
            primary_key = primary_key[: -len(" TIMESERIES")]
        # remove backticks used to delimit and escape special characters in primary key
        return primary_key[1:-1].replace("``", "`")

    def get_pk_from_table_create_stmt(self, full_table_name: str) -> List[str]:
        """
        Get primary keys of a table from SHOW CREATE TABLE.
        """
        try:
            # example output:
            # `CREATE TABLE cat.foo.bar (
            #   `id` INT NOT NULL,
            #   `ts` TIMESTAMP NOT NULL,
            #   CONSTRAINT pk PRIMARY KEY (`id`, `ts`))
            # USING delta
            # TBLPROPERTIES (
            #   'delta.minReaderVersion' = '1',
            #   'delta.minWriterVersion' = '2')`
            create_stmt = self._spark.sql(
                f"""SHOW CREATE TABLE {sanitize_multi_level_name(full_table_name.lower())}"""
            ).first()[0]
        except:
            return []

        # A workaround of ES-761665: SHOW CREATE TABLE does not escape table names and constraint names properly
        create_stmt = create_stmt.replace(
            f"CREATE TABLE {full_table_name} (", "CREATE TABLE table (", 1
        )
        # This doesn't work if there is a user created (non-default) PK constraint with special characters in name,
        # but that should be rare enough.
        default_pk_name = SparkClient._default_pk_name(full_table_name.split(".")[2])
        create_stmt = create_stmt.replace(
            f"CONSTRAINT {default_pk_name} PRIMARY KEY (",
            f"CONSTRAINT pk PRIMARY KEY (",
            1,
        )

        create_stmt_parsed = sqlparse.parse(create_stmt)[0]
        _, parenthesis = create_stmt_parsed.token_next_by(i=sqlparse.sql.Parenthesis)

        for idx, token in enumerate(parenthesis.tokens):
            # parse within the parentheses for the primary key definition of the form `PRIMARY KEY ( key_column [, ...] )`
            # and avoid indexing errors
            if (
                idx >= 4
                and isinstance(token, sqlparse.sql.Parenthesis)
                and parenthesis.tokens[idx - 2].match(sqlparse.tokens.Keyword, "KEY")
                and parenthesis.tokens[idx - 4].match(
                    sqlparse.tokens.Keyword, "PRIMARY"
                )
            ):
                for subtoken in token.tokens:
                    if isinstance(subtoken, sqlparse.sql.Identifier):
                        return [SparkClient._get_pk_from_identifier(subtoken)]
                    if isinstance(subtoken, sqlparse.sql.IdentifierList):
                        return [
                            SparkClient._get_pk_from_identifier(identifier)
                            for identifier in subtoken.get_identifiers()
                        ]

        return []

    def set_cols_not_null(self, full_table_name: str, cols: List[str]):
        """
        Set columns in a table NOT NULL.

        Raises
            DeltaAnalysisException: if column contain nulls
        """
        if not cols:
            return
        for c in cols:
            self._spark.sql(
                f"ALTER TABLE {sanitize_multi_level_name(full_table_name)} ALTER COLUMN {sanitize_identifier(c)} SET NOT NULL"
            )

    def set_cols_pk(
        self, full_table_name: str, pk_cols: List[str], pk_name: Optional[str] = None
    ):
        """
        Set Primary Key constraint on table.

        Raises
            PrimaryKeyColumnsNullableException: if PK columns contains NULLABLE columns
        """
        if not pk_cols:
            return
        self._spark.sql(SparkClient.set_pk_statement(full_table_name, pk_cols, pk_name))

    @staticmethod
    def _default_pk_name(table_name):
        return table_name + "_pk"

    @staticmethod
    def set_pk_statement(
        full_table_name: str, pk_cols: List[str], pk_name: Optional[str] = None
    ):
        catalog_name, schema_name, table_name = full_table_name.split(".")
        if not pk_name:
            pk_name = SparkClient._default_pk_name(table_name)
        return f"ALTER TABLE {sanitize_multi_level_name(full_table_name)} ADD CONSTRAINT {sanitize_identifier(pk_name)} PRIMARY KEY({', '.join(sanitize_identifiers(pk_cols))})"

    @staticmethod
    def _write_to_delta_table(delta_table_name, timestamp_keys, df, mode):
        SparkClient._validate_timestamp_key_columns(df, timestamp_keys)
        return (
            df.write.option("mergeSchema", "true")
            .format("delta")
            .mode(mode)
            .saveAsTable(sanitize_multi_level_name(delta_table_name))
        )

    @staticmethod
    def _df_is_empty_optimized(df):
        """
        Check if the Spark DataFrame is empty.
        Using limit(1) and then count to check size rather than dropping to RDD level.
        """
        return df.limit(1).count() == 0

    @staticmethod
    def _df_columns_contain_nulls(df, columns):
        """
        Check if any of the target columns in the Spark DataFrame contain null values.
        If df or columns is empty, return False.
        """
        if not columns or SparkClient._df_is_empty_optimized(df):
            return False
        null_filter = " OR ".join([f"{column} IS NULL" for column in columns])
        filtered_df = df.filter(null_filter)
        return not SparkClient._df_is_empty_optimized(filtered_df)

    @staticmethod
    def _validate_timestamp_key_columns(df, timestamp_keys):
        if SparkClient._df_columns_contain_nulls(df, timestamp_keys):
            _logger.warning("DataFrame has null values in timestamp key column.")

    def attempt_to_update_delta_table_schema(self, delta_table_name, new_schema):
        df = self.empty_df(new_schema)
        (
            df.write.option("mergeSchema", "true")
            .format("delta")
            .mode("append")
            .saveAsTable(sanitize_multi_level_name(delta_table_name))
        )

    def _generate_merge_operation(
        self, feature_table_name, primary_keys, timestamp_keys, source_df_schema
    ):
        from delta.tables import DeltaTable

        result_table_alias = "result_table"
        batch_table_alias = "updates_table"
        source_df_columns_names = source_df_schema.fieldNames()
        feature_names = self.get_feature_table_schema(feature_table_name).fieldNames()
        keys = primary_keys + timestamp_keys

        def get_update_expression(feature):
            if feature in source_df_columns_names:
                # feature column exists in source_df
                return f"{batch_table_alias}.{sanitize_identifier(feature)}"
            else:
                # feature column missing in source_df, use existing value
                return f"{result_table_alias}.{sanitize_identifier(feature)}"

        def get_insert_expression(feature):
            if feature in source_df_columns_names:
                return f"{batch_table_alias}.{sanitize_identifier(feature)}"
            else:
                return lit(None)

        features = set(source_df_columns_names + feature_names)
        update_expr = {
            sanitize_identifier(feature): get_update_expression(feature)
            for feature in features
        }
        insert_expr = {
            sanitize_identifier(feature): get_insert_expression(feature)
            for feature in features
        }

        merge_condition = " AND ".join(
            [f"{result_table_alias}.{k} = {batch_table_alias}.{k}" for k in keys]
        )

        feature_table = DeltaTable.forName(
            self._spark, sanitize_multi_level_name(feature_table_name)
        )

        def merge(batch_df):
            self._validate_timestamp_key_columns(batch_df, timestamp_keys)
            return (
                feature_table.alias(result_table_alias)
                .merge(batch_df.alias(batch_table_alias), merge_condition)
                .whenNotMatchedInsert(values=insert_expr)
                .whenMatchedUpdate(set=update_expr)
                .execute()
            )

        return merge

    def _merge_df_into_delta_table(
        self,
        feature_table_name,
        primary_keys,
        timestamp_keys,
        source_df,
    ):
        merge_fn = self._generate_merge_operation(
            feature_table_name, primary_keys, timestamp_keys, source_df.schema
        )
        merge_fn(source_df)

    def _merge_streaming_df_into_delta_table(
        self,
        feature_table_name,
        primary_keys,
        timestamp_keys,
        zorder_keys,
        source_df,
        trigger,
        checkpoint_location=None,
    ):
        merge_fn = self._generate_merge_operation(
            feature_table_name, primary_keys, timestamp_keys, source_df.schema
        )

        def batch_fn(batch_df, batch_id):
            merge_fn(batch_df)
            if zorder_keys and batch_id % self.STREAMING_ZORDER_INTERVAL == 0:
                self._zorder_delta_table(feature_table_name, zorder_keys)

        options = {}
        if checkpoint_location is not None:
            options["checkpointLocation"] = checkpoint_location

        return (
            source_df.writeStream.trigger(**trigger)
            .outputMode("update")
            .foreachBatch(batch_fn)
            .options(**options)
            .start()
        )

    def _zorder_delta_table(self, feature_table_name, zorder_keys):
        self._spark.sql(
            f"OPTIMIZE {sanitize_multi_level_name(feature_table_name)} ZORDER BY ({', '.join(zorder_keys)})"
        )
