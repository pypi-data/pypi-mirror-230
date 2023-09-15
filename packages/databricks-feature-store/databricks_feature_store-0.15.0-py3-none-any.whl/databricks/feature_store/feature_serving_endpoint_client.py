import json
import os
import re
import sys
from typing import Dict, List, Optional, Union

import mlflow
from mlflow.entities.model_registry.model_version import ModelVersion
from mlflow.tracking import MlflowClient
from pyspark import TaskContext
from pyspark.sql import SparkSession

import databricks.feature_store.local_models as local_models
from databricks.feature_store.entities.feature_function import FeatureFunction
from databricks.feature_store.entities.feature_lookup import FeatureLookup
from databricks.feature_store.entities.feature_serving_endpoint import (
    EndpointCoreConfig,
    FeatureServingEndpoint,
    Servable,
)
from databricks.feature_store.entities.on_demand_column_info import OnDemandColumnInfo
from databricks.feature_store.utils import request_context, training_scoring_utils
from databricks.feature_store.utils.request_context import RequestContext
from databricks.feature_store.utils.rest_utils import http_request, verify_rest_response

# TODO(ML-32116): Remove this flag once the feature serving endpoint client is enabled.
ENABLE_FEATURE_SERVING_ENDPOINT_CLIENT = True

BASE_API_PATH = "/api/2.0/serving-endpoints"
MODEL_NAME_PREFIX = "feature-serving-model-"
SERVED_MODEL_NAME_PREFIX = "feature-serving-served-model-"

# Must be one or more characters including alphanumeric and dash. The first and
# last characters can only be alphanumeric.
ENDPOINT_NAME_REGEX = "^([a-zA-Z0-9][a-zA-Z0-9-]{0,62}[a-zA-Z0-9]|[a-zA-Z0-9])$"

ENDPOINT_STATE_MAPPING = {
    "NOT_UPDATING": "READY",
    "UPDATE_FAILED": "FAILED",
    "IN_PROGRESS": "IN_PROGRESS",
}

FSE_MODEL_DESC = (
    "A special model used internally by Feature & Function Serving. Do not delete or "
    "update this model otherwise serving endpoint may have unintended behavior."
)


def check_enable_flag(func):
    def wrapper(*args, **kwargs):
        if not ENABLE_FEATURE_SERVING_ENDPOINT_CLIENT:
            raise NotImplementedError
        return func(*args, **kwargs)

    return wrapper


