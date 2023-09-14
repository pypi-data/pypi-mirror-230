import tempfile
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Union

import pandas as pd
from pyspark import sql as pyspark_sql
from pyspark.sql import streaming as pyspark_streaming

from tecton import tecton_context
from tecton import types as sdk_types
from tecton._internals import ingest_utils
from tecton._internals import type_utils
from tecton.framework.data_frame import TectonDataFrame
from tecton.tecton_context import TectonContext
from tecton_core import materialization_context
from tecton_core import schema
from tecton_core import schema_derivation_utils as core_schema_derivation_utils
from tecton_core import specs
from tecton_proto.args import feature_view_pb2
from tecton_proto.args import virtual_data_source_pb2 as virtual_data_source__args_pb2
from tecton_proto.common import schema_pb2
from tecton_proto.common import spark_schema_pb2
from tecton_spark import data_source_helper
from tecton_spark import schema_derivation_utils
from tecton_spark import schema_spark_utils
from tecton_spark import spark_schema_wrapper


_CHECKPOINT_DIRECTORIES: List[tempfile.TemporaryDirectory] = []


def start_stream_preview(
    data_source: specs.DataSourceSpec,
    table_name: str,
    apply_translator: bool,
    option_overrides: Optional[Dict[str, str]],
) -> pyspark_streaming.StreamingQuery:
    df = get_stream_preview_dataframe(data_source, apply_translator, option_overrides)

    # Set a tempdir checkpointLocation. This is needed for the stream preview to work in EMR notebooks. The
    # TemporaryDirectory object handles cleaning up the temporary directory when it is destroyed, so add the object to
    # a global list that will be cleaned up with the program exits. (This isn't guaranteed - but it's not the end of
    # the world if we leak some temporary directories.)
    d = tempfile.TemporaryDirectory()
    _CHECKPOINT_DIRECTORIES.append(d)

    return (
        df.writeStream.format("memory")
        .queryName(table_name)
        .option("checkpointLocation", d.name)
        .outputMode("append")
        .start()
    )


def get_stream_preview_dataframe(
    data_source: specs.DataSourceSpec, apply_translator: bool, option_overrides: Optional[Dict[str, str]]
) -> pyspark_sql.DataFrame:
    """
    Helper function that allows start_stream_preview() to be unit tested, since we can't easily unit test writing
    to temporary tables.
    """
    spark = tecton_context.TectonContext.get_instance()._spark

    if apply_translator or isinstance(data_source.stream_source, specs.SparkStreamSourceSpec):
        return data_source_helper.get_ds_dataframe(
            spark, data_source, consume_streaming_data_source=True, stream_option_overrides=option_overrides
        )
    else:
        return data_source_helper.get_non_dsf_raw_stream_dataframe(spark, data_source.stream_source, option_overrides)


def derive_view_schema_for_feature_view(
    fv_args: feature_view_pb2.FeatureViewArgs,
    transformations: Sequence[specs.TransformationSpec],
    data_sources: Sequence[specs.DataSourceSpec],
) -> schema_pb2.Schema:
    spark = TectonContext.get_instance()._spark
    return schema_derivation_utils.get_feature_view_view_schema(spark, fv_args, transformations, data_sources)


def spark_schema_to_tecton_schema(spark_schema: spark_schema_pb2.SparkSchema) -> schema_pb2.Schema:
    wrapper = spark_schema_wrapper.SparkSchemaWrapper.from_proto(spark_schema)
    return schema_spark_utils.schema_from_spark(wrapper.unwrap()).proto


def derive_materialization_schema_for_feature_view(
    view_schema: schema_pb2.Schema,
    feature_view_args: feature_view_pb2.FeatureViewArgs,
) -> schema_pb2.Schema:
    is_aggregate = len(feature_view_args.materialized_feature_view_args.aggregations) > 0
    if not is_aggregate:
        return view_schema

    return core_schema_derivation_utils.compute_aggregate_materialization_schema_from_view_schema(
        view_schema, feature_view_args, is_spark=True
    )


