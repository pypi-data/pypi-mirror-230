from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, Optional

import numpy as np
import pandas

from .common import UnionAllDataForDialect
from .query_tree import ColumnWiseReduceNode, MapNode, RowWiseReduceNode


class AbstractConnection(ABC):
    @abstractmethod
    def case_insensitive_identifiers(self):
        pass

    @abstractmethod
    def case_fold_identifiers(self):
        pass

    @abstractmethod
    def get_user_connection() -> Any:
        pass

    @abstractmethod
    def run_query_and_return_results(self, query):
        pass

    @abstractmethod
    def format_name(self, name):
        pass

    @abstractmethod
    def format_value(self, value):
        pass

    @abstractmethod
    def execute(self, tree_node):
        pass

    @abstractmethod
    def run_query_and_return_dataframe(self, query, use_cache: bool):
        pass

    @abstractmethod
    def get_row_transfer_limit(self):
        pass

    @abstractmethod
    def get_temp_table_metadata(self, table_name):
        pass

    @abstractmethod
    def get_num_rows(self, tree_node):
        pass

    @abstractmethod
    def get_project_columns(self, tree_node, fn):
        pass

    @abstractmethod
    def get_unique_values(self, node, column):
        pass

    @abstractmethod
    def get_max_str_splits(self, query_tree, column, pat, n):
        pass

    @abstractmethod
    def materialize_table(self, table_name, materialized_table_name):
        pass

    @abstractmethod
    def generate_memory_usage(self, column_names):
        pass

    @abstractmethod
    def to_pandas(self, tree_node):
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def generate_join(
        self,
        tree_node_left,
        tree_node_right,
        how,
        left_on,
        right_on,
        left_order_column_name,
        right_order_column_name,
        result_order_column_name,
        db_index_column_name: Optional[str],
        indicator,
    ):
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def generate_select(self, table_name, column_list, skipfooter=0):
        pass

    @abstractmethod
    def generate_rename_columns(
        self,
        tree_node_input,
        column_name_renames,
        input_order_column_name,
        result_order_column_name,
        original_row_labels_column_names: list[str],
    ):
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def materialize_csv_file_as_table(
        self,
        table_name,
        column_names,
        column_types,
        file_path,
        sep,
        header,
        na_values,
        on_bad_lines,
        order_column_name,
    ):
        pass

    @abstractmethod
    def table_exists(self, table_name):
        pass

    @abstractmethod
    def drop_table(self, table_name):
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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

    @abstractmethod
    def generate_select_from_in(self, node):
        pass

    @abstractmethod
    def generate_drop_na_columns_query(self, how, thresh, subset, index_name, columns):
        pass

    @abstractmethod
    def generate_drop_na_rows_predicate(self, how, thresh, columns):
        pass

    @abstractmethod
    def generate_get_from_binary_comparison_node_query(self, input_node, indexer_node):
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def generate_broadcast_binary_op_query(
        self, op, broadcast_binary_op_node, input_node, broadcast_node
    ):
        pass

    @abstractmethod
    def generate_method_fill_na(
        self, method, limit, columns, group_cols: Optional[list[str]] = None
    ):
        pass

    @abstractmethod
    def generate_value_dict_fill_na(
        self, label, value_dict, limit, group_cols, upcast_to_object
    ):
        pass

    @abstractmethod
    def generate_project_columns_query(
        self,
        input_node,
        column_names,
        column_expressions,
        order_column_name,
        row_labels_column_names,
        has_aggregation,
        reset_order,
    ):
        pass

    @abstractmethod
    def generate_string_values_from_values(self, values):
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def generate_row_numbers_query(self, node):
        pass

    @abstractmethod
    def generate_column_is_min_predicate(self, column_name):
        pass

    @abstractmethod
    def generate_column_is_max_predicate(self, column_name):
        pass

    @abstractmethod
    def generate_lag_val_expr(self, column_name, order_column_name):
        pass

    @abstractmethod
    def generate_map_node_query(self, node: MapNode) -> str:
        pass

    @abstractmethod
    def generate_column_wise_reduce_node_query(self, node: ColumnWiseReduceNode) -> str:
        pass

    @abstractmethod
    def generate_row_wise_reduce_node_query(self, node: RowWiseReduceNode) -> str:
        pass

    @abstractmethod
    def generate_project_node_query(self, node):
        pass

    @abstractmethod
    def generate_map_function(self, function, params_list):
        pass

    @abstractmethod
    def generate_map_column_expressions(self, labels_to_apply_over, n):
        pass

    @abstractmethod
    def generate_str_rpartition(self, column_name, sep, expand):
        pass

    @abstractmethod
    def generate_cumulative_function(
        self,
        cumulative_function,
        col,
        skipna,
        window,
        non_numeric_col: bool,
        expanding,
        other_col,
    ):
        pass

    @abstractmethod
    def generate_downsample_function(
        self,
        col,
        offset: pandas.DateOffset,
        start_val: pandas.Timestamp,
        end_val: pandas.Timestamp,
        sum_interval: float,
    ):
        pass

    @abstractmethod
    def generate_downsample_index_function(
        self,
        col,
        offset: pandas.DateOffset,
        start_val: pandas.Timestamp,
        end_val: pandas.Timestamp,
    ):
        pass

    @abstractmethod
    def generate_upsample_function(
        self,
        col,
        offset: pandas.DateOffset,
        start_val: pandas.Timestamp,
        end_val: pandas.Timestamp,
        sum_interval: float,
        interval: float,
    ):
        pass

    @abstractmethod
    def generate_cast_to_type(self, col, cast_type):
        pass

    @abstractmethod
    def generate_get_first_element_by_row_label_rank(self, col, row_labels_column_name):
        pass

    @abstractmethod
    def generate_replace_nan_with_0(self, col):
        pass

    @abstractmethod
    def generate_abs(self, col):
        pass

    @abstractmethod
    def generate_round(self, col, decimals):
        pass

    # Used for groupby.head()
    @abstractmethod
    def generate_groupby_head_predicate(self, by, order_column, n):
        pass

    # Used for groupby.tail()
    @abstractmethod
    def generate_groupby_tail_predicate(self, by, order_column, n):
        pass

    # Used for groupby.nth()
    @abstractmethod
    def generate_groupby_nth_predicate(self, by, order_column, n):
        pass

    @abstractmethod
    def generate_pivot(
        self,
        grouping_column_name,
        pivot_column_name,
        values_column_names,
        unique_values,
        input_node,
    ):
        pass

    @abstractmethod
    def generate_casted_columns(
        self, column_names, cast_from_map, cast_to_map, **kwargs
    ):
        pass

    @abstractmethod
    def generate_truthy_bool_expression(self, column_name, column_type):
        pass

    @abstractmethod
    def generate_derived_columns_sql(self, input_node):
        pass

    @abstractmethod
    def generate_reassign_order_post_union_command(
        self, column_names, input_node_order_column_name, input_node_sql
    ):
        pass

    @abstractmethod
    def generate_new_row_labels_columns_command(
        self, new_row_label_column_name, column_names, input_node_sql, new_row_labels
    ):
        pass

    @abstractmethod
    def generate_isin_collection_expression(
        self, column_name: str, column_type: np.dtype, values
    ):
        pass

    @abstractmethod
    def generate_dataframe_isin_series(self, column_name):
        pass

    @abstractmethod
    def generate_dataframe_isin_dataframe(self, column_name):
        pass

    @abstractmethod
    def generate_between_time_filter_expression(
        self,
        index_name: str,
        start_time_micros: int,
        end_time_micros: int,
        include_start: bool,
        include_end: bool,
        compare_start_to_utc_time: bool,
        compare_end_to_utc_time: bool,
    ):
        pass

    @abstractmethod
    def generate_union_all_query(
        self,
        data: list[UnionAllDataForDialect],
        column_names,
        row_labels_column_names,
        order_column_name,
        new_dtypes,
    ):
        pass

    @abstractmethod
    def generate_row_value_equals_group_by_key_predicate(self, by_columns, lookup_key):
        pass

    @abstractmethod
    def generate_row_value_not_equals_predicate(
        self, column_name: str, values: Iterable
    ) -> str:
        pass

    @abstractmethod
    def generate_pandas_query_predicate(
        self,
        query: str,
        local_dict: Dict[str, Any],
        global_dict: Dict[str, Any],
        input_columns: list[str],
        column_name_mapper,
    ):
        pass

    @abstractmethod
    def generate_dates_within_offset_of_min_predicate(
        self, column_name: str, offset: pandas.DateOffset
    ):
        pass

    @abstractmethod
    def generate_dates_within_offset_of_max_predicate(
        self, column_name: str, offset: pandas.DateOffset
    ):
        pass

    @abstractmethod
    def _run_query_and_return_dataframe_uncached(self, query):
        pass

    @abstractmethod
    def materialize_pandas_dataframe_as_table(self, table_name, pandas_dataframe):
        pass

    @abstractmethod
    def timedelta_to_datetime_addend(self, timedelta: pandas.Timedelta) -> str:
        pass

    @abstractmethod
    def scalar_timestamp_for_subtraction(self, timestamp: pandas.Timestamp):
        pass

    @abstractmethod
    def generate_datetime_plus_timedelta(
        self, datetime_sql: str, timedelta_sql: str
    ) -> str:
        pass

    @abstractmethod
    def generate_datetime_minus_timedelta(self, left_sql: str, right_sql: str) -> str:
        pass

    def generate_datetime_minus_datetime(self, left_sql: str, right_sql: str) -> str:
        pass

    def generate_equal_null_predicate(self, lhs: str, rhs: str) -> str:
        pass

    @abstractmethod
    def generate_bitwise_and(self, op_1, op_2) -> str:
        pass

    @abstractmethod
    def generate_bitwise_or(self, op_1, op_2) -> str:
        pass

    @abstractmethod
    def generate_bitwise_xor(self, op_1, op_2) -> str:
        pass

    @abstractmethod
    def generate_coalesce(self, column_list) -> str:
        pass

    @abstractmethod
    def generate_subselect_expression(self, input_sql):
        pass

    @abstractmethod
    def generate_reorder_columns_statement(
        self, input_node_sql, column_list, order_column_name, row_labels_column_name
    ):
        pass

    @abstractmethod
    def get_last_table_update_time(self, table_name):
        pass
