import logging
from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from urllib.parse import urlparse

import attrs
import pandas as pd
import pyarrow
from pyarrow import fs

from tecton_core import conf
from tecton_core.query.executor_params import QueryTreeStagingLocation
from tecton_core.query.executor_params import QueryTreeStep
from tecton_core.query.node_interface import NodeRef
from tecton_core.query.node_interface import QueryNode
from tecton_core.query.node_interface import recurse_query_tree
from tecton_core.query.node_utils import get_staging_nodes
from tecton_core.query.nodes import DataSourceScanNode
from tecton_core.query.nodes import MultiOdfvPipelineNode
from tecton_core.query.nodes import StagingNode
from tecton_core.query.nodes import UserSpecifiedDataNode
from tecton_core.query.query_tree_compute import QueryTreeCompute
from tecton_core.query.query_tree_compute import StagingConfig
from tecton_core.query.rewrite import QueryTreeRewriter


NUM_STAGING_PARTITIONS = 10
logger = logging.getLogger(__name__)


@dataclass
class QueryTreeOutput:
    # A map from table name to pyarrow table
    staged_data: Dict[str, pyarrow.Table]
    odfv_input_df: Optional[pd.DataFrame] = None
    result_df: Optional[pd.DataFrame] = None


@attrs.define
class QueryTreeExecutor:
    pipeline_compute: QueryTreeCompute
    agg_compute: QueryTreeCompute
    # TODO(danny): Consider separating aggregation from AsOfJoin, so we can process sub nodes and delete old
    #  tables in duckdb when doing `from_source=True`
    odfv_compute: QueryTreeCompute
    query_tree_rewriter: QueryTreeRewriter
    executor: ThreadPoolExecutor = attrs.field(init=False)
    s3fs: Optional[fs.S3FileSystem] = attrs.field(init=False)
    _temp_table_registered: Optional[Dict[str, set]] = None

    def __attrs_post_init__(self):
        # TODO(danny): Expose as configs
        self.executor = ThreadPoolExecutor(max_workers=10)
        awsAccessKey = conf.get_or_none("AWS_ACCESS_KEY_ID")
        awsSecretKey = conf.get_or_none("AWS_SECRET_ACCESS_KEY")
        awsSessionToken = conf.get_or_none("AWS_SESSION_TOKEN")
        if awsSecretKey and awsAccessKey:
            self.s3fs = fs.S3FileSystem(
                region="us-west-2",
                access_key=awsAccessKey,
                secret_key=awsSecretKey,
                session_token=awsSessionToken,
            )
        else:
            self.s3fs = None

    def cleanup(self):
        self.executor.shutdown()
        # TODO(danny): drop temp tables

    def exec_qt(self, qt_root: NodeRef) -> pd.DataFrame:
        # TODO(danny): make ticket to avoid needing setting a global SQL_DIALECT conf
        orig_dialect = conf.get_or_raise("SQL_DIALECT")
        try:
            if conf.get_bool("DUCKDB_DEBUG"):
                logger.warning(
                    "---------------------------------- Executing overall QT ----------------------------------"
                )
                logger.warning(f"QT: \n{qt_root.pretty_str(columns=True)}")
            # TODO(danny): refactor this into separate QT type
            if isinstance(qt_root.node, DataSourceScanNode):
                # This is used if the user is using GHF(entities=) or if the spine is tecton_ds.get_data_frame()
                conf.set("SQL_DIALECT", self.pipeline_compute.get_dialect())
                output_pa = self.pipeline_compute.run_sql(qt_root.to_sql(), return_dataframe=True)
                return output_pa.to_pandas()

            # Executes the feature view pipeline and stages into memory or S3
            output = self._exec_qt_node(qt_root, QueryTreeStep.PIPELINE)
            # Does partial aggregations (if applicable) and spine joins
            output = self._exec_qt_node(qt_root, QueryTreeStep.AGGREGATION, output)
            # Runs ODFVs (if applicable)
            output = self._exec_qt_node(qt_root, QueryTreeStep.ODFV, output)
            return output.result_df
        finally:
            # TODO(danny): remove staged data
            conf.set("SQL_DIALECT", orig_dialect)

    def _exec_qt_node(
        self,
        qt_node: NodeRef,
        query_tree_step: QueryTreeStep,
        prev_step_output: Optional[QueryTreeOutput] = None,
    ) -> QueryTreeOutput:
        if conf.get_bool("DUCKDB_DEBUG"):
            logger.warning(f"------------- Executing stage: {query_tree_step} -------------")
            logger.warning(f"QT: \n{qt_node.pretty_str(description=False)}")

        start_time = datetime.now()
        if query_tree_step == QueryTreeStep.PIPELINE:
            step_output = self._execute_pipeline_stage(qt_node)
            self.query_tree_rewriter.rewrite(qt_node, query_tree_step)
        elif query_tree_step == QueryTreeStep.AGGREGATION:
            step_output = self._execute_agg_stage(prev_step_output, qt_node)
            self.query_tree_rewriter.rewrite(qt_node, query_tree_step)
        elif query_tree_step == QueryTreeStep.ODFV:
            step_output = self._execute_odfv_stage(prev_step_output, qt_node)
        else:
            msg = f"Unexpected compute type {query_tree_step}"
            raise Exception(msg)

        if conf.get_bool("DUCKDB_BENCHMARK"):
            stage_done_time = datetime.now()
            logger.warning(f"{query_tree_step.name}_TIME_SEC: {(stage_done_time - start_time).total_seconds()}")
        return step_output

    def _execute_pipeline_stage(self, qt_node: NodeRef) -> QueryTreeOutput:
        conf.set("SQL_DIALECT", self.pipeline_compute.get_dialect())
        # TODO(danny): handle case where the spine is a sql query string, so no need to pull down as dataframe
        self._maybe_register_temp_tables(qt_root=qt_node, compute=self.pipeline_compute)

        # For STAGING: concurrently stage nodes matching the QueryTreeStep.PIPELINE filter
        staging_nodes_to_process = get_staging_nodes(qt_node, QueryTreeStep.PIPELINE)
        if len(staging_nodes_to_process) == 0:
            # There are no FV that rely on raw data (e.g. ODFV with request source)
            return QueryTreeOutput(staged_data={})
        staging_futures = self._stage_tables_and_load_pa(
            nodes_to_process=staging_nodes_to_process,
            compute=self.pipeline_compute,
        )
        staged_data = {}
        for future in staging_futures:
            table_name, pa_table = future.result()
            staged_data[table_name] = pa_table

        return QueryTreeOutput(staged_data=staged_data)

    def _execute_agg_stage(self, output: Optional[QueryTreeOutput], qt_node: NodeRef) -> QueryTreeOutput:
        # Need to explicitly set this dialect since it's used for creating the SQL command in QT `to_sql` commands
        conf.set("SQL_DIALECT", self.agg_compute.get_dialect())
        assert output

        # The AsOfJoins need access to a spine, which are registered here.
        self._maybe_register_temp_tables(qt_root=qt_node, compute=self.agg_compute)

        visited_tables = set()
        # Register staged pyarrow tables in agg compute
        for table_name, pa_table in output.staged_data.items():
            if conf.get_bool("DUCKDB_DEBUG"):
                logger.warning(f"Registering staged table to agg compute with schema:\n{pa_table.schema}")
            self.agg_compute.register_temp_table(table_name, pa_table)
            visited_tables.add(table_name)

        try:
            return self._process_agg_join(output, self.agg_compute, qt_node)
        finally:
            for table in visited_tables:
                self.agg_compute.run_sql(f"DROP TABLE IF EXISTS {table}")

    def _execute_odfv_stage(self, prev_step_output, qt_node):
        assert prev_step_output
        assert prev_step_output.odfv_input_df is not None
        has_odfvs = self._tree_has_odfvs(qt_node)
        if has_odfvs:
            result_df = self.odfv_compute.run_odfv(qt_node, prev_step_output.odfv_input_df)
        else:
            result_df = prev_step_output.odfv_input_df
        step_output = QueryTreeOutput(
            staged_data=prev_step_output.staged_data,
            odfv_input_df=prev_step_output.odfv_input_df,
            result_df=result_df,
        )
        return step_output

    def _tree_has_odfvs(self, qt_node):
        has_odfvs = False

        def check_for_odfv(node):
            if isinstance(node, MultiOdfvPipelineNode):
                nonlocal has_odfvs
                has_odfvs = True

        recurse_query_tree(
            qt_node,
            lambda node: check_for_odfv(node) if not has_odfvs else None,
        )
        return has_odfvs

    def _process_agg_join(
        self, output: QueryTreeOutput, compute: QueryTreeCompute, qt_node: NodeRef
    ) -> QueryTreeOutput:
        # TODO(danny): change the "stage" in the StagingNode to be more for the destination stage
        staging_nodes_to_process = get_staging_nodes(qt_node, QueryTreeStep.AGGREGATION)

        if len(staging_nodes_to_process) > 0:
            # There should be a single StagingNode. It is either there for materialization or ODFVs.
            assert len(staging_nodes_to_process) == 1
            staging_futures = self._stage_tables_and_load_pa(
                nodes_to_process=staging_nodes_to_process,
                compute=self.agg_compute,
            )
            assert len(staging_futures) == 1
            _, pa_table = staging_futures[0].result()
            odfv_input_df = pa_table.to_pandas()
            return QueryTreeOutput(staged_data=output.staged_data, odfv_input_df=odfv_input_df)

        # There are no StagingNodes, so we can execute the remainder of the query tree.
        output_df_pa = compute.run_sql(qt_node.to_sql(), return_dataframe=True)
        odfv_input_df = output_df_pa.to_pandas()
        return QueryTreeOutput(staged_data=output.staged_data, odfv_input_df=odfv_input_df)

    def _stage_tables_and_load_pa(
        self,
        nodes_to_process: List[QueryNode],
        compute: QueryTreeCompute,
    ) -> List[Future]:
        staging_futures = []
        for node in nodes_to_process:
            # TODO(danny): also process UserSpecifiedDataNode
            if isinstance(node, StagingNode):
                future = self.executor.submit(self._process_staging_node, node, compute)
                staging_futures.append(future)
        return staging_futures

    def _process_staging_node(self, qt_node: StagingNode, compute: QueryTreeCompute) -> Tuple[str, pyarrow.Table]:
        start_time = datetime.now()
        staging_table_name = qt_node.staging_table_name_unique()
        stage_dir_uri = None
        if qt_node.staging_destination_uri:
            stage_dir_uri = urlparse(f"{qt_node.staging_destination_uri.geturl()}{staging_table_name}")
        staging_config = StagingConfig(
            destination=qt_node.staging_location,
            sql_string=qt_node._to_staging_query_sql(),
            table_name=staging_table_name,
            stage_dir_uri=stage_dir_uri,
            num_partitions=NUM_STAGING_PARTITIONS,
        )
        maybe_memory_table = compute.stage(staging_config=staging_config)
        staging_done_time = datetime.now()
        if conf.get_bool("DUCKDB_DEBUG"):
            elapsed_staging_time = (staging_done_time - start_time).total_seconds()
            logger.warning(f"Stage {staging_table_name} elapsed: {elapsed_staging_time} seconds")

        if qt_node.staging_location == QueryTreeStagingLocation.MEMORY:
            assert maybe_memory_table is not None
            return staging_table_name, maybe_memory_table
        elif qt_node.staging_location in (
            QueryTreeStagingLocation.S3,
            QueryTreeStagingLocation.FILE,
        ):
            assert stage_dir_uri
            import pyarrow.parquet as pq

            if qt_node.staging_location == QueryTreeStagingLocation.S3:
                # Don't use full url since arrow expects only bucket/key instead of s3://bucket/key
                pa_table = pq.read_table(f"{stage_dir_uri.netloc}{stage_dir_uri.path}", filesystem=self.s3fs)
            else:
                pa_table = pq.read_table(stage_dir_uri.path)
            read_s3_time = datetime.now()
            if conf.get_bool("DUCKDB_DEBUG"):
                logger.warning(
                    f"Load from S3 {staging_table_name} elapsed: "
                    f"{(read_s3_time - staging_done_time).total_seconds()} seconds"
                )
            if conf.get_bool("DUCKDB_BENCHMARK"):
                logger.warning(f"S3_DATA_NBYTES_{staging_table_name}: {pa_table.nbytes}")
            return staging_table_name, pa_table
        else:
            msg = f"Unsupported staging mode: {qt_node.staging_location}"
            raise Exception(msg)

    def _maybe_register_temp_tables(self, qt_root: NodeRef, compute: QueryTreeCompute) -> None:
        self._temp_table_registered = self._temp_table_registered or {}

        dialect = compute.get_dialect()
        if dialect not in self._temp_table_registered:
            self._temp_table_registered[dialect] = set()

        def maybe_register_temp_table(node):
            if isinstance(node, UserSpecifiedDataNode):
                tmp_table_name = node.data._temp_table_name
                if tmp_table_name in self._temp_table_registered[dialect]:
                    return
                df = node.data.to_pandas()
                if conf.get_bool("DUCKDB_DEBUG"):
                    logger.warning(f"Registering user specified data with schema:\n{df.dtypes}")
                compute.register_temp_table_from_pandas(tmp_table_name, df)
                self._temp_table_registered[dialect].add(tmp_table_name)

        recurse_query_tree(
            qt_root,
            maybe_register_temp_table,
        )
