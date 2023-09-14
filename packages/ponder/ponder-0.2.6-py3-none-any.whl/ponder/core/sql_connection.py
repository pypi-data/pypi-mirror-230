from __future__ import annotations

import copy
import logging
import random
import string
import sys
from typing import Iterable, Optional

import cloudpickle
import numpy as np
import pandas
from pandas.api.types import is_object_dtype
from pandas.core.dtypes.common import pandas_dtype

import ponder.core.registry as registry
from ponder.core.common import get_execution_configuration
from ponder.core.connection_dialect_mixin import ConnectionDialectPassthroughMixin
from ponder.core.dataframequerytreehelper import DFCaseFold
from ponder.core.error_codes import PonderError, make_exception

from .abstract_connection import AbstractConnection
from .common import (
    __PONDER_ORDER_COLUMN_NAME__,
    __PONDER_REDUCED_COLUMN_NAME__,
    __PONDER_ROW_LABELS_COLUMN_NAME__,
    __ROWID_VALUE_SIZE_TO_MATERIALIZE__,
    __SQL_QUERY_LEN_LIMIT__,
    APPLY_FUNCTION,
    copying_cache,
    groupby_view_funcs,
    groupby_window_funcs,
)
from .query_tree import (
    BinaryPredicate,
    ColumnWiseReduceNode,
    MapNode,
    RowWiseReduceNode,
)

logger = logging.getLogger(__name__)


