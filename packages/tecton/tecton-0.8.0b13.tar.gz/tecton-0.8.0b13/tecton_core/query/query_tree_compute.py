import dataclasses
import logging
import os
import threading
import typing
from abc import ABC
from abc import abstractmethod
from typing import Optional
from urllib.parse import ParseResult

import attrs
import pandas as pd
import pyarrow
import sqlparse

from tecton_core import conf
from tecton_core.query.executor_params import QueryTreeStagingLocation
from tecton_core.query.node_interface import NodeRef
from tecton_core.query.sql_compat import Dialect


if typing.TYPE_CHECKING:
    import snowflake.snowpark
    from duckdb import DuckDBPyConnection

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class StagingConfig:
    destination: QueryTreeStagingLocation
    sql_string: str
    table_name: str
    num_partitions: Optional[int]
    stage_dir_uri: Optional[ParseResult]


class QueryTreeCompute(ABC):
    """
    Base class for compute (e.g. DWH compute or Python compute) which can be
    used for different stages of executing the query tree.
    """

    @abstractmethod
    def get_dialect(self) -> Dialect:
        pass

    @abstractmethod
    def run_sql(self, sql_string: str, return_dataframe: bool = False) -> Optional[pyarrow.Table]:
        pass

    @abstractmethod
    def run_odfv(self, qt_node: NodeRef, input_df: pd.DataFrame) -> pd.DataFrame:
        pass

    @abstractmethod
    def register_temp_table(self, table_name: str, pa_table: pyarrow.Table) -> None:
        pass

    # TODO(danny): remove this once we convert connectors to return arrow tables instead of pandas dataframes
    @abstractmethod
    def register_temp_table_from_pandas(self, table_name: str, pandas_df: pd.DataFrame) -> None:
        pass

    @abstractmethod
    def stage(self, staging_config: StagingConfig) -> Optional[pyarrow.Table]:
        pass


