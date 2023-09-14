from typing import Tuple

import attrs

from tecton_core.query import nodes
from tecton_core.query.node_interface import QueryNode


@attrs.frozen
class PartialAggDuckDbNode(nodes.PartialAggNode):
    @classmethod
    def from_query_node(cls, query_node: nodes.PartialAggNode) -> QueryNode:
        return cls(
            input_node=query_node.input_node,
            fdw=query_node.fdw,
            window_start_column_name=query_node.window_start_column_name,
            window_end_column_name=query_node.window_end_column_name,
            aggregation_anchor_time=query_node.aggregation_anchor_time,
        )

    @property
    def columns(self) -> Tuple[str, ...]:
        # NOTE: this m13n schema will be computed based on whoever is running
        # the FVPipelineNode, which in ToP will be snowflake. This means
        # there are casing differences.
        cols = list(super().columns)
        # TODO(danny): Remove this hack for DuckDB (i.e. force including the anchor time since in Tecton on
        #  Snowflake, we don't include the anchor time in the m13n schema) once validation respects DuckDB mode for
        #  Snowflake SQL pipelines
        if self.window_start_column_name not in cols:
            cols.append(self.window_start_column_name)
            if self.fdw.time_key in cols:
                cols.remove(self.fdw.time_key)
        return tuple(cols)