def derive_view_schema_for_feature_table(
    fv_args: feature_view_pb2.FeatureViewArgs,
) -> schema_pb2.Schema:
    output_schema = fv_args.feature_table_args.schema
    wrapper = spark_schema_wrapper.SparkSchemaWrapper.from_proto(output_schema)


def derive_batch_schema(
    ds_args: virtual_data_source__args_pb2.VirtualDataSourceArgs,
    batch_post_processor: Optional[Callable],
    batch_data_source_function: Optional[Callable],
) -> spark_schema_pb2.SparkSchema:
    spark = TectonContext.get_instance()._spark
    return schema_derivation_utils.derive_batch_schema(spark, ds_args, batch_post_processor, batch_data_source_function)


def derive_stream_schema(
    ds_args: virtual_data_source__args_pb2.VirtualDataSourceArgs,
    stream_post_processor: Optional[Callable],
    stream_data_source_function: Optional[Callable],
) -> spark_schema_pb2.SparkSchema:
    spark = TectonContext.get_instance()._spark
    return schema_derivation_utils.derive_stream_schema(
        spark, ds_args, stream_post_processor, stream_data_source_function
    )


_TRANSFORMATION_RUN_TEMP_VIEW_PREFIX = "_tecton_transformation_run_"
CONST_TYPE = Union[str, int, float, bool]


def run_transformation_mode_spark_sql(
    *inputs: Union[pd.DataFrame, pd.Series, TectonDataFrame, pyspark_sql.DataFrame, CONST_TYPE],
    transformer: Callable,
    context: materialization_context.BaseMaterializationContext = None,
    transformation_name: str,
) -> TectonDataFrame:
    def create_temp_view(df, dataframe_index) -> str:
        df = TectonDataFrame._create(df).to_spark()
        temp_view = f"{_TRANSFORMATION_RUN_TEMP_VIEW_PREFIX}{transformation_name}_input_{dataframe_index}"
        df.createOrReplaceTempView(temp_view)
        return temp_view

    args = [create_temp_view(v, i) if not isinstance(v, CONST_TYPE.__args__) else v for i, v in enumerate(inputs)]
    if context is not None:
        args.append(context)

    spark = TectonContext.get_instance()._get_spark()
    return TectonDataFrame._create(spark.sql(transformer(*args)))


def run_transformation_mode_pyspark(
    *inputs: Union[pd.DataFrame, pd.Series, TectonDataFrame, pyspark_sql.DataFrame, CONST_TYPE],
    transformer: Callable,
    context: materialization_context.BaseMaterializationContext,
) -> TectonDataFrame:
    args = [TectonDataFrame._create(v).to_spark() if not isinstance(v, CONST_TYPE.__args__) else v for v in inputs]
    if context is not None:
        args.append(context)

    return TectonDataFrame._create(transformer(*args))


def write_dataframe_to_path_or_url(
    df: Union[pyspark_sql.DataFrame, pd.DataFrame], df_path: str, upload_url: str, view_schema: schema.Schema
):
    """Used for Feature Table ingest and deleting keys."""
    # We write in the native format and avoid converting Pandas <-> Spark due to partially incompatible
    # type system, in specifically missing Int in Pandas
    if isinstance(df, pyspark_sql.DataFrame):
        df.write.parquet(df_path)
        return

    if upload_url:
        ingest_utils.upload_df_pandas(upload_url, df)
    elif df_path:
        spark_df = ingest_utils.convert_pandas_to_spark_df(df, view_schema)
        spark_df.write.parquet(df_path)


def get_request_schema_from_tecton_schema(tecton_schema: schema_pb2.Schema) -> List[sdk_types.Field]:
    """Convert TectonSchema into a list of Tecton Fields."""
    columns_and_types = schema.Schema(tecton_schema).column_name_and_data_types()
    request_schema = []
    for c_and_t in columns_and_types:
        name = c_and_t[0]
        data_type = type_utils.sdk_type_from_tecton_type(c_and_t[1])
        request_schema.append(sdk_types.Field(name, data_type))
    return request_schema
