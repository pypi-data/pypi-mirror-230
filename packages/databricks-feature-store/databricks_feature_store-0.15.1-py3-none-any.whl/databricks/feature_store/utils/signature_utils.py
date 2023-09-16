import logging
from typing import Any, Dict, Optional

import mlflow
from mlflow.models import ModelSignature
from mlflow.types import ColSpec
from mlflow.types import DataType as MlflowDataType
from mlflow.types import Schema

from databricks.feature_store.entities.feature_column_info import FeatureColumnInfo
from databricks.feature_store.entities.feature_spec import FeatureSpec
from databricks.feature_store.entities.on_demand_column_info import OnDemandColumnInfo
from databricks.feature_store.entities.source_data_column_info import (
    SourceDataColumnInfo,
)

_logger = logging.getLogger(__name__)

# These types are unsupported due to MLflow signatures lacking any equivalent types.
# We thus cannot construct a ColSpec for any column that uses these types.
UNSUPPORTED_SPARK_TYPE_PREFIXES = ["array", "decimal", "map"]
# All supported feature store types must be either in this map or in
# UNSUPPORTED_SPARK_TYPE_PREFIXES
TYPE_MAP = {
    "smallint": MlflowDataType.integer,  # Upcast to integer
    "int": MlflowDataType.integer,
    "bigint": MlflowDataType.long,
    "float": MlflowDataType.float,
    "double": MlflowDataType.double,
    "boolean": MlflowDataType.boolean,
    "date": MlflowDataType.datetime,
    "timestamp": MlflowDataType.datetime,
    "string": MlflowDataType.string,
    "binary": MlflowDataType.binary,
}


def is_unsupported_type(type_str: str):
    return any(
        [type_str.startswith(prefix) for prefix in UNSUPPORTED_SPARK_TYPE_PREFIXES]
    )


def convert_spark_data_type_to_mlflow_signature_type(spark_type):
    """
    Maps Databricks SQL types to MLflow signature types.
    docs.databricks.com/sql/language-manual/sql-ref-datatypes.html#language-mappings
    """
    return TYPE_MAP.get(spark_type)


def get_input_schema_from_feature_spec(feature_spec: FeatureSpec) -> Schema:
    """
    Produces an MLflow signature schema from a feature spec.
    Source data columns are marked as required inputs and feature columns
    (both lookups and on-demand features) are marked as optional inputs.

    :param feature_spec: FeatureSpec object with datatypes for each column.
    """
    # If we're missing any data types for any column, we are likely dealing with a
    # malformed feature spec and should halt signature construction.
    if any([ci.data_type is None for ci in feature_spec.column_infos]):
        raise Exception("Training set does not contain column data types.")

    source_data_cols = [
        ci
        for ci in feature_spec.column_infos
        if isinstance(ci.info, SourceDataColumnInfo)
    ]
    # Don't create signature if any source data columns (required) are of complex types.
    if any(
        [
            ci.data_type is None or is_unsupported_type(ci.data_type)
            for ci in source_data_cols
        ]
    ):
        raise Exception(
            "Input DataFrame contains column data types not supported by "
            "MLflow model signatures."
        )
    required_input_colspecs = [
        ColSpec(
            convert_spark_data_type_to_mlflow_signature_type(ci.data_type),
            ci.info.output_name,
            optional=False,
        )
        for ci in source_data_cols
    ]
    feature_cols = [
        ci
        for ci in feature_spec.column_infos
        if isinstance(ci.info, (FeatureColumnInfo, OnDemandColumnInfo))
    ]
    unsupported_feature_cols = [
        ci for ci in feature_cols if is_unsupported_type(ci.data_type)
    ]
    optional_input_colspecs = [
        ColSpec(
            convert_spark_data_type_to_mlflow_signature_type(ci.data_type),
            ci.output_name,
            optional=True,
        )
        for ci in feature_cols
        if not is_unsupported_type(ci.data_type)
    ]
    if unsupported_feature_cols:
        feat_string = ", ".join(
            [f"{ci.output_name} ({ci.data_type})" for ci in unsupported_feature_cols]
        )
        _logger.warning(
            f"The following features will not be included in the input schema because their"
            f" data types are not supported by MLflow model signatures: {feat_string}. "
            f"These features cannot be overridden during model serving."
        )
    return Schema(required_input_colspecs + optional_input_colspecs)


def get_output_schema_from_labels(label_type_map: Optional[Dict[str, str]]) -> Schema:
    """
    Produces an MLflow signature schema from the provided label type map.
    :param label_type_map: Map label column name -> data type
    """
    if not label_type_map:
        raise Exception("Training set does not contain a label.")
    if any([is_unsupported_type(dtype) for dtype in label_type_map.values()]):
        raise Exception(
            "Labels are of data types not supported by MLflow model signatures."
        )
    else:
        output_colspecs = [
            ColSpec(
                convert_spark_data_type_to_mlflow_signature_type(spark_type),
                col_name,
                optional=False,
            )
            for col_name, spark_type in label_type_map.items()
        ]
        return Schema(output_colspecs)


def get_mlflow_signature_from_feature_spec(
    feature_spec: FeatureSpec,
    label_type_map: Optional[Dict[str, str]],
    override_output_schema: Optional[Schema],
    params: Optional[Dict[str, Any]] = None,
) -> Optional[ModelSignature]:
    """
    Produce an MLflow signature from a feature spec and label type map.
    Source data columns are marked as required inputs and feature columns
    (both lookups and on-demand features) are marked as optional inputs.

    Reads output types from the cached label -> datatype map in the training set.
    If override_output_schema is provided, it will always be used as the output schema.

    :param feature_spec: FeatureSpec object with datatypes for each column.
    :param label_type_map: Map of label column name -> datatype
    :param override_output_schema: User-provided output schema to use if provided.
    """
    kwargs = {}
    kwargs["inputs"] = get_input_schema_from_feature_spec(feature_spec)
    try:
        output_schema = override_output_schema or get_output_schema_from_labels(
            label_type_map
        )
        kwargs["outputs"] = output_schema
    except Exception as e:
        _logger.warning(f"Could not infer an output schema: {e}")

    if params:
        try:
            from mlflow.types.utils import _infer_param_schema

            kwargs["params"] = _infer_param_schema(params)
        except Exception as e:
            _logger.warning(f"Could not infer params schema: {e}")

    return mlflow.models.ModelSignature(**kwargs)


def drop_signature_inputs(signature):
    """
    Drop ModelSignature inputs field.
    This is useful for feature store model's raw_model.
    `params` support requires model containing a ModelSignature with
    `params` schema, whereas the feature store model's input schema
    does not apply to raw_model's input, so we would eliminate the inputs
    field of the model signature.

    :param signature: ModelSignature object.
    """
    if signature:
        outputs_schema = signature.outputs
        params_schema = signature.params if hasattr(signature, "params") else None
        try:
            # Only for mlflow>=2.6.0 ModelSignature contains params attribute
            if params_schema:
                return ModelSignature(outputs=outputs_schema, params=params_schema)
            elif outputs_schema:
                return ModelSignature(outputs=outputs_schema)
        except TypeError:
            _logger.warning(
                "ModelSignature without inputs is not supported, please upgrade "
                "mlflow >= 2.7.0 to use the feature."
            )