@attrs.frozen
class SnowflakeCompute(QueryTreeCompute):
    session: "snowflake.snowpark.Session"
    lock: threading.RLock = threading.RLock()

    def run_sql(self, sql_string: str, return_dataframe: bool = False) -> Optional[pyarrow.Table]:
        if conf.get_bool("DUCKDB_DEBUG"):
            sql_string = sqlparse.format(sql_string, reindent=True)
            logging.warning(f"SNOWFLAKE QT: run SQL {sql_string}")
        # Snowflake connections are not thread-safe. Launch Snowflake jobs without blocking the result. The lock is
        # released after the query is sent
        with self.lock:
            snowpark_df = self.session.sql(sql_string)
            if return_dataframe:
                # TODO(TEC-16169): check types are converted properly
                async_job = snowpark_df.toPandas(block=False)
            else:
                async_job = snowpark_df.collect(block=False)

        if return_dataframe:
            df = async_job.result(result_type="pandas")
            df = self._post_process_pandas(snowpark_df, df)
            return pyarrow.Table.from_pandas(df)
        else:
            async_job.result(result_type="no_result")
            return None

    @staticmethod
    def _post_process_pandas(snowpark_df: "snowflake.snowpark.DataFrame", pandas_df: pd.DataFrame) -> pd.DataFrame:
        """Converts a Snowpark DataFrame to a Pandas DataFrame while preserving types."""
        import snowflake.snowpark

        snowpark_schema = snowpark_df.schema

        for field in snowpark_schema:
            # TODO(TEC-16169): Handle other types.
            if field.datatype == snowflake.snowpark.types.LongType():
                pandas_df[field.name] = pandas_df[field.name].astype("int64")

        return pandas_df

    def get_dialect(self) -> Dialect:
        return Dialect.SNOWFLAKE

    def run_odfv(self, qt_node: NodeRef, input_df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError

    def register_temp_table_from_pandas(self, table_name: str, pandas_df: pd.DataFrame) -> None:
        # Not quoting identifiers / keeping the upload case-insensitive to be consistent with the query tree sql
        # generation logic, which is also case-insensitive. (i.e. will upper case selected fields).
        self.session.write_pandas(
            pandas_df,
            table_name=table_name,
            auto_create_table=True,
            table_type="temporary",
            quote_identifiers=False,
            overwrite=True,
        )

    def register_temp_table(self, table_name: str, pa_table: pyarrow.Table) -> None:
        self.register_temp_table_from_pandas(table_name, pa_table.to_pandas())

    def stage(self, staging_config: StagingConfig) -> Optional[pyarrow.Table]:
        if staging_config.destination == QueryTreeStagingLocation.MEMORY:
            df = self.run_sql(staging_config.sql_string, return_dataframe=True)
            return df

        if staging_config.destination == QueryTreeStagingLocation.S3:
            # TODO(danny): consider using pypika for this
            # TODO(danny): add temp credentials
            assert staging_config.stage_dir_uri
            final_sql = f"""
                COPY INTO '{staging_config.stage_dir_uri.geturl()}'
                FROM ({staging_config.sql_string})
                CREDENTIALS = (
                    AWS_KEY_ID='{conf.get_or_none('AWS_ACCESS_KEY_ID')}'
                    AWS_SECRET_KEY='{conf.get_or_none('AWS_SECRET_ACCESS_KEY')}'
                )
                FILE_FORMAT = (TYPE=parquet) MAX_FILE_SIZE = 32000000
                HEADER = TRUE
            """
            # Note: doesn't include a separate PARTITION BY since that slows down this query significantly
            self.run_sql(final_sql)
        elif staging_config.destination == QueryTreeStagingLocation.DWH:
            final_sql = f"""
                CREATE OR REPLACE TEMPORARY TABLE {staging_config.table_name} AS
                ({staging_config.sql_string});
            """

            self.run_sql(final_sql)
        else:
            msg = f"Unexpected staging destination type: {staging_config.destination}"
            raise Exception(msg)

        # Only returns df if it's in memory
        return None


@attrs.frozen
class DuckDBCompute(QueryTreeCompute):
    session: "DuckDBPyConnection"

    def run_sql(self, sql_string: str, return_dataframe: bool = False) -> Optional[pyarrow.Table]:
        # Notes on case sensitivity:
        # 1. DuckDB is case insensitive when referring to column names, though preserves the
        #    underlying data casing when exporting to e.g. parquet.
        #    See https://duckdb.org/2022/05/04/friendlier-sql.html#case-insensitivity-while-maintaining-case
        #    This means that when using Snowflake for pipeline compute, the view + m13n schema is auto upper-cased
        # 2. When there is a spine provided, the original casing of that spine is used (since DuckDB separately
        #    registers the spine).
        # 3. When exporting values out of DuckDB (to user, or for ODFVs), we coerce the casing to respect the
        #    explicit schema specified. Thus ODFV definitions should reference the casing specified in the dependent
        #    FV's m13n schema.
        if conf.get_bool("DUCKDB_DEBUG"):
            sql_string = sqlparse.format(sql_string, reindent=True)
            logging.warning(f"DUCKDB: run SQL {sql_string}")
        duckdb_relation = self.session.sql(sql_string)
        if return_dataframe:
            return duckdb_relation.arrow()
        return None

    def get_dialect(self) -> Dialect:
        return Dialect.DUCKDB

    def register_temp_table_from_pandas(self, table_name: str, pandas_df: pd.DataFrame) -> None:
        self.run_sql(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM pandas_df")

    def register_temp_table(self, table_name: str, pa_table: pyarrow.Table) -> None:
        # NOTE: alternatively, can page through table + insert with SELECT *
        # FROM pa_table LIMIT 100000 OFFSET 100000*<step>. This doesn't seem
        # to offer any memory benefits and only slows down the insert.
        self.run_sql(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM pa_table")

    def run_odfv(self, qt_node: NodeRef, input_df: pd.DataFrame) -> pd.DataFrame:
        # TODO: leverage duckdb udfs
        pass

    def stage(self, staging_config: StagingConfig) -> Optional[pyarrow.Table]:
        # First stage into an in memory table in DuckDB before exporting
        create_table_sql = f"""
            CREATE OR REPLACE TEMP TABLE {staging_config.table_name} AS ({staging_config.sql_string})
        """
        self.run_sql(create_table_sql)
        if staging_config.destination == QueryTreeStagingLocation.MEMORY:
            return self.run_sql(f"SELECT * FROM {staging_config.table_name}", return_dataframe=True)
        elif staging_config.destination == QueryTreeStagingLocation.S3:
            # TODO(danny): consider using pypika for this
            assert staging_config.stage_dir_uri
            final_sql = f"""
                LOAD httpfs;
                SET s3_region='us-west-2';
                SET s3_access_key_id='{conf.get_or_none('AWS_ACCESS_KEY_ID')}';
                SET s3_secret_access_key='{conf.get_or_none('AWS_SECRET_ACCESS_KEY')}';
                SET s3_session_token='{conf.get_or_none('AWS_SESSION_TOKEN')}';
                COPY {staging_config.table_name} TO '{staging_config.stage_dir_uri.geturl()}' (FORMAT PARQUET,
                PER_THREAD_OUTPUT TRUE);
            """
        elif staging_config.destination == QueryTreeStagingLocation.FILE:
            assert staging_config.stage_dir_uri
            stage_dir_folder = staging_config.stage_dir_uri.path
            os.makedirs(os.path.dirname(stage_dir_folder), exist_ok=True)
            final_sql = f"""
                COPY {staging_config.table_name} TO '{stage_dir_folder}' (FORMAT PARQUET, PER_THREAD_OUTPUT TRUE);
            """
        elif staging_config.destination == QueryTreeStagingLocation.DWH:
            final_sql = f"""
                CREATE OR REPLACE TEMPORARY TABLE {staging_config.table_name} AS
                ({staging_config.sql_string});
            """
        else:
            msg = f"Unexpected staging config type {staging_config.destination}"
            raise Exception(msg)

        # Only returns df if it's in memory
        self.run_sql(final_sql)
        return None


@attrs.frozen
class PandasCompute(QueryTreeCompute):
    def run_sql(self, sql_string: str, return_dataframe: bool = False) -> Optional[pyarrow.Table]:
        raise NotImplementedError

    def get_dialect(self) -> Dialect:
        return Dialect.PANDAS

    def register_temp_table_from_pandas(self, table_name: str, pandas_df: pd.DataFrame) -> None:
        raise NotImplementedError

    def register_temp_table(self, table_name: str, pa_table: pyarrow.Table) -> None:
        raise NotImplementedError

    def run_odfv(self, qt_node: NodeRef, input_df: pd.DataFrame) -> pd.DataFrame:
        from tecton_core.query.pandas.translate import pandas_convert_odfv_only

        if conf.get_bool("DUCKDB_DEBUG"):
            logger.warning(f"Input dataframe to ODFV execution: {input_df.dtypes}")

        pandas_node = pandas_convert_odfv_only(qt_node, input_df)
        return pandas_node.to_dataframe()

    def stage(self, staging_config: StagingConfig) -> Optional[pyarrow.Table]:
        raise NotImplementedError
