import logging
from typing import Dict

from mlflow.utils.annotations import deprecated

from databricks.feature_store.api.proto.feature_catalog_pb2 import (
    FeatureTable as ProtoFeatureTable,
)
from databricks.feature_store.entities._feature_store_object import _FeatureStoreObject


class FeatureTable(_FeatureStoreObject):
    """
    Value class describing one feature table.

    This will typically not be instantiated directly, instead the
    :meth:`FeatureStoreClient.create_table <databricks.feature_store.client.FeatureStoreClient.create_table>`
    will create :class:`.FeatureTable` objects.
    """

    def __init__(
        self,
        name,
        table_id,
        description,
        primary_keys,
        partition_columns,
        features,
        creation_timestamp=None,
        online_stores=None,
        notebook_producers=None,
        job_producers=None,
        table_data_sources=None,
        path_data_sources=None,
        custom_data_sources=None,
        timestamp_keys=None,
        tags=None,
    ):

        """Initialize a FeatureTable object."""
        self.name = name
        self.table_id = table_id
        self.description = description
        self.primary_keys = primary_keys
        self.partition_columns = partition_columns
        self.features = features
        self.creation_timestamp = creation_timestamp
        self.online_stores = online_stores if online_stores is not None else []
        self.notebook_producers = (
            notebook_producers if notebook_producers is not None else []
        )
        self.job_producers = job_producers if job_producers is not None else []
        self.table_data_sources = (
            table_data_sources if table_data_sources is not None else []
        )
        self.path_data_sources = (
            path_data_sources if path_data_sources is not None else []
        )
        self.custom_data_sources = (
            custom_data_sources if custom_data_sources is not None else []
        )
        self.timestamp_keys = timestamp_keys if timestamp_keys is not None else []
        self._tags = tags

    @property
    @deprecated("FeatureTable.primary_keys", since="v0.3.6")
    def keys(self):
        return self.primary_keys

    @property
    def tags(self) -> Dict[str, str]:
        """
        Get the tags associated with the feature table.

        :return a Dictionary of all tags associated with the feature table as key/value pairs
        """
        if self._tags is None:
            # If no tags are set, self._tags is expected an empty dictionary.
            raise ValueError(
                "Internal error: tags have not been fetched for this FeatureTable instance"
            )
        return self._tags

    @classmethod
    def from_proto(cls, feature_table_proto: ProtoFeatureTable):
        """Return a FeatureStore object from a proto.

        Note: `repeated` proto fields are cast from
              `google.protobuf.pyext._message.RepeatedScalarContainer`
              to list.

        :param FeatureTable feature_table_proto: Prototype for a :class:`.FeatureTable` object.
        :return FeatureTable: a FeatureStore object from a proto.
        """
        return cls(
            name=feature_table_proto.name,
            table_id=feature_table_proto.id,
            description=feature_table_proto.description,
            primary_keys=list(feature_table_proto.primary_keys),
            partition_columns=list(feature_table_proto.partition_keys),
            features=list(feature_table_proto.features),
            creation_timestamp=feature_table_proto.creation_timestamp,
            online_stores=list(feature_table_proto.online_stores),
            notebook_producers=list(feature_table_proto.notebook_producers),
            job_producers=list(feature_table_proto.job_producers),
            table_data_sources=[
                s.table for s in feature_table_proto.data_sources if s.table
            ],
            path_data_sources=[
                s.path for s in feature_table_proto.data_sources if s.path
            ],
            custom_data_sources=[
                s.custom_source
                for s in feature_table_proto.data_sources
                if s.custom_source
            ],
            timestamp_keys=list(feature_table_proto.timestamp_keys),
            tags=None,
        )