class FeatureServingEndpointClient:
    def __init__(self, get_host_creds, fs_client):
        self._get_host_creds = get_host_creds
        self._endpoint_name_matcher = re.compile(ENDPOINT_NAME_REGEX)
        self._log_model_func = fs_client.log_model
        self._create_training_set = fs_client.create_training_set
        self._model_registry_uri = fs_client._model_registry_uri
        self._training_scoring_client = fs_client._training_scoring_client

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
        self._mlflow_client = MlflowClient()

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

    @check_enable_flag
    def create_feature_serving_endpoint(
        self,
        name: str,
        config: EndpointCoreConfig,
    ) -> FeatureServingEndpoint:
        # Run additional validation logic required for feature serving endpoints. Existing validation logic, such as
        # validating the uniqueness of FeatureFunction output names, are run as part of Feature Store client methods.
        servables = config.servables
        self._validate_endpoint_name(name)
        self._validate_no_renaming_in_feature_lookups(servables.features)
        self._verify_endpoint_not_exists(name)

        model_name = self._get_model_name(name)
        model_version = self._create_model(
            model_name=model_name,
            features=servables.features,
            extra_pip_requirements=servables.extra_pip_requirements,
        )

        request_body = self._get_create_endpoint_request_body(
            endpoint_name=name,
            model_version_number=model_version.version,
            workload_size=servables.workload_size,
            scale_to_zero_enabled=servables.scale_to_zero_enabled,
        )
        try:
            result = self._call_api(path="", method="POST", json_body=request_body)
        except Exception as e:
            # clean up the model when error returned from the backend
            self._mlflow_client.delete_registered_model(name=self._get_model_name(name))
            raise e
        return self._convert_to_feature_serving_endpoint(result)

    @check_enable_flag
    def get_feature_serving_endpoint(self, name) -> FeatureServingEndpoint:
        self._validate_endpoint_name(name)
        result = self._call_api(f"/{name}", method="GET", json_body={})
        return self._convert_to_feature_serving_endpoint(result)

    @check_enable_flag
    def delete_feature_serving_endpoint(self, name) -> None:
        self._validate_endpoint_name(name)
        self._call_api(f"/{name}", "DELETE", {})
        self._mlflow_client.delete_registered_model(name=self._get_model_name(name))

    def _list_endpoints(self):
        listresult = self._call_api(path="", method="GET", json_body=None)
        if "endpoints" in listresult:
            return listresult["endpoints"]
        else:
            # when the result is empty the key "endpoints" is missing.
            return []

    def _create_model(
        self,
        model_name: str,
        features: List[Union[FeatureLookup, FeatureFunction]],
        extra_pip_requirements: Optional[List[str]],
    ) -> ModelVersion:
        # To prevent the FS client being added to the model dependency, import IdentityModel
        # with manipulation to sys.path so that the class is imported as
        # <databricks_identity_model.IdentityModel>. This is necessary for SRTI to import the
        # file directly from Python path while loading the model.
        model_file = os.path.dirname(local_models.__file__)
        sys.path.append(model_file)
        from databricks_identity_model import IdentityModel

        sys.path.pop()

        model = IdentityModel()
        training_set = self._create_training_set(
            self._create_dummy_training_df(features),
            label=None,
            feature_lookups=features,
        )
        # Log model with identity_model copied into artifacts.
        self._log_model_func(
            model,
            model_name,
            flavor=mlflow.pyfunc,
            training_set=training_set,
            code_path=[os.path.join(model_file, "databricks_identity_model.py")],
            extra_pip_requirements=extra_pip_requirements,
        )
        model_version = self._register_model(model_name)
        self._update_model_description(model_name)
        return model_version

    def _register_model(self, model_name) -> ModelVersion:
        # The call to mlflow.pyfunc.log_model will create an active run, so it is safe to
        # obtain the run_id for the active run.
        run_id = mlflow.tracking.fluent.active_run().info.run_id

        # The call to mlflow.set_registry_uri sets the model registry globally, so it needs
        # to be set appropriately each time. If no model_registry_uri is specified, we pass
        # in an empty string to reset the model registry to the local one.
        mlflow.set_registry_uri(self._model_registry_uri or "")
        return mlflow.register_model(
            "runs:/%s/%s" % (run_id, model_name),
            model_name,
            await_registration_for=mlflow.tracking._model_registry.DEFAULT_AWAIT_MAX_SLEEP_SECONDS,
        )

    def _update_model_description(self, model_name) -> None:
        self._mlflow_client.update_registered_model(model_name, FSE_MODEL_DESC)

    def _validate_endpoint_name(self, name):
        if not self._endpoint_name_matcher.match(name):
            raise ValueError(
                "Endpoint name must only contain alphanumeric and dashes."
                " The first or last character cannot be dash"
            )

    def _verify_endpoint_not_exists(self, endpoint_name) -> None:
        existing_endpoints = self._list_endpoints()
        if endpoint_name in {endpoint["name"] for endpoint in existing_endpoints}:
            raise ValueError(f"Endpoint {endpoint_name} already exists")

    def _get_model_name(self, endpoint_name) -> str:
        return MODEL_NAME_PREFIX + endpoint_name

    def _get_create_endpoint_request_body(
        self,
        endpoint_name,
        model_version_number,
        workload_size,
        scale_to_zero_enabled,
    ) -> Dict:
        model_name = self._get_model_name(endpoint_name)
        # TODO(ML-28153): use protobuf to construct the request.
        served_models = [
            {
                "name": f"{SERVED_MODEL_NAME_PREFIX}{endpoint_name}",
                "model_name": model_name,
                "model_version": model_version_number,
                "workload_size": workload_size,
                "scale_to_zero_enabled": scale_to_zero_enabled,
            }
        ]
        return {
            "name": endpoint_name,
            "config": {
                "served_models": served_models,
            },
            "is_feature_serving": True,
        }

    def _create_dummy_training_df(
        self, features: List[Union[FeatureLookup, FeatureFunction]]
    ):
        req_context = RequestContext(request_context.CREATE_TRAINING_SET)

        feature_lookups = [f for f in features if isinstance(f, FeatureLookup)]
        feature_functions = [f for f in features if isinstance(f, FeatureFunction)]

        ft_metadata = training_scoring_utils.get_table_metadata(
            self._training_scoring_client._catalog_client,
            self._training_scoring_client._spark_client,
            feature_lookups,
            req_context,
        )

        # Collect OnDemandColumnInfos
        on_demand_column_infos = [
            OnDemandColumnInfo(
                udf_name=feature_function.udf_name,
                input_bindings=feature_function.input_bindings,
                output_name=feature_function.output_name,
            )
            for feature_function in feature_functions
        ]
        on_demand_inputs = [
            (input_name, odci)
            for odci in on_demand_column_infos
            for input_name in odci.input_bindings.values()
        ]
        on_demand_output_names = [odci.output_name for odci in on_demand_column_infos]

        # Collect FeatureColumnInfos
        feature_column_infos = training_scoring_utils.explode_feature_lookups(
            feature_lookups,
            ft_metadata.feature_table_features_map,
            ft_metadata.feature_table_metadata_map,
        )
        feature_inputs = [
            (input_name, fci)
            for fci in feature_column_infos
            for input_name in fci.lookup_key
        ]
        feature_output_names = [fci.output_name for fci in feature_column_infos]

        all_output_names = feature_output_names + on_demand_output_names

        # Get missing on demand inputs by comparing against all feature and function outputs
        missing_on_demand_inputs = [
            (input_name, odci)
            for (input_name, odci) in on_demand_inputs
            if input_name not in all_output_names
        ]

        # Get missing lookup inputs by comparing against all feature and function outputs
        missing_lookup_inputs = [
            (input_name, fci)
            for (input_name, fci) in feature_inputs
            if input_name not in all_output_names
        ]

        uc_function_infos = training_scoring_utils.get_uc_function_infos(
            self._training_scoring_client._information_schema_spark_client,
            {odci.udf_name for odci in on_demand_column_infos},
        )

        # schema is a list of human readable datatype strings such as "user_id int"
        schema = set()

        for input_name, odci in missing_on_demand_inputs:
            function_info = uc_function_infos[odci.udf_name]
            input_param = next(
                p
                for p in function_info.input_params
                if odci.input_bindings[p.name] == input_name
            )
            schema.add(f"{input_name} {input_param.type_text}")

        for feature_name, fci in missing_lookup_inputs:
            lookup_keys = fci.lookup_key
            table_keys = ft_metadata.feature_table_metadata_map[
                fci.table_name
            ].primary_keys
            for (lookup_key, table_key) in zip(lookup_keys, table_keys):
                data_type = (
                    ft_metadata.feature_table_data_map[fci.table_name]
                    .schema[table_key]
                    .dataType.simpleString()
                )
                schema.add(f"{lookup_key} {data_type}")

        return self._spark.createDataFrame([], ",".join(list(schema)))

    def _validate_no_renaming_in_feature_lookups(
        self, features: List[Union[FeatureLookup, FeatureFunction]]
    ):
        feature_lookups = [f for f in features if isinstance(f, FeatureLookup)]
        for lookup in feature_lookups:
            if len(lookup._rename_outputs):
                raise ValueError(
                    f"FeatureLookup rename_outputs is not allowed for feature serving endpoints"
                )

    # path starts with '/'
    # method can be GET/POST/etc
    def _call_api(self, path, method, json_body) -> Dict:
        api = BASE_API_PATH + path
        host_creds = self._get_host_creds()
        if method in ["GET", "DELETE"]:
            response = http_request(
                host_creds=host_creds,
                endpoint=api,
                method=method,
            )
        else:
            response = http_request(
                host_creds=host_creds,
                endpoint=api,
                method=method,
                json=json_body,
            )
        verify_rest_response(response=response, endpoint=api)
        return json.loads(response.text)

    def _convert_to_feature_serving_endpoint(
        self, json_result
    ) -> FeatureServingEndpoint:
        json_state = json_result["state"]["config_update"]
        return FeatureServingEndpoint(
            json_result["name"],
            json_result["creator"],
            json_result["creation_timestamp"],
            ENDPOINT_STATE_MAPPING.get(json_state, "UNKNOWN"),
        )
