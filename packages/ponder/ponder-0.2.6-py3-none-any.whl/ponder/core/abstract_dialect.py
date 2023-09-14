from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, List, Optional

import numpy as np
import pandas

from ponder.core.common import (
    __PONDER_ORDER_COLUMN_NAME__,
    GROUPBY_FUNCTIONS,
    REDUCE_FUNCTION,
    UnionAllDataForDialect,
)


class AbstractDialect(ABC):
    @abstractmethod
    def generate_sanitized_name(self, col_name):
        pass

    @abstractmethod
    def format_name(self, name):
        pass

    @abstractmethod
    def format_value(self, value):
        pass

    @abstractmethod
    def format_value_by_type(self, value):
        pass

    @abstractmethod
    def format_table_name(self, table_or_query):
        pass

    @abstractmethod
    def generate_join_command(
        self,
        select_list,
        left_node_query,
        right_node_query,
        how,
        left_on,
        right_on,
        left_order_column_name,
        right_order_column_name,
        result_order_column_name,
        db_index_column_name: Optional[str],
        indicator=False,
    ):
        pass

    @abstractmethod
    def generate_join_asof_command(
        self,
        left_node_query,
        left_node_columns,
        right_node_query,
        right_node_columns,
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
    def generate_rename_columns_command(
        self,
        input_query,
        input_column_names,
        input_order_column_name,
        column_name_renames,
        original_row_labels_column_names: list[str],
        result_order_column_name=__PONDER_ORDER_COLUMN_NAME__,
    ):
        pass

    @abstractmethod
    def generate_read_table_command(self, table_name, column_list=None, skipfooter=0):
        pass

    @abstractmethod
    def generate_map_function(self, function, params_list):
        pass

    @abstractmethod
    def generate_count(self, params_list):
        pass

    @abstractmethod
    def generate_isna(self, params_list):
        pass

    @abstractmethod
    def generate_notna(self, params_list):
        pass

    @abstractmethod
    def generate_dt_nanosecond(self, params_list):
        pass

    @abstractmethod
    def generate_dt_microsecond(self, params_list):
        pass

    @abstractmethod
    def generate_dt_second(self, params_list):
        pass

    @abstractmethod
    def generate_dt_minute(self, params_list):
        pass

    @abstractmethod
    def generate_dt_hour(self, params_list):
        pass

    @abstractmethod
    def generate_dt_day(self, params_list):
        pass

    @abstractmethod
    def generate_dt_dayofweek(self, params_list):
        pass

    @abstractmethod
    def generate_dt_day_name(self, params_list):
        pass

    @abstractmethod
    def generate_dt_dayofyear(self, params_list):
        pass

    @abstractmethod
    def generate_dt_week(self, params_list):
        pass

    @abstractmethod
    def generate_dt_month(self, params_list):
        pass

    @abstractmethod
    def generate_dt_month_name(self, params_list):
        pass

    @abstractmethod
    def generate_dt_quarter(self, params_list):
        pass

    @abstractmethod
    def generate_dt_year(self, params_list):
        pass

    @abstractmethod
    def generate_dt_tz_convert(self, params_list):
        pass

    @abstractmethod
    def generate_dt_tz_localize(self, params_list):
        pass

    @abstractmethod
    def generate_str_center(self, params_list):
        pass

    @abstractmethod
    def generate_str_contains(self, params_list):
        pass

    @abstractmethod
    def generate_str_count(self, params_list):
        pass

    @abstractmethod
    def generate_str_decode(self, params_list):
        pass

    @abstractmethod
    def generate_str_encode(self, params_list):
        pass

    @abstractmethod
    def generate_str_endswith(self, params_list):
        pass

    @abstractmethod
    def generate_str_extract(self, column_name, pat, flags):
        pass

    @abstractmethod
    def generate_str_find(self, params_list):
        pass

    @abstractmethod
    def generate_str_index(self, params_list):
        pass

    @abstractmethod
    def generate_str_findall(self, params_list):
        pass

    @abstractmethod
    def generate_str_fullmatch(self, params_list):
        pass

    @abstractmethod
    def generate_str_get(self, params_list):
        pass

    @abstractmethod
    def generate_str_join(self, params_list):
        pass

    @abstractmethod
    def generate_str_lstrip(self, params_list):
        pass

    @abstractmethod
    def generate_str_ljust(self, params_list):
        pass

    @abstractmethod
    def generate_str_match(self, params_list):
        pass

    # Unlike most other string functions, this method returns a list of strings because
    # it takes one column as input and returns three columns as output, each requiring
    # its own SQL expression.
    @abstractmethod
    def generate_str_partition(self, column_name, sep, expand):
        pass

    @abstractmethod
    def generate_str_removeprefix(self, params_list):
        pass

    @abstractmethod
    def generate_str_removesuffix(self, params_list):
        pass

    @abstractmethod
    def generate_str_repeat(self, params_list):
        pass

    @abstractmethod
    def generate_str_replace(self, params_list):
        pass

    @abstractmethod
    def generate_str_rfind(self, params_list):
        pass

    generate_str_rindex = generate_str_rfind

    @abstractmethod
    def generate_str_rjust(self, params_list):
        pass

    # Unlike most other string functions, this method returns a list of strings because
    # it takes one column as input and returns three columns as output, each requiring
    # its own SQL expression.
    @abstractmethod
    def generate_str_rpartition(self, column_name, sep, expand):
        pass

    @abstractmethod
    def generate_str_rsplit(self, params_list):
        pass

    @abstractmethod
    def generate_str_rstrip(self, params_list):
        pass

    @abstractmethod
    def generate_str_slice(self, params_list):
        pass

    @abstractmethod
    def generate_str_slice_replace(self, params_list):
        pass

    @abstractmethod
    def generate_str_split(self, params_list):
        pass

    @abstractmethod
    def generate_str_startswith(self, params_list):
        pass

    @abstractmethod
    def generate_str_strip(self, params_list):
        pass

    @abstractmethod
    def generate_str_swapcase(self, params_list):
        pass

    @abstractmethod
    def generate_str_translate(self, params_list):
        pass

    @abstractmethod
    def generate_str_wrap(self, params_list):
        pass

    @abstractmethod
    def generate_str_capitalize(self, params_list):
        pass

    @abstractmethod
    def generate_str_isalnum(self, params_list):
        pass

    @abstractmethod
    def generate_str_isalpha(self, params_list):
        pass

    @abstractmethod
    def generate_str_isdecimal(self, params_list):
        pass

    @abstractmethod
    def generate_str_isdigit(self, params_list):
        pass

    @abstractmethod
    def generate_str_islower(self, params_list):
        pass

    @abstractmethod
    def generate_str_isnumeric(self, params_list):
        pass

    @abstractmethod
    def generate_str_isspace(self, params_list):
        pass

    @abstractmethod
    def generate_str_istitle(self, params_list):
        pass

    @abstractmethod
    def generate_str_isupper(self, params_list):
        pass

    @abstractmethod
    def generate_str_len(self, params_list):
        pass

    @abstractmethod
    def generate_str_title(self, params_list):
        pass

    @abstractmethod
    def generate_str_lower(self, params_list):
        pass

    @abstractmethod
    def generate_str_upper(self, params_list):
        pass

    @abstractmethod
    def generate_window_function(
        self,
        function,
        col,
        skipna,
        window=None,
        non_numeric_col: Optional[bool] = None,
        expanding: Optional[bool] = None,
        partition_by: Optional[List] = None,
        agg_args: Optional[List] = None,
        agg_kwargs: Optional[Dict] = None,
        other_col=None,
    ):
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
    def generate_reduction_column_transformation(
        self,
        function,
        formatted_col: str,
        percentile=None,
        params_list=None,
        formatted_other_col: str = None,
    ):
        pass

    @abstractmethod
    def generate_truthy_bool_expression(self, column_name, column_type):
        pass

    @abstractmethod
    def generate_map_node_command(
        self,
        conn,
        function_sql: str,
        labels_to_apply_over: list[str],
        all_columns: list[str],
        input_node_sql: str,
    ) -> str:
        pass

    @abstractmethod
    def generate_casted_columns(self, column_names, cast_from_map, cast_to_map):
        pass

    @abstractmethod
    def generate_groupby_nth_predicate(self, by, order_column, n):
        pass

    @abstractmethod
    def generate_groupby_window_command(
        self,
        input_query,
        input_column_names,
        aggregation_function_map,
        group_by_columns,
        row_labels_column_names,
        input_order_column_name,
        aggregation_function_args,
        aggregation_function_kwargs,
        other_col_id,
    ):
        pass

    @abstractmethod
    def generate_groupby_view_command(
        self,
        input_query,
        input_column_names,
        aggregation_function_map,
        group_by_columns,
        row_labels_column_names,
        input_order_column_name,
        result_order_column_name,
        sort_by_group_keys,
        aggregation_function_args,
        aggregation_function_kwargs,
    ):
        pass

    @abstractmethod
    def generate_groupby_command(
        self,
        input_query,
        input_column_names,
        aggregation_function_map,
        group_by_columns,
        input_order_column_name,
        result_order_column_name,
        sort_by_group_keys: bool,
        aggregation_function_args,
        aggregation_function_kwargs,
        dropna_groupby_keys,
        other_col_id,
    ):
        pass

    @abstractmethod
    def generate_groupby_head_predicate(self, by, order_column, n):
        pass

    @abstractmethod
    def generate_groupby_tail_predicate(self, by, order_column, n):
        pass

    @abstractmethod
    def generate_drop_na_columns_query(self, how, thresh, subset, index_name, columns):
        pass

    @abstractmethod
    def generate_drop_na_rows_predicate(self, how, thresh, columns):
        pass

    @abstractmethod
    def generate_string_values_from_values(self, values):
        pass

    @abstractmethod
    def generate_get_dummies_command(
        self,
        non_dummy_cols,
        column,
        unique_vals,
        order_column_name,
        row_labels_column_names,
        input_node_column_names,
        input_node_row_labels_column_names,
        input_node_order_column_name,
        input_node_query,
        prefix,
        prefix_sep,
    ):
        pass

    @abstractmethod
    def generate_get_unique_values(self, input_node_sql, column_name):
        pass

    @abstractmethod
    def generate_column_is_min_predicate(self, column_name, by_columns):
        pass

    @abstractmethod
    def generate_column_is_max_predicate(self, column_name, by_columns):
        pass

    @abstractmethod
    def generate_column_wise_reduce_node_command(
        self,
        function: REDUCE_FUNCTION,
        labels_to_apply_over: list[str],
        input_node_sql: str,
        percentile: Optional[float] = None,
        params_list: Optional[object] = None,
        other_col_id: str = None,
    ) -> str:
        pass

    @abstractmethod
    def generate_row_wise_reduce_node_command(
        self,
        input_column_names: list[str],
        input_column_types,
        function: REDUCE_FUNCTION,
        input_node_sql: str,
        order_and_labels_column_strings: str,
        result_column_name: str,
    ) -> str:
        pass

    @abstractmethod
    def generate_map_column_expressions(self, labels_to_apply_over, n):
        pass

    @abstractmethod
    def generate_downsample_command(
        self,
        col,
        offset: pandas.DateOffset,
        start_val: pandas.Timestamp,
        end_val: pandas.Timestamp,
        sum_interval: float,
    ):
        pass

    @abstractmethod
    def generate_downsample_index_command(
        self,
        col,
        offset: pandas.DateOffset,
        start_val: pandas.Timestamp,
        end_val: pandas.Timestamp,
    ):
        pass

    @abstractmethod
    def generate_upsample_command(
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
    def generate_get_first_element_by_row_label_rank_command(
        self, col, row_labels_column_name
    ):
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

    @abstractmethod
    def generate_pivot_command(
        self,
        grouping_column_name,
        pivot_column_name,
        values_column_name,
        unique_values,
        input_node_query,
        input_node_order_column_name,
        aggfunc: GROUPBY_FUNCTIONS,
        add_qualifier_to_new_column_names,
    ):
        pass

    @abstractmethod
    def generate_reassign_order_post_union_command(self, column_names, input_node_sql):
        pass

    @abstractmethod
    def generate_new_row_labels_columns_command(
        self, new_row_label_column_names, column_names, input_node_sql, new_row_labels
    ):
        pass

    @abstractmethod
    def generate_isin_collection_expression(
        self, column_name: str, column_type: np.dtype, values: Iterable
    ):
        pass

    @abstractmethod
    def generate_dataframe_isin_series(
        self,
        column_name,
    ):
        pass

    @abstractmethod
    def generate_dataframe_isin_dataframe(
        self,
        column_name,
    ):
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
        node_data_list: list[UnionAllDataForDialect],
        column_names,
        row_labels_column_names,
        order_column_name,
        new_dtypes,
    ):
        pass

    @abstractmethod
    def generate_row_value_equals_group_by_key_predicate(
        self, by_columns: Iterable, lookup_key: Iterable
    ):
        pass

    @abstractmethod
    def generate_row_value_not_equals_predicate(
        self, column_name: str, values: Iterable
    ) -> str:
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
    def generate_datetime_plus_timedelta(
        self, datetime_sql: str, timedelta_sql: str
    ) -> str:
        pass

    @abstractmethod
    def generate_datetime_minus_timedelta(self, left_sql: str, right_sql: str) -> str:
        pass

    @abstractmethod
    def generate_datetime_minus_datetime(self, left_sql: str, right_sql: str) -> str:
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
    def generate_autoincrement_type(self):
        pass

    @abstractmethod
    def generate_subselect_expression(self, input_sql):
        pass

    @abstractmethod
    def generate_create_table_command(
        self,
        table_name,
        column_names,
        column_types,
        order_column_name,
        order_column_type,
        is_temp,
        is_global_temp,
        for_csv=False,
    ):
        pass

    @abstractmethod
    def generate_replace_values_statement(
        self,
        input_node_sql,
        column_list,
        replace_values_column_name,
        replace_values_dict,
    ):
        pass
