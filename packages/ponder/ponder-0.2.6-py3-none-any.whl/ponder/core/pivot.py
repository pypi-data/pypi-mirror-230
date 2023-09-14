import copy
import logging
import sys

from .common import generate_column_name_from_value
from .query_tree import QueryTreeNode, QueryTreeNodeDependency

logger = logging.getLogger(__name__)


class PivotNode(QueryTreeNode):
    def __init__(
        self,
        conn,
        input_node,
        grouping_column_name,
        pivot_column_name,
        values_column_name,
        unique_values,
        aggfunc,
        add_qualifier_to_new_column_names=True,
    ):
        super(PivotNode, self).__init__(conn)
        self._input_node = input_node
        self._grouping_column_name = grouping_column_name
        self._pivot_column_name = pivot_column_name
        self._values_column_name = values_column_name
        self._unique_values = unique_values
        self._aggfunc = aggfunc
        self._add_qualifier_to_new_column_names = add_qualifier_to_new_column_names

    def generate_sql(self):
        sql_query = self._conn.generate_pivot(
            self._grouping_column_name,
            self._pivot_column_name,
            self._values_column_name,
            self._unique_values,
            self._input_node,
            self._aggfunc,
            self._add_qualifier_to_new_column_names,
        )

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def get_column_names(self):
        string_vals = [
            generate_column_name_from_value(value) for value in self._unique_values
        ]
        ret_col_vals = [
            f"{self._values_column_name}_{val}"
            if self._add_qualifier_to_new_column_names
            else val
            for val in string_vals
        ]
        if self._grouping_column_name is not None:
            return [self._grouping_column_name] + ret_col_vals
        else:
            return ret_col_vals

    def get_row_labels_column_names(self):
        return (
            [self._grouping_column_name]
            if self._grouping_column_name is not None
            else []
        )

    def get_column_types(self):
        ret_dtypes_column_names = (
            [self._grouping_column_name]
            if self._grouping_column_name is not None
            else []
        )
        ret_dtypes_column_names.extend(
            ([self._values_column_name] * len(self._unique_values))
        )
        input_node_dtypes = copy.deepcopy(
            self._input_node.dtypes[ret_dtypes_column_names]
        ).reset_index(drop=True)
        return input_node_dtypes.tolist()

    def data_hash(self):
        return self._input_node.data_hash()

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            parents=[self._input_node],
            extras={
                "grouping_column_name": self._grouping_column_name,
                "pivot_column_name": self._pivot_column_name,
                "values_column_name": self._values_column_name,
                "unique_values": self._unique_values,
                "aggfunc": self._aggfunc,
            },
        )
