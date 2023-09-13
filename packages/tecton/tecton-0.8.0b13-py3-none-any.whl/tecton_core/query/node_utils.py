from collections import deque
from typing import Deque
from typing import List
from typing import Union

from tecton_core.query import sql_compat
from tecton_core.query.executor_params import QueryTreeStep
from tecton_core.query.node_interface import NodeRef
from tecton_core.query.node_interface import QueryNode
from tecton_core.query.node_interface import recurse_query_tree
from tecton_core.query.nodes import FeatureViewPipelineNode
from tecton_core.query.nodes import StagingNode
from tecton_proto.args.transformation_pb2 import TransformationMode


def get_staging_nodes(qt_root: NodeRef, query_tree_step: QueryTreeStep) -> List[QueryNode]:
    """Returns all StagingNodes in the query tree that belong to the specified QueryTreeStep."""
    staging_nodes = []
    queue: Deque = deque()
    queue.append(qt_root)
    while len(queue) > 0:
        curr_node = queue.pop().node
        if isinstance(curr_node, StagingNode) and curr_node.query_tree_step == query_tree_step:
            staging_nodes.append(curr_node)
            continue
        for child_node_ref in curr_node.inputs:
            queue.append(child_node_ref)
    return staging_nodes


def get_first_input_node_of_class(
    qt_root: NodeRef, node_class: type, as_node_ref: bool = False
) -> Union[QueryNode, NodeRef, None]:
    """Returns the first node in the query tree that is an instance of the specified class.

    Optionally returns the NodeRef instead of the QueryNode itself.
    """
    if isinstance(qt_root.node, node_class):
        return qt_root if as_node_ref else qt_root.node

    for child in qt_root.node.inputs:
        node = get_first_input_node_of_class(child, node_class, as_node_ref=as_node_ref)
        if node is not None:
            return node
    return None


def get_dialect(qt_root: NodeRef) -> sql_compat.Dialect:
    """Returns the dialect of the query tree. Raises an error if more than one dialect is present."""
    encountered_dialects = set()

    def _extract_dialect_from_fv(node: FeatureViewPipelineNode) -> None:
        nonlocal encountered_dialects
        transform_specs = node.feature_definition_wrapper.transformations
        for transform_spec in transform_specs:
            mode = transform_spec.transformation_mode
            if mode == TransformationMode.TRANSFORMATION_MODE_PYTHON:
                encountered_dialects.add(sql_compat.Dialect.PANDAS)
            elif mode == TransformationMode.TRANSFORMATION_MODE_SPARK_SQL:
                encountered_dialects.add(sql_compat.Dialect.SPARK)
            elif mode == TransformationMode.TRANSFORMATION_MODE_PYSPARK:
                encountered_dialects.add(sql_compat.Dialect.SPARK)
            elif mode == TransformationMode.TRANSFORMATION_MODE_SNOWPARK:
                # TODO(danny): should probably be a snowpark dialect
                encountered_dialects.add(sql_compat.Dialect.SNOWFLAKE)
            elif mode == TransformationMode.TRANSFORMATION_MODE_SNOWFLAKE_SQL:
                encountered_dialects.add(sql_compat.Dialect.SNOWFLAKE)
            elif mode == TransformationMode.TRANSFORMATION_MODE_PANDAS:
                encountered_dialects.add(sql_compat.Dialect.PANDAS)

    recurse_query_tree(
        qt_root,
        lambda node: _extract_dialect_from_fv(node) if isinstance(node, FeatureViewPipelineNode) else None,
    )

    if len(encountered_dialects) > 1:
        msg = f"Cannot have multiple types of transformation modes: {encountered_dialects}"
        raise Exception(msg)

    if len(encountered_dialects) == 0:
        # TODO: Do not fall back on SQL_DIALECT, as this can be very confusing.
        return sql_compat.dialect()
    return encountered_dialects.pop()
