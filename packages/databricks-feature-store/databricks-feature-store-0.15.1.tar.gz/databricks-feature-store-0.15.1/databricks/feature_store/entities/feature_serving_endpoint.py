from typing import List, Optional, Union

from mlflow.utils import databricks_utils

from databricks.feature_store.entities._feature_store_object import _FeatureStoreObject
from databricks.feature_store.entities.feature_function import FeatureFunction
from databricks.feature_store.entities.feature_lookup import FeatureLookup

FEATURE_SERVING_ENDPOINT_PREFIX = "serving-endpoints"


class Servable(_FeatureStoreObject):
    def __init__(
        self,
        features: List[Union[FeatureLookup, FeatureFunction]],
        workload_size: str = "Small",
        scale_to_zero_enabled: bool = True,
        extra_pip_requirements: Optional[List[str]] = None,
    ):
        """
        A Servable is a group of features to be served and related configurations.
        :param features: A list of FeatureLookups and FeatureFunctions.
        :param workload_size: Allowed values are Small, Medium, Large.
        :param scale_to_zero_enabled: If enabled, the cluster size will scale to 0 when there is no traffic for certain amount of time.
        :param extra_pip_requirements: The requirements needed by FeatureFunctions.
        """
        self.features = features
        self.workload_size = workload_size
        self.scale_to_zero_enabled = scale_to_zero_enabled
        self.extra_pip_requirements = extra_pip_requirements


class EndpointCoreConfig(_FeatureStoreObject):
    def __init__(self, servables: Servable):
        self.servables = servables


class FeatureServingEndpoint(_FeatureStoreObject):
    def __init__(
        self,
        name: str,
        creator: str,
        creation_time_millis: int,
        state: str,
    ):
        self._name = name
        self._creator = creator
        self._creation_time_millis = creation_time_millis
        self._state = state

    @property
    def name(self) -> str:
        return self._name

    @property
    def creator(self) -> str:
        return self._creator

    @property
    def creation_time_millis(self) -> int:
        return self._creation_time_millis

    @property
    def state(self) -> str:
        """The state of the endpoint. Value could be READY, FAILED or IN_PROGRESS."""
        return self._state

    @property
    def url(self) -> str:
        return "/".join(
            [self._get_workspace_host(), FEATURE_SERVING_ENDPOINT_PREFIX, self.name]
        )

    def _get_workspace_host(self):
        local_host, _ = databricks_utils.get_workspace_info_from_dbutils()
        return local_host
