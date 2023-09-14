# Licensed to Modin Development Team under one or more contributor license agreements.
# See the NOTICE file distributed with this work for additional information regarding
# copyright ownership.  The Modin Development Team licenses this file to you under the
# Apache License, Version 2.0 (the "License"); you may not use this file except in
# compliance with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
from __future__ import annotations

import logging
import math
import random
import re
import string
from functools import reduce
from typing import Dict, Iterable, List, Optional, Pattern

import numpy as np
import pandas
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_object_dtype,
    is_scalar,
    is_string_dtype,
)
from pandas.core.dtypes.common import is_bool_dtype, is_numeric_dtype, pandas_dtype

from ponder.core.common import (
    __ISIN_DATAFRAME_LEFT_PREFIX__,
    __ISIN_DATAFRAME_RIGHT_PREFIX__,
    __ISIN_SERIES_VALUES_COLUMN_NAME__,
    __PONDER_AGG_OTHER_COL_ID__,
    __PONDER_AGG_OTHER_COL_NAME__,
    __PONDER_ORDER_COLUMN_NAME__,
    __PONDER_ROW_LABELS_COLUMN_NAME__,
    __PONDER_TEMP_TABLE_ROWID_COLUMN__,
    GROUPBY_FUNCTIONS,
    REDUCE_FUNCTION,
    UnionAllDataForDialect,
    generate_column_name_from_value,
)
from ponder.core.error_codes import PonderError, make_exception
from ponder.core.sql_dialect import (
    _pandas_offset_object_to_n_and_sql_unit,
    _pandas_start_val_to_end_period,
)

from ..postgres.postgres_dialect import _regex_params, postgres_dialect

logger = logging.getLogger(__name__)


