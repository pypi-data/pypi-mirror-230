from __future__ import annotations

import random
import string
from typing import Any, Dict, Iterable, Optional

import numpy as np
import pandas

from .common import UnionAllDataForDialect


########################################################
# ConnectionDialectPassthroughMixin is a set of functions
# which implement AbstractConnection, but which simply
# passthrough the call to the underlying dialect. It is
# inherited by SQLConnection
#
class ConnectionDialectPassthroughMixin:
    def __init__(self):
        pass

    def initialize(self, connection, dialect):
        self._dialect = dialect
        self._connection = connection

    def generate_subquery_table_name(self):
        return f"""PONDER_{"".join(
            random.choices(string.ascii_uppercase, k=10)
        )}"""

    def generate_sanitized_name(self, col_name):
        return self._dialect.generate_sanitized_name(col_name)

    def format_name(self, name):
        return self._dialect.format_name(name)

    def format_names_list(self, name):
        return self._dialect.format_names_list(name)

    def format_name_thrice(self, name):
        return self._dialect.format_name_thrice(name)

    def format_names_list_thrice(self, name):
        return self._dialect.format_names_list_thrice(name)

    def format_value(self, value):
        return self._dialect.format_value(value)

    def format_value_by_type(self, value):
        return self._dialect.format_value_by_type(value)

    def format_name_cast_to_type(self, value, type):
        return self._dialect.format_name_cast_to_type(value, type)

    def generate_false_constant(self):
        return self._dialect.generate_false_constant()

    def generate_map_column_expressions(self, labels_to_apply_over, n):
        return self._dialect.generate_map_column_expressions(labels_to_apply_over, n)

    def generate_column_is_min_predicate(self, column_name, by_columns):
        return self._dialect.generate_column_is_min_predicate(column_name, by_columns)

    def generate_column_is_max_predicate(self, column_name, by_columns):
        return self._dialect.generate_column_is_max_predicate(column_name, by_columns)

    def generate_select(self, table_name, column_list, skipfooter=0):
        return self._dialect.generate_read_table_command(
            table_name, column_list, skipfooter
        )

    def generate_drop_na_columns_query(self, how, thresh, subset, index_name, columns):
        return self._dialect.generate_drop_na_columns_query(
            how, thresh, subset, index_name, columns
        )

    def generate_drop_na_rows_predicate(self, how, thresh, columns):
        return self._dialect.generate_drop_na_rows_predicate(how, thresh, columns)

    def generate_string_values_from_values(self, values):
        return self._dialect.generate_string_values_from_values(values)

    def generate_str_rjust(self, params_list):
        return self._dialect.generate_str_rjust(self, params_list)

    # Unlike most other string functions, this method returns a list of strings because
    # it takes one column as input and returns three columns as output, each requiring
    # its own SQL expression.
    def generate_str_rpartition(self, column_name, sep, expand):
        return self._dialect.generate_str_rpartition(column_name, sep, expand)

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
        return self._dialect.generate_window_function(
            cumulative_function,
            col,
            skipna,
            window,
            non_numeric_col,
            expanding,
            other_col=other_col,
        )

    def generate_with_cross_join_col_expr(self, col, kwargs):
        return self._dialect.generate_with_cross_join_col_exp(col, kwargs)

    def generate_downsample_function(
        self,
        col,
        offset: pandas.DateOffset,
        start_val: pandas.Timestamp,
        end_val: pandas.Timestamp,
        sum_interval: float,
    ):
        return self._dialect.generate_downsample_command(
            col, offset, start_val, end_val, sum_interval
        )

    def generate_downsample_index_function(
        self,
        col,
        offset: pandas.DateOffset,
        start_val: pandas.Timestamp,
        end_val: pandas.Timestamp,
    ):
        return self._dialect.generate_downsample_index_command(
            col, offset, start_val, end_val
        )

    def generate_upsample_function(
        self,
        col,
        offset: pandas.DateOffset,
        start_val: pandas.Timestamp,
        end_val: pandas.Timestamp,
        sum_interval: float,
        interval: float,
    ):
        return self._dialect.generate_upsample_command(
            col, offset, start_val, end_val, sum_interval, interval
        )

    def generate_cast_to_type(self, col, cast_type):
        return self._dialect.generate_cast_to_type_command(col, cast_type)

    def generate_get_first_element_by_row_label_rank(self, col, row_labels_column_name):
        return self._dialect.generate_get_first_element_by_row_label_rank_command(
            col, row_labels_column_name
        )

    def generate_replace_nan_with_0(self, col):
        return self._dialect.generate_replace_nan_with_0(col)

    def generate_abs(self, col):
        return self._dialect.generate_abs(col)

    def generate_round(self, col, decimals):
        return self._dialect.generate_round(col, decimals)

    # Used for groupby.head()
    def generate_groupby_head_predicate(self, by, order_column, n):
        formatted_by = ",".join(self.format_names_list(by))
        formatted_order_column = self.format_name(order_column)
        return self._dialect.generate_groupby_head_predicate(
            formatted_by, formatted_order_column, n
        )

    # Used for groupby.tail()
    def generate_groupby_tail_predicate(self, by, order_column, n):
        formatted_by = ",".join(self.format_names_list(by))
        formatted_order_column = self.format_name(order_column)
        return self._dialect.generate_groupby_tail_predicate(
            formatted_by, formatted_order_column, n
        )

    # Used for groupby.nth()
    def generate_groupby_nth_predicate(self, by, order_column, n):
        formatted_by = ",".join(self.format_names_list(by))
        formatted_order_column = self.format_name(order_column)
        return self._dialect.generate_groupby_nth_predicate(
            formatted_by, formatted_order_column, n
        )

    def generate_casted_columns(
        self, column_names, cast_from_map, cast_to_map, **kwargs
    ):
        return self._dialect.generate_casted_columns(
            column_names, cast_from_map, cast_to_map, **kwargs
        )

    def generate_truthy_bool_expression(self, column_name, column_type):
        return self._dialect.generate_truthy_bool_expression(column_name, column_type)

    def generate_reassign_order_post_union_command(self, column_names, input_node_sql):
        return self._dialect.generate_reassign_order_post_union_command(
            column_names, input_node_sql
        )

    def generate_new_row_labels_columns_command(
        self, new_row_label_column_name, column_names, input_node_sql, new_row_labels
    ):
        return self._dialect.generate_new_row_labels_columns_command(
            new_row_label_column_name, column_names, input_node_sql, new_row_labels
        )

    def generate_isin_collection_expression(
        self, column_name: str, column_type: np.dtype, values
    ):
        return self._dialect.generate_isin_collection_expression(
            column_name, column_type, values
        )

    def generate_dataframe_isin_series(self, column_name):
        return self._dialect.generate_dataframe_isin_series(column_name)

    def generate_dataframe_isin_dataframe(self, column_name):
        return self._dialect.generate_dataframe_isin_dataframe(column_name)

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
        return self._dialect.generate_between_time_filter_expression(
            index_name,
            start_time_micros,
            end_time_micros,
            include_start,
            include_end,
            compare_start_to_utc_time,
            compare_end_to_utc_time,
        )

    def generate_row_ge_value_predicate(self, column_name: str, value) -> str:
        return self._dialect.generate_row_ge_value_predicate(column_name, value)

    def generate_row_le_value_predicate(self, column_name: str, value) -> str:
        return self._dialect.generate_row_le_value_predicate(column_name, value)

    def generate_row_between_inclusive_predicate(
        self, column_name: str, value_start, value_stop
    ) -> str:
        return self._dialect.generate_row_between_inclusive_predicate(
            column_name, value_start, value_stop
        )

    def generate_union_all_query(
        self,
        data: list[UnionAllDataForDialect],
        column_names,
        row_labels_column_names,
        order_column_name,
        new_dtypes,
    ):
        return self._dialect.generate_union_all_query(
            data, column_names, row_labels_column_names, order_column_name, new_dtypes
        )

    def generate_row_value_equals_group_by_key_predicate(self, by_columns, lookup_key):
        return self._dialect.generate_row_value_equals_group_by_key_predicate(
            by_columns, lookup_key
        )

    def generate_row_value_not_equals_predicate(
        self, column_name: str, values: Iterable
    ) -> str:
        return self._dialect.generate_row_value_not_equals_predicate(
            column_name, values
        )

    def generate_pandas_query_predicate(
        self,
        query: str,
        local_dict: Dict[str, Any],
        global_dict: Dict[str, Any],
        input_columns: list[str],
        column_name_mapper,
    ):
        return self._dialect.generate_pandas_query_predicate(
            query, local_dict, global_dict, input_columns, column_name_mapper
        )

    def generate_dates_within_offset_of_min_predicate(
        self, column_name: str, offset: pandas.DateOffset
    ):
        return self._dialect.generate_dates_within_offset_of_min_predicate(
            column_name, offset
        )

    def generate_dates_within_offset_of_max_predicate(
        self, column_name: str, offset: pandas.DateOffset
    ):
        return self._dialect.generate_dates_within_offset_of_max_predicate(
            column_name, offset
        )

    def generate_map_function(self, function, params_list):
        return self._dialect.generate_map_function(function, params_list)

    def generate_lag_val_expr(self, column_name, order_column_name):
        formatted_column_name = self.format_name(column_name)
        formatted_order_column_name = self.format_name(order_column_name)
        return f"""
            LAG({formatted_column_name}, 1)
            OVER (
                ORDER BY {formatted_order_column_name}
            )
            """

    def generate_pandas_mask(
        self, binary_pred_str, dbcolumn, value_dict, upcast_to_object
    ):
        return self._dialect.generate_pandas_mask(
            binary_pred_str, dbcolumn, value_dict, upcast_to_object
        )

    def generate_value_dict_fill_na(
        self, label, value_dict, limit, group_cols, upcast_to_object
    ):
        return self._dialect.generate_value_dict_fill_na(
            label, value_dict, limit, group_cols, upcast_to_object
        )

    def generate_method_fill_na(
        self, method, limit, columns, group_cols: Optional[list[str]] = None
    ):
        return self._dialect.generate_method_fill_na(method, limit, columns, group_cols)

    def generate_cut_expression(self, column_name, categories, bins):
        return self._dialect.generate_cut_expression(column_name, categories, bins)

    def generate_pct_change(self, column_name, periods):
        return self._dialect.generate_pct_change(column_name, periods)

    def generate_diff(self, column_name, periods):
        return self._dialect.generate_diff(column_name, periods)

    def timedelta_to_datetime_addend(self, timedelta: pandas.Timedelta) -> str:
        return self._dialect.generate_timedelta_to_datetime_addend(timedelta)

    def scalar_timestamp_for_subtraction(self, timestamp: pandas.Timestamp):
        return self._dialect.generate_scalar_timestamp_for_subtraction(timestamp)

    def generate_datetime_plus_timedelta(
        self, datetime_sql: str, timedelta_sql: str
    ) -> str:
        return self._dialect.generate_datetime_plus_timedelta(
            datetime_sql, timedelta_sql
        )

    def generate_datetime_minus_timedelta(self, left_sql: str, right_sql: str) -> str:
        return self._dialect.generate_datetime_minus_timedelta(left_sql, right_sql)

    def generate_datetime_minus_datetime(self, left_sql: str, right_sql: str) -> str:
        return self._dialect.generate_datetime_minus_datetime(left_sql, right_sql)

    def generate_equal_null_predicate(self, lhs: str, rhs: str) -> str:
        return self._dialect.generate_equal_null_predicate(lhs, rhs)

    def generate_bitwise_negation(self, op) -> str:
        return self._dialect.generate_bitwise_negation(op)

    def generate_bitwise_and(self, op_1, op_2) -> str:
        return self._dialect.generate_bitwise_and(op_1, op_2)

    def generate_bitwise_or(self, op_1, op_2) -> str:
        return self._dialect.generate_bitwise_or(op_1, op_2)

    def generate_bitwise_xor(self, op_1, op_2) -> str:
        return self._dialect.generate_bitwise_or(op_1, op_2)

    def generate_coalesce(self, column_list) -> str:
        return self._dialect.generate_coalesce(column_list)

    def generate_subselect_expression(self, input_sql):
        return self._dialect.generate_subselect_expression(input_sql)

    def generate_boolean_negation(self, op) -> str:
        return self._dialect.generate_boolean_negation(op)
