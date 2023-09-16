from databricks.feature_store.api.proto.feature_catalog_pb2 import (
    FeatureSpecInfo as ProtoFeatureSpecInfo,
)
from databricks.feature_store.entities._feature_store_object import _FeatureStoreObject


class FeatureSpecInfo(_FeatureStoreObject):
    """
    Value class describing a feature spec.

    This will typically not be instantiated directly, instead the
    :meth:`FeatureStoreClient.create_feature_spec <databricks.feature_store.client.FeatureStoreClient.create_feature_spec>`
    will create :class:`.FeatureSpecInfo` objects.
    """

    def __init__(
        self,
        name,
        creator,
        creation_timestamp_ms,
    ):

        """Initialize a FeatureSpecInfo object."""
        self.name = name
        self.creator = creator
        self.creation_timestamp_ms = creation_timestamp_ms

    @classmethod
    def from_proto(cls, feature_spec_info_proto: ProtoFeatureSpecInfo):
        """Return a FeatureSpecInfo object from a proto.

        :param ProtoFeatureSpecInfo feature_spec_info_proto: Prototype for a :class:`.FeatureSpecInfo` object.
        :return FeatureSpecInfo: a FeatureSpecInfo object from a proto.
        """
        return cls(
            name=feature_spec_info_proto.name,
            creator=feature_spec_info_proto.creator,
            creation_timestamp_ms=feature_spec_info_proto.creation_timestamp_ms,
        )