class duckdb_dialect(postgres_dialect):
    pandas_type_to_duckdb_type_map = {
        "bool": "BOOLEAN",
        "date": "TIMESTAMP",
        "datetime64[ms]": "TIMESTAMP",
        "datetime64[ns]": "TIMESTAMP",
        "datetime": "TIMESTAMP",
        "float": "REAL",
        "float64": "DOUBLE",
        "uint8": "INTEGER",
        "int": "INTEGER",
        "int8": "INTEGER",
        "int16": "INTEGER",
        "int32": "INTEGER",
        "int64": "BIGINT",
        "str": "VARCHAR",
        "object": "VARCHAR",
        "unicode": "VARCHAR",
    }

    def format_datetime_format(self, time_column, datetime_format):
        return f"strptime({time_column}, " f"'{datetime_format}')::DATETIME"

    def format_value(self, value):
        if isinstance(value, str):
            value = value.replace("\\", "\\\\").replace("'", "''")
        return f"'{value}'" if isinstance(value, str) else f"{value}"

    def format_value_by_type(self, value):
        if value is None:
            return "NULL"
        if isinstance(value, pandas.Timestamp):
            return f"'{value}'::timestamp"
        if isinstance(value, str):
            return f"'{value}'"
        if isinstance(value, pandas.Interval):
            return (
                "{_ponder_python_object_type: 'pandas.Interval', "
                + f"'data': {{'left': {self.format_value_by_type(value.left)}, "
                + f"'right': {self.format_value_by_type(value.right)}, "
                + f"'closed': {self.format_value_by_type(value.closed)}}}}}"
            )
        return f"{value}"

    def format_table_name(self, table_or_query):
        if self.is_query_like(table_or_query):
            return f"({table_or_query})"
        if "." in table_or_query:
            return table_or_query
        return f'"{table_or_query}"'

    # DuckDB accepts the pandas datetime format specifiers, more or less
    def pandas_datetime_format_to_db_datetime_format(self, pandas_format: str) -> str:
        # Python pads %f on the right while DuckDB pads %f on the left
        # so to correct for this we convert %f to %g milliseconds. This could result
        # in compatibility problems if someone really is using 6-digit microsecond
        # granularity, but this is one of many little issues related to pandas/DuckDB
        # time handling; see: https://github.com/duckdb/duckdb/issues/6270
        pandas_format = pandas_format.replace("%f", "%g")
        return pandas_format

    def generate_create_temp_table_with_rowid_command(self, temp_table_name, sql_query):
        # If the input table is a query - there won't be a rowid column we can use
        # so we have to generate one.
        if self.is_query_like(sql_query):
            return super().generate_create_temp_table_with_rowid_command(
                temp_table_name=temp_table_name, sql_query=sql_query
            )
        else:
            row_labels_clause = f", rowid AS {__PONDER_ORDER_COLUMN_NAME__}"

        formatted_sql_query = self.format_table_name(sql_query)
        return (
            f"CREATE TEMP TABLE {self.format_table_name(temp_table_name)} AS SELECT * "
            f"{row_labels_clause}"
            f" FROM {formatted_sql_query}"
        )

    def generate_temp_table_for_subquery(self, temp_table_name, query):
        logger
        logger.debug(f"Postgres dialect {temp_table_name}")
        return (
            f"""
            CREATE TEMP TABLE {self.format_table_name(temp_table_name)} AS
            ({query})
            """,
            f"""
            SELECT * FROM {self.format_table_name(temp_table_name)}
            """,
        )

    def generate_create_temp_table_for_wherein(self, temp_table_name, rowids):
        logger
        logger.debug(f"DuckDB dialect {temp_table_name}")

        __VALUE_SIZE__ = 2000
        rowid_insert_exp = []
        for i in range(0, len(rowids), __VALUE_SIZE__):
            rowids_to_insert = ", ".join(
                [
                    f"({rowid})"
                    for rowid in rowids[i : (i + __VALUE_SIZE__)]  # noqa: E203
                ]
            )
            rowid_insert_exp.append(rowids_to_insert)

        formatted_temp_table_name = self.format_table_name(temp_table_name)
        return_arr = [
            f"""
            CREATE TEMP TABLE {formatted_temp_table_name} AS SELECT
            {__PONDER_TEMP_TABLE_ROWID_COLUMN__} FROM VALUES {rowid_insert_exp[0]} AS
             TEMPVAL({__PONDER_TEMP_TABLE_ROWID_COLUMN__})
            """,
        ]
        for i in range(1, len(rowid_insert_exp)):
            return_arr.append(
                f"""
                INSERT INTO {formatted_temp_table_name}
                SELECT {__PONDER_TEMP_TABLE_ROWID_COLUMN__} FROM
                VALUES {rowid_insert_exp[i]}  AS
                TEMPVAL({__PONDER_TEMP_TABLE_ROWID_COLUMN__})
                """
            )
        return_arr.append(
            f"""
            SELECT {__PONDER_TEMP_TABLE_ROWID_COLUMN__}
            FROM {formatted_temp_table_name}
            """,
        )
        logger.debug(f"DuckDB dialect return array size {len(return_arr)}")
        return return_arr

    def generate_create_table_from_df_command(self, table_name, df_name, temp=True):
        return f"""CREATE {'TEMPORARY' if temp else ''} TABLE {table_name}
            AS SELECT * FROM {df_name}"""

    def generate_groupby_result_order_expr(
        self,
        group_by_columns,
        input_order_column_name,
        result_order_column_name,
        sort_by_group_keys,
    ):
        group_by_column_string_for_order = ", ".join(
            [
                *(group_by_columns if sort_by_group_keys else []),
                input_order_column_name,
            ]
        )
        result_order_column_expression = (
            f"ROW_NUMBER() OVER (ORDER BY {group_by_column_string_for_order}) AS"
            + f" {result_order_column_name}"
        )
        return result_order_column_expression

    def generate_pivot_without_grouping_command(
        self,
        pivot_column_name,
        values_column_name,
        unique_values,
        input_node_query,
        input_node_order_column_name,
        aggregation_call,
        add_qualifier_to_new_column_names,
    ):
        formatted_pivot_column_name = self.format_name(pivot_column_name)

        str_unique_values = [
            generate_column_name_from_value(unique_value)
            for unique_value in unique_values
        ]
        # DuckDB slavishly produces column names that are exactly the same as the
        # data.
        formatted_once_final_values_column_names = []
        new_columns_prefix = (
            values_column_name + "_" if add_qualifier_to_new_column_names else ""
        )
        for v in str_unique_values:
            col_name = new_columns_prefix + v
            final_col = f"{v} AS {self.format_name(col_name)}"
            formatted_once_final_values_column_names.append(final_col)

        ret_val = f"""
            SELECT {input_node_order_column_name},
                {", ".join(formatted_once_final_values_column_names)}
            FROM (PIVOT (SELECT * FROM ({input_node_query})
            ORDER BY {values_column_name})
            ON {formatted_pivot_column_name}
            USING {aggregation_call})
        """
        return ret_val

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
        if aggfunc in (
            GROUPBY_FUNCTIONS.NUNIQUE,
            GROUPBY_FUNCTIONS.PROD,
            GROUPBY_FUNCTIONS.SIZE,
            GROUPBY_FUNCTIONS.FIRST,
            GROUPBY_FUNCTIONS.LAST,
        ):
            # TODO(https://ponderdata.atlassian.net/browse/POND-896): support these
            # methods.
            raise make_exception(
                NotImplementedError,
                PonderError.DUCKDB_PIVOT_UNSUPPORTED_AGGREGATION_FUNCTION,
                f"pivot_table() with aggregation function {aggfunc} not supported yet",
            )
        aggregation_call = self.generate_reduction_column_transformation(
            aggfunc,
            self.format_name(values_column_name),
        )

        if grouping_column_name is None:
            return self.generate_pivot_without_grouping_command(
                pivot_column_name,
                values_column_name,
                unique_values,
                input_node_query,
                input_node_order_column_name,
                aggregation_call,
                add_qualifier_to_new_column_names,
            )

        formatted_group_col_name_once = self.format_name(grouping_column_name)
        formatted_pivot_column_name = self.format_name(pivot_column_name)

        str_unique_values = [
            generate_column_name_from_value(unique_value)
            for unique_value in unique_values
        ]
        # DuckDB slavishly produces column names that are exactly the same as the
        # data.
        formatted_once_final_values_column_names = []
        new_columns_prefix = (
            values_column_name + "_" if add_qualifier_to_new_column_names else ""
        )
        for v in str_unique_values:
            col_name = new_columns_prefix + v
            final_col = f"{self.format_name(v)} AS {self.format_name(col_name)}"
            formatted_once_final_values_column_names.append(final_col)

        ret_val = f"""
            SELECT
                {formatted_group_col_name_once},
                ROW_NUMBER() OVER (
                    ORDER BY {formatted_group_col_name_once}) -1
                AS {__PONDER_ORDER_COLUMN_NAME__},
                {", ".join(formatted_once_final_values_column_names)}
            FROM (PIVOT ({input_node_query}) ON {formatted_pivot_column_name}
            USING {aggregation_call} GROUP BY {formatted_group_col_name_once})
        """
        return ret_val

    def generate_downsample_command(
        self,
        col,
        offset: pandas.DateOffset,
        start_val: pandas.Timestamp,
        end_val: pandas.Timestamp,
        sum_interval: float,
    ):
        n, unit = _pandas_offset_object_to_n_and_sql_unit(offset)
        end_val = _pandas_start_val_to_end_period(end_val, unit)
        if unit == "second":
            return f"TIME_BUCKET(INTERVAL '{n} seconds', {self.format_name(col)})"
        elif unit == "minute":
            return f"TIME_BUCKET(INTERVAL '{n} minutes', {self.format_name(col)})"
        elif unit == "hour":
            return f"TIME_BUCKET(INTERVAL '{n} hours', {self.format_name(col)})"
        elif unit == "day":
            return f"TIME_BUCKET(INTERVAL '{n} days', {self.format_name(col)})"
        elif unit == "week":
            if n == 1:
                return (
                    f"DATE_TRUNC({self.format_value(unit)}, "
                    f"{self.format_name(col)}) - 1"
                )
            return (
                f"LEAD(DATE_TRUNC({self.format_value(unit)}, "
                f"{self.format_name(col)}) - 1, 1, {self.format_value(end_val)})"
                f"OVER (ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)})"
            )
        elif unit == "month":
            if n == 1:
                return (
                    f"LAST_DAY(TIME_BUCKET(INTERVAL '{n} MONTHS', "
                    f"{self.format_name(col)}))"
                )
            return (
                f"LEAD(LAST_DAY(TIME_BUCKET(INTERVAL '{n} MONTHS', "
                f"{self.format_name(col)})), 1, {self.format_value(end_val)}) "
                f"OVER (ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)})"
            )
        elif unit == "quarter":
            interval_num = n * 3
            if n == 1:
                return (
                    f"LAST_DAY(DATE_TRUNC({self.format_value(unit)}, "
                    f"TIME_BUCKET(INTERVAL '{interval_num} months', "
                    f"{self.format_name(col)})) + INTERVAL 2 MONTH)"
                )
            return (
                f"LEAD(LAST_DAY(DATE_TRUNC({self.format_value(unit)}, "
                f"TIME_BUCKET(INTERVAL '{interval_num} months', "
                f"{self.format_name(col)})) + INTERVAL 2 MONTH), 1, "
                f"{self.format_value(end_val)})"
                f"OVER (ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)})"
            )
        elif unit == "year":
            if n == 1:
                return (
                    f"LAST_DAY(DATE_TRUNC({self.format_value(unit)}, "
                    f"TIME_BUCKET(INTERVAL '{n} years', "
                    f"{self.format_name(col)})) - 1 + INTERVAL 1 YEAR)"
                )
            return (
                f"LEAD(LAST_DAY(DATE_TRUNC({self.format_value(unit)}, "
                f"TIME_BUCKET(INTERVAL '{n} years', "
                f"{self.format_name(col)})) - 1 + INTERVAL 1 YEAR), 1, "
                f"{self.format_value(end_val)})"
                f"OVER (ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)})"
            )

    def generate_downsample_index_command(
        self,
        col,
        offset: pandas.DateOffset,
        start_val: pandas.Timestamp,
        end_val: pandas.Timestamp,
    ):
        # Uses a generator to create uniform sampled index
        # for cases where there are empty buckets not handled by
        # TIME_SLICE
        n, unit = _pandas_offset_object_to_n_and_sql_unit(offset)
        start_val = _pandas_start_val_to_end_period(start_val, unit)
        end_val = _pandas_start_val_to_end_period(end_val, unit)

        if unit == "week":
            interval_num = n * 7
            return (
                f"SELECT * FROM "
                f"GENERATE_SERIES(TIMESTAMP {self.format_value(start_val)}, "
                f"TIMESTAMP {self.format_value(end_val)}, "
                f"INTERVAL {interval_num} DAY)"
            )
        elif unit == "month":
            return (
                f"SELECT LAST_DAY(COLUMNS(*)) AS "
                f"{self.format_name('generate_series')} "
                f"FROM GENERATE_SERIES(TIMESTAMP {self.format_value(start_val)}, "
                f"TIMESTAMP {self.format_value(end_val)}, "
                f"INTERVAL {n} {unit})"
            )
        elif unit == "quarter":
            interval_num = n * 3
            return (
                f"SELECT LAST_DAY(COLUMNS(*)) AS "
                f"{self.format_name('generate_series')} "
                f"FROM GENERATE_SERIES(TIMESTAMP {self.format_value(start_val)}, "
                f"TIMESTAMP {self.format_value(end_val)}, "
                f"INTERVAL {interval_num} MONTH)"
            )
        elif unit == "year":
            return (
                f"SELECT LAST_DAY(COLUMNS(*)) AS "
                f"{self.format_name('generate_series')} "
                f"FROM GENERATE_SERIES(TIMESTAMP {self.format_value(start_val)}, "
                f"TIMESTAMP {self.format_value(end_val)}, "
                f"INTERVAL {n} {unit})"
            )
        else:
            return (
                f"SELECT * FROM GENERATE_SERIES(TIMESTAMP "
                f"{self.format_value(start_val)}, "
                f"TIMESTAMP {self.format_value(end_val)}, "
                f"INTERVAL {n} {unit})"
            )

    def generate_upsample_command(
        self,
        col,
        offset: pandas.DateOffset,
        start_val: pandas.Timestamp,
        end_val: pandas.Timestamp,
        sum_interval: float,
        interval: float,
    ):
        # Use GENERATE_SERIES to create rows based on the start_val
        n, unit = _pandas_offset_object_to_n_and_sql_unit(offset)
        start_val = _pandas_start_val_to_end_period(start_val, unit)
        end_val = _pandas_start_val_to_end_period(end_val, unit)

        if unit == "week":
            # DuckDB does have include the week keyword so we use days
            n *= 7
            unit = "day"
        elif unit == "quarter":
            # DuckDB identifies Quarters 0-3 separately so instead we use months
            n *= 3
            unit = "month"
        return (
            f"SELECT TIME_BUCKET(INTERVAL {int(interval)} SECOND, "
            f"{self.format_name('generate_series')}) AS {self.format_name(col)}, "
            f"{self.format_name('generate_series')} FROM "
            f"(SELECT * FROM GENERATE_SERIES(TIMESTAMP "
            f"{self.format_value(start_val)}, "
            f"TIMESTAMP {self.format_value(end_val)}, "
            f"INTERVAL {n} {unit}))"
        )

    def generate_temporary_sequence(self, sequence_name):
        return f"CREATE TEMPORARY SEQUENCE {sequence_name} MINVALUE 0"

    def generate_create_table_command(
        self,
        table_name,
        column_names,
        column_types,
        order_column_name,
        order_column_type,
        is_temp,
        is_global_temp,
    ):
        table_name = self.format_table_name(table_name)
        create_statement = "CREATE TABLE "
        if is_temp and not is_global_temp:
            create_statement = "CREATE TEMPORARY TABLE "

        # TODO: Fix setting the col label to a data column without
        # updating the list of row label names
        try:
            columns_clause = ", ".join(
                [
                    self.format_name(column_name)
                    + " "
                    + self.pandas_type_to_duckdb_type_map[str(column_type)]
                    for column_name, column_type in zip(column_names, column_types)
                ]
            )
        except Exception as e:
            raise make_exception(
                RuntimeError,
                PonderError.DUCKDB_CREATE_TABLE_FAILED,
                """Create table failed possibly because
                column types are not mapped correctly""",
            ) from e

        if not is_temp and not is_global_temp:
            if len(order_column_name or "") > 0:
                columns_clause += (
                    f", {self.format_name(order_column_name)} "
                    + self.pandas_type_to_postgres_type_map[str(order_column_type)]
                )

        create_statement += f" {table_name} ( {columns_clause} )"

        return create_statement

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
        left_by_formatted = self.format_names_list(left_by)
        right_by_formatted = self.format_names_list(right_by)

        left_on_formatted = self.format_names_list(left_on)
        right_on_formatted = self.format_names_list(right_on)

        if direction == "forward":
            if allow_exact_matches is False:
                operator = "<"
            else:
                operator = "<="

        if direction == "backward":
            if allow_exact_matches is False:
                operator = ">"
            else:
                operator = ">="

        on_fragment = " AND ".join(
            [
                f"{left_by_column} = {right_by_column}"
                for left_by_column, right_by_column in zip(
                    left_by_formatted, right_by_formatted
                )
            ]
        )

        if len(on_fragment) > 0:
            on_fragment += " AND "
        on_fragment += " AND ".join(
            [
                f"{left_on_column} {operator} {right_on_column}"
                for left_on_column, right_on_column in zip(
                    left_on_formatted, right_on_formatted
                )
            ]
        )

        select_list = self.format_names_list(left_node_columns)
        select_list.extend(
            self.format_names_list(
                [
                    right_node_column
                    for right_node_column in right_node_columns
                    if right_node_column not in right_on
                    and right_node_column not in right_by
                ]
            )
        )

        select_list_fragment = ", ".join(select_list)
        if left_order_column_name not in left_node_columns:
            select_list_fragment += f", {self.format_name(left_order_column_name)}"

        if __PONDER_ROW_LABELS_COLUMN_NAME__ not in left_node_columns:
            select_list_fragment += (
                f", {self.format_name(__PONDER_ROW_LABELS_COLUMN_NAME__)}"
            )

        result_order_column_expression = (
            f", {self.format_name(left_order_column_name)} "
            + f"AS {self.format_name(result_order_column_name)}"
        )
        select_list_fragment += result_order_column_expression

        row_number_field_name = f"""PONDER_{"".join(
            random.choices(string.ascii_uppercase, k=10)
        )}"""
        row_number_fragment = f"""
            ROW_NUMBER() OVER (
                PARTITION BY {left_order_column_name}
                ORDER BY {", ".join(right_on_formatted)}
                    {'DESC' if direction == 'forward' else 'ASC'}
            ) AS {row_number_field_name}
        """

        tolerance_fragment = ""
        if tolerance is not None:
            if isinstance(tolerance, pandas.Timedelta):
                total_microseconds = tolerance.microseconds
                tolerance_fragment = (
                    f" AND ABS(DATE_DIFF('MICROSECONDS', {left_on_formatted[0]}, "
                    + f"{right_on_formatted[0]})) < {total_microseconds}"
                )
            elif isinstance(tolerance, int):
                tolerance_fragment = (
                    f" AND ABS({left_on_formatted[0]} - {right_on_formatted[0]}) "
                    + f"< {tolerance}"
                )

        where_fragment = f" QUALIFY {row_number_field_name} = 1"

        ret_val = f"""
        SELECT
            {", ".join((
                select_list_fragment,
                row_number_fragment))}
        FROM (
            {left_node_query}
        ) AS LEFT_TABLE
        LEFT JOIN (
            SELECT
                {", ".join(self.format_names_list(right_node_columns))}
            FROM (
                {right_node_query}
            )
        ) AS RIGHT_TABLE
        ON
            {on_fragment} {tolerance_fragment} {where_fragment}
        ORDER BY
            {self.format_name(result_order_column_name)}
        """
        return ret_val

    def generate_load_table_from_csv_command(
        self,
        file_path,
        table_name,
        column_names,
        column_types,
        sep=",",
        header=0,
        date_format=None,
        na_values="",
        on_bad_lines="error",
    ):
        columns_clause = ", ".join(
            [
                f"""'{self.format_name(column_name)}' :
                    '{self.pandas_type_to_duckdb_type_map[str(column_type)]}'"""
                for column_name, column_type in zip(column_names, column_types)
            ]
        )

        insert_columns_clause = ", ".join(
            [self.format_name(column_name) for column_name in column_names]
        )

        columns_clause = ", COLUMNS = {" + columns_clause + "}"

        header_clause = ", HEADER = FALSE"

        skip_clause = f", SKIP = {header + 1}" if isinstance(header, int) else ""

        null_clause = "" if na_values is None else f", NULLSTR = '{na_values}'"

        on_bad_lines_clause = (
            "" if on_bad_lines == "error" else ", IGNORE_ERRORS = True"
        )

        command = (
            f"INSERT INTO {table_name}({insert_columns_clause})"
            f" (SELECT * FROM READ_CSV('{file_path}', timestampformat='{date_format}',"
            f" DELIM = '{sep}' {skip_clause} {header_clause} {null_clause} "
            f" {on_bad_lines_clause} {columns_clause}))"
        )
        return command

    def generate_copy_into_table_parquet_command(
        self, table_name, column_names, files, hive_partitioning
    ):
        formatted_cols = [self.format_name(column_name) for column_name in column_names]

        columns_clause = ",".join(formatted_cols)
        read_parquet_frag = (
            f"read_parquet({files}, hive_partitioning={hive_partitioning})"
        )
        from_clause = f" FROM ( SELECT {columns_clause} FROM {read_parquet_frag} )"

        command = f"INSERT INTO {table_name} ( {columns_clause} ) {from_clause}"
        # httpfs needs to be installed via DuckDB and not as another dependency
        command = f"INSTALL httpfs; LOAD httpfs; {command}"
        return command

    def generate_drop_sequence_command(self, sequence_name):
        return f"DROP SEQUENCE {sequence_name}"

    def generate_create_table_from_dataframe(self, table_name, dataframe_name):
        return f"CREATE TEMPORARY TABLE {table_name} AS SELECT * FROM {dataframe_name}"

    def generate_pandas_timestamp_to_date(self, timestamp: pandas.Timestamp):
        return f"TIMESTAMP {self.format_value(timestamp)}"

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
        select_clauses = []
        other_col = None
        if other_col_id is not None:
            # Special case to add columns that will later become an index
            other_col = input_column_names[other_col_id]
            select_clauses.append(f"{other_col_id} AS {__PONDER_AGG_OTHER_COL_ID__}")
            select_clauses.append(f"'{other_col}' AS {__PONDER_AGG_OTHER_COL_NAME__}")
        for input_column_name in input_column_names:
            formatted_col = self.format_name(input_column_name)
            if input_column_name in row_labels_column_names:
                # Special case resample since input_column_name is both
                # a row label name and a data column name. TODO(FIX):
                # this is a workaround for a BUG upstream.
                continue
            if input_column_name in aggregation_function_map:
                func = aggregation_function_map[input_column_name]
                skipna = aggregation_function_kwargs.get("skipna", False)
                transform = self.generate_window_function(
                    func,
                    input_column_name,
                    skipna=skipna,
                    partition_by=group_by_columns,
                    agg_args=aggregation_function_args,
                    agg_kwargs=aggregation_function_kwargs,
                    other_col=other_col,
                )
                select_clause = f"{transform} AS {formatted_col}"
            else:
                select_clause = f"{formatted_col}"
            select_clauses.append(select_clause)

        select_column_list = ",".join(select_clauses)

        return f"""
            SELECT
                {select_column_list},
                {", ".join(self.format_names_list(row_labels_column_names))},
                {self.format_name(input_order_column_name)}
            FROM
                ({input_query})
            """

    def generate_truthy_bool_expression(self, column_name, column_type):
        if is_string_dtype(column_type):
            falsy_check = f"LENGTH(TRIM({column_name})) = 0"
        elif is_numeric_dtype(column_type) and not is_bool_dtype(column_type):
            falsy_check = f"{column_name} = 0"
        else:
            falsy_check = f"{column_name} = false"

        return f"""
            CASE WHEN {column_name} IS NULL OR {falsy_check} THEN FALSE ELSE TRUE END
            """

    def generate_category_list_object(self, column_name, category_list):
        return (
            "{'_ponder_category': "
            + f"IFNULL(ARRAY_POSITION({category_list}, "
            + f"{self.format_name(column_name)}), "
            + "0) - 1 }"
        )

    def generate_category_object(self, column_name):
        return (
            "{'_ponder_category': "
            + "DENSE_RANK() OVER (ORDER BY "
            + f"{self.format_name(column_name)}) - 1"
            + "}"
        )

    def generate_reduction_column_transformation(
        self,
        function,
        formatted_col: str,
        percentile=None,
        params_list=None,
        formatted_other_col: str = None,
    ):
        if function is REDUCE_FUNCTION.BOOL_COUNT:
            return f"SUM(CAST({formatted_col} AS INT))"
        elif function is REDUCE_FUNCTION.COUNT_UNIQUE_INCLUDING_NULL:
            transformed = f"APPROX_COUNT_DISTINCT({formatted_col})"
            transformed += (
                f" + APPROX_COUNT_DISTINCT(CASE WHEN {formatted_col} IS NULL "
                + "THEN 1 ELSE NULL END)"
            )
            return transformed
        elif function is REDUCE_FUNCTION.COUNT_UNIQUE_EXCLUDING_NULL:
            return f"APPROX_COUNT_DISTINCT({formatted_col})"
        elif function is GROUPBY_FUNCTIONS.UNIQUE:
            return f"LIST({formatted_col})"
        elif function in (REDUCE_FUNCTION.SKEW, GROUPBY_FUNCTIONS.SKEW):
            return f"SKEWNESS({formatted_col})"
        elif function == GROUPBY_FUNCTIONS.PROD:
            return f"PRODUCT({formatted_col})"
        elif function in (REDUCE_FUNCTION.LOGICAL_OR, GROUPBY_FUNCTIONS.ANY):
            return f"bool_or({formatted_col})"
        elif function in (REDUCE_FUNCTION.LOGICAL_AND, GROUPBY_FUNCTIONS.ALL):
            return f"bool_and({formatted_col})"
        elif function is REDUCE_FUNCTION.STR_CAT:
            if params_list is None:
                raise make_exception(
                    RuntimeError,
                    PonderError.DUCKDB_STR_CAT_REDUCE_MISSING_PARAMS_LIST,
                    "Reduce node must have a params_list value for the STR_CAT "
                    + "reduce function.",
                )
            sep, na_rep = params_list
            if sep is None:
                sep = ""
            sep = f"'{sep}'"
            if na_rep is None:
                na_rep = "NULL"
            else:
                na_rep = f"'{na_rep}'"
            return f"""STRING_AGG(
                CASE WHEN
                    {formatted_col} IS NULL
                THEN
                    {na_rep}
                ELSE
                    {formatted_col}
                END,
                {sep}
            )
            """
        else:
            return super().generate_reduction_column_transformation(
                function, formatted_col, percentile, params_list, formatted_other_col
            )

    def generate_rolling_window_command(
        self,
        cumulative_function,
        col,
        window,
        non_numeric_col: bool,
        other_col,
    ):
        formatted_col = self.format_name(col)
        formatted_other_col = None if other_col is None else self.format_name(other_col)

        if cumulative_function == "COUNT":
            return f"""
                IF(COUNT(*) OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                ROWS BETWEEN {window-1} PRECEDING AND CURRENT ROW)={window},
                COUNT({formatted_col}) OVER (ORDER BY
                {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN {window-1}
                PRECEDING AND CURRENT ROW), NULL)
                """

        # Standard error of mean (SEM) does not have native postgres support
        # thus calculated as STDDEV/SQRT(N-1)
        if cumulative_function == "SEM":
            if non_numeric_col:
                return "NULL"
            return f"""
            CASE WHEN
            COUNT({formatted_col}) OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                ROWS BETWEEN {window-1} PRECEDING AND CURRENT ROW)={window}
            THEN
                (STDDEV({formatted_col}) OVER (ORDER BY
                {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN {window-1}
                PRECEDING AND CURRENT ROW))/SQRT({window-1})
            ELSE
                NULL
            END
            """

        if cumulative_function == "CORR":
            assert formatted_other_col is not None
            if non_numeric_col or window < 2:
                return "NULL"

            count_exp = f"""
            SUM(CAST(
                ({formatted_col} IS NOT NULL AND {formatted_other_col} IS NOT NULL)
                AS INT
            ))
            OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
            ROWS BETWEEN {window-1} PRECEDING AND CURRENT ROW)"""

            sigmas_exp = f"""
                    STDDEV_POP(
                        CASE WHEN {formatted_col} IS NULL
                        THEN NULL ELSE {formatted_other_col} END
                    )
                    OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN
                    {window-1} PRECEDING AND CURRENT ROW) *
                    STDDEV_POP(
                        CASE WHEN {formatted_other_col} IS NULL
                        THEN NULL ELSE {formatted_col} END
                    )
                    OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN
                    {window-1} PRECEDING AND CURRENT ROW)"""

            return f"""
                CASE WHEN {count_exp}={window} AND {count_exp} * {sigmas_exp} > 0
                THEN (
                    SUM(CAST(1 AS INT64)*{formatted_other_col}*{formatted_col}) OVER
                    (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN {window-1}
                    PRECEDING AND CURRENT ROW) - (
                        SUM(
                            CASE WHEN {formatted_col} IS NULL
                            THEN NULL ELSE {formatted_other_col} END
                        )
                        OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN
                        {window-1} PRECEDING AND CURRENT ROW) *
                        SUM(
                            CASE WHEN {formatted_other_col} IS NULL
                            THEN NULL ELSE {formatted_col} END
                        )
                        OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN
                        {window-1} PRECEDING AND CURRENT ROW) / {count_exp}
                    )) / (
                        {count_exp} * {sigmas_exp}
                    )
                ELSE NULL
                END
                """

        if cumulative_function == "COV":
            assert formatted_other_col is not None
            if non_numeric_col or window < 2:
                return "NULL"

            count_exp = f"""
            SUM(CAST(
                ({formatted_col} IS NOT NULL AND {formatted_other_col} IS NOT NULL)
                AS INT
            ))
            OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
            ROWS BETWEEN {window-1} PRECEDING AND CURRENT ROW)"""

            return f"""
                CASE WHEN {count_exp}={window}
                THEN (
                    SUM(CAST(1 AS INT64)*{formatted_other_col}*{formatted_col}) OVER
                    (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN {window-1}
                    PRECEDING AND CURRENT ROW) - (
                        SUM(
                            CASE WHEN {formatted_col} IS NULL
                            THEN NULL ELSE {formatted_other_col} END
                        )
                        OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN
                        {window-1} PRECEDING AND CURRENT ROW) *
                        SUM(
                            CASE WHEN {formatted_other_col} IS NULL
                            THEN NULL ELSE {formatted_col} END
                        )
                        OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN
                        {window-1} PRECEDING AND CURRENT ROW) / {count_exp}
                    )) / (
                        {count_exp}-1
                    )
                ELSE NULL
                END
                """

        return f"""
        CASE WHEN COUNT({formatted_col}) OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
             ROWS BETWEEN {window - 1} PRECEDING AND CURRENT ROW)={window}
        THEN
            {cumulative_function}({formatted_col}) OVER (ORDER BY
            {__PONDER_ORDER_COLUMN_NAME__}
                ROWS BETWEEN {window - 1} PRECEDING AND CURRENT ROW)
        ELSE
            NULL
        END
        """

    def generate_expanding_window_command(
        self,
        cumulative_function,
        col,
        min_window,
        non_numeric_col: bool,
        other_col,
    ):
        formatted_col = self.format_name(col)
        formatted_other_col = None if other_col is None else self.format_name(other_col)

        if cumulative_function == "COUNT":
            return f"""
            CASE WHEN COUNT({__PONDER_ORDER_COLUMN_NAME__}) OVER
                 (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS
                 BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)>={min_window}
            THEN
                COUNT({formatted_col}) OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
            ELSE
                NULL
            END
            """

        if cumulative_function == "SEM":
            if non_numeric_col:
                return "NULL"

            count_expression = f"""COUNT({formatted_col})
             OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)"""

            return f"""
            CASE WHEN {count_expression}>={min_window}
            THEN
                (STDDEV({formatted_col}) OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW))
                /SQRT({count_expression}-1)
            ELSE
               NULL
            END
            """

        if cumulative_function == "CORR":
            assert formatted_other_col is not None
            if non_numeric_col:
                return "NULL"

            count_exp = f"""
            SUM(CAST(
                ({formatted_col} IS NOT NULL AND {formatted_other_col} IS NOT NULL)
                AS INT
            ))
             OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)"""

            sigmas_exp = f"""
                    STDDEV_POP(
                        CASE WHEN {formatted_col} IS NULL
                        THEN NULL ELSE {formatted_other_col} END
                    )
                    OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN
                    UNBOUNDED PRECEDING AND CURRENT ROW) *
                    STDDEV_POP(
                        CASE WHEN {formatted_other_col} IS NULL
                        THEN NULL ELSE {formatted_col} END
                    )
                    OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN
                    UNBOUNDED PRECEDING AND CURRENT ROW)"""

            return f"""
                CASE WHEN {count_exp}>={min_window} AND {count_exp} * {sigmas_exp} > 0
                THEN (
                    SUM(CAST(1 AS INT64)*{formatted_other_col}*{formatted_col}) OVER
                    (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN UNBOUNDED
                    PRECEDING AND CURRENT ROW) - (
                        SUM(
                            CASE WHEN {formatted_col} IS NULL
                            THEN NULL ELSE {formatted_other_col} END
                        )
                        OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN
                        UNBOUNDED PRECEDING AND CURRENT ROW) *
                        SUM(
                            CASE WHEN {formatted_other_col} IS NULL
                            THEN NULL ELSE {formatted_col} END
                        )
                        OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN
                        UNBOUNDED PRECEDING AND CURRENT ROW) / {count_exp}
                    )) / (
                        {count_exp} * {sigmas_exp}
                    )
                ELSE NULL
                END
                """

        if cumulative_function == "COV":
            assert formatted_other_col is not None
            if non_numeric_col:
                return "NULL"

            count_exp = f"""
            SUM(CAST(
                ({formatted_col} IS NOT NULL AND {formatted_other_col} IS NOT NULL)
                AS INT
            ))
            OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)"""

            return f"""
                CASE WHEN {count_exp}>=GREATEST({min_window}, 2)
                THEN (
                    SUM(CAST(1 AS INT64)*{formatted_other_col}*{formatted_col}) OVER
                    (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN UNBOUNDED
                    PRECEDING AND CURRENT ROW) - (
                        SUM(
                            CASE WHEN {formatted_col} IS NULL
                            THEN NULL ELSE {formatted_other_col} END
                        )
                        OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN
                        UNBOUNDED PRECEDING AND CURRENT ROW) *
                        SUM(
                            CASE WHEN {formatted_other_col} IS NULL
                            THEN NULL ELSE {formatted_col} END
                        )
                        OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN
                        UNBOUNDED PRECEDING AND CURRENT ROW) / {count_exp}
                    )) / (
                        {count_exp}-1
                    )
                ELSE NULL
                END
                """

        return f"""
        CASE WHEN COUNT({formatted_col}) OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)>={min_window}
        THEN
            {cumulative_function}({formatted_col}) OVER (ORDER BY
            {__PONDER_ORDER_COLUMN_NAME__}
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
        ELSE
            NULL
        END
        """

    def generate_get_first_element_by_row_label_rank_command(
        self, col, row_labels_column_name
    ):
        return (
            f"CASE WHEN RANK() OVER "
            f"(PARTITION BY {self.format_name(col)} "
            f"ORDER BY {self.format_name(row_labels_column_name)})=1 "
            f"THEN {self.format_name(col)} ELSE NULL END"
        )

    def generate_replace_nan_with_0(self, col):
        return f"COALESCE({self.format_name(col)}, 0)"

    def generate_groupby_window_first_expression(
        self, formatted_col, partition_by_clause
    ):
        return f"""
            FIRST_VALUE({formatted_col} IGNORE NULLS)
            OVER (
                {partition_by_clause}
                ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            )"""

    def generate_groupby_window_last_expression(
        self, formatted_col, partition_by_clause
    ):
        return f"""
            LAST_VALUE({formatted_col} IGNORE NULLS)
            OVER (
                {partition_by_clause}
                ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
            )"""

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
        if window:
            if not expanding:
                return self.generate_rolling_window_command(
                    function, col, window, non_numeric_col, other_col
                )
            else:
                return self.generate_expanding_window_command(
                    function, col, window, non_numeric_col, other_col
                )

        from ponder.core.common import CUMULATIVE_FUNCTIONS

        # partition_by should be set for cumulative group by functions
        if partition_by:
            keys = ",".join(self.format_names_list(partition_by))
            partition_by_clause = f"PARTITION BY {keys}" if partition_by else ""
        else:
            partition_by_clause = ""

        # Should be careful to not format the name earlier
        formatted_col = self.format_name(col)
        if function in (
            CUMULATIVE_FUNCTIONS.SUM,
            GROUPBY_FUNCTIONS.CUMSUM,
        ):
            if skipna is False:
                return f"""
                    SUM({formatted_col})
                    OVER (
                        {partition_by_clause}
                        ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                    )"""
            else:
                return f"""
                CASE WHEN {formatted_col} IS NULL
                THEN NULL
                ELSE
                SUM({formatted_col})
                    OVER (
                        {partition_by_clause}
                        ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
                END
                """
        elif function in (
            CUMULATIVE_FUNCTIONS.PROD,
            GROUPBY_FUNCTIONS.CUMPROD,
        ):
            if skipna is False:
                return f"""
                CASE WHEN
                    (
                        SUM(CAST(({formatted_col} = 0) AS INT))
                        OVER (
                            {partition_by_clause}
                            ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                        )
                    ) > 0
                THEN 0 ELSE
                    (CASE WHEN
                        (
                            SUM(CAST(({formatted_col} < 0) AS INT))
                            OVER (
                                {partition_by_clause}
                                ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                            ) % 2
                        ) = 0
                    THEN 1 ELSE -1 END)
                    *
                    EXP(SUM(LN(ABS({formatted_col})))
                        OVER (
                            {partition_by_clause}
                            ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                        )
                    )
                END
                """
            else:
                return f"""
                CASE WHEN {formatted_col} IS NULL THEN NULL
                WHEN
                    (
                        SUM(CAST(({formatted_col} = 0) AS INT))
                        OVER (
                            {partition_by_clause}
                            ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                        )
                    ) > 0
                THEN 0
                ELSE
                    (CASE WHEN
                        SUM(CAST(({formatted_col} < 0) AS INT))
                        OVER ({partition_by_clause}
                            ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                        ) % 2 = 0
                    THEN 1 ELSE -1 END)
                    *
                    EXP(SUM(LN(ABS({formatted_col})))
                        OVER ({partition_by_clause}
                            ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                        )
                    )
                END
               """
        elif function in (
            CUMULATIVE_FUNCTIONS.MAX,
            GROUPBY_FUNCTIONS.CUMMAX,
        ):
            if skipna is False:
                return f"""
                MAX({formatted_col})
                OVER (
                    {partition_by_clause}
                    ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                )"""
            else:
                return f"""
                CASE WHEN {formatted_col} IS NULL
                THEN NULL
                ELSE
                    (
                        MAX({formatted_col})
                        OVER (
                            {partition_by_clause}
                            ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                        )
                    )
                END
                """
        elif function in (
            CUMULATIVE_FUNCTIONS.MIN,
            GROUPBY_FUNCTIONS.CUMMIN,
        ):
            if skipna is False:
                return f"""
                MIN({formatted_col})
                OVER (
                    {partition_by_clause}
                    ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                )"""
            else:
                return f"""
                CASE WHEN {formatted_col} IS NULL
                THEN NULL
                ELSE
                    (
                        MIN({formatted_col})
                        OVER (
                            {partition_by_clause}
                            ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                        )
                    )
                END
                """
        elif function == GROUPBY_FUNCTIONS.FIRST:
            return self.generate_groupby_window_first_expression(
                formatted_col, partition_by_clause
            )
        elif function == GROUPBY_FUNCTIONS.LAST:
            return self.generate_groupby_window_last_expression(
                formatted_col, partition_by_clause
            )
        elif function == GROUPBY_FUNCTIONS.ASFREQ:
            return f"""
            FIRST_VALUE({formatted_col})
            OVER (
                {partition_by_clause}
                ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            )"""
        elif function == GROUPBY_FUNCTIONS.CUMCOUNT:
            # This is kind of a special case because it doesn't follow the other
            # cumulative functions.
            # TODO: handle ascending kwarg
            return f"""
                COUNT(*)
                OVER (
                    {partition_by_clause}
                    ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) - 1"""
        elif function == GROUPBY_FUNCTIONS.NGROUP:
            keys = ",".join(self.format_names_list(partition_by))
            order = "ASC" if agg_kwargs.get("ascending", True) else "DESC"
            return f"""
                DENSE_RANK() OVER (
                    ORDER BY ({keys}) {order}
                ) - 1"""
        elif function == GROUPBY_FUNCTIONS.PCT_CHANGE:
            # This should call the child class's dialect. Currently generate_pct_change
            # is only supported on Snowflake so this may throw an error for other DBs.
            return self.generate_pct_change(
                col, agg_kwargs["periods"], partition_by_clause
            )
        elif function == GROUPBY_FUNCTIONS.DIFF:
            # Ideally this should be in the query compiler layer, but since we wrap
            # groupby functions in one method, we can't.
            if agg_kwargs["axis"] == 1 or agg_kwargs["axis"] == "columns":
                raise make_exception(
                    NotImplementedError,
                    PonderError.DUCKDB_GROUPBY_DIFF_AXIS_1_NOT_IMPLEMENTED,
                    "groupby.diff() with axis=1 not implemented yet",
                )
            return self.generate_diff(col, agg_kwargs["periods"], partition_by_clause)

        raise make_exception(
            RuntimeError,
            PonderError.DUCKDB_WINDOW_UNKNOWN_FUNCTION,
            f"Unknown function {function}",
        )

    def generate_union_all_query(
        self,
        node_data_list: list[UnionAllDataForDialect],
        column_names,
        row_labels_column_names,
        order_column_name,
        new_dtypes,
    ):
        variant_columns = set()
        for node in node_data_list:
            for c, dtype in node.dtypes.items():
                if dtype != new_dtypes[c] and is_object_dtype(new_dtypes[c]):
                    variant_columns.add(c)
        subqueries = []
        for i, node in enumerate(node_data_list):
            # need to name columns in the same order when doing union all, otherwise we
            # get infuriating bugs.
            # "If the tables have the same number of columns, but the columns are not in
            # the same order, the query results will probably be incorrect."    source:
            # https://docs.postgres.com/en/sql-reference/operators-query.html#general-usage-notes
            node_column_names_set = set(node.dtypes.keys())
            final_column_names_set = set(column_names)
            if node_column_names_set != final_column_names_set:
                raise make_exception(
                    RuntimeError,
                    PonderError.DUCKDB_UNION_ALL_COLUMN_NAME_MISMATCH,
                    "Internal error: node in union has set of column names "
                    + f"{node_column_names_set} that are not the same as final column "
                    + f"names {final_column_names_set}",
                )
            column_expressions = []
            for c in column_names:
                dtype = node.dtypes[c]
                if c in variant_columns:
                    column_expressions.append(
                        f"""
                        JSON_EXTRACT_STRING(TO_JSON({self.format_name(c)}),'$')
                        AS {self.format_name(c)}
                        """
                    )
                else:
                    column_expressions.append(self.format_name(c))
            columns_clause = ", ".join(
                (
                    *column_expressions,
                    *self.format_names_list(
                        (
                            *row_labels_column_names,
                            order_column_name,
                        )
                    ),
                )
            )
            subqueries.append(
                f"""
                SELECT
                    {columns_clause},
                    {i} AS {self.format_name("_TABLE_ORDER_")}
                FROM (
                    {node.sql}
                )
            """
            )
        return " UNION ALL ".join(subqueries)

    def generate_drop_na_columns_query(self, how, thresh, subset, index_name, columns):
        if subset is not None:
            where_clause = (
                f" WHERE {self.format_name(index_name)} "
                + f'IN ({", ".join(str(p) for p in subset)})'
            )
        else:
            where_clause = ""
        if thresh is not None:
            columns_selection = ", ".join(
                (
                    f"""
                    CASE WHEN
                        (
                            SELECT COUNT({self.format_name(col)})
                            FROM INNER_QUERY{where_clause}
                        ) >= {thresh}
                    THEN
                        TRUE
                    ELSE
                        FALSE
                    END AS {self.format_name(col)}
                    """
                    for col in columns
                )
            )
        elif how == "any":
            columns_selection = ", ".join(
                f"""
                    CASE WHEN
                        (
                            SELECT SUM(CAST(({self.format_name(col)} IS NULL) AS INT))
                            FROM INNER_QUERY{where_clause}
                        ) = 0
                    THEN
                        TRUE
                    ELSE
                        FALSE
                    END AS {self.format_name(col)}
                    """
                for col in columns
            )
        else:
            columns_selection = ", ".join(
                (
                    f"""
                        CASE WHEN
                            (
                                SELECT COUNT({self.format_name(col)})
                                FROM INNER_QUERY{where_clause}
                            ) = 0
                        THEN
                            FALSE
                        ELSE
                            TRUE
                        END AS {self.format_name(col)}
                        """
                    for col in columns
                )
            )

        return columns_selection

    def generate_drop_na_rows_predicate(self, how, thresh, columns):
        if len(columns) == 0:
            return "WHERE FALSE"
        if thresh is not None:
            col_conditions = [
                f"CASE WHEN {self.format_name(col)} IS NULL THEN 0 ELSE 1 END"
                for col in columns
            ]
            condition = f'{" + ".join(col_conditions)} >= {thresh}'
        elif how == "any":
            condition = " AND ".join(
                [f"{self.format_name(col)} IS NOT NULL" for col in columns]
            )
        else:
            condition = " OR ".join(
                [f"{self.format_name(col)} IS NOT NULL" for col in columns]
            )

        return f"WHERE {condition}"

    def generate_dt_tz_convert(self, params_list):
        # DuckDB does not store timezones internally and it has no
        # CONVERT_TIMEZONE function like Snowflake. The TIMEZONE function
        # will allow for the display of a timestamp in certain zones but
        # we cannot perform subsquent operations on those timezones, even
        # if they were correct. We cannot be sure that this operation will
        # result in the correct timezone/result
        raise make_exception(
            NotImplementedError,
            PonderError.DUCKDB_TIMEZONE_CONVERSION_NOT_SUPPORTED,
            "Converting timezones is not supported on DuckDB",
        )

    def generate_str_center(self, params_list):
        col_name_quoted, width, fillchar = params_list
        return f"""
        RPAD(
            LPAD(
                {col_name_quoted},
                CAST(GREATEST(
                    LENGTH({col_name_quoted}),
                    (
                        LENGTH({col_name_quoted}) +
                        CEIL(1.0 * ({width} - LENGTH({col_name_quoted}) - 1) / 2)
                    )
                ) AS INTEGER),
                '{fillchar}'
            ),
            CAST(GREATEST(
                LENGTH({col_name_quoted}),
                {width}
            ) AS INTEGER),
            '{fillchar}'
        )
        """

    def generate_str_contains(self, params_list):
        col_name_quoted, pat, case, flags, na, regex = params_list
        if not regex and case:
            if pandas.isnull(na):
                exp = f"({col_name_quoted} LIKE '{pat}')"
            else:
                exp = f"""
                    CASE WHEN
                        ({col_name_quoted} LIKE '{pat}') IS NULL
                    THEN
                        {na}
                    ELSE
                        {col_name_quoted} LIKE '{pat}'
                    END
                """
        else:
            pat = f"CONCAT('.*',REPLACE('{pat}','.','\\\\.'),'.*')"
            if not case or (regex and (flags & re.IGNORECASE != 0)):
                col_name_quoted = f"UPPER({col_name_quoted})"
                pat = f"UPPER({pat})"
            if pandas.isnull(na):
                exp = f"REGEXP_MATCHES({col_name_quoted},{pat})"
            else:
                exp = f"""
                    CASE WHEN
                        REGEXP_MATCHES({col_name_quoted},{pat}) IS NULL
                    THEN
                        {na}
                    ELSE
                        REGEXP_MATCHES({col_name_quoted},{pat})
                    END
                """
        return exp

    def generate_str_count(self, params_list):
        col_name_quoted, pat, flags = tuple(params_list)
        if flags & re.IGNORECASE != 0:
            pat = f"'(?i){pat}'"
        else:
            pat = f"'{pat}'"
        exp = f"ARRAY_LENGTH(REGEXP_EXTRACT_ALL({col_name_quoted},{pat},0))"
        return exp

    def generate_str_decode(self, params_list):
        col_name_quoted, encoding, errors = tuple(params_list)
        pat = re.compile("^utf[ _\\-]*8")
        if encoding.lower() == "ascii" or pat.fullmatch(encoding.lower()):
            encoding = "utf-8"
        if encoding != "utf-8":
            raise make_exception(
                NotImplementedError,
                PonderError.DUCKDB_STR_DECODE_UNSUPPORTED_ENCODING,
                "str.decode() only supports 'ascii' and 'utf-8' encodings currently",
            )
        exp = f"TO_CHAR({col_name_quoted},'{encoding}')"
        return exp

    def generate_str_encode(self, params_list):
        col_name_quoted, encoding, errors = tuple(params_list)
        pat = re.compile("^utf[ _\\-]*8")
        if encoding.lower() == "ascii" or pat.fullmatch(encoding.lower()):
            encoding = "utf8"
        if encoding != "utf8":
            raise make_exception(
                NotImplementedError,
                PonderError.DUCKDB_STR_ENCODE_UNSUPPORTED_ENCODING,
                "str.encode() only supports 'ascii' and 'utf8' encodings currently",
            )
        exp = f"TO_BINARY({col_name_quoted},'{encoding}')"
        return exp

    def generate_str_endswith(self, params_list):
        col_name_quoted, pat, na = params_list
        pat = f"%{pat}"
        if pandas.isnull(na):
            exp = f"({col_name_quoted} LIKE '{pat}')"
        else:
            exp = f"""
                CASE WHEN
                    ({col_name_quoted} LIKE '{pat}') IS NULL
                THEN
                    {na}
                ELSE
                    {col_name_quoted} LIKE '{pat}'
                END
            """
        return exp

    def generate_str_extract(self, column_name, pat, flags):
        n = re.compile(pat).groups
        col_name_quoted = self.format_name(column_name)
        pat = f"""'(?{"i" if (flags & re.IGNORECASE) != 0 else ""}:{pat})'"""
        # TODO(PERF): Could use a single REGEXP_EXTRACT call to get a struct of all the
        # matches and then unpack the struct into multiple columns. However, that does
        # not fit nicely into the query tree map paradigm, which always maps one column
        # to one column.
        return [
            f"""
                    CASE WHEN
                        REGEXP_MATCHES({col_name_quoted},{pat})
                    THEN
                    REGEXP_EXTRACT(
                        {col_name_quoted},
                        {pat},
                        {i+1}
                    )
                    ELSE
                        NULL
                    END
                """
            for i in range(n)
        ]

    def generate_str_find(self, params_list):
        col_name_quoted, sub, start, end = tuple(params_list)
        if start < 0:
            start_str = f"(GREATEST({start}+LENGTH({col_name_quoted}),0)+1)"
        else:
            start_str = f"{max(start,0)+1}"
        if end is None:
            exp = f"POSITION('{sub}' IN SUBSTR({col_name_quoted},{start_str}))"
        else:
            if end < 0:
                end_str = f"GREATEST({end}+LENGTH({col_name_quoted}),0)"
            else:
                end_str = f"(LEAST(LENGTH({col_name_quoted}),{end}))"
            exp = f"""
                POSITION(
                    '{sub}' IN
                    SUBSTR(
                        {col_name_quoted},
                        {start_str},
                        GREATEST({end_str} - {start_str}+1,0)
                    )
                )
            """
        exp = f"CASE WHEN {exp}=0 THEN -1 ELSE {exp}+{start_str}-2 END"
        return exp

    def generate_str_findall(self, params_list):
        col_name_quoted, pat, flags = params_list
        exp = (
            f"REGEXP_SUBSTR_ALL({col_name_quoted},'{pat}',1,1,'{_regex_params(flags)}')"
        )
        return exp

    def generate_str_fullmatch(self, params_list):
        col_name_quoted, pat, case, flags, na = params_list
        pat = f"{pat}"
        if flags & re.IGNORECASE == 0 and not case:
            flags = flags | re.IGNORECASE
        if flags & re.IGNORECASE != 0:
            col_name_quoted = f"UPPER({col_name_quoted})"
            pat = f"UPPER('{pat}')"
        else:
            pat = f"'{pat}'"
        if pandas.isnull(na):
            return f"REGEXP_MATCHES({col_name_quoted},{pat})"
        return f"""
            CASE WHEN
                REGEXP_MATCHES({col_name_quoted},{pat}) IS NULL
            THEN
                {na}
            ELSE
                REGEXP_MATCHES({col_name_quoted},{pat})
            END
        """

    def generate_str_get(self, params_list):
        col_name_quoted, i = params_list
        # Need to cast to keep SQL compiler happy
        col_name_quoted = f"TO_JSON({col_name_quoted})"
        if i >= 0:
            str_exp = f"SUBSTR(JSON_EXTRACT_STRING({col_name_quoted},'$'),{i+1},1)"
            arr_exp = f"""
                CAST(JSON_EXTRACT_STRING({col_name_quoted},'$') AS VARCHAR[])[{i+1}]
            """
        else:
            str_exp = f"""SUBSTR(
                JSON_EXTRACT_STRING({col_name_quoted},'$'),
                {i+1}+LENGTH(JSON_EXTRACT_STRING({col_name_quoted},'$')),1
            )"""
            arr_exp = f"""
                CASE WHEN
                    {abs(i)} >
                    ARRAY_LENGTH(CAST(
                        JSON_EXTRACT_STRING({col_name_quoted},'$') AS VARCHAR[]
                    ))
                THEN
                    NULL
                ELSE
                    JSON_EXTRACT_STRING({col_name_quoted},'$')[
                        ARRAY_LENGTH(CAST(
                            JSON_EXTRACT_STRING({col_name_quoted},'$') AS VARCHAR[]
                        ))-{abs(i)}
                    ]
                END
            """
        str_exp = f"CASE WHEN {str_exp}='' THEN NULL ELSE {str_exp} END"
        return f"""
            CASE WHEN
                JSON_TYPE({col_name_quoted})='VARCHAR'
            THEN
                {str_exp}
            ELSE
                {arr_exp}
            END
        """

    def generate_str_join(self, params_list):
        col_name_quoted, sep = params_list
        exp1 = f"STRING_AGG(UNNEST({col_name_quoted}),'{sep}')"
        exp2 = f"""
            CONCAT(
                REGEXP_REPLACE(
                    SUBSTR(
                        {col_name_quoted},
                        1,
                        LENGTH({col_name_quoted})-1
                    ),
                    '(.)','\\1{sep}','g'
                ),
                SUBSTR({col_name_quoted}, LENGTH({col_name_quoted}))
            )"""
        exp = f"""
            CASE WHEN
                IS_ARRAY(TO_VARIANT({col_name_quoted}))
            THEN
                {exp1}
            ELSE
                {exp2}
            END
        """
        return exp

    def generate_str_ljust(self, params_list):
        col_name_quoted, width, fillchar = params_list
        exp = f"""
            RPAD(
                {col_name_quoted},
                CAST(GREATEST(
                    LENGTH({col_name_quoted}),
                    {width}
                ) AS INTEGER),
                '{fillchar}'
                )
                """
        return exp

    def generate_str_match(self, params_list):
        col_name_quoted, pat, case, flags, na = params_list
        pat = f"{pat}.*"
        if flags & re.IGNORECASE == 0 and not case:
            flags = flags | re.IGNORECASE
        if flags & re.IGNORECASE != 0:
            col_name_quoted = f"UPPER({col_name_quoted})"
            pat = f"UPPER('{pat}')"
        else:
            pat = f"'{pat}'"
        if pandas.isnull(na):
            exp = f"REGEXP_MATCHES({col_name_quoted},{pat})"
        else:
            exp = f"""
                CASE WHEN
                    REGEXP_MATCHES({col_name_quoted},{pat}) IS NULL
                THEN
                    {na}
                ELSE
                    REGEXP_MATCHES({col_name_quoted},{pat})
                END
            """
        return exp

    # Unlike most other string functions, this method returns a list of strings because
    # it takes one column as input and returns three columns as output, each requiring
    # its own SQL expression.
    def generate_str_partition(self, column_name, sep, expand):
        col_name_quoted = self.format_name(column_name)
        sep_start = f"POSITION('{sep}' IN {col_name_quoted})"
        if len(sep) == 1:
            sep_end = sep_start
        else:
            sep_end = f"{sep_start}+{len(sep)-1}"
        pre_sep = f"{sep_start}-1"
        post_sep = f"{sep_start}+{len(sep)}"
        part1 = f"LEFT({col_name_quoted},{pre_sep})"
        part2 = f"SUBSTR({col_name_quoted},{sep_start},{len(sep)})"
        part3 = f"""
            SUBSTR({col_name_quoted},{post_sep},LENGTH({col_name_quoted})-{sep_end})
        """
        if expand:
            return [
                f"CASE WHEN {col_name_quoted} IS NULL THEN NULL ELSE {part1} END",
                f"CASE WHEN {col_name_quoted} IS NULL THEN NULL ELSE {part2} END",
                f"CASE WHEN {col_name_quoted} IS NULL THEN NULL ELSE {part3} END",
            ]
        return [
            f"""
                CASE WHEN
                    {col_name_quoted} IS NULL
                THEN
                    NULL
                ELSE
                    [{part1},{part2},{part3}]
                END
            """
        ]

    def generate_str_removeprefix(self, params_list):
        col_name_quoted, prefix = params_list
        exp = f"""
                CASE WHEN
                    LEFT({col_name_quoted},{len(prefix)})='{prefix}'
                THEN
                    SUBSTR({col_name_quoted},{len(prefix)+1})
                ELSE
                    {col_name_quoted}
                END
            """
        return exp

    def generate_str_removesuffix(self, params_list):
        col_name_quoted, suffix = params_list
        exp = f"""
                CASE WHEN
                    RIGHT({col_name_quoted},{len(suffix)})='{suffix}'
                THEN
                    LEFT({col_name_quoted},LENGTH({col_name_quoted})-{len(suffix)})
                ELSE
                    {col_name_quoted}
                END
            """
        return exp

    def generate_str_replace(self, params_list):
        col_name_quoted, pat, repl, n, case, flags, regex = params_list
        if callable(repl):
            raise make_exception(
                NotImplementedError,
                PonderError.DUCKDB_STR_REPLACE_CALLABLE_REPL,
                "str.replace() does not support callable `repl` param yet",
            )
        if isinstance(pat, Pattern):
            raise make_exception(
                NotImplementedError,
                PonderError.DUCKDB_STR_REPLACE_COMPILED_REGEX,
                "str.replace() does not support compiled regex for `pat` param yet",
            )
        if n == 0 and (case is None or case):
            exp = f"{col_name_quoted}"
        elif regex or (case is not None and not case) or n > 0:
            if not regex:
                pat = f"{re.escape(pat)}"
            pat = pat.encode("unicode-escape").decode()
            if flags & re.IGNORECASE == 0 and not case:
                flags = flags | re.IGNORECASE
            if flags & re.IGNORECASE != 0:
                pat = f"'(?i){pat}'"
            else:
                pat = f"'{pat}'"
            if n <= 0:
                exp = f"REGEXP_REPLACE({col_name_quoted},{pat},'{repl}','g')"
            else:
                split_idx = f"""
                        CASE WHEN
                            REGEXP_INSTR({col_name_quoted},{pat},1,1,1)=0
                        THEN
                            0
                        ELSE
                            CASE WHEN
                                REGEXP_INSTR({col_name_quoted},{pat},1,{n},1)=0
                            THEN
                                LENGTH({col_name_quoted})+1
                            ELSE
                                REGEXP_INSTR({col_name_quoted},{pat},1,{n},1)
                            END - 1
                        END
                    """
                exp = f"""
                        CONCAT(
                            REGEXP_REPLACE(
                                SUBSTR({col_name_quoted},1,{split_idx}),
                                {pat},
                                '{repl}',
                                'g'
                            ),
                            SUBSTR({col_name_quoted},{split_idx}+1)
                        )
                    """
        else:
            pat = f"'{pat}'"
            exp = f"REPLACE({col_name_quoted},{pat},'{repl}')"
        return exp

    def generate_str_rfind(self, params_list):
        col_name_quoted, sub, start, end = params_list
        if start < 0:
            start_str = f"(GREATEST({start}+LENGTH({col_name_quoted}),0)+1)"
        else:
            start_str = f"{max(start,0)+1}"
        if end is None:
            end_str = f"LENGTH({col_name_quoted})+1"  # noqa F541
        else:
            if end < 0:
                end_str = f"({end}+LENGTH({col_name_quoted})+1)"
            else:
                end_str = f"(-1*GREATEST(-1*LENGTH({col_name_quoted}),{-1*end})+1)"
        exp = f"""
        CASE WHEN
            {start_str} > LENGTH({col_name_quoted}) OR
            POSITION(
                '{sub}' IN
                REVERSE(
                    SUBSTR(
                        {col_name_quoted},
                        {start_str},
                        GREATEST({end_str} - {start_str},0)
                    )
                )
            ) = 0
        THEN
            -1
        ELSE
            {end_str} - POSITION(
                '{sub}' IN
                REVERSE(
                    SUBSTR(
                        {col_name_quoted},
                        {start_str},
                        GREATEST({end_str} - {start_str},0)
                    )
                )
            ) - 1
        END
        """
        return exp

    generate_str_rindex = generate_str_rfind

    def generate_str_rjust(self, params_list):
        col_name_quoted, width, fillchar = params_list
        exp = f"""
        LPAD(
            {col_name_quoted},
            CAST(GREATEST(
                LENGTH({col_name_quoted}),
                {width}
            ) AS INTEGER),
            '{fillchar}')
        """
        return exp

    # Unlike most other string functions, this method returns a list of strings because
    # it takes one column as input and returns three columns as output, each requiring
    # its own SQL expression.
    def generate_str_rpartition(self, column_name, sep, expand):
        col_name_quoted = self.format_name(column_name)
        sep_end = f"""
                (
                    LENGTH({col_name_quoted})-POSITION(
                        '{sep[::-1]}' IN
                        REVERSE({col_name_quoted})
                    )+1
                )
            """
        if len(sep) == 1:
            sep_start = sep_end
        else:
            sep_start = f"{sep_end}-{len(sep)-1}"
        pre_sep = f"{sep_end}-{len(sep)}"
        post_sep = f"{sep_start}+1"
        part1 = f"LEFT({col_name_quoted},{pre_sep})"
        part2 = f"SUBSTR({col_name_quoted},{sep_start},{len(sep)})"
        part3 = f"""
            SUBSTR({col_name_quoted},{post_sep},LENGTH({col_name_quoted})-{sep_end})
        """
        if expand:
            return [
                f"CASE WHEN {col_name_quoted} IS NULL THEN NULL ELSE {part1} END",
                f"CASE WHEN {col_name_quoted} IS NULL THEN NULL ELSE {part2} END",
                f"CASE WHEN {col_name_quoted} IS NULL THEN NULL ELSE {part3} END",
            ]
        return [
            f"""
                CASE WHEN
                    {col_name_quoted} IS NULL
                THEN
                    NULL
                ELSE
                    [{part1},{part2},{part3}]
                END
            """
        ]

    def generate_str_rsplit(self, params_list):
        col_name_quoted, pat, n, expand = params_list
        if pat is None:
            regex_pat = f"'[ \t\r\n]+'"  # noqa F541
            regex_pat_extended = f"'.*[ \t\r\n]+'"  # noqa F541
            exp = f"""REGEXP_REPLACE(
                TRIM({col_name_quoted},{regex_pat}),{regex_pat},' ','g'
            )"""
            pat = " "
            n_for_split_idx = f"""
                    CASE WHEN
                        REGEXP_LIKE({col_name_quoted},{regex_pat_extended})
                    THEN
                        {n+1}
                    ELSE
                        {n}
                    END
                """
        else:
            regex_pat = f"REVERSE('{pat}')"
            exp = f"{col_name_quoted}"  # noqa F541
            n_for_split_idx = n
        if n <= 0:
            exp = f"SPLIT({exp},'{pat}')"
        else:
            split_idx = f"""
            1 + LENGTH(
                {col_name_quoted}) -
                REGEXP_INSTR(
                    REVERSE(
                        {col_name_quoted}),
                        {regex_pat},
                        1,
                        {n_for_split_idx},
                        1
                    )
                )"""
            exp = f"""
            CASE WHEN
                {n+1} > ARRAY_LENGTH(SPLIT({exp},'{pat}'))
            THEN
                SPLIT({exp},'{pat}')
            ELSE
                ARRAY_PREPEND(
                    ARRAY_SLICE(
                        SPLIT(
                            {exp},
                            '{pat}'
                        ),
                        {-1*n},
                        __MAX_INT__
                    ),
                    SUBSTR(
                        {col_name_quoted},
                        1,
                        {split_idx}
                    )
                )
            END
            """
        return exp

    def generate_str_slice(self, params_list):
        column_name_quoted, start, stop, step = params_list
        if start is None:
            start = 1
            start_str = f"1"  # noqa F541
        elif start < 0:
            start_str = f"(GREATEST({start}+LENGTH({column_name_quoted}),0)+1)"
        else:
            start_str = f"{max(start,0)+1}"
        if stop is None:
            stop_str = f"(LENGTH({column_name_quoted})+1)"  # noqa F541
        elif stop < 0:
            stop_str = f"({stop}+LENGTH({column_name_quoted})+1)"
        else:
            stop_str = f"(-1*GREATEST(-1*LENGTH({column_name_quoted}),{-1*stop})+1)"
        if step is None or step == 1:
            exp = f"SUBSTR({column_name_quoted},{start_str},{stop_str}-{start_str})"
        else:
            if start * stop < 0 or stop is None:
                raise make_exception(
                    NotImplementedError,
                    PonderError.DUCKDB_STR_SLICE_UNSUPPORTED_START_STOP_STEP_COMBINATION,  # noqa: E501
                    "str.slice() does not support step > 1 along with (a) no stop, "
                    + "or (b) start and stop with different signs",
                )
            n = int((stop - start) / step)
            exp = f"CONCAT("  # noqa F541
            for i in range(n):
                exp = f"{exp}SUBSTR({column_name_quoted},{start_str}+{i*step},1)"
                if i < n - 1:
                    exp = f"{exp},"
            exp = f"CASE WHEN {column_name_quoted} IS NULL THEN NULL ELSE {exp}) END"
        return exp

    def generate_str_slice_replace(self, params_list):
        column_name_quoted, start, stop, repl = params_list
        if start is None:
            start_str = f"1"  # noqa F541
        elif start < 0:
            start_str = f"(GREATEST({start}+LENGTH({column_name_quoted}),0)+1)"
        else:
            start_str = f"{max(start,0)+1}"
        if stop is None:
            stop_str = f"(LENGTH({column_name_quoted})+1)"  # noqa F541
        elif stop < 0:
            stop_str = f"({stop}+LENGTH({column_name_quoted})+1)"
        else:
            stop_str = f"(-1*GREATEST(-1*LENGTH({column_name_quoted}),{-1*stop})+1)"
        if repl is None:
            repl = ""
        exp = f"""
        CONCAT(
            LEFT(
                {column_name_quoted},
                {start_str} - 1
            ),
            '{repl}',
            RIGHT(
                {column_name_quoted},
                LENGTH(
                    {column_name_quoted}
                ) - {stop_str} + 1
            )
        )"""
        exp = f"CASE WHEN {column_name_quoted} IS NULL THEN NULL ELSE {exp} END"
        return exp

    def generate_str_split(self, params_list):
        col_name_quoted, pat, n, expand = params_list
        if pat is None:
            regex_pat = f"'[ \t\r\n]+'"  # noqa F541
            regex_pat_extended = f"'[ \t\r\n]+.*'"  # noqa F541
            exp = f"REGEXP_REPLACE(TRIM({col_name_quoted},{regex_pat}),{regex_pat},' ')"
            pat = " "
            n_for_split_idx = (
                f"IF(REGEXP_MATCHES({col_name_quoted},{regex_pat_extended}),{n+1},{n})"
            )
        else:
            regex_pat = f"'{pat}'"
            exp = f"{col_name_quoted}"  # noqa F541
            n_for_split_idx = n
        if n <= 0:
            exp = f"REGEXP_SPLIT_TO_ARRAY({exp},'{pat}')"
        else:
            split_idx = f"INSTR({col_name_quoted},{regex_pat})"
            if n_for_split_idx > 1:
                # We need the index of the n_for_split_idx occurence of regex_pat
                # to mimic Snowflake REGEXP_INSTR behavior
                pattern_length = len(eval(regex_pat))
                for _ in range(n_for_split_idx - 1):
                    split_idx += (
                        f" + INSTR(SUBSTR({col_name_quoted},"
                        f"{split_idx}+{pattern_length}),{regex_pat})"
                        f" + {pattern_length}"
                    )
            exp = f"""
            IF({n+1} > ARRAY_LENGTH(REGEXP_SPLIT_TO_ARRAY({exp},'{pat}')),
                REGEXP_SPLIT_TO_ARRAY({exp},'{pat}'),
                ARRAY_APPEND(
                    ARRAY_SLICE(
                        REGEXP_SPLIT_TO_ARRAY({exp},'{pat}'),
                        0,
                        {n}
                    ),
                    SUBSTR(
                        {col_name_quoted},
                        {split_idx}
                    )
                )
            )"""
        return exp

    def generate_str_startswith(self, params_list):
        col_name_quoted, pat, na = params_list
        pat = f"{pat}%"
        if pandas.isnull(na):
            exp = f"({col_name_quoted} LIKE '{pat}')"
        else:
            exp = f"""
                CASE WHEN
                    ({col_name_quoted} LIKE '{pat}') IS NULL
                THEN
                    {na}
                ELSE
                    {col_name_quoted} LIKE '{pat}'
                END
            """
        return exp

    def generate_str_wrap(self, params_list):
        col_name_quoted, width = params_list
        exp = f"""
                CASE WHEN
                    MOD(LENGTH({col_name_quoted}),{width})=0
                THEN
                    SUBSTR(
                        REGEXP_REPLACE(
                            {col_name_quoted},
                            '(.{{{{{width}}}}})',
                            '\\1\n',
                            'g'
                        ),
                        1,
                        CAST(FLOOR(LENGTH({col_name_quoted})*(1+1/{width})-1) AS INT64
                    ))
                ELSE
                    REGEXP_REPLACE({col_name_quoted},'(.{{{{{width}}}}})','\\1\n','g')
                END
            """
        return exp

    def generate_str_capitalize(self, params_list):
        col_name_quoted = params_list[0]
        exp = f"""
        CONCAT(
            UPPER(
                LEFT(
                    {col_name_quoted},
                    1
                )
            ),
            LOWER(
                RIGHT(
                    {col_name_quoted},
                    LENGTH({col_name_quoted}) - 1
                )
            )
        )"""
        exp = f"CASE WHEN {col_name_quoted} IS NULL THEN NULL ELSE {exp} END"
        return exp

    def generate_str_isalnum(self, params_list):
        col_name_quoted = params_list[0]
        return f"({col_name_quoted} SIMILAR TO '[a-zA-Z0-9]+')"

    def generate_str_isalpha(self, params_list):
        col_name_quoted = params_list[0]
        return f"({col_name_quoted} SIMILAR TO '[a-zA-Z]+')"

    def generate_str_isdecimal(self, params_list):
        col_name_quoted = params_list[0]
        return f"({col_name_quoted} SIMILAR TO '[0-9]+')"

    def generate_str_isdigit(self, params_list):
        col_name_quoted = params_list[0]
        return f"({col_name_quoted} SIMILAR TO '[0-9]+')"

    def generate_str_islower(self, params_list):
        col_name_quoted = params_list[0]
        return f"""
            ({col_name_quoted} SIMILAR TO '.*[a-zA-Z]+.*') AND
            {col_name_quoted} = LOWER({col_name_quoted})
        """

    def generate_str_isnumeric(self, params_list):
        col_name_quoted = params_list[0]
        return f"({col_name_quoted} SIMILAR TO '[0-9]+')"

    def generate_str_istitle(self, params_list):
        col_name_quoted = params_list[0]
        return f"""
        {col_name_quoted} SIMILAR TO '.*[a-zA-Z]+.*' AND
        {col_name_quoted} = INITCAP({col_name_quoted})"""

    def generate_str_isupper(self, params_list):
        col_name_quoted = params_list[0]
        return f"""
        {col_name_quoted} SIMILAR TO '.*[a-zA-Z]+.*' AND
        {col_name_quoted} = UPPER({col_name_quoted})"""

    def generate_read_table_command(self, table_name, column_list=None, skipfooter=0):
        formatted_table_name = self.format_name(table_name)

        if column_list is not None:
            formatted_columns_list = self.format_names_list(column_list)
            selected_columns_list = ", ".join(formatted_columns_list)
            if __PONDER_ORDER_COLUMN_NAME__ not in column_list:
                selected_columns_list = (
                    selected_columns_list
                    + f", rowid AS {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}"
                )
            if __PONDER_ROW_LABELS_COLUMN_NAME__ not in column_list:
                selected_columns_list = (
                    selected_columns_list
                    + f""", rowid AS
                    {self.format_name(__PONDER_ROW_LABELS_COLUMN_NAME__)}"""
                )
            return (
                f"SELECT {selected_columns_list} FROM {formatted_table_name} "
                f"WHERE ({self.format_name(__PONDER_ORDER_COLUMN_NAME__)} "
                f"< (SELECT COUNT(*) FROM {formatted_table_name})"
                f" - {skipfooter})"
            )
        return (
            f"SELECT * FROM {formatted_table_name} "
            f"WHERE ({self.format_name(__PONDER_ROW_LABELS_COLUMN_NAME__)} "
            f"< (SELECT COUNT(*) FROM {formatted_table_name})"
            f" - {skipfooter})"
        )

    def generate_row_wise_reduce_node_command(
        self,
        input_column_names: list[str],
        input_column_types,
        function: REDUCE_FUNCTION,
        input_node_sql: str,
        order_and_labels_column_strings: str,
        result_column_name: str,
    ) -> str:
        cols = ",".join(self.format_names_list(input_column_names))
        if function is REDUCE_FUNCTION.COUNT_UNIQUE_INCLUDING_NULL:
            # TODO: DuckDB does not natively support including nulls
            # so we have to investigate using ARRAY_AGG and ARRAY_FLATTEN
            # which requires us changing the structure of the SQL generated
            function_call = f"ARRAY_LENGTH(ARRAY_DISTINCT(ARRAY[{cols}]))"
        elif function is REDUCE_FUNCTION.COUNT_UNIQUE_EXCLUDING_NULL:
            function_call = f"ARRAY_LENGTH(ARRAY_DISTINCT(ARRAY[{cols}]))"
        elif function is REDUCE_FUNCTION.MIN:
            function_call = f"LEAST({cols})"
        elif function is REDUCE_FUNCTION.MAX:
            function_call = f"GREATEST({cols})"
        elif function is REDUCE_FUNCTION.SUM:
            function_call = " + ".join(self.format_names_list(input_column_names))
        else:
            raise make_exception(
                ValueError,
                PonderError.DUCKDB_ROW_WISE_REDUCE_INVALID_FUNCTION,
                f"Cannot execute row-wise reduce function {function}",
            )
        query = f"SELECT {order_and_labels_column_strings}"
        query += f", {function_call} AS {self.format_name(result_column_name)}"
        query += f" FROM ({input_node_sql})"
        return query

    def generate_isin_collection_expression(
        self, column_name: str, column_type: np.dtype, values: Iterable
    ):
        value_strings = []
        # Seems to be a pandas bug: isin never considers nulls to be equal when values
        # is a series, but it does consider nulls to be equal when values is a list
        # or dict or dataframe.
        # this may be https://github.com/pandas-dev/pandas/issues/35565
        # duckdb '3 in (NULL,)' returns NULL, whereas in postgres it returns True. If we
        # find we are looking for NULL, then we have to check explicitly for NULL.
        look_for_null = False
        for value in values:
            # if the value translates to null in sql for this column type, tell postgres
            # to look for null.
            if is_numeric_dtype(column_type):
                if value is np.nan:
                    look_for_null = True
                    continue
            elif is_datetime64_any_dtype(column_type):
                if value is pandas.NaT:
                    look_for_null = True
                    continue
            elif value is None:
                look_for_null = True
                continue
            if is_scalar(value) and pandas.isnull(value):
                # We don't have a way to represent different null types in SQL, while
                # in python null are objects that can always be compared to each other
                # with __equals__. in our current representation of data, I don't think
                # we can't have a null type that doesn't match the column type, e.g.
                # np.NaN can only appear in numeric columns. So just assume this null
                # type doesn't match.
                continue
            # Now we know we don't have a null.
            if isinstance(value, str):
                value_strings.append(f"'{value}'")
            elif pandas.api.types.is_number(value):
                value_strings.append(str(value))
            else:
                raise make_exception(
                    NotImplementedError,
                    PonderError.DUCKDB_ISIN_COLLECTION_UNSUPPORTED_VALUE,
                    f"Cannot apply isin to value {value} of type {type(value).__name__}",  # noqa: E501
                )
        if len(value_strings) == 0:
            # duckdb throws syntax error for empty lists
            return (
                f"{self.format_name(column_name)} IS NULL" if look_for_null else "FALSE"
            )

        # IN returns NULL when column_name is NULL, whereas pandas considers
        # null.isin(non_non_values) to be false.
        contains_check = (
            f"{self.format_name(column_name)} IS NOT NULL AND "
            + f"{self.format_name(column_name)} IN "
            + f"({', '.join(value_strings)})"
        )
        return (
            f"({contains_check}) OR {self.format_name(column_name)} IS NULL"
            if look_for_null
            else contains_check
        )

    def generate_dataframe_isin_series(
        self,
        column_name,
    ):
        # make structs out of the values so we can compare mixed types. note that
        # struct {'a': null} is equal to {'b': null}, so we have to explicitly check
        # that neither value is null.
        return (
            f"{self.format_name(column_name)}  IS NOT NULL AND "
            + f"{self.format_name(__ISIN_SERIES_VALUES_COLUMN_NAME__)} IS NOT NULL "
            + f'AND {{"struct_value": {self.format_name(column_name)} }} = '
            + '{"struct_value": '
            + f"{self.format_name(__ISIN_SERIES_VALUES_COLUMN_NAME__)} }}"
        )

    def generate_dataframe_isin_dataframe(
        self,
        column_name,
    ):
        return f"""
            IFNULL(
                {self.format_name(column_name +
                    __ISIN_DATAFRAME_LEFT_PREFIX__)} =
                    {self.format_name(column_name +
                        __ISIN_DATAFRAME_RIGHT_PREFIX__)},
                FALSE
            )
        """

    def generate_timedelta_to_datetime_addend(self, timedelta: pandas.Timedelta) -> str:
        # pandas.to_timedelta() converts to nanoseconds which is not supported
        # by DuckDB so we use microseconds instead
        return str(timedelta // pandas.Timedelta("1us"))

    def generate_scalar_timestamp_for_subtraction(
        self, timestamp: pandas.Timestamp
    ) -> str:
        return f"'{timestamp}'"

    def generate_number_to_datetime_cast(self, column_name, column_type, **kwargs):
        unit = kwargs.get("unit", "ns")
        unit = unit if unit is not None else "ns"
        if unit == "ns":
            raise make_exception(
                ValueError,
                PonderError.DUCKDB_DOES_NOT_SUPPORT_FLOAT_DATETIME_CONVERSION,
                "DuckDB does not support nanoseconds.",
            )
        origin = kwargs.get("origin", "unix")
        if origin == "unix":
            operand1 = "'epoch'::TIMESTAMP"
        elif isinstance(origin, (int, float)):
            operand1 = f"epoch_ms({origin})"
        else:
            timestamp_str = pandas.Timestamp(origin).strftime("%Y-%m-%d %H:%M:%S.%f")
            operand1 = f"strptime('{timestamp_str}', '%Y-%m-%d %H:%M:%S.%f')"
        column_name = self.format_name(column_name)
        if column_type == "float":
            import warnings

            warnings.warn(
                "Truncating nanoseconds since DuckDB does not "
                + "support nanosecond precision."
            )
            if unit == "us":
                column_name = f"FLOOR({column_name})"
            elif unit in ["s", "ms"]:
                scale = {"s": 1e6, "ms": 1e3}[unit]
                column_name = f"FLOOR({column_name} * {scale})"
                unit = "us"
        if unit == "D":
            operand2 = f"TO_DAYS({column_name}::INT)"
        elif unit == "s":
            operand2 = f"TO_SECONDS({column_name}::INT)"
        elif unit == "ms":
            operand2 = f"TO_MILLISECONDS({column_name}::INT)"
        else:
            operand2 = f"TO_MICROSECONDS({column_name}::INT)"
        if unit != "D" or column_type != "float":
            return f"({operand1} + {operand2})::TIMESTAMP"
        else:
            decimal_part = f"({column_name} - FLOOR({column_name}))"
            days = f"FLOOR({column_name})"
            seconds = f"({decimal_part} * 86400)"
            microseconds = f"FLOOR(({seconds} - FLOOR({seconds}))*1e6)"
            plus_days = f"{operand1} + TO_DAYS({days}::INT)"
            plus_seconds = f"{plus_days} + TO_SECONDS({seconds}::INT)"
            return f"({plus_seconds} + TO_MICROSECONDS({microseconds}::INT))::TIMESTAMP"

    def generate_datetime_plus_timedelta(
        self, datetime_sql: str, timedelta_sql: str
    ) -> str:
        return f"{datetime_sql} + to_microseconds({timedelta_sql})"

    def generate_datetime_minus_timedelta(self, left_sql: str, right_sql: str) -> str:
        # The timedelta will always be the RHS expression as pandas throws
        # an error with timedelta on the LHS
        return f"{left_sql} - to_microseconds({right_sql})"

    def generate_datetime_minus_datetime(self, left_sql: str, right_sql: str) -> str:
        # Snowflake uses nanoseconds which is not supported by DuckDB so use
        # microseconds instead
        return f"DATESUB('microseconds', {right_sql}, {left_sql})"

    def generate_compare_post_join_results(
        self, original_columns: list[str], original_types: list[pandas_dtype]
    ) -> tuple[list[str], list[str], list[str]]:
        """Generate the column names, expressions, and types for the compare
        result.
        Parameters
        ----------
        original_columns : list[str]
            The original column names.
        original_types : list[pandas_dtype]
            The original column types.
        Returns
        -------
        tuple[list[str], list[str], list[str]]
            The column names, expressions, and types, in that order, for the compare
            result.
        """
        column_names = []
        column_expressions = []
        column_types = []
        for column, type in zip(original_columns, original_types):
            # note pandas uses NaNs even for non-numeric columns, but then we'd have to
            # convert the column to variant type. too much work
            column_names.append(f"{column}_self")
            formatted_self_name = self.format_name(f"{column}_x")
            formatted_other_name = self.format_name(f"{column}_y")
            column_expressions.append(
                f"""
                    CASE WHEN EQUAL_NULL({formatted_self_name}, {formatted_other_name})
                    THEN NULL ELSE {formatted_self_name} END
                """
            )
            column_types.append(type)
            column_names.append(f"{column}_other")
            column_expressions.append(
                f"""
                    CASE WHEN EQUAL_NULL({formatted_self_name}, {formatted_other_name})
                    THEN NULL ELSE {formatted_other_name} END
                """
            )
            column_types.append(type)
        return column_names, column_expressions, column_types

    def generate_with_cross_join_col_exp(self, col, kwargs):
        purpose = kwargs.get("purpose", "rolling")

        if purpose not in ["rolling", "expanding"]:
            raise make_exception(
                NotImplementedError,
                PonderError.DUCKDB_CROSS_JOIN_PURPOSE_NOT_IMPLEMENTED,
                f"Cross join for the purpose {purpose} not implemented yet",
            )

        view_names = kwargs.get("view_names", None)
        if view_names is None:
            view_names = ["", ""]
        elif len(view_names) != 2:
            raise make_exception(
                TypeError,
                PonderError.DUCKDB_CROSS_JOIN_VIEW_NAMES_LENGTH_NOT_2,
                f"{view_names} must be of length 2, got {len(view_names)}.",
            )
        else:
            view_names[0] = f"{view_names[0]}."
            view_names[1] = f"{view_names[1]}."

        win_func = kwargs.get("win_func", None)
        win_type = kwargs.get("win_type", None)
        window = kwargs.get("window", None)

        # This is deliberately made as a list instead of equality check
        # to make it extendable
        if win_type is not None and win_type.lower() not in ["gaussian"]:
            raise make_exception(
                NotImplementedError,
                PonderError.DUCKDB_CROSS_JOIN_WIN_TYPE_NOT_IMPLEMENTED,
                f"Cross join with {win_type} not implemented yet",
            )

        if win_type is not None and win_type.lower() == "gaussian":
            # This is deliberately made as a list instead of equality check
            # to make it extendable
            if win_func not in ["SUM", "AVG", "STDDEV", "VARIANCE"]:
                raise make_exception(
                    NotImplementedError,
                    PonderError.DUCKDB_GAUSSIAN_AGGREGATION_FUNCTION_NOT_IMPLEMENTED,
                    f"Gaussian aggregation function {win_func} not implemented yet.",
                )

            std = kwargs.get("std", None)
            weight = f"""
                EXP(-0.5 * POW(({window - (window+1)/2} -
                    {view_names[0]}{__PONDER_ORDER_COLUMN_NAME__} +
                    {view_names[1]}{__PONDER_ORDER_COLUMN_NAME__})/{std}, 2))"""
            if win_func == "SUM":
                return f"""
                    CASE WHEN COUNT({view_names[1]}{self.format_name(col)}) < {window}
                    THEN NULL
                    ELSE SUM({weight} * {view_names[1]}{self.format_name(col)})
                    END
                """
            else:
                from scipy.signal.windows import gaussian

                weights = gaussian(window, std)
                sum_weights = reduce(lambda x, y: x + y, weights)
                sq_weights = list(map(lambda x: x * x, weights))
                sum_sq_weights = reduce(lambda x, y: x + y, sq_weights)
                weighting_ratio = sum_weights / (
                    sum_weights * sum_weights - sum_sq_weights
                )
                if math.isinf(weighting_ratio):
                    weighting_ratio = "NULL"

                window_specs = f"""
                    OVER (
                        ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                        ROWS BETWEEN {window} PRECEDING AND CURRENT ROW
                    )
                """
                window_specs = ""
                if win_func == "AVG":
                    return f"""
                        CASE WHEN
                            COUNT({view_names[1]}{self.format_name(col)}) < {window}
                        THEN NULL
                        ELSE
                            SUM({weight} * {view_names[1]}{self.format_name(col)}) /
                            {sum_weights}
                        END
                    """
                elif win_func == "VARIANCE":
                    return f"""
                        CASE WHEN
                            COUNT({view_names[1]}{self.format_name(col)}) {window_specs}
                            < {window}
                        THEN NULL
                        ELSE
                            {weighting_ratio} *
                            SUM({weight} *
                                POW(
                                    {view_names[1]}{self.format_name(col)} -
                                    {view_names[0]}{self.format_name(col+'_MU')},
                                    2
                                )
                            ) {window_specs}
                        END
                    """
                elif win_func == "STDDEV":
                    return f"""
                        CASE WHEN
                            COUNT({view_names[1]}{self.format_name(col)}) {window_specs}
                            < {window}
                        THEN NULL
                        ELSE
                            SQRT(
                                {weighting_ratio} *
                                SUM({weight} *
                                    pow(
                                        {view_names[1]}{self.format_name(col)} -
                                        {view_names[0]}{self.format_name(col+'_MU')},
                                        2
                                    )
                                ) {window_specs}
                            )
                        END
                    """
        elif (
            # Per the Pandas documentation, a minimum of 4 (or 3) periods are required
            # for a kurtosis (or skew) calculation. In practice, this seems to only
            # apply for rolling but not expanding windows.
            purpose == "rolling"
            and (
                (win_func == "KURTOSIS" and window < 4)
                or (win_func == "SKEW" and window < 3)
            )
        ):
            return "NULL"
        elif win_func == "QUANTILE":
            quantile = kwargs.get("quantile", 0.5)
            return f"""
            CASE WHEN COUNT({view_names[1]}{self.format_name(col)}) < {window}
            THEN NULL ELSE PERCENTILE_CONT({quantile})
            WITHIN GROUP (ORDER BY ({view_names[1]}{self.format_name(col)})) END
            """
        elif win_func == "RANK":
            method = kwargs.get("method", "average")
            ascending = kwargs.get("ascending", True)
            comp = ">"
            addend = ""
            if ascending:
                comp = "<"
            if method == "min":
                addend = "+1"
            elif method == "max":
                comp = f"{comp}="
            else:
                assert (
                    method == "average"
                ), f"Expected 'average' for 'method', got '{method}'"
                addend = f"""
                +(SUM(CAST(
                    ({view_names[1]}{self.format_name(col)}=
                    {view_names[0]}{self.format_name(col)})
                    AS INT
                ))+1)/2
                """
            return f"""
            CASE WHEN COUNT({view_names[1]}{self.format_name(col)}) < {window}
            THEN NULL
            ELSE
                CASE WHEN
                    {view_names[0]}{self.format_name(col)} IS NULL
                THEN  NULL
                ELSE SUM(CAST(
                    ({view_names[1]}{self.format_name(col)}{comp}
                    {view_names[0]}{self.format_name(col)}) AS INT
                )) END {addend}
            END
            """
        elif win_func in ["MEDIAN", "KURTOSIS", "SKEW"]:
            if win_func == "SKEW":
                win_func = "SKEWNESS"
            return f"""
            CASE WHEN COUNT({view_names[1]}{self.format_name(col)}) < {window}
            THEN NULL ELSE {win_func}({view_names[1]}{self.format_name(col)}) END
            """
        else:
            raise make_exception(
                NotImplementedError,
                PonderError.DUCKDB_WINDOW_FUNCTION_NOT_IMPLEMENTED,
                f"Aggregation function {win_func} not implemented yet.",
            )

    def generate_simple_unpivot(
        self, input_node_query, input_query_cols, transposed=False
    ):
        formatted_input_query_cols = [self.format_name(col) for col in input_query_cols]
        input_cols_str = ", ".join(formatted_input_query_cols)
        if not transposed:
            return f"""
                SELECT {__PONDER_ORDER_COLUMN_NAME__} AS R, C, V
                FROM (
                    UNPIVOT ({input_node_query})
                    ON {input_cols_str}
                    INTO
                        NAME C
                        VALUE V
                )
            """
        else:
            return f"""
                SELECT R, {__PONDER_ORDER_COLUMN_NAME__} AS C, V
                FROM (
                    UNPIVOT ({input_node_query})
                    ON {input_cols_str}
                    INTO
                        NAME R
                        VALUE V
                )
            """

    def generate_dot_product_matrix(
        self,
        input_query,
        output_columns,
    ):
        # Input query is assumed to be properly formatted and always produces
        # R, C, V columns
        formatted_output_columns = [self.format_name(col) for col in output_columns]
        formatted_output_col_str = ", ".join(formatted_output_columns)
        return f"""
        WITH MATMUL AS ({input_query})
        PIVOT (
            SELECT R AS "{__PONDER_ORDER_COLUMN_NAME__}",
            "{__PONDER_ORDER_COLUMN_NAME__}" AS "{__PONDER_ROW_LABELS_COLUMN_NAME__}",
            C, V
            FROM MATMUL
        )
        ON C IN ({formatted_output_col_str})
        USING SUM(V)
        """

    def generate_serialized_dot_product_from_unpivot(
        self,
        left_table,
        right_table,
        transposed_left=False,
        transposed_right=False,
    ):
        where_clause = "WHERE "
        if transposed_left:
            where_clause = where_clause + " LEFT_TABLE.C = "
        else:
            where_clause = where_clause + " CAST(LEFT_TABLE.C AS INTEGER) = "

        if transposed_right:
            where_clause = where_clause + "CAST(RIGHT_TABLE.R AS INTEGER) "
        else:
            where_clause = where_clause + "RIGHT_TABLE.R "

        return f"""
        SELECT LEFT_TABLE.R AS R, RIGHT_TABLE.C AS C,
        SUM(LEFT_TABLE.V * RIGHT_TABLE.V) AS V
        FROM ({left_table}) AS LEFT_TABLE,
            ({right_table}) AS RIGHT_TABLE
        {where_clause}
        GROUP BY LEFT_TABLE.R, RIGHT_TABLE.C
        """

    def generate_pct_change(self, column_name, periods, partition_by_clause=""):
        column_name = self.format_name(column_name)
        order_col = __PONDER_ORDER_COLUMN_NAME__
        # periods can be negative in Snowflake, but we would need to use LEAD
        # for other DBs most likely.
        lag_window = f"""LAG({column_name}, {periods}) OVER (
            {partition_by_clause}
            ORDER BY {order_col}
            )"""

        return f"({column_name} - {lag_window}) / ({lag_window})"

    def generate_dt_dayofweek(self, params_list):
        col_name_quoted = params_list[0]
        return f"ISODOW({col_name_quoted}::timestamp)-1"

    def generate_dt_week(self, params_list):
        col_name_quoted = params_list[0]
        return f"WEEK(CAST({col_name_quoted} AS TIMESTAMP))"

    def generate_dt_dayofyear(self, params_list):
        col_name_quoted = params_list[0]
        return f"DAYOFYEAR({col_name_quoted}::timestamp)"

    def generate_dt_quarter(self, params_list):
        col_name_quoted = params_list[0]
        return f"QUARTER({col_name_quoted}::timestamp)"

    def generate_dt_microsecond(self, params_list):
        col_name_quoted = params_list[0]
        return f"MICROSECOND({col_name_quoted}::timestamp)"

    def generate_dt_nanosecond(self, params_list):
        return f"{self.generate_dt_microsecond(params_list)}//1000"

    def generate_dt_year(self, params_list):
        col_name_quoted = params_list[0]
        return f"YEAR({col_name_quoted}::timestamp)"

    def generate_dt_day_name(self, params_list):
        col_name_quoted = params_list[0]
        return f"""
        CASE DAYOFWEEK({col_name_quoted}::timestamp)
            WHEN 0 THEN 'Sunday'
            WHEN 1 THEN 'Monday'
            WHEN 2 THEN 'Tuesday'
            WHEN 3 THEN 'Wednesday'
            WHEN 4 THEN 'Thursday'
            WHEN 5 THEN 'Friday'
            WHEN 6 THEN 'Saturday'
            END"""

    def generate_dt_month_name(self, params_list):
        # the first param is the quoted column name.
        c = params_list[0]
        return f"""
        CASE MONTH({c}::timestamp)
            WHEN 1 THEN 'January'
            WHEN 2 THEN 'February'
            WHEN 3 THEN 'March'
            WHEN 4 THEN 'April'
            WHEN 5 THEN 'May'
            WHEN 6 THEN 'June'
            WHEN 7 THEN 'July'
            WHEN 8 THEN 'August'
            WHEN 9 THEN 'September'
            WHEN 10 THEN 'October'
            WHEN 11 THEN 'November'
            WHEN 12 THEN 'December'
            END"""

    def generate_dt_tz_localize(self, params_list):
        col_name_quoted, tz = params_list
        return (
            f"{col_name_quoted}::TIMESTAMP"
            if tz is None
            else f"""MAKE_TIMESTAMPTZ(
                year({col_name_quoted}), month({col_name_quoted}),
                day({col_name_quoted}), hour({col_name_quoted}),
                minute({col_name_quoted}),
                microsecond({col_name_quoted})/1000000,
                {self.format_value(tz)})"""
        )

    def _generate_dates_within_offset_of_min_or_max_predicate(
        self,
        column_name: str,
        offset: pandas.DateOffset,
        min: bool,
    ):
        n, postgres_unit = _pandas_offset_object_to_n_and_sql_unit(offset)
        formatted_time = self.format_name(column_name)
        # maybe doing separate min() query, joining with that, and then filtering (all
        # probably at the query compiler layer) is more performant than the single row
        # subquery here, but this version is quicker to write. Can revisit later.
        diff_arg1, diff_arg2 = (
            (f"MIN({formatted_time}) OVER ()", formatted_time)
            if min
            else (
                formatted_time,
                f"MAX({formatted_time}) OVER ()",
            )
        )
        return f"""
            QUALIFY DATEDIFF(
                '{postgres_unit}',
                {diff_arg1},
                {diff_arg2}
            ) < {n}
        """

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
        formatted_index_name = self.format_name(index_name)

        def time_micros(datetime_expression):
            # We need microseconds since midnight. Following the pandas datetime index's
            # _time_to_micros,convert the hour, minute, second, and subsecond components
            # of the time to microseconds and sum the results together.
            return f"""
            FLOOR(DATE_PART('MICROSECOND', {datetime_expression}) / 1000) +
            1000000 * (
                60 * 60 * DATE_PART('HOUR', {datetime_expression}) +
                60 * DATE_PART('MINUTE', {datetime_expression}) +
                DATE_PART('SECOND', {datetime_expression})
            )"""

        start_compare_time_maybe_timezone_adjusted = time_micros(
            f"{formatted_index_name} AT TIME ZONE 'UTC'"
            if compare_start_to_utc_time
            else formatted_index_name
        )
        end_compare_time_maybe_timezone_adjusted = time_micros(
            f"{formatted_index_name} AT TIME ZONE 'UTC'"
            if compare_end_to_utc_time
            else formatted_index_name
        )
        return f"""
            WHERE
                {start_compare_time_maybe_timezone_adjusted}
                    {">=" if include_start else ">"}
                    {start_time_micros} AND
                {end_compare_time_maybe_timezone_adjusted}
                    {"<=" if include_end else "<"}
                    {end_time_micros}
            """

    def generate_bitwise_and(self, op_1, op_2) -> str:
        return f"{str(op_1)} & {str(op_2)}"

    def generate_bitwise_or(self, op_1, op_2) -> str:
        return f"{str(op_1)} | {str(op_2)}"

    def generate_bitwise_xor(self, op_1, op_2) -> str:
        return f"XOR({str(op_1)},{str(op_2)})"

    def generate_map_column_expressions(self, labels_to_apply_over, n):
        return [
            f"""
            IF(ARRAY_LENGTH({labels_to_apply_over[0]})>{i},
                {labels_to_apply_over[0]}[{i+1}]::STRING,
                NULL)
            """
            for i in range(n)
        ]

    def generate_value_dict_fill_na(
        self,
        label,
        value_dict,
        limit,
        group_cols: list[str],
        upcast_to_object,
    ):
        if upcast_to_object:
            raise make_exception(
                NotImplemented,
                PonderError.DUCKDB_FILLNA_MIXED_TYPES_NOT_IMPLEMENTED,
                message="fillna with mixed types not implemented for DuckDB",
            )
        if label not in value_dict:
            return label
        formatted_value = self.format_value(value_dict[label])
        if group_cols is None:
            partition_by_sql = ""
        else:
            partition_by_sql = (
                f" PARTITION BY "
                f"({','.join(self.format_name(c) for c in group_cols)})"
            )

        if limit is not None:
            return f"""
                CASE WHEN
                        SUM(CAST(({self.format_name(label)} IS NULL) AS INT))
                        OVER (
                            {partition_by_sql}
                            ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                        ) <= {limit}
                    AND
                        {self.format_name(label)} IS NULL
                THEN {formatted_value} ELSE {self.format_name(label)} END
                """
        else:
            return f"""
                CASE WHEN {self.format_name(label)} IS NULL
                THEN {formatted_value} ELSE {self.format_name(label)} END
            """

    def generate_method_fill_na(
        self, method, limit, columns, group_cols: Optional[list[str]] = None
    ):
        if group_cols is None:
            partition_by_sql = ""
        else:
            partition_by_sql = (
                f"PARTITION BY ({','.join(self.format_name(c) for c in group_cols)})"
            )

        if method == "ffill":
            between_range = (
                f"{limit} PRECEDING AND 0 FOLLOWING"
                if limit
                else "UNBOUNDED PRECEDING AND CURRENT ROW"
            )
            col_selections = []
            for col in columns:
                col_selections.append(
                    f"""
                LAST_VALUE({self.format_name(col)} IGNORE NULLS)
                OVER (
                    {partition_by_sql}
                    ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                    ROWS BETWEEN {between_range}
                )
                AS {self.format_name(col)}
                """
                )
            columns_selection = ", ".join(col_selections)
        elif method == "bfill":
            between_range = (
                f"0 PRECEDING AND {limit} FOLLOWING"
                if limit
                else "CURRENT ROW AND UNBOUNDED FOLLOWING"
            )
            col_selections = []
            for col in columns:
                col_selections.append(
                    f"""
                FIRST_VALUE({self.format_name(col)} IGNORE NULLS)
                OVER (
                    {partition_by_sql}
                    ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                    ROWS BETWEEN {between_range}
                )
                AS {self.format_name(col)}
                """
                )
            columns_selection = ", ".join(col_selections)
        else:
            raise make_exception(
                ValueError,
                PonderError.DUCKDB_FILLNA_INVALID_METHOD,
                "received method from fillna that is not ffill or bfill",
            )
        return columns_selection

    # Duplicates code in SnowFlake, but it's not enough to
    # warrant a mix-in or change in the hierarchy
    def generate_find_last_altered_time_command(
        self, database_name, schema_name, table_name
    ):
        # Using ILIKE for now - once we start handling case sensitivity
        # correctly - the ILIKE condition will change to TABLE_NAME = 'foo'
        # from TABLE_NAME ILIKE 'foo'
        return (
            'SELECT LAST_ALTERED FROM INFORMATION_SCHEMA."TABLES" WHERE'
            f" TABLE_CATALOG ILIKE '{database_name}' AND TABLE_SCHEMA ILIKE"
            f" '{schema_name}' AND TABLE_NAME LIKE '{table_name}'"
        )

    def generate_cast_to_type_command(self, col, cast_type):
        return (
            f"CAST({self.format_name(col)} AS "
            f"{self.pandas_type_to_duckdb_type_map[cast_type]})"
        )

    def generate_pandas_mask(
        self,
        binary_pred_str,
        dbcolumn,
        value_dict,
        upcast_to_object,
    ):
        raise make_exception(
            exception_class=NotImplementedError,
            code=PonderError.DUCKDB_MASK_NOT_IMPLEMENTED,
            message="Mask not yet supported in DuckDB dialect",
        )
