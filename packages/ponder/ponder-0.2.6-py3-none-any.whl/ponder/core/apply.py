import logging
import random
import string
import sys

import numpy as np

from ponder.core.common import __SQL_QUERY_LEN_LIMIT__, get_execution_configuration

from .query_tree import QueryTreeNode, QueryTreeNodeDependency

logger = logging.getLogger(__name__)


class ApplyUDFNode(QueryTreeNode):
    def __init__(
        self,
        conn,
        node,
        func,
        output_column_list,
        output_column_types,
        db_output_column_types,
        axis,
        result_type,
        row_labels_dtypes,
        apply_type,
        na_action,
        func_args,
        func_kwargs,
    ):
        super().__init__(conn)
        self._func = func
        self._input_node = node

        self._function_name = f"""PONDER_{"".join(
            random.choices(string.ascii_uppercase, k=10)
        )}"""
        self._row_labels_dtypes = row_labels_dtypes
        self._apply_type = apply_type
        self._na_action = na_action
        self._func_args = (func_args,)
        self._func_kwargs = func_kwargs

        # We need the output_aliases_map so that we can get from the
        # output column aliases -> actual columns. We use aliases in the udtf
        # output since we can't always use the original column names. As a
        # result, we need to the output names for the query which we then just
        # map back to the original.
        output_column_aliases, output_aliases_map = self._conn.setup_udtf(
            self._function_name,
            func,
            self._input_node.get_column_names(),
            self._input_node.dtypes,
            output_column_list,
            db_output_column_types,
            node.get_order_column_name(),
            node.get_row_labels_column_names(),
            row_labels_dtypes,
            apply_type,
            na_action,
            func_args,
            func_kwargs,
        )

        # We don't have a good way of tracking this information, but we need to keep
        # a tab on the labels and position columns
        self._labels_and_pos_cols = [
            self.get_order_column_name()
        ] + self.get_row_labels_column_names()
        self._labels_and_pos_dtypes = [np.dtype(int)] + self._row_labels_dtypes

        self._output_column_names = output_column_aliases[:]
        self._output_aliases_map = output_aliases_map

        # Set the column_names and column_types, skipping over the order and labels
        # The reason we have to do this here is because the output_column_list and
        # output_column_types include the row and position columns. They need to bc
        # we include them as part of the UDTF to maintain the final order.
        self._column_names = []
        self._column_types = []
        for alias, dtype in zip(output_column_aliases, output_column_types):
            col_name = self._output_aliases_map[alias]
            if col_name not in self._labels_and_pos_cols:
                self._column_names.append(col_name)
                self._column_types.append(dtype)

    def get_column_names(self):
        return self._column_names

    def get_column_types(self):
        return self._column_types

    # Note: this assumption may not hold in the future
    def get_order_column_name(self):
        return self._input_node.get_order_column_name()

    # Note: this assumption may not hold in the future
    def get_row_labels_column_names(self):
        return self._input_node.get_row_labels_column_names()

    def generate_sql(self):
        # input_node has the CORRECT column names and types but does not include
        # the label and position columns. We correct that here by manually adding
        # it in for the sake of SQL generation. We don't actually want to modify
        # the column names and types in this node.
        input_node_sql = self._input_node.generate_sql()
        if (
            get_execution_configuration().mask_with_temp_table
            and len(input_node_sql) >= __SQL_QUERY_LEN_LIMIT__
        ):
            temp_table_name = self._conn.create_temp_table_name()
            (
                temp_table_create_sql,
                temp_table_project_sql,
            ) = self._conn._dialect.generate_temp_table_for_subquery(
                temp_table_name, input_node_sql
            )

            logger.debug(f"{self.__class__.__name__} {temp_table_name} being created")
            self._conn.run_query_and_return_results(temp_table_create_sql)
            logger.debug(f"{self.__class__.__name__} {temp_table_name} DONE")
            input_node_sql = temp_table_project_sql

        input_node_column_types = (
            self._input_node.get_column_types() + self._labels_and_pos_dtypes
        )
        sql_query = self._conn.generate_apply_command(
            input_node_sql,
            self._function_name,
            self._func,
            self._input_node.get_column_names() + self._labels_and_pos_cols,
            input_node_column_types,
            self._output_column_names,
            self._output_aliases_map,
            self._input_node.get_order_column_name(),
            self._input_node.get_row_labels_column_names(),
            self._apply_type,
            self._na_action,
            self._func_args,
            self._func_kwargs,
        )

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def data_hash(self):
        # df.apply can either result in a df with the same structure
        # or something entirely different
        if self._input_node.get_column_names() != self.get_column_names():
            hash(
                tuple(
                    dict.fromkeys(
                        (self._func, self._func_args, self._input_node.data_hash())
                    )
                )
            )
        else:
            return self._input_node.data_hash()

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            parents=[self._input_node],
            extras={
                "func": self._func,
                "function_name": self._function_name,
                "func_args": self._func_args,
                "func_kwargs": self._func_kwargs,
                "apply_type": self._apply_type,
                "na_action": self._na_action,
            },
        )


class ApplyStoredProcedureNode(QueryTreeNode):
    def __init__(
        self,
        conn,
        node,
        output_column_list,
        output_column_types,
        row_labels_column_name,
        row_labels_dtypes,
        func,
    ):
        super().__init__(conn)
        self._func = func
        self._input_node = node

        self._function_name = f"""PONDER_{"".join(
            random.choices(string.ascii_uppercase, k=10)
        )}"""

        self._materialized_table_name = f"""PONDER_{"".join(
            random.choices(string.ascii_uppercase, k=10)
        )}"""

        input_node_query = self._input_node.generate_sql()

        self._sql_query = self._conn.setup_stored_procedure_temp_table(
            input_node_query,
            func,
            self._function_name,
            self._materialized_table_name,
            output_column_list,
            output_column_types,
            row_labels_column_name,
            row_labels_dtypes[0],
        )

        metadata = conn.get_temp_table_metadata(self._materialized_table_name)
        # Unzip the metadata pairs:
        # [(col_0, type_0), (col_1, type_1)] => [[col_0, col_1], [type_0, type_1]]
        self._column_names, self._column_types = metadata

    def generate_sql(self):
        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {self._sql_query}"""
        )
        return self._sql_query

    def get_column_names(self):
        return self._column_names

    def get_column_types(self):
        return self._column_types

    def data_hash(self):
        return hash(self._materialized_table_name)

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            parents=[self._input_node],
            extras={
                "func": self._func,
                "function_name": self._function_name,
                "materialized_table_name": self._materialized_table_name,
            },
        )