class SQLConnection(ConnectionDialectPassthroughMixin, AbstractConnection):
    def __init__(self, connection, dialect):
        if dialect is None:
            raise make_exception(
                RuntimeError,
                PonderError.PONDER_DIALECT_NOT_SET,
                "Dialect not set for connection",
            )
        self._dialect = dialect

        # user connection object
        self._connection = connection
        self.materialized_tables = {}
        self.materialized_udfs = {}
        self.table_materialization_time = {}
        self._query_timeout = get_execution_configuration().query_timeout
        # Call the initializers/license checks specific to that connection
        # this may involve multiple queries
        self.check_license()
        self.initialize(self._connection, self._dialect)

    def check_license(self):
        registry.validate_engine_license(self._connection)

    def initialize(self, connection, dialect):
        # Nothing to do here, specific to this connection class
        raise make_exception(
            RuntimeError,
            PonderError.PONDER_UNKNOWN_USAGE_NOT_ENABLED,
            "connection initializer must be overridden",
        )

    def get_user_connection(self):
        return self._connection

    def case_insensitive_identifiers(self):
        return False

    def case_fold_identifiers(self):
        return DFCaseFold.NO_FOLD

    def default_materialize_pandas_dataframe_as_table(
        self, table_name, pandas_dataframe, order_column_name
    ):
        create_sql = self._dialect.generate_create_table_command(
            table_name,
            pandas_dataframe.columns,
            pandas_dataframe.dtypes,
            order_column_name,
            None,
            True,
            False,
        )
        query = f"INSERT INTO {self._dialect.format_table_name(table_name)} VALUES "
        values = pandas_dataframe.to_numpy(na_value=None)

        def convert(x):
            import datetime

            if isinstance(x, pandas.Timestamp):
                return f"'{str(x)}'"
            if isinstance(x, datetime.date):
                return str(x)
            if x is None:
                return "NULL"
            # ensure all strings have quotes
            if isinstance(x, str):
                return f"'{x}'"
            return x

        def convert_arr(arr):
            return [convert(val) for val in arr]

        values = [convert_arr(col) for col in values]
        tuples = [tuple(x) for x in values]

        def tuple_block(iterable, block_size=1000):
            length = len(iterable)
            for ndx in range(0, length, block_size):
                yield iterable[ndx : min(ndx + block_size, length)]

        self.run_query_no_results(create_sql)
        for block in tuple_block(tuples, block_size=1000):
            # We have to do this value by value to make sure
            # "NULL" is written as a literal, where as other
            # strings are quoted (see convert fn above)
            insert_values = ", ".join(
                "(" + ", ".join(str(item) for item in tuple_item) + ")"
                for tuple_item in block
            )
            insert_query = query + insert_values
            self.run_query_no_results(insert_query)
        return table_name

    ##################################################
    # Functions which require introspecting the query tree
    # or introspecting the connection
    ##################################################

    def execute(self, tree_node):
        # interpret the tree
        # fire off execution
        tree_node_sql = tree_node.generate_sql()
        self.run_query_and_return_results(tree_node_sql)

    def _run_query_and_return_dataframe_uncached(self, query):
        return self.run_query_and_return_results(query)

    def run_query_and_return_dataframe(self, query, use_cache: bool):
        return (
            self._run_query_and_return_dataframe_cached(query)
            if use_cache
            else self._run_query_and_return_dataframe_uncached(query)
        )

    # Use the cache decorator to cache dataframe results with query string as cache key.
    # use copying_cache because the result is mutable and we don't want one caller to
    # mutate the cached result that we provide to another caller.
    @copying_cache
    def _run_query_and_return_dataframe_cached(self, query):
        return self._run_query_and_return_dataframe_uncached(query)

    def get_row_transfer_limit(self):
        return get_execution_configuration().row_transfer_limit

    def create_temp_table_name(self):
        return f"""Ponder_{"".join(
                random.choices(string.ascii_lowercase, k=10)
            )}"""

    def get_temp_table_metadata(self, table_name):
        read_metadata_command = self._dialect.generate_read_table_metadata_statement(
            table_name
        )
        # We sometimes read metadata directly from tables the user knows about and may
        # change, e.g. "CUSTOMER", as opposed to temporary tables like
        # "Ponder_hgxuixrlzr". Metadata for such queries can change between read_sql()
        # calls, so don't cache the results.
        df = self.run_query_and_return_dataframe(read_metadata_command, use_cache=False)
        df = df.loc[
            :,
            ~df.columns.isin(
                (
                    __PONDER_ORDER_COLUMN_NAME__,
                    __PONDER_ROW_LABELS_COLUMN_NAME__,
                    # Some databases (redshift) will have these as lower-case
                    __PONDER_ORDER_COLUMN_NAME__.lower(),
                    __PONDER_ROW_LABELS_COLUMN_NAME__.lower(),
                )
            ),
        ]
        return (df.columns.tolist(), df.dtypes.tolist())

    def get_last_table_update_time(self, table_name):
        # if the table name passed to us is really a query, we'll have to parse
        # the query to find the individual table names.  We can cross that
        # bridge when we get to it. For now return null.
        if self._dialect.is_query_like(table_name):
            return None
        result = self.run_query_and_return_results(
            self._dialect.generate_find_last_altered_time_command(
                self._database, self._schema, table_name
            )
        )
        if len(result) == 0:
            return None
        return result[0][0]

    def get_num_rows(self, tree_node):
        sql = tree_node.get_root().generate_sql()
        result = self.run_query_and_return_results(
            self._dialect.generate_select_count_star_statement(sql)
        )
        return result[0][0]

    def generate_join(
        self,
        tree_node_left,
        tree_node_right,
        select_list,
        how,
        left_on,
        right_on,
        left_order_column_name,
        right_order_column_name,
        result_order_column_name,
        db_index_column_name: Optional[list],
        indicator,
    ):
        if indicator and "_merge" in select_list:
            # make a copy else the query tree node's column list
            # will change.  We remove the column named "_merge" here
            # 'cuz the dialect will add it with the correct syntax later.
            new_select_list = select_list[:]
            new_select_list.remove("_merge")
            select_list = new_select_list

        left_node_query = tree_node_left.generate_sql()

        if (
            get_execution_configuration().mask_with_temp_table
            and len(left_node_query) >= __SQL_QUERY_LEN_LIMIT__
        ):
            temp_table_name = self.create_temp_table_name()
            (
                temp_table_create_sql,
                temp_table_project_sql,
            ) = self._dialect.generate_temp_table_for_subquery(
                temp_table_name, left_node_query
            )
            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} being created"""
            )
            self.run_query_and_return_results(temp_table_create_sql)
            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} DONE"""
            )
            left_node_query = temp_table_project_sql

        right_node_query = tree_node_right.generate_sql()
        if (
            get_execution_configuration().mask_with_temp_table
            and len(right_node_query) >= __SQL_QUERY_LEN_LIMIT__
        ):
            temp_table_name = self.create_temp_table_name()
            (
                temp_table_create_sql,
                temp_table_project_sql,
            ) = self._dialect.generate_temp_table_for_subquery(
                temp_table_name, right_node_query
            )

            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} being created"""
            )
            self.run_query_and_return_results(temp_table_create_sql)
            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} DONE"""
            )
            right_node_query = temp_table_project_sql

        join_query_sql = self._dialect.generate_join_command(
            select_list,
            left_node_query,
            right_node_query,
            how,
            left_on,
            right_on,
            left_order_column_name,
            right_order_column_name,
            result_order_column_name,
            db_index_column_name,
            indicator,
        )
        return join_query_sql

    def generate_join_asof(
        self,
        tree_node_left,
        tree_node_right,
        left_on,
        right_on,
        left_by,
        right_by,
        tolerance,
        allow_exact_matches,
        direction,
        left_order_column_name,
        right_order_column_name,
        result_order_column_name,
    ):
        select_list = tree_node_left.get_column_names()[:]
        select_list.extend(tree_node_right.get_column_names())

        left_node_query = tree_node_left.generate_sql()
        right_node_query = tree_node_right.generate_sql()

        join_asof_sql = self._dialect.generate_join_asof_command(
            left_node_query,
            tree_node_left.get_column_names(),
            right_node_query,
            tree_node_right.get_column_names(),
            left_on,
            right_on,
            left_by,
            right_by,
            tolerance,
            allow_exact_matches,
            direction,
            left_order_column_name,
            right_order_column_name,
            result_order_column_name,
        )
        return join_asof_sql

    def generate_rename_columns(
        self,
        tree_node_input,
        column_name_renames,
        input_order_column_name,
        result_order_column_name,
        original_row_labels_column_names: list[str],
    ):
        input_column_names = tree_node_input.get_column_names()
        input_node_sql = tree_node_input.generate_sql()
        if (
            get_execution_configuration().mask_with_temp_table
            and len(input_node_sql) >= __SQL_QUERY_LEN_LIMIT__
        ):
            temp_table_name = self.create_temp_table_name()
            (
                temp_table_create_sql,
                temp_table_project_sql,
            ) = self._dialect.generate_temp_table_for_subquery(
                temp_table_name, input_node_sql
            )

            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} being created"""
            )
            self.run_query_and_return_results(temp_table_create_sql)
            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} DONE"""
            )
            input_node_sql = temp_table_project_sql

        return self._dialect.generate_rename_columns_command(
            input_node_sql,
            input_column_names,
            input_order_column_name,
            column_name_renames,
            original_row_labels_column_names,
            result_order_column_name,
        )

    def generate_groupby(
        self,
        sort_by_group_keys: bool,
        groupby_node,
        aggregation_function_map,
        row_labels_column_names,
        input_order_column_name,
        result_order_column_name,
        group_by_column_names: list[str],
        aggregation_func_args,
        aggregation_func_kwargs,
        dropna_groupby_keys,
        other_col_id,
    ):
        groupby_node_input_query = groupby_node.get_input().generate_sql()
        if (
            get_execution_configuration().mask_with_temp_table
            and len(groupby_node_input_query) >= __SQL_QUERY_LEN_LIMIT__
        ):
            temp_table_name = self.create_temp_table_name()
            (
                temp_table_create_sql,
                temp_table_project_sql,
            ) = self._dialect.generate_temp_table_for_subquery(
                temp_table_name, groupby_node_input_query
            )

            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} being created"""
            )
            self.run_query_and_return_results(temp_table_create_sql)
            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} DONE"""
            )
            groupby_node_input_query = temp_table_project_sql

        # If we have: df.groupby("a").agg({"b": "sum", "c": "cumsum"}), we will
        # have a different output structure from what we expect. This will require
        # some more effort in restructuring the output Index.
        agg_func_in_window_funcs = [
            agg_func in groupby_window_funcs
            for agg_func in aggregation_function_map.values()
        ]

        # Same case as above but for any view functions
        agg_func_in_view_funcs = [
            agg_func in groupby_view_funcs
            for agg_func in aggregation_function_map.values()
        ]

        # We check to see that if we have any agg_func in our set of window funcs
        # then we should make sure that all of them are window funcs. If not, we
        # raise a NotImplementedError. See POND-805 for more details.
        if any(agg_func_in_window_funcs):
            if not all(agg_func_in_window_funcs):
                raise make_exception(
                    NotImplementedError,
                    PonderError.AGG_FUNC_HAS_BOTH_WINDOW_AND_REDUCTION_METHODS,
                    "groupby() does not support a mix of window and reduction "
                    + "functions yet",
                )
            # Below we use the input node's columns to make sure that
            # __PONDER_AGG_OTHER_COL_ID__ and __PONDER_AGG_OTHER_COL_NAME__ had not been
            # inserted yet.
            return self._dialect.generate_groupby_window_command(
                groupby_node_input_query,
                groupby_node.get_input().get_column_names(),
                aggregation_function_map,
                group_by_column_names,
                row_labels_column_names,
                input_order_column_name,
                aggregation_func_args,
                aggregation_func_kwargs,
                other_col_id,
            )

        # Basically do the same check as before, but for the view functions as well.
        # The long term solution is to have aggregate do what normal pandas does,
        # which is compute each function independently and then join them together.
        if any(agg_func_in_view_funcs):
            if not all(agg_func_in_view_funcs):
                raise make_exception(
                    NotImplementedError,
                    PonderError.AGG_FUNC_HAS_BOTH_VIEW_AND_REDUCTION_METHODS,
                    "groupby() does not support a mix of view and reduction "
                    + "functions yet",
                )
            # We define groupby view functions to be funcs like head, tail, nth, which
            # don't modify any data, but return a "view" of the data. While reduction
            # and window groupby functions apply functions to each column of the data,
            # view functions act like a filter and return a subset of the data. Thus,
            # the SQL generated is slightly different, so we have separate functions.

            return self._dialect.generate_groupby_view_command(
                groupby_node_input_query,
                groupby_node.get_column_names(),
                aggregation_function_map,
                group_by_column_names,
                row_labels_column_names,
                input_order_column_name,
                result_order_column_name,
                sort_by_group_keys,
                aggregation_func_args,
                aggregation_func_kwargs,
            )

        return self._dialect.generate_groupby_command(
            groupby_node_input_query,
            groupby_node.get_input().get_column_names(),
            aggregation_function_map,
            group_by_column_names,
            input_order_column_name,
            result_order_column_name,
            sort_by_group_keys,
            aggregation_func_args,
            aggregation_func_kwargs,
            dropna_groupby_keys,
            other_col_id,
        )

    def drop_table(self, table_name):
        drop_table_command = self._dialect.generate_drop_table_command(table_name)
        self.run_query_and_return_results(drop_table_command)

    # Some connection classes behave poorly if results are requested
    # when none are returned (even an empty set). For all the rest we
    # have this passthrough to the default function which can be
    # overridden
    def run_query_no_results(self, query):
        self.run_query_and_return_results(query)
        return

    def materialize_rows_to_table(
        self,
        table_name,
        column_names,
        column_types,
        if_exists,
        index,
        index_label,
        row_labels_column_names: list[str],
        row_labels_types: list[np.dtype],
        input_query,
    ):
        table_already_exists = self.table_exists(table_name)
        if if_exists == "fail" and table_already_exists:
            raise make_exception(
                RuntimeError,
                PonderError.GENERIC_SQL_MATERIALIZE_ROWS_TO_TABLE_THAT_ALREADY_EXISTS,
                f"{table_name} already exists.",
            )

        if if_exists == "replace" and table_already_exists:
            self.drop_table(table_name)
            table_already_exists = False

        if table_already_exists is not True:
            create_columns_list = [
                column_name
                for column_name in column_names
                if column_name not in row_labels_column_names
            ]

            if index:
                create_columns_list.extend(row_labels_column_names)

            create_order_column_name = None
            create_order_column_type = None

            create_columns_types = [
                column_types[i]
                for i in range(len(column_types))
                if column_names[i] not in row_labels_column_names
            ]
            if index:
                create_columns_types.extend(row_labels_types)

            create_command = self._dialect.generate_create_table_command(
                table_name,
                create_columns_list,
                create_columns_types,
                create_order_column_name,
                create_order_column_type,
                False,
                False,
            )
            self.run_query_no_results(create_command)

        insert_rows_command = self._dialect.generate_insert_rows_command(
            table_name,
            column_names,
            row_labels_column_names,
            index,
            index_label,
            input_query,
        )
        self.run_query_no_results(insert_rows_command)

    def materialize_table(self, table_name, materialized_table_name):
        materialize_table = True
        most_recent_table_update_time = self.get_last_table_update_time(table_name)
        if (
            most_recent_table_update_time is not None
            and table_name in self.table_materialization_time
        ):
            if (
                most_recent_table_update_time
                <= self.table_materialization_time[table_name]
            ) is True:
                materialize_table = False

        if materialize_table is False and table_name in self.materialized_tables:
            return self.materialized_tables[table_name]

        materialization_query = (
            self._dialect.generate_create_temp_table_with_rowid_command(
                materialized_table_name, table_name
            )
        )

        self.run_query_no_results(materialization_query)

        self.materialized_tables[table_name] = materialized_table_name
        self.table_materialization_time[table_name] = most_recent_table_update_time
        return materialized_table_name

    def generate_dot_product_command(
        self,
        left_node,
        right_node,
        output_cols,
        transposed=False,
        transposed_other=False,
    ):
        left_node_sql = left_node.generate_sql()

        if (
            get_execution_configuration().mask_with_temp_table
            and len(left_node_sql) >= __SQL_QUERY_LEN_LIMIT__
        ):
            temp_table_name = self.create_temp_table_name()
            (
                temp_table_create_sql,
                temp_table_project_sql,
            ) = self._dialect.generate_temp_table_for_subquery(
                temp_table_name, left_node_sql
            )
            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} being created"""
            )
            self.run_query_and_return_results(temp_table_create_sql)
            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} DONE"""
            )
            left_node_sql = temp_table_project_sql

        unpivot_left = self._dialect.generate_simple_unpivot(
            left_node_sql, left_node.get_column_names(), transposed
        )

        right_node_sql = right_node.generate_sql()
        if (
            get_execution_configuration().mask_with_temp_table
            and len(right_node_sql) >= __SQL_QUERY_LEN_LIMIT__
        ):
            temp_table_name = self.create_temp_table_name()
            (
                temp_table_create_sql,
                temp_table_project_sql,
            ) = self._dialect.generate_temp_table_for_subquery(
                temp_table_name, right_node_sql
            )
            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} being created"""
            )
            self.run_query_and_return_results(temp_table_create_sql)
            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} DONE"""
            )
            right_node_sql = temp_table_project_sql

        unpivot_right = self._dialect.generate_simple_unpivot(
            right_node_sql, right_node.get_column_names(), transposed_other
        )
        serialized_dot_prod = (
            self._dialect.generate_serialized_dot_product_from_unpivot(
                unpivot_left,
                unpivot_right,
                transposed_left=transposed,
                transposed_right=transposed_other,
            )
        )
        final_query = self._dialect.generate_dot_product_matrix(
            serialized_dot_prod, output_cols
        )
        return final_query

    def generate_get_dummies_query(
        self,
        input_node,
        non_dummy_cols,
        column,
        unique_vals,
        order_column_name,
        row_labels_column_names,
        prefix,
        prefix_sep,
    ):
        input_node_sql = input_node.generate_sql()
        if (
            get_execution_configuration().mask_with_temp_table
            and len(input_node_sql) >= __SQL_QUERY_LEN_LIMIT__
        ):
            temp_table_name = self.create_temp_table_name()
            (
                temp_table_create_sql,
                temp_table_project_sql,
            ) = self._dialect.generate_temp_table_for_subquery(
                temp_table_name, input_node_sql
            )

            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} being created"""
            )
            self.run_query_and_return_results(temp_table_create_sql)
            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} DONE"""
            )
            input_node_sql = temp_table_project_sql

        return self._dialect.generate_get_dummies_command(
            non_dummy_cols,
            column,
            unique_vals,
            order_column_name,
            row_labels_column_names,
            input_node.get_column_names(),
            input_node.get_row_labels_column_names(),
            input_node.get_order_column_name(),
            input_node_sql,
            prefix,
            prefix_sep,
        )

    def generate_map_node_query(self, node: MapNode) -> str:
        return self._dialect.generate_map_node_command(
            self,
            node._function.generate_sql(self),
            node._labels_to_apply_over,
            # TODO(https://ponderdata.atlassian.net/browse/POND-840): query tree and
            # connections shouldn't have to sort out the problem of
            # _labels_to_apply_over including row labels columns.
            [
                *node.get_column_names(),
                node.get_order_column_name(),
                *node.get_row_labels_column_names(),
            ],
            node._input_node.generate_sql(),
        )

    def generate_column_wise_reduce_node_query(self, node: ColumnWiseReduceNode) -> str:
        input_node_sql = node._input_node.generate_sql()
        if (
            get_execution_configuration().mask_with_temp_table
            and len(input_node_sql) >= __SQL_QUERY_LEN_LIMIT__
        ):
            temp_table_name = self.create_temp_table_name()
            (
                temp_table_create_sql,
                temp_table_project_sql,
            ) = self._dialect.generate_temp_table_for_subquery(
                temp_table_name, input_node_sql
            )

            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} being created"""
            )
            self.run_query_and_return_results(temp_table_create_sql)
            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} DONE"""
            )
            input_node_sql = temp_table_project_sql

        return self._dialect.generate_column_wise_reduce_node_command(
            node._function,
            node._labels_to_apply_over,
            input_node_sql,
            node.percentile(),
            node.params_list(),
            node._other_col_id,
        )

    def generate_row_wise_reduce_node_query(self, node: RowWiseReduceNode) -> str:
        input_node_sql = node._input_node.generate_sql()
        if (
            get_execution_configuration().mask_with_temp_table
            and len(input_node_sql) >= __SQL_QUERY_LEN_LIMIT__
        ):
            temp_table_name = self.create_temp_table_name()
            (
                temp_table_create_sql,
                temp_table_project_sql,
            ) = self._dialect.generate_temp_table_for_subquery(
                temp_table_name, input_node_sql
            )

            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} being created"""
            )
            self.run_query_and_return_results(temp_table_create_sql)
            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} DONE"""
            )
            input_node_sql = temp_table_project_sql

        return self._dialect.generate_row_wise_reduce_node_command(
            node._input_node.get_column_names(),
            node._input_node.get_column_types(),
            node._function,
            input_node_sql,
            self.get_order_and_labels_column_strings(node),
            node._result_column_name,
        )

    def generate_with_cross_join_full_command(
        self,
        input_node,
        column_names,
        column_expressions,
        order_column_name,
        row_labels_column_names,
        kwargs,
    ):
        input_node_sql = input_node.generate_sql()
        if (
            get_execution_configuration().mask_with_temp_table
            and len(input_node_sql) >= __SQL_QUERY_LEN_LIMIT__
        ):
            temp_table_name = self.create_temp_table_name()
            (
                temp_table_create_sql,
                temp_table_project_sql,
            ) = self._dialect.generate_temp_table_for_subquery(
                temp_table_name, input_node_sql
            )

            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} being created"""
            )
            self.run_query_and_return_results(temp_table_create_sql)
            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} DONE"""
            )
            input_node_sql = temp_table_project_sql

        return self._dialect.generate_with_cross_join_full_command(
            input_node_sql,
            column_names,
            column_expressions,
            order_column_name,
            row_labels_column_names,
            kwargs,
        )

    def generate_pivot(
        self,
        grouping_column_name,
        pivot_column_name,
        values_column_name,
        unique_values,
        input_node,
        aggfunc,
        add_qualifier_to_new_column_names,
    ):
        return self._dialect.generate_pivot_command(
            grouping_column_name,
            pivot_column_name,
            values_column_name,
            unique_values,
            input_node.generate_sql(),
            input_node.get_order_column_name(),
            aggfunc,
            add_qualifier_to_new_column_names,
        )

    def generate_derived_columns_sql(self, input_node):
        expressions = input_node._column_node.get_expressions()
        predicates = input_node._column_node.get_predicates()
        if len(expressions) > 0:
            # The replace operation automatically adds an " AS " fragment to the
            # column.  This works in many cases, but, sometimes causes trouble
            # because the replace might be an intermediate operation to a renaming
            # that happens in an outer context.  I believe this is a artifact of
            # our dependence on the python interpreter - unless the inner expression
            # involving the replace is fully evaluated - the outer expression doesn't
            # get a chance to specify what the new column should be called.
            modified_expressions = [
                predicate.partition(" AS ")[0]
                if len([c for c in predicate.partition(" AS ")[0] if c == "("])
                == len([c for c in predicate.partition(" AS ")[0] if c == ")"])
                else predicate
                for predicate in expressions
            ]
            column_sql = (
                f"{', '.join(map(str, modified_expressions))} AS"
                f" {self.format_name(input_node._new_column_name)}"
            )
        elif len(predicates) > 0:
            column_sql = (
                f"{', '.join(map(str, predicates))} AS"
                f" {self.format_name(input_node._new_column_name)}"
            )
        else:
            column_sql = (
                f"{input_node._column_node.generate_sql()} AS "
                + self.format_name(input_node._new_column_name)
            )
        formatted_input_node_columns_list = self.format_names_list(
            input_node._input_node.get_column_names()
        )
        input_node_sql = input_node._input_node.generate_sql()
        if (
            get_execution_configuration().mask_with_temp_table
            and len(input_node_sql) >= __SQL_QUERY_LEN_LIMIT__
        ):
            temp_table_name = self.create_temp_table_name()
            (
                temp_table_create_sql,
                temp_table_project_sql,
            ) = self._dialect.generate_temp_table_for_subquery(
                temp_table_name, input_node_sql
            )

            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} being created"""
            )
            self.run_query_and_return_results(temp_table_create_sql)
            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} DONE"""
            )
            input_node_sql = temp_table_project_sql

        return f"""
        SELECT
            {self.get_order_and_labels_column_strings(input_node)},
            {", ".join(formatted_input_node_columns_list)},
            {column_sql}
        FROM
            {self._dialect.generate_subselect_expression(input_node_sql)}
    """

    def generate_project_node_query(self, node):
        input_node_sql = node._input_node.generate_sql()
        if (
            get_execution_configuration().mask_with_temp_table
            and len(input_node_sql) >= __SQL_QUERY_LEN_LIMIT__
        ):
            temp_table_name = self.create_temp_table_name()
            (
                temp_table_create_sql,
                temp_table_project_sql,
            ) = self._dialect.generate_temp_table_for_subquery(
                temp_table_name, input_node_sql
            )

            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} being created"""
            )
            self.run_query_and_return_results(temp_table_create_sql)
            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} DONE"""
            )
            input_node_sql = temp_table_project_sql

        if node._precompute_columns:
            columns_selection = ", ".join(
                [f"{self.format_name(col)}" for col in node._column_names]
            )
        else:
            columns_selection = node._columns_selection

        select_string = self.get_order_and_labels_column_strings(node)
        if columns_selection != "":
            select_string += ", " + columns_selection
        return (
            f"SELECT {select_string} FROM "
            f"{self.generate_subselect_expression(input_node_sql)}"
        )

    def generate_row_numbers_query(self, node):
        order_column_name_clauses = []
        if __PONDER_ORDER_COLUMN_NAME__ not in node.get_column_names():
            order_column_name_clauses.append(
                f"""
            ROW_NUMBER()
            OVER (
                ORDER BY {self._dialect.format_name(__PONDER_ORDER_COLUMN_NAME__)}
            ) -1 AS {self._dialect.format_name(__PONDER_ORDER_COLUMN_NAME__)}
            """
            )
        row_label_select_clauses = []
        if (
            node._keep_old_row_numbers
            and __PONDER_ROW_LABELS_COLUMN_NAME__ not in node.get_column_names()
        ):
            row_label_select_clauses.append(
                f"{self._dialect.format_name(__PONDER_ORDER_COLUMN_NAME__)} "
                f"AS {self._dialect.format_name(__PONDER_ROW_LABELS_COLUMN_NAME__)}"
            )
        else:
            row_label_select_clauses.extend(
                self.format_names_list(node.get_row_labels_column_names())
            )

        input_node_sql = node._input_node.generate_sql()
        if (
            get_execution_configuration().mask_with_temp_table
            and len(input_node_sql) >= __SQL_QUERY_LEN_LIMIT__
        ):
            temp_table_name = self.create_temp_table_name()
            (
                temp_table_create_sql,
                temp_table_project_sql,
            ) = self._dialect.generate_temp_table_for_subquery(
                temp_table_name, input_node_sql
            )

            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} being created"""
            )
            self.run_query_and_return_results(temp_table_create_sql)
            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} DONE"""
            )
            input_node_sql = temp_table_project_sql

        return f"""
            SELECT
                {",".join((
                    *self.format_names_list(node.get_column_names()),
                    *order_column_name_clauses,
                    *row_label_select_clauses))}
            FROM {self._dialect.generate_subselect_expression(input_node_sql)}
            """

    def generate_project_columns_query(
        self,
        input_node,
        column_names,
        column_expressions,
        order_column_name,
        row_labels_column_names,
        has_aggregation,
        reset_order=False,
    ):
        column_select_strings = (
            f"{self.format_name(expr) if expr == name else expr} AS "
            + self.format_name(name)
            for name, expr in zip(column_names, column_expressions)
        )
        order_columns_list = []
        if order_column_name not in column_names:
            formatted_order_column_name = self.format_name(order_column_name)
            if has_aggregation:
                order_columns_list.append(
                    f"MIN({formatted_order_column_name}) AS "
                    + formatted_order_column_name
                )
            else:
                if reset_order:
                    reset_order_column_clause = (
                        f"ROW_NUMBER() OVER (ORDER BY"
                        f" {formatted_order_column_name}) -1 AS "
                        + formatted_order_column_name
                    )
                    order_columns_list.append(reset_order_column_clause)
                else:
                    order_columns_list.append(formatted_order_column_name)
        row_labels_columns_list = []
        for row_labels_column_name in row_labels_column_names:
            if row_labels_column_name not in column_names:
                formatted_row_labels_column_name = self.format_name(
                    row_labels_column_name
                )
                # TODO: its probably a bug to take the min of the row labels itself.
                # The new row label should the be the row label of the first row with
                # respect to the order column. It's complex to write that in SQL,
                # though.
                if has_aggregation:
                    row_labels_columns_list.append(
                        f"MIN({formatted_row_labels_column_name}) "
                        + f"AS {formatted_row_labels_column_name}"
                    )
                else:
                    row_labels_columns_list.append(formatted_row_labels_column_name)

        input_node_sql = input_node.generate_sql()
        if (
            get_execution_configuration().mask_with_temp_table
            and len(input_node_sql) >= __SQL_QUERY_LEN_LIMIT__
        ):
            temp_table_name = self.create_temp_table_name()
            (
                temp_table_create_sql,
                temp_table_project_sql,
            ) = self._dialect.generate_temp_table_for_subquery(
                temp_table_name, input_node_sql
            )

            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} being created"""
            )
            self.run_query_and_return_results(temp_table_create_sql)
            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} DONE"""
            )
            input_node_sql = temp_table_project_sql

        return f"""
        SELECT
            {", ".join(
                (*column_select_strings,
                *row_labels_columns_list,
                *order_columns_list))}
        FROM {self._dialect.generate_subselect_expression(input_node_sql)}
        """

    def generate_broadcast_binary_op_query(
        self, op, broadcast_binary_op_node, input_node, broadcast_node, new_columns
    ):
        left_columns = input_node.get_column_names()
        left_types = input_node.get_column_types()
        right_columns = broadcast_node.get_column_names()
        right_types = broadcast_node.get_column_types()
        overlapped_cols = [col for col in left_columns if col in right_columns]
        exp_dict = {}
        for col in new_columns:
            if col in overlapped_cols:
                left_idx = left_columns.index(col)
                right_idx = right_columns.index(col)
                left_exp = self.format_name(left_columns[left_idx])
                right_exp = self.format_name(right_columns[right_idx] + "_ponder_right")
                exp_dict[col] = BinaryPredicate(
                    self,
                    lhs=left_exp,
                    lhs_type=left_types[left_idx],
                    lhs_is_literal=False,
                    lhs_is_column=True,
                    op=op,
                    rhs=right_exp,
                    rhs_type=right_types[right_idx],
                    rhs_is_literal=False,
                    rhs_is_column=True,
                )
            elif len(right_columns) == 1:
                if col == right_columns[0]:
                    continue
                left_idx = left_columns.index(col)
                left_exp = self.format_name(col)
                if right_columns[0] in overlapped_cols:
                    right_exp = self.format_name(right_columns[0] + "_ponder_right")
                else:
                    right_exp = self.format_name(right_columns[0])
                exp_dict[col] = BinaryPredicate(
                    self,
                    lhs=left_exp,
                    lhs_type=left_types[left_idx],
                    lhs_is_literal=False,
                    lhs_is_column=True,
                    op=op,
                    rhs=right_exp,
                    rhs_type=right_types[0],
                    rhs_is_literal=False,
                    rhs_is_column=True,
                )
            else:
                exp_dict[col] = "NULL"

        broadcast_node_sql = broadcast_node.generate_sql()

        if (
            get_execution_configuration().mask_with_temp_table
            and len(broadcast_node_sql) >= __SQL_QUERY_LEN_LIMIT__
        ):
            temp_table_name = self.create_temp_table_name()
            (
                temp_table_create_sql,
                temp_table_project_sql,
            ) = self._dialect.generate_temp_table_for_subquery(
                temp_table_name, broadcast_node_sql
            )
            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} being created"""
            )
            self.run_query_and_return_results(temp_table_create_sql)
            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} DONE"""
            )
            broadcast_node_sql = temp_table_project_sql

        right_sql = f"""
            SELECT
                {", ".join(
                    (self.format_name(right_col) +
                   f" AS {self.format_name(right_col+'_ponder_right')}")
                for right_col in broadcast_node.get_column_names())}
            FROM {self._dialect.generate_subselect_expression(broadcast_node_sql)}
            """
        input_node_sql = input_node.generate_sql()
        if (
            get_execution_configuration().mask_with_temp_table
            and len(input_node_sql) >= __SQL_QUERY_LEN_LIMIT__
        ):
            temp_table_name = self.create_temp_table_name()
            (
                temp_table_create_sql,
                temp_table_project_sql,
            ) = self._dialect.generate_temp_table_for_subquery(
                temp_table_name, input_node_sql
            )
            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} being created"""
            )
            self.run_query_and_return_results(temp_table_create_sql)
            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} DONE"""
            )
            input_node_sql = temp_table_project_sql

        return f"""
            SELECT
                {self.get_order_and_labels_column_strings(broadcast_binary_op_node)},
                {", ".join(f"{str(exp_dict[col])} AS {self.format_name(col)}"
                for col in exp_dict.keys())}
            FROM ({input_node_sql}) AS _PONDER_LEFT_
            CROSS JOIN (
                {right_sql}) AS _PONDER_RIGHT_"""

    def get_binary_post_join_query_and_metadata(
        self,
        left_columns,
        left_types,
        right_columns,
        right_types,
        op,
        left_suffix,
        right_suffix,
        input_node,
    ):
        # in pandas 1.5, Index.sort can only take None or False
        all_cols = left_columns.union(right_columns, sort=False)
        overlapped_cols = left_columns.intersection(right_columns, sort=False)
        exp_list = []
        for col in all_cols:
            if col in overlapped_cols:
                left_idx = left_columns.get_loc(col)
                right_idx = right_columns.get_loc(col)
                left_exp = self.format_name(f"{col}{left_suffix}")
                right_exp = self.format_name(f"{col}{right_suffix}")
                exp_list.append(
                    (
                        col,
                        BinaryPredicate(
                            self,
                            lhs=left_exp,
                            lhs_type=left_types[left_idx],
                            lhs_is_literal=False,
                            lhs_is_column=True,
                            op=op,
                            rhs=right_exp,
                            rhs_type=right_types[right_idx],
                            rhs_is_literal=False,
                            rhs_is_column=True,
                        ),
                    ),
                )
            elif len(right_columns) == 1:
                if col == right_columns[0]:
                    continue
                left_idx = left_columns.get_loc(col)
                left_exp = self.format_name(col)
                if right_columns[0] in overlapped_cols:
                    right_exp = self.format_name(f"{right_columns[0]}{right_suffix}")
                else:
                    right_exp = self.format_name(right_columns[0])
                right_types_list = (
                    right_types.tolist()
                    if isinstance(right_types, pandas.Series)
                    else right_types
                )
                exp_list.append(
                    (
                        col,
                        BinaryPredicate(
                            self,
                            lhs=left_exp,
                            lhs_type=left_types[left_idx],
                            lhs_is_literal=False,
                            lhs_is_column=True,
                            op=op,
                            rhs=right_exp,
                            rhs_type=right_types_list[0],
                            rhs_is_literal=False,
                            rhs_is_column=True,
                        ),
                    ),
                )
            else:
                exp_list.append((col, "NULL"))
        input_node_sql = input_node.generate_sql()
        if (
            get_execution_configuration().mask_with_temp_table
            and len(input_node_sql) >= __SQL_QUERY_LEN_LIMIT__
        ):
            temp_table_name = self.create_temp_table_name()
            (
                temp_table_create_sql,
                temp_table_project_sql,
            ) = self._dialect.generate_temp_table_for_subquery(
                temp_table_name, input_node_sql
            )

            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} being created"""
            )
            self.run_query_and_return_results(temp_table_create_sql)
            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} DONE"""
            )
            input_node_sql = temp_table_project_sql

        query = f"""
            SELECT
                {self.get_order_and_labels_column_strings(input_node)},
                {", ".join(
                    [f"{str(entry[1])} AS {self.format_name(entry[0])}"
                    for entry in exp_list])}
            FROM {self.generate_subselect_expression(input_node_sql)}
            """
        # return a list since this code will be executed with different column names
        # and we need to have the right order.
        metadata = [
            (
                col,
                exp.return_type()
                if isinstance(exp, BinaryPredicate)
                else np.dtype(object),
            )
            for col, exp in exp_list
        ]
        return [query, metadata]

    def generate_sort_values_query(
        self,
        input_node,
        sort_columns,
        ascending,
        input_node_order_column_name,
        keep_old_row_numbers,
        row_labels_column_names,
        handle_duplicates,
    ):
        # Not doing a copy here causes the cached copy to get affected in some cases.
        # TODO: investigate this issue more closely so we don't have to copy the list.
        all_sort_columns = copy.deepcopy(sort_columns)
        if input_node_order_column_name not in all_sort_columns:
            all_sort_columns.append(input_node_order_column_name)
        if handle_duplicates is None:
            sort_columns_selection = ", ".join(
                f"{self.format_name(col)} {'ASC' if ascending else 'DESC'}"
                for col in all_sort_columns
            )
        elif handle_duplicates == "first":
            # nlargest/smallest case where we want to keep only the first duplicate
            # Sort by ascending row number to keep the first duplicate value in the sort
            sort_columns_selection = ", ".join(
                f"""
                {self.format_name(col)}
                {'ASC' if ascending or col == '_PONDER_ROW_NUMBER_' else 'DESC'}
                {'NULLS LAST'}
                """
                for col in all_sort_columns
            )
        input_node_columns_list = self.format_names_list(input_node.get_column_names())
        columns_selection = f"""
            {", ".join(input_node_columns_list)},
            ROW_NUMBER() OVER (
                ORDER BY {sort_columns_selection}
            ) -1 AS {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
            """
        if (
            keep_old_row_numbers
            and __PONDER_ROW_LABELS_COLUMN_NAME__ not in input_node.get_column_names()
        ):
            columns_selection += (
                f", {self.format_name(__PONDER_ORDER_COLUMN_NAME__)} "
                + f"AS {self.format_name(__PONDER_ROW_LABELS_COLUMN_NAME__)}"
            )
        else:
            columns_selection = ", ".join(
                (columns_selection, *self.format_names_list(row_labels_column_names))
            )
        return f"""
            SELECT
                {columns_selection}
            FROM {self._dialect.generate_subselect_expression(
                    input_node.generate_sql()
                    )
                    }
            """

    def generate_get_from_binary_comparison_node_query(self, input_node, indexer_node):
        input_node_sql = input_node.generate_sql()
        if (
            get_execution_configuration().mask_with_temp_table
            and len(input_node_sql) >= __SQL_QUERY_LEN_LIMIT__
        ):
            temp_table_name = self.create_temp_table_name()
            (
                temp_table_create_sql,
                temp_table_project_sql,
            ) = self._dialect.generate_temp_table_for_subquery(
                temp_table_name, input_node_sql
            )

            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} being created"""
            )
            self.run_query_and_return_results(temp_table_create_sql)
            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} DONE"""
            )
            input_node_sql = temp_table_project_sql

        return f"""
            SELECT *
            FROM {self.generate_subselect_expression(input_node_sql)}
            WHERE
                {" AND ".join(str(p) for p in indexer_node.get_predicates())}"""

    def generate_select_from_in(self, node):
        if node._col_labels is None:
            stringified_columns = "*"
        else:
            stringified_columns = ", ".join(
                (
                    self.get_order_and_labels_column_strings(node),
                    *[str(self.format_name(column)) for column in node._col_labels],
                )
            )
        input_node_sql = node._input_node.generate_sql()

        if (
            get_execution_configuration().mask_with_temp_table
            and len(input_node_sql) >= __SQL_QUERY_LEN_LIMIT__
        ):
            temp_table_name = self.create_temp_table_name()
            (
                temp_table_create_sql,
                temp_table_project_sql,
            ) = self._dialect.generate_temp_table_for_subquery(
                temp_table_name, input_node_sql
            )
            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} being created"""
            )
            self.run_query_and_return_results(temp_table_create_sql)
            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} DONE"""
            )
            input_node_sql = temp_table_project_sql

        if node._row_labels is not None:
            if (
                get_execution_configuration().mask_with_temp_table
                and len(node._row_labels) > __ROWID_VALUE_SIZE_TO_MATERIALIZE__
            ):
                temp_table_name = self.create_temp_table_name()

                # generate_create_temp_table_for_wherein returns a big
                # array of SQL queries because in case of a lot of rowids, the temp
                # table creation and insertion into it has to be split across many
                # queries, otherwise it again causes error due to SQL blowup.
                # The very first sql_exp_arr[0] query is always the CREATE TEMP TABLE
                # query. The very last query sql_exp_arr[-1] is always the
                # SELECT query from this temp table that gets inserted in the
                # WHERE IN clause.
                # All the queries in between are INSERT INTO queries
                # to add the rowids in the temp table in batches.
                sql_exp_arr = self._dialect.generate_create_temp_table_for_wherein(
                    temp_table_name=temp_table_name,
                    rowids=node._row_labels,
                )
                for i in range(0, len(sql_exp_arr) - 1):
                    logger.debug(
                        f"""
                        {self.__class__.__name__}.{sys._getframe().f_code.co_name}
                        rowids being inserted in {temp_table_name}....
                        """
                    )
                    self.run_query_and_return_results(sql_exp_arr[i])
                logger.debug(
                    f"""
                    {self.__class__.__name__}.{sys._getframe().f_code.co_name}
                    rowids insertion in {temp_table_name} DONE"""
                )
                output_sql = f"""
                    SELECT
                        {stringified_columns}
                    FROM {self._dialect.generate_subselect_expression(input_node_sql)}
                    WHERE
                        {
                            self.format_name(node._column_names_for_filter[0])
                        } IN ({sql_exp_arr[-1]})
                    """
            else:
                if len(node._column_names_for_filter) > 1:
                    raise make_exception(
                        NotImplementedError,
                        PonderError.GENERIC_SQL_IN_FILTER_ON_MULTIPLE_COLUMNS_NOT_SUPPORTED,  # noqa: E501
                        "Ponder Internal Error: cannot filter "
                        + "with a condition on multiple columns yet",
                    )
                if len(node._row_labels) == 1:
                    single_label = node._row_labels[0]
                    if isinstance(single_label, str):
                        single_label = self.format_value(single_label)
                    elif isinstance(single_label, pandas.Timestamp):
                        single_label = self.format_value_by_type(single_label)
                    row_positions = f"({single_label})"
                elif len(node._row_labels) == 0:
                    # Edge case where we drop all rows
                    output_sql = f"SELECT {stringified_columns} FROM "
                    f"{self.generate_subselect_expression(input_node_sql)} LIMIT 0"
                    return output_sql
                else:
                    row_positions = (
                        "("
                        + ", ".join(
                            self.format_value_by_type(p) for p in node._row_labels
                        )
                        + ")"
                    )

                output_sql = f"""
                    SELECT
                        {stringified_columns}
                    FROM {self._dialect.generate_subselect_expression(input_node_sql)}
                    WHERE
                        {
                            self.format_name(node._column_names_for_filter[0])
                        } IN {row_positions}
                    """
        else:
            output_sql = (
                f"SELECT {stringified_columns} FROM "
                f"{self._dialect.generate_subselect_expression(input_node_sql)}"
            )
        return output_sql

    def get_order_and_labels_column_strings(self, node):
        assert (
            node.get_order_column_name() not in node.get_row_labels_column_names()
        ), "Row and Order column must be named differently!"
        return ", ".join(
            (
                self.format_name(node.get_order_column_name()),
                *self.format_names_list(node.get_row_labels_column_names()),
            )
        )

    def generate_str_extract(self, column_name, pat, flags):
        return self._dialect.generate_str_extract(column_name, pat, flags)

    def generate_str_partition(self, column_name, sep, expand):
        return self._dialect.generate_str_partition(column_name, sep, expand)

    def generate_compare_post_join_results(
        self, original_columns: list[str], original_types: Iterable[pandas_dtype]
    ) -> tuple[list[str], list[str], list[str]]:
        return self._dialect.generate_compare_post_join_results(
            original_columns, original_types
        )

    def update_pandas_df_with_supplementary_columns(self, pandas_df):
        pandas_df_copy = pandas_df.copy(deep=True)
        pandas_df_copy[__PONDER_ORDER_COLUMN_NAME__] = pandas_df_copy[
            __PONDER_ROW_LABELS_COLUMN_NAME__
        ] = range(len(pandas_df_copy))
        return pandas_df_copy

    def setup_udtf(
        self,
        function_name,
        func,
        input_column_names,
        input_column_types,
        output_column_names,
        output_column_types,
        order_column_names,
        row_label_column_names,
        row_label_dtypes,
        apply_type,
        na_action,
        func_args,
        func_kwargs,
    ):
        output_aliases_map = {
            output_column_name: output_column_name
            for output_column_name in output_column_names
        }
        return (output_column_names, output_aliases_map)

    def generate_apply_command(
        self,
        input_node_sql,
        function_name,
        func,
        input_column_names,
        input_column_types,
        output_column_names,
        output_alias_map,
        order_column_names,
        row_label_column_names,
        apply_type,
        na_action,
        func_args,
        func_kwargs,
    ):
        table_name = f"USERFUNC_{function_name}"

        if table_name not in self.materialized_udfs:
            metadata_cols = [order_column_names] + row_label_column_names
            input_column_names_without_metadata = [
                input_column_name
                for input_column_name in input_column_names
                if input_column_name not in metadata_cols
            ]

            pandas_df = self.run_query_and_return_dataframe(
                input_node_sql, use_cache=True
            )
            pandas_df_without_input_columns = pandas_df[
                input_column_names_without_metadata
            ]
            function_ref = cloudpickle.loads(func)
            if apply_type == APPLY_FUNCTION.ROW_WISE:
                table_df = pandas_df_without_input_columns.apply(
                    function_ref, axis=1, args=func_args[0], **func_kwargs
                )
            else:
                table_df = pandas_df_without_input_columns.applymap(
                    function_ref, na_action=na_action, **func_kwargs
                )
            if not isinstance(table_df, pandas.DataFrame):
                table_df = table_df.to_frame(name=__PONDER_REDUCED_COLUMN_NAME__)
            table_df.columns = output_column_names

            if len(input_column_names_without_metadata) > 0:
                table_df = pandas.concat(
                    [table_df, pandas_df[metadata_cols]],
                    axis=1,
                )
            table_name = self.materialize_pandas_dataframe_as_table(
                table_name, table_df, None
            )
            self.materialized_udfs[table_name] = self.generate_select(
                table_name, table_df.columns
            )

        return self.materialized_udfs[table_name]

    def setup_stored_procedure_temp_table(
        self,
        input_node_sql,
        func,
        function_name,
        table_name,
        output_column_names,
        output_column_types,
        row_labels_column_name,
        row_label_column_type,
    ):
        pandas_df = self.run_query_and_return_dataframe(input_node_sql, use_cache=True)
        function_ref = cloudpickle.loads(func)
        if __PONDER_ORDER_COLUMN_NAME__ in pandas_df.columns:
            pandas_df.drop(columns=[__PONDER_ORDER_COLUMN_NAME__], inplace=True)
        if __PONDER_ROW_LABELS_COLUMN_NAME__ in pandas_df.columns:
            pandas_df.drop(columns=[__PONDER_ROW_LABELS_COLUMN_NAME__], inplace=True)

        for column in pandas_df.columns:
            if is_object_dtype(pandas_df[column]):
                pandas_df[column].replace(np.nan, None, inplace=True)
        table_df = pandas_df.apply(function_ref)
        if not isinstance(table_df, pandas.DataFrame):
            table_df = table_df.to_frame()
        table_df.reset_index(inplace=True)
        full_output_columns = [row_labels_column_name]
        full_output_columns.extend(output_column_names)
        table_df.columns = full_output_columns
        table_name = self.materialize_pandas_dataframe_as_table(
            table_name, table_df, None
        )
        return self._dialect.generate_read_sp_temp_table(
            table_name,
            output_column_names,
            row_labels_column_name,
        )

    def generate_equal_null_predicate(self, lhs: str, rhs: str) -> str:
        return self._dialect.generate_equal_null_predicate(lhs, rhs)

    def generate_bitwise_and(self, op_1, op_2) -> str:
        return self._dialect.generate_bitwise_and(op_1, op_2)

    def generate_bitwise_or(self, op_1, op_2) -> str:
        return self._dialect.generate_bitwise_or(op_1, op_2)

    def generate_bitwise_xor(self, op_1, op_2) -> str:
        return self._dialect.generate_bitwise_or(op_1, op_2)

    def generate_select_with_renamed_columns(
        self, table_name, column_list, renamed_column_list, non_renamed_columns=None
    ):
        formatted_table_name = self.format_name(table_name)

        select_fields_fragment = ", ".join(
            [
                f"""{self.format_name(column_list[i])}
                    AS {self.format_name(renamed_column_list[i])}"""
                for i in range(len(column_list))
            ]
        )

        if non_renamed_columns:
            select_fields_fragment = (
                select_fields_fragment
                + ", "
                + ", ".join(
                    [
                        f""" {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                          AS {self.format_name(column)}"""
                        for column in non_renamed_columns
                    ]
                )
            )

        return f"SELECT {select_fields_fragment} FROM {formatted_table_name}"

    def generate_coalesce(self, column_list) -> str:
        return self._dialect.generate_coalesce(column_list)

    def to_csv(self, path, node, sep=",", header=True, date_format=None, na_rep=""):
        pandas_df = self.to_pandas(node, enforce_row_limit=False)

        pandas_df = pandas_df[node.get_column_names()]

        pandas_df.to_csv(
            path,
            sep=sep,
            header=header,
            date_format=date_format,
            na_rep=na_rep,
            index=False,
        )

    def generate_limit_clause(self):
        return f"LIMIT {get_execution_configuration().row_transfer_limit + 1}"

    def generate_reorder_columns_statement(
        self, input_node_sql, column_list, order_column_name, row_labels_column_names
    ):
        new_column_list = column_list[:]
        if order_column_name not in column_list:
            new_column_list.append(order_column_name)
        for col in row_labels_column_names:
            if col not in new_column_list:
                new_column_list.append(col)
        return self._dialect.generate_reorder_columns_statement(
            input_node_sql, new_column_list
        )

    def generate_sanitized_values(self, value_list):
        return None

    def generate_replace_values_statement(
        self,
        input_node,
        replace_values_column_name,
        replace_values_dict,
        order_column_name,
        row_label_columns_names,
    ):
        output_column_list = input_node.get_column_names()[:]

        if order_column_name not in output_column_list:
            output_column_list.append(order_column_name)

        for col_name in row_label_columns_names:
            if col_name not in output_column_list:
                output_column_list.append(col_name)

        sql = self._dialect.generate_replace_values_statement(
            input_node.generate_sql(),
            output_column_list,
            replace_values_column_name,
            replace_values_dict,
        )
        return sql

    def get_unique_values(self, input_node, column):
        sql = self._dialect.generate_get_unique_values(
            input_node.generate_sql(), column
        )
        results = self.run_query_and_return_results(sql)
        return [row[0] for row in results]

    def generate_memory_usage(self, column_names):
        all_columns = column_names + [
            __PONDER_ROW_LABELS_COLUMN_NAME__,
            __PONDER_ORDER_COLUMN_NAME__,
        ]
        all_columns = list(set(all_columns))

        all_selects = [f""" 0 AS {self._dialect.format_name(c)}""" for c in all_columns]

        return f"""
            SELECT
                {", ".join(all_selects)}
        """
