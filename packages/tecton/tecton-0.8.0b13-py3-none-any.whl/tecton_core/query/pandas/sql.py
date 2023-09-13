from typing import Union

import attrs
import pandas

from tecton_athena.athena_session import AthenaSession  # noqa: TID251


@attrs.frozen
class SqlExecutor:
    session: Union[AthenaSession]

    def read_sql(self, sql: str) -> pandas.DataFrame:
        raise NotImplementedError
