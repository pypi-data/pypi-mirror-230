from __future__ import annotations

import hashlib
import logging
import math
import random
import re
import string
import uuid
import warnings
from datetime import date
from functools import reduce
from typing import Dict, Iterable, List, Optional, Pattern

import numpy as np
import pandas
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_object_dtype,
    is_scalar,
    is_string_dtype,
)
from pandas.core.dtypes.common import is_numeric_dtype, pandas_dtype

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
    get_execution_configuration,
)
from ponder.core.error_codes import PonderError, make_exception
from ponder.core.sql_dialect import (
    SQLDialect,
    _pandas_offset_object_to_n_and_sql_unit,
    _pandas_offset_object_to_seconds,
    _pandas_start_val_to_end_period,
)

logger = logging.getLogger(__name__)


class bigquery_dialect(SQLDialect):
    pandas_type_to_bigquery_type_map = {
        "boolean": "BOOLEAN",
        "bool": "BOOLEAN",
        "date": "DATETIME",
        "datetime64[ms]": "TIMESTAMP",
        "datetime64[ns]": "TIMESTAMP",
        "datetime": "TIMESTAMP",
        "float": "FLOAT64",
        "float64": "FLOAT64",
        "int": "INT64",
        "int8": "BIGINT",
        "int16": "BIGINT",
        "int32": "BIGINT",
        "int64": "BIGINT",
        "uint8": "BIGINT",
        "str": "STRING",
        "object": "STRING",
    }

    valid_name_regex_pattern = re.compile("^[A-Z_][A-Z0-9_\\$]*")

    def __init__(self):
        super().__init__()
        self._obfuscate = False
        self._salt = uuid.uuid4().hex
        self._valid_name_regex_pattern = re.compile("^[A-Z_][A-Z0-9_\\$]*")

    def format_table_name(self, table_or_query):
        if self._obfuscate:
            # just doing something random to obfuscate.
            return (
                hashlib.sha256(
                    self._salt.encode() + table_or_query.encode()
                ).hexdigest()
                + ":"
                + self._salt
            )
        if self.is_query_like(table_or_query):
            return f"({table_or_query})"
        return f"`{table_or_query}`"

    def format_name(self, name):
        if not isinstance(name, str):
            name = str(name)
        if self._obfuscate:
            # just doing something random to obfuscate.
            return (
                hashlib.sha256(self._salt.encode() + name.encode()).hexdigest()
                + ":"
                + self._salt
            )
        return f"{name}"

    def format_name_thrice(self, name):
        if self._obfuscate:
            # just doing something random to obfuscate.
            return self.format_name(name)

        return f"{name}"

    def format_name_quarce(self, name):
        if self._obfuscate:
            # just doing something random to obfuscate.
            return self.format_name(name)

        return f"{name}"

    def format_names_list(self, names):
        return [self.format_name(name) for name in names]

    def format_names_list_thrice(self, names):
        return [
            self.format_name_thrice(name)
            if not name.startswith('"')
            else self.format_name_quarce(name)
            for name in names
        ]

    def format_value(self, value):
        if not isinstance(value, str):
            return value
        escaped = value.replace("\\", "\\\\").replace("'", "\\'")
        return f"'{escaped}'"

    def format_value_by_type(self, value):
        if value is None:
            return "NULL"
        if isinstance(value, pandas.Timestamp):
            return f'TIMESTAMP("{value}")'
        if isinstance(value, str):
            return f"'{value}'"
        elif isinstance(value, pandas.Interval):
            return (
                """JSON '{"_ponder_python_object_type": "pandas.Interval","""
                + '"data": {'
                + f'"left": {self.format_value_by_type(value.left)}, '
                + f'"right": {self.format_value_by_type(value.right)}, '
                + f""""closed": {f'"{value.closed}"'} }}}}'"""
            )
        return f"{value}"

    def format_name_cast_to_type(self, name, type):
        if type.__name__ == pandas.Timestamp.__name__:
            return f"TIMESTAMP({self.format_name(name)})"
        return self.format_name(name)

    def set_obfuscate(self):
        self._obfuscate = True

    def generate_get_current_database_command(self):
        return "SELECT CURRENT_DATABASE()"

    def generate_get_current_schema_command(self):
        return "SELECT CURRENT_SCHEMA()"

    def generate_get_command(self, stage_path, local_path):
        command = "get " + "@" + stage_path + " file://" + local_path + ";"
        return command

    def generate_copy_into_table_command(
        self,
        table_name,
        column_names,
        column_types,
        sep=",",
        header=0,
        na_values="",
        on_bad_lines="error",
    ):
        skip_header = 0
        if not isinstance(header, str):
            skip_header = header + 1
        columns_clause = ", ".join(
            [self.format_name(column_name) for column_name in column_names]
        )

        from_clause = ", ".join(
            [
                f"${column_index}"
                if (
                    self.pandas_type_to_bigquery_type_map[str(column_type)] != "BOOLEAN"
                )
                else f"CAST(${column_index} AS BOOL)"
                for column_index, column_type in zip(
                    [i for i in range(1, len(column_types) + 1)], column_types
                )
            ]
        )
        from_clause = f" FROM ( SELECT {from_clause} FROM @%{table_name} )"

        on_error_fragment = "ON_ERROR=CONTINUE" if on_bad_lines == "skip" else ""

        command = (
            f"COPY INTO {table_name} ( {columns_clause} ) {from_clause} purge = true"
            f" file_format = (type = csv NULL_IF='{na_values}'"
            f" FIELD_OPTIONALLY_ENCLOSED_BY='\"' FIELD_DELIMITER='{sep}'"
            f" SKIP_HEADER={skip_header}, ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE)"
            f" {on_error_fragment}"
        )
        return command

    def generate_select_count_star_statement(self, table):
        formatted_table_name = self.format_table_name(table)
        return f"SELECT COUNT(*) FROM ({formatted_table_name});"

    def generate_read_table_metadata_statement(
        self,
        table_or_query,
    ):
        formatted_table_or_query = self.format_table_name(table_or_query)
        return f"SELECT * FROM {formatted_table_or_query} LIMIT 1"

    def generate_use_warehouse_command(self, warehouse_name):
        return "USE WAREHOUSE " + self.format_name(warehouse_name) + ";"

    def generate_use_database_command(self, database_name):
        return "USE DATABASE " + self.format_name(database_name) + ";"

    def generate_use_schema_command(self, schema_name):
        return "USE SCHEMA " + self.format_name(schema_name) + ";"

    def generate_use_role_command(self, role_name):
        return "USE ROLE " + self.format_name(role_name) + ";"

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

        # Standard error of mean (SEM) does not have native dbms support
        # thus calculated as STDDEV/SQRT(N-1)
        if cumulative_function == "SEM":
            if non_numeric_col:
                return "NULL"
            return f"""
                IF(COUNT({formatted_col}) OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                ROWS BETWEEN {window-1} PRECEDING AND CURRENT ROW)={window},
                (STDDEV({formatted_col}) OVER (ORDER BY
                {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN {window-1}
                PRECEDING AND CURRENT ROW))/SQRT({window-1}), NULL)
                """

        if cumulative_function == "CORR":
            assert formatted_other_col is not None
            if non_numeric_col or window < 2:
                return "NULL"

            count_exp = f"""
            COUNTIF({formatted_col} IS NOT NULL AND {formatted_other_col} IS NOT NULL)
             OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
             ROWS BETWEEN {window-1} PRECEDING AND CURRENT ROW)"""

            sigmas_exp = f"""
                    STDDEV_POP(IF({formatted_col} IS NULL,NULL,{formatted_other_col}))
                    OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN
                    {window-1} PRECEDING AND CURRENT ROW) *
                    STDDEV_POP(IF({formatted_other_col} IS NULL,NULL,{formatted_col}))
                    OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN
                    {window-1} PRECEDING AND CURRENT ROW)"""

            return f"""
                IF({count_exp}={window} AND {count_exp} * {sigmas_exp} > 0, (
                    SUM({formatted_other_col}*{formatted_col}) OVER (ORDER BY
                    {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN {window-1}
                    PRECEDING AND CURRENT ROW) - (
                        SUM(IF({formatted_col} IS NULL,NULL,{formatted_other_col}))
                        OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN
                        {window-1} PRECEDING AND CURRENT ROW) *
                        SUM(IF({formatted_other_col} IS NULL,NULL,{formatted_col}))
                        OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN
                        {window-1} PRECEDING AND CURRENT ROW) / {count_exp}
                    )
                ) / (
                    {count_exp} * {sigmas_exp}
                ), NULL)
                """

        if cumulative_function == "COV":
            assert formatted_other_col is not None
            if non_numeric_col or window < 2:
                return "NULL"

            count_exp = f"""
            COUNTIF({formatted_col} IS NOT NULL AND {formatted_other_col} IS NOT NULL)
             OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
             ROWS BETWEEN {window-1} PRECEDING AND CURRENT ROW)"""

            return f"""
                IF({count_exp}={window}, (
                    SUM({formatted_other_col}*{formatted_col}) OVER (ORDER BY
                    {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN {window-1}
                    PRECEDING AND CURRENT ROW) - (
                        SUM(IF({formatted_col} IS NULL,NULL,{formatted_other_col}))
                        OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN
                        {window-1} PRECEDING AND CURRENT ROW) *
                        SUM(IF({formatted_other_col} IS NULL,NULL,{formatted_col}))
                        OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN
                        {window-1} PRECEDING AND CURRENT ROW) / {count_exp}
                    )
                ) / (
                    {count_exp}-1
                ), NULL)
                """

        return f"""
        IF(COUNT({formatted_col}) OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
         ROWS BETWEEN {window - 1} PRECEDING AND CURRENT ROW)={window},
            {cumulative_function}({formatted_col}) OVER (ORDER BY
            {__PONDER_ORDER_COLUMN_NAME__}
                ROWS BETWEEN {window - 1} PRECEDING AND CURRENT ROW),
                NULL)"""

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
                IF(COUNT({__PONDER_ORDER_COLUMN_NAME__}) OVER
                 (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS
                 BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)>={min_window},
                 COUNT({formatted_col}) OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                 ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), NULL)
                """

        if cumulative_function == "SEM":
            if non_numeric_col:
                return "NULL"

            count_expression = f"""COUNT({formatted_col})
             OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)"""

            return f"""
            IF({count_expression}>={min_window},
             (STDDEV({formatted_col}) OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
              ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW))
             /SQRT({count_expression}-1), NULL)
            """

        if cumulative_function == "CORR":
            assert formatted_other_col is not None
            if non_numeric_col:
                return "NULL"

            count_exp = f"""
            COUNTIF({formatted_col} IS NOT NULL AND {formatted_other_col} IS NOT NULL)
             OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)"""

            sigmas_exp = f"""
                    STDDEV_POP(IF({formatted_col} IS NULL,NULL,{formatted_other_col}))
                    OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN
                    UNBOUNDED PRECEDING AND CURRENT ROW) *
                    STDDEV_POP(IF({formatted_other_col} IS NULL,NULL,{formatted_col}))
                    OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN
                    UNBOUNDED PRECEDING AND CURRENT ROW)"""

            return f"""
                IF({count_exp}>={min_window} AND {count_exp} * {sigmas_exp} > 0, (
                    SUM({formatted_other_col}*{formatted_col}) OVER (ORDER BY
                    {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN UNBOUNDED
                    PRECEDING AND CURRENT ROW) - (
                        SUM(IF({formatted_col} IS NULL,NULL,{formatted_other_col}))
                        OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN
                        UNBOUNDED PRECEDING AND CURRENT ROW) *
                        SUM(IF({formatted_other_col} IS NULL,NULL,{formatted_col}))
                        OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN
                        UNBOUNDED PRECEDING AND CURRENT ROW) / {count_exp}
                    )
                ) / (
                    {count_exp} * {sigmas_exp}
                ), NULL)
                """

        if cumulative_function == "COV":
            assert formatted_other_col is not None
            if non_numeric_col:
                return "NULL"

            count_exp = f"""
            COUNTIF({formatted_col} IS NOT NULL AND {formatted_other_col} IS NOT NULL)
             OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)"""

            return f"""
                IF({count_exp}>=GREATEST({min_window}, 2), (
                    SUM({formatted_other_col}*{formatted_col}) OVER (ORDER BY
                    {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN UNBOUNDED
                    PRECEDING AND CURRENT ROW) - (
                        SUM(IF({formatted_col} IS NULL,NULL,{formatted_other_col}))
                        OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN
                        UNBOUNDED PRECEDING AND CURRENT ROW) *
                        SUM(IF({formatted_other_col} IS NULL,NULL,{formatted_col}))
                        OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN
                        UNBOUNDED PRECEDING AND CURRENT ROW) / {count_exp}
                    )
                ) / (
                    {count_exp}-1
                ), NULL)
                """

        return f"""
            IF(COUNT({formatted_col}) OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)>={min_window},
            {cumulative_function}({formatted_col}) OVER (ORDER BY
            {__PONDER_ORDER_COLUMN_NAME__}
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW),
                NULL)"""

    def generate_downsample_command(
        self,
        col,
        offset: pandas.DateOffset,
        start_val: pandas.Timestamp,
        end_val: pandas.Timestamp,
        sum_interval: float,
    ):
        n, unit = _pandas_offset_object_to_n_and_sql_unit(offset)
        n_sec = _pandas_offset_object_to_seconds(offset)
        if unit in ("second", "minute", "hour", "day"):
            return (
                f"TIMESTAMP_SECONDS(DIV(UNIX_SECONDS(TIMESTAMP("
                f"{self.format_name(col)})), {n_sec}) * {n_sec})"
            )
        else:
            end_val = _pandas_start_val_to_end_period(end_val, unit)
            if unit == "week":
                # Special case for week end Sunday
                return (
                    f"LEAD(LAST_DAY(DATETIME(TIMESTAMP_SECONDS(DIV(UNIX_SECONDS("
                    f"TIMESTAMP({self.format_name(col)})), {n_sec}) * {n_sec})), "
                    f"{unit}(monday)), 1, "
                    f"CAST({self.format_value(end_val)} as DATETIME)) "
                    f"OVER (ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)})"
                )
            else:
                # Case month, quarter, year
                return (
                    f"LAST_DAY(DATETIME(TIMESTAMP_SECONDS(DIV(UNIX_SECONDS("
                    f"TIMESTAMP({self.format_name(col)})), {n_sec}) "
                    f"* {n_sec} + {n_sec})), {unit})"
                )

    def generate_downsample_index_command(
        self,
        col,
        offset: pandas.DateOffset,
        start_val: pandas.Timestamp,
        end_val: pandas.Timestamp,
    ):
        # Uses a generator to create uniform sampled index
        n, unit = _pandas_offset_object_to_n_and_sql_unit(offset)
        start_val = _pandas_start_val_to_end_period(start_val, unit)
        end_val = _pandas_start_val_to_end_period(end_val, unit)

        if unit in ("week", "month", "quarter", "year"):
            # We need to convert start_val from a TIMESTAMP to DATE
            # in order to use GENERATE_DATE_ARRAY which supports
            # intervals week, month, quarter, year. We calculate
            # the number of seconds since 1970-01-01 00:00:00 UTC
            # using UNIX_SECONDS, then divide by 86400 (number of seconds
            # in a day), then convert to DATE using DATE_FROM_UNIX_DATE
            return (
                f"SELECT * FROM UNNEST(GENERATE_DATE_ARRAY("
                f"DATE_FROM_UNIX_DATE(CAST(FLOOR(UNIX_SECONDS("
                f"{self.format_value(start_val)}) / 86400) AS INT64)), "
                f"DATE_FROM_UNIX_DATE(CAST(FLOOR(UNIX_SECONDS("
                f"{self.format_value(end_val)}) / 86400) AS INT64)), "
                f"INTERVAL {n} {unit})) AS {self.format_name('generate_series')}"
            )
        else:
            return (
                f"SELECT * FROM UNNEST(GENERATE_TIMESTAMP_ARRAY( "
                f"{self.format_value(start_val)}, {self.format_value(end_val)}, "
                f"INTERVAL {n} {unit})) AS {self.format_name('generate_series')}"
            )

    def generate_use_admin_role_command(self):
        return "USE ROLE SYSADMIN;"

    def generate_query_tag_command(self):
        return 'ALTER SESSION SET QUERY_TAG="PONDER QUERY"'

    def generate_query_timeout_command(self, query_timeout):
        return f"ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS={query_timeout}"

    def generate_temp_table_for_subquery(self, temp_table_name, query):
        logger.debug(f"BigQuery dialect {temp_table_name}")
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
        logger.debug(f"BigQuery dialect {temp_table_name}")

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
        logger.debug(f"BigQuery dialect return array size {len(return_arr)}")
        return return_arr

    def generate_update_temp_table_command(self, temp_table_name):
        return f"""ALTER TABLE {temp_table_name} ADD COLUMN _PONDER_ROW_LABELS_ INT;
                 UPDATE {temp_table_name} SET
                {__PONDER_ROW_LABELS_COLUMN_NAME__}={__PONDER_ORDER_COLUMN_NAME__}
                 WHERE TRUE;
            """

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
        # Join on index needs to be replaced with their respective column names
        left_on = [
            left_order_column_name if on == __PONDER_ORDER_COLUMN_NAME__ else on
            for on in left_on
        ]
        right_on = [
            right_order_column_name if on == __PONDER_ORDER_COLUMN_NAME__ else on
            for on in right_on
        ]

        join_clause = " AND ".join(
            [
                # nulls count as matching in pandas joins:
                # pandas.DataFrame([[None, 1]], columns=['a', 'b']).merge(
                #   pandas.DataFrame([[None, 2]], columns=['a', 'b']),
                #   on='a',
                #   how='left',
                #   indicator=True)
                # )
                # the _merge column in result is 'both' for the above.
                # ... but bigquery gives "FULL OUTER JOIN cannot be used without a
                # condition that is an equality of fields from both sides of the join",
                # so skip the fix there for now. TODO: work around that bug with
                # https://stackoverflow.com/a/45431044/17554722 or another solution.
                (
                    (
                        f"LEFT_TABLE.{self.format_name(left_clause)} = "
                        + f"RIGHT_TABLE.{self.format_name(right_clause)}"
                    )
                    if how == "outer"
                    else (
                        f"(LEFT_TABLE.{self.format_name(left_clause)} = "
                        + f"RIGHT_TABLE.{self.format_name(right_clause)} OR "
                        + f"(LEFT_TABLE.{self.format_name(left_clause)} IS NULL AND "
                        + f"RIGHT_TABLE.{self.format_name(right_clause)} IS NULL))"
                    )
                )
                for left_clause, right_clause in zip(left_on, right_on)
            ]
        )

        on_clause = " ON " + join_clause

        if how == "cross":
            on_clause = ""

        formatted_select_list = self.format_names_list(select_list)

        select_clause = ", ".join(
            (
                *formatted_select_list,
                self.format_name(left_order_column_name),
                self.format_name(right_order_column_name),
            )
        )

        if indicator:
            if how == "left":
                indicator_clause = (
                    f"CASE WHEN {self.format_name(right_order_column_name)} IS NULL "
                    f"THEN 'left_only' ELSE 'both' END AS _merge "
                )
            elif how == "right":
                indicator_clause = (
                    f"CASE WHEN {self.format_name(left_order_column_name)} IS NULL "
                    f"THEN 'right_only' ELSE 'both' END AS _merge "
                )
            elif how == "outer":
                indicator_clause = (
                    f"CASE WHEN {self.format_name(left_order_column_name)} IS NULL "
                    f"THEN 'right_only' "
                    f"WHEN {self.format_name(right_order_column_name)} IS NULL "
                    f"THEN 'left_only' ELSE 'both' END AS _merge "
                )
            elif how == "inner":
                indicator_clause = "'both' AS _merge "
            else:
                raise make_exception(
                    NotImplementedError,
                    PonderError.BIGQUERY_JOIN_INDICATOR_UNSUPPORTED_JOIN_TYPE,
                    "Indicator Clause only supported for left joins currently",
                )
            select_clause = select_clause + ", " + indicator_clause
        result_order_column_expression = ""
        if how == "left" or how == "inner" or how == "outer" or how == "cross":
            if db_index_column_name is None:
                row_labels = (
                    f" {self.format_name(left_order_column_name)} AS"
                    f" {self.format_name(__PONDER_ROW_LABELS_COLUMN_NAME__)}"
                )
            else:
                if (
                    isinstance(db_index_column_name, list)
                    and len(db_index_column_name) > 1
                ):
                    make_exception(
                        NotImplementedError,
                        PonderError.BIGQUERY_JOIN_WITH_MULTIPLE_INDEX_NOT_IMPLEMENTED,
                        "Multiple index columns not implemented for joins",
                    )
                row_labels = f"LEFT_TABLE.{db_index_column_name[0]}"

            # https://ponderdata.atlassian.net/browse/POND-1396
            # When we are joining on the order columns we need to preserve
            # the PONDER_ROW_ORDER from the original join values rather than
            # re-index
            if (
                len(left_on) == 1
                and left_on[0] == left_order_column_name
                and len(right_on) == 1
                and right_on[0] == right_order_column_name
            ):
                result_order_column_expression = (
                    f", COALESCE({self.format_name(left_order_column_name)}, "
                    f" {self.format_name(right_order_column_name)}) AS"
                    f" {self.format_name(result_order_column_name)},"
                    f" {row_labels}"
                )
            else:
                result_order_column_expression = (
                    ", ROW_NUMBER() OVER (ORDER BY"
                    f" {self.format_name(left_order_column_name)},"
                    f" {self.format_name(right_order_column_name)}) - 1 AS"
                    f" {self.format_name(result_order_column_name)},"
                    f" {row_labels}"
                )
        else:
            order_labels_expressions = (
                ", ROW_NUMBER() OVER (ORDER BY"
                f" {self.format_name(right_order_column_name)},"
                f" {self.format_name(left_order_column_name)}) - 1 AS"
            )

            result_order_column_expression = (
                f"{order_labels_expressions}"
                f" {self.format_name(result_order_column_name)}"
                f" {order_labels_expressions}"
                f" {self.format_name(__PONDER_ROW_LABELS_COLUMN_NAME__)}"
            )
        if how == "outer":
            how = "full outer"
        select_clause += result_order_column_expression
        order_by = f"ORDER BY {self.format_name(result_order_column_name)}"
        ret_val = (
            f"SELECT {select_clause} FROM ({left_node_query}) AS LEFT_TABLE"
            f" {how.upper()} JOIN ({right_node_query}) AS RIGHT_TABLE"
            f" {on_clause} {order_by}"
        )
        return ret_val

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
                    f" AND ABS(TIMESTAMP_DIFF({left_on_formatted[0]}, "
                    + f"{right_on_formatted[0]}, MICROSECOND)) < {total_microseconds}"
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

    def generate_ponder_order_column(self, order_by_clause):
        return f"ROW_NUMBER() OVER (ORDER BY {order_by_clause}) -1 "

    def generate_rename_columns_command(
        self,
        input_query,
        input_column_names,
        input_order_column_name,
        column_name_renames,
        original_row_labels_column_names: list[str],
        result_order_column_name=__PONDER_ORDER_COLUMN_NAME__,
    ):
        select_column_clause = ", ".join(
            [
                f"{self.format_name(c)} AS"
                f" {self.format_name(column_name_renames[c])}"
                if c in column_name_renames
                else self.format_name(c)
                for c in [*original_row_labels_column_names, *input_column_names]
            ]
        )
        formatted_input_order_col = self.format_name(input_order_column_name)
        formatted_result_order_col = self.format_name(result_order_column_name)
        return f"""SELECT
                {select_column_clause},
                {formatted_input_order_col} AS {formatted_result_order_col}
            FROM (
                {input_query}
            )
            """

    def _generate_groupby_result_order_expr(
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
        select_clauses = []
        for input_column_name in input_column_names:
            formatted_col = self.format_name(input_column_name)
            if input_column_name in row_labels_column_names:
                # Special case resample since input_column_name is both
                # a row label name and a data column name. TODO(FIX):
                # this is a workaround for a BUG upstream.
                continue
            select_clause = f"{formatted_col}"
            select_clauses.append(select_clause)

        result_order_column_expression = self.format_name(input_order_column_name)

        # Only .nth() actually obeys as_index, so we create the result order column.
        # We use all() here because aggregation_function_map is a dictionary.
        # In pandas 2.0, we will no longer need to follow this behavior. See:
        # https://github.com/pandas-dev/pandas/issues/51250#issuecomment-1424883953
        if all(
            [
                func == GROUPBY_FUNCTIONS.NTH
                for func in aggregation_function_map.values()
            ]
        ):
            result_order_column_expression = self._generate_groupby_result_order_expr(
                self.format_names_list(group_by_columns),
                self.format_name(input_order_column_name),
                self.format_name(result_order_column_name),
                sort_by_group_keys,
            )

        select_column_list = ",".join(select_clauses)

        return f"""
            SELECT
                {select_column_list},
                {", ".join(self.format_names_list(row_labels_column_names))},
                {result_order_column_expression}
            FROM
                ({input_query})
            """

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
        def _generate_groupby_reduction_transform(
            func, formatted_col, agg_args, agg_kwargs, formatted_other_col
        ):
            if func is GROUPBY_FUNCTIONS.NUNIQUE:
                dropna = agg_kwargs.get("dropna")
                # This is a hack, but we can just make use of the REDUCE_FUNCTION
                # enum here instead of doing something separate.
                if dropna:
                    func = REDUCE_FUNCTION.COUNT_UNIQUE_EXCLUDING_NULL
                else:
                    func = REDUCE_FUNCTION.COUNT_UNIQUE_INCLUDING_NULL
            # In general, we should be explicit about handling the respective kwargs
            # of the aggregation functions.
            percentile = agg_kwargs["q"] if func is GROUPBY_FUNCTIONS.QUANTILE else None
            return self.generate_reduction_column_transformation(
                func,
                formatted_col,
                percentile=percentile,
                params_list=None,
                formatted_other_col=formatted_other_col,
            )

        select_clauses = []
        formatted_other_col = None
        if other_col_id is not None:
            # Special case to add columns that will later become an index
            other_col = list(aggregation_function_map.keys())[other_col_id]
            formatted_other_col = self.format_name(other_col)
            select_clauses.append(
                f"MIN({other_col_id}) AS {__PONDER_AGG_OTHER_COL_ID__}"
            )
            select_clauses.append(
                f"MIN('{other_col}') AS {__PONDER_AGG_OTHER_COL_NAME__}"
            )
        for input_column_name in input_column_names:
            formatted_col = self.format_name(input_column_name)
            if input_column_name in aggregation_function_map:
                func = aggregation_function_map[input_column_name]
                transform = _generate_groupby_reduction_transform(
                    func,
                    formatted_col,
                    aggregation_function_args,
                    aggregation_function_kwargs,
                    formatted_other_col,
                )
                select_clause = f"{transform} AS {formatted_col}"
            else:
                select_clause = f"{formatted_col}"
            select_clauses.append(select_clause)

        select_column_list = ",".join(select_clauses)
        formatted_group_by_columns = self.format_names_list(group_by_columns)
        result_order_column_expression = self._generate_groupby_result_order_expr(
            formatted_group_by_columns,
            f"MIN({self.format_name(input_order_column_name)})",
            self.format_name(result_order_column_name),
            sort_by_group_keys,
        )

        if dropna_groupby_keys:
            where_predicates = [
                f"{col} IS NOT NULL" for col in formatted_group_by_columns
            ]
            where_clause = f"""
                        WHERE
                            {" AND ".join(where_predicates)}
                        """
        else:
            where_clause = ""

        # N. B. we never need to track a separate row labels column because either we
        # have as_index=True, in which case the new row labels are the group by keys,
        # or we have as_index=False, in which case the new row labels are the default
        # RangeIndex (translating to DBMSPositionMapping). groupby drops any
        # existing index.
        return f"""
            SELECT
                {select_column_list},
                {result_order_column_expression}
            FROM
                ({input_query})
            {where_clause}
            GROUP BY
                {",".join(formatted_group_by_columns)}
            """

    def generate_get_first_element_by_row_label_rank_command(
        self, col, row_labels_column_name
    ):
        # Cast Partition By column as string since BigQuery
        # cannot parition by float values
        return (
            f"IF(RANK() OVER "
            f"(PARTITION BY CAST({self.format_name(col)} AS STRING) "
            f"ORDER BY {self.format_name(row_labels_column_name)}) = 1, "
            f"{self.format_name(col)}, NULL)"
        )

    def generate_replace_nan_with_0(self, col):
        return f"COALESCE({self.format_name(col)}, 0)"

    # N.B. this is not super well named, but this generates window functions for groupby
    # , rolling, expanding windows, as well as cumulative functions. Long term solution
    # would be to break these into separate functions, but we will leave this for now.
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
            # BigQuery only supports partition by for Numeric/String
            # columns so we cast to String to handle all cases
            keys = ", ".join(
                [
                    f"CAST({col_name} AS STRING)"
                    for col_name in self.format_names_list(partition_by)
                ]
            )
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
                    IF({formatted_col} IS NULL, NULL, SUM({formatted_col})
                    OVER (
                        {partition_by_clause}
                        ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
                    )"""
        elif function in (
            CUMULATIVE_FUNCTIONS.PROD,
            GROUPBY_FUNCTIONS.CUMPROD,
        ):
            if skipna is False:
                return f"""
                    IF(
                        (
                            MOD(
                                COUNTIF({formatted_col} < 0)
                                OVER (
                                    {partition_by_clause}
                                    ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                                ),
                                2
                            )
                        ) = 0,
                        1,
                        -1)
                    *
                    EXP(
                        SUM(LN(ABS({formatted_col})))
                        OVER (
                            {partition_by_clause}
                            ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                        )
                    )"""
            else:
                return f"""
                    IF({formatted_col} IS NULL,
                        NULL,
                        IF
                            (
                            MOD(
                                COUNTIF({formatted_col} < 0)
                                OVER (
                                    {partition_by_clause}
                                    ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                                ),
                                2
                            ) = 0,
                            1,
                            -1) *
                        EXP(
                            SUM(LN(ABS({formatted_col})))
                            OVER (
                                {partition_by_clause}
                                ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                            )
                        )
                    )"""
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
                IF({formatted_col} IS NULL,
                    NULL,
                    (
                        MAX({formatted_col})
                        OVER (
                            {partition_by_clause}
                            ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                        )
                    )
                )"""
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
                IF({formatted_col} IS NULL,
                    NULL,
                    (
                        MIN({formatted_col})
                        OVER (
                            {partition_by_clause}
                            ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                        )
                    )
                )"""
        elif function == GROUPBY_FUNCTIONS.FIRST:
            return f"""
            FIRST_VALUE({formatted_col} IGNORE NULLS)
            OVER (
                {partition_by_clause}
                ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            )"""
        elif function == GROUPBY_FUNCTIONS.LAST:
            return f"""
            LAST_VALUE({formatted_col} IGNORE NULLS)
            OVER (
                {partition_by_clause}
                ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
            )"""
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
                    ORDER BY {keys} {order}
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
                    PonderError.BIGQUERY_GROUPBY_DIFF_AXIS_1,
                    "groupby.diff() with axis=1 not implemented yet",
                )
            return self.generate_diff(col, agg_kwargs["periods"], partition_by_clause)
        raise make_exception(
            RuntimeError,
            PonderError.BIGQUERY_WINDOW_UNKNOWN_FUNCTION,
            f"Unknown function {function}",
        )

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
        table_name = self.format_table_name(table_name)
        create_statement = "CREATE TABLE "
        if is_temp is True and is_global_temp is False:
            create_statement = "CREATE TABLE " if for_csv else "CREATE TEMPORARY TABLE "

        create_statement += table_name + " ( "

        # TODO: Fix setting the col label to a data column without
        # updating the list of row label names
        try:
            columns_clause = ", ".join(
                [
                    self.format_name(column_name)
                    + " "
                    + self.pandas_type_to_bigquery_type_map[str(column_type).lower()]
                    for column_name, column_type in zip(column_names, column_types)
                ]
            )
        except Exception as e:
            raise make_exception(
                RuntimeError,
                PonderError.BIGQUERY_CREATE_TABLE_FAILED,
                "Create table failed possibly because column types are not mapped "
                + "correctly",
            ) from e

        # add the row order/row labels columns only for temp tables.
        if (is_temp or is_global_temp) and order_column_name not in column_names:
            # apparently this weird syntax lets you check if the string is None
            # or an empty string
            if len(order_column_name or "") > 0:
                columns_clause += f", {self.format_name(order_column_name)} BIGINT"

            columns_clause += (
                f", {self.format_name(__PONDER_ROW_LABELS_COLUMN_NAME__)} BIGINT"
            )
        else:
            if (
                len(order_column_name or "") > 0
                and order_column_name not in column_names
            ):
                columns_clause += (
                    f", {self.format_name(order_column_name)} "
                    + self.pandas_type_to_bigquery_type_map[str(order_column_type)]
                )
        expiration_clause = (
            """OPTIONS (expiration_timestamp=TIMESTAMP_ADD(
                CURRENT_TIMESTAMP(), INTERVAL 1 HOUR))"""
            if for_csv
            else ""
        )
        create_statement += columns_clause + f" ) {expiration_clause}"

        return create_statement

    def generate_drop_table_command(self, table_name):
        return f"DROP TABLE {self.format_table_name(table_name)}"

    def generate_insert_rows_command(
        self,
        table_name,
        column_names,
        row_labels_column_names,
        index,
        index_label,
        input_query,
    ):
        table_name = self.format_table_name(table_name)
        select_columns_text = ", ".join(
            self.format_name(column_name)
            for column_name in column_names
            if column_name not in row_labels_column_names
        )

        if index:
            select_columns_text += ", ".join(
                (select_columns_text, *self.format_names_list(row_labels_column_names))
            )

        insert_columns_text = select_columns_text[:]

        if index is True:
            if len(index_label or "") > 0:
                select_columns_text += (
                    f", {self.format_names_list(row_labels_column_names)} AS"
                    f" {self.format_name(index_label)}"
                )
                insert_columns_text += f", {self.format_name(index_label)}"
            else:
                select_columns_text += (
                    f", {self.format_names_list(row_labels_column_names)}"
                )
                insert_columns_text += (
                    f", {self.format_names_list(row_labels_column_names)}"
                )

        insert_rows_command = (
            f"INSERT INTO {table_name} ({insert_columns_text}) SELECT"
            f" {select_columns_text} FROM ({input_query})"
        )

        return insert_rows_command

    def generate_string_values_from_values(self, values):
        str_unique_vals = [
            "na"
            if unique_val is None
            else unique_val.strftime("%Y-%m-%d %H:%M:%S")
            if isinstance(unique_val, date)
            else str(unique_val)
            if not isinstance(unique_val, str)
            else unique_val
            for unique_val in values
        ]

        return str_unique_vals

    def generate_pivot_command(
        self,
        grouping_column_name,
        pivot_column_name,
        values_column_name,
        unique_values,
        input_node_query,
        _input_node_order_column_name,
        aggfunc: GROUPBY_FUNCTIONS,
        add_qualifier_to_new_column_names,
    ):
        formatted_group_col_name_once = self.format_name(grouping_column_name)
        formatted_group_col_name_thrice = self.format_name_thrice(grouping_column_name)
        formatted_pivot_column_name = self.format_name(pivot_column_name)
        formatted_pivot_column_name_fragment = (
            ", " + self.format_name(pivot_column_name)
            if pivot_column_name != grouping_column_name
            else ""
        )

        str_unique_values = [
            generate_column_name_from_value(unique_value)
            for unique_value in unique_values
        ]
        if aggfunc in (
            GROUPBY_FUNCTIONS.MEDIAN,
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
                PonderError.BIGQUERY_PIVOT_UNSUPPORTED_AGGREGATION,
                f"pivot_table() with aggregation function {aggfunc} not supported yet",
            )
        aggregation_call = self.generate_reduction_column_transformation(
            aggfunc,
            self.format_name(values_column_name),
        )
        new_columns_prefix = (
            values_column_name + "_" if add_qualifier_to_new_column_names else ""
        )
        formatted_once_final_values_column_names = self.format_names_list(
            (new_columns_prefix + v for v in str_unique_values)
        )
        """
            SQL comments below are numbered in the order that you should read the query.
            (same applies mutis mutandis for "last")
            1. _PONDER_PIVOT_GB_ contains
              a. the values coluumn
              b. the grouping column
              c. (possibly) the pivot column
            2. pivot _PONDER_PIVOT_GB_ by the pivot column. thus for each combination
               of pivot column value and grouping column row, apply the aggregation
               function to get a single value.
              a. n.b. we also use the "AS P()" expression to alias the pivot columns.
                 by default snowflake will put single quotes around the column names
                 coming from values of the pivot column (see pivot docs), e.g. 'JAN',
                 'FEB', 'MAR'. However, once we put quotes, snowflake **may** (it
                 depends on casing of the columns) actually put a quote in the columns,
                 so then we have to escape the column names again:
                https://ponder-org.slack.com/archives/C03N1PRVB8R/p1678238528194529
            3. add row_number() over grouping column, thus sorting by the grouping
               column.
        """
        return f"""
            SELECT
                {formatted_group_col_name_thrice} AS {formatted_group_col_name_once},
                ROW_NUMBER() OVER (
                    ORDER BY {formatted_group_col_name_once}) -1
                AS {__PONDER_ORDER_COLUMN_NAME__},
                {", ".join(
                    f"{self.format_name(str_unique_values[i])} as {c}" for i, c in
                    enumerate(formatted_once_final_values_column_names))}
            FROM (
                WITH _PONDER_PIVOT_GB_ AS (
                    SELECT
                        {self.format_name(values_column_name)},
                        {formatted_group_col_name_once}
                        {formatted_pivot_column_name_fragment}
                    FROM (
                        {input_node_query}
                    )
                )
                SELECT
                    *
                FROM
                    _PONDER_PIVOT_GB_
                    PIVOT(
                        {aggregation_call}
                        FOR {formatted_pivot_column_name} in (
                            {", ".join([f"'{val}'" for val in unique_values])})
                    )
            )
        """

    def generate_find_last_altered_time_command(self, table_name):
        assert "." in table_name, "need a fully qualified table name to get schema"
        schema_name, table_name = table_name.split(".")
        return f'''SELECT TIMESTAMP_MILLIS(last_modified_time) FROM
            `{schema_name}.__TABLES__` WHERE TABLE_ID = "{table_name}"'''

    def generate_abort_detached_queries_command(self):
        return "ALTER SESSION SET ABORT_DETACHED_QUERY=TRUE;"

    def generate_number_to_datetime_cast(self, column_name, column_type, **kwargs):
        unit = kwargs.get("unit", "ns")
        unit = unit if unit is not None else "ns"
        if unit == "ns":
            raise make_exception(
                ValueError,
                PonderError.BIGQUERY_DOES_NOT_SUPPORT_FLOAT_DATETIME_CONVERSION,
                "BigQuery does not support nanoseconds.",
            )
        origin = kwargs.get("origin", "unix")
        column_name = self.format_name(column_name)
        if column_type == "float":
            import warnings

            warnings.warn(
                "Truncating nanoseconds since BigQuery does not "
                + "support nanosecond precision."
            )
            if unit == "us":
                column_name = f"CAST(FLOOR({column_name}) as INT64)"
            elif unit in ["s", "ms"]:
                scale = {"s": 1e6, "ms": 1e3}[unit]
                column_name = f"CAST(FLOOR({column_name} * {scale}) as INT64)"
                unit = "us"
        if origin == "unix":
            if unit == "s":
                return f"TIMESTAMP_SECONDS({column_name})"
            elif unit == "ms":
                return f"TIMESTAMP_MILLIS({column_name})"
            elif unit == "us":
                return f"TIMESTAMP_MICROS({column_name})"
        if origin == "unix":
            operand1 = "TIMESTAMP_SECONDS(0)"
        elif isinstance(origin, (int, float)):
            operand1 = f"TIMESTAMP_MILLIS({origin})"
        else:
            operand1 = self.generate_scalar_timestamp_for_subtraction(
                pandas.Timestamp(origin)
            )
        if unit == "D":
            operand2 = f"INTERVAL {column_name} DAY"
        elif unit == "s":
            operand2 = f"INTERVAL {column_name} SECOND"
        elif unit == "ms":
            operand2 = f"INTERVAL {column_name} MILLISECOND"
        else:
            operand2 = f"INTERVAL {column_name} MICROSECOND"
        if unit != "D" or column_type != "float":
            return f"TIMESTAMP_ADD({operand1}, {operand2})"
        else:
            decimal_part = f"({column_name} - FLOOR({column_name}))"
            days = f"FLOOR({column_name})"
            seconds = f"({decimal_part} * 86400)"
            microseconds = f"FLOOR(({seconds} - FLOOR({seconds}))*1e6)"
            plus_days = f"TIMESTAMP_ADD({operand1}, INTERVAL CAST({days} as INT64) DAY)"
            plus_seconds = (
                f"TIMESTAMP_ADD({plus_days}, INTERVAL CAST({seconds} as INT64) SECOND)"
            )
            microseconds = f"CAST({microseconds} AS INT64)"
            return f"TIMESTAMP_ADD({plus_seconds}, INTERVAL {microseconds} MICROSECOND)"

    def generate_casted_columns(
        self, column_names, cast_from_map, cast_to_map, **kwargs
    ):
        ret_column_expressions = []
        for column_name in column_names:
            if column_name in cast_to_map:
                if (
                    isinstance(cast_to_map[column_name], pandas.CategoricalDtype)
                    or cast_to_map[column_name] == "category"
                ):
                    column_expr = self.format_name(column_name)
                else:
                    db_type = self.pandas_type_to_bigquery_type_map[
                        cast_to_map[column_name]
                    ]
                    cast_from_type = cast_from_map[column_name]
                    is_db_type_int = db_type in (
                        "INT",
                        "INT64",
                        "SMALLINT",
                        "INTEGER",
                        "BIGINT",
                        "TINYINT",
                        "BYTEINT",
                    )
                    if cast_from_type == "float" and is_db_type_int:
                        column_expr = (
                            f"CAST(FLOOR({self.format_name(column_name)}) AS {db_type})"
                        )
                    elif cast_from_type == "str" and db_type == "DATETIME":
                        # BigQuery handles the datetime format parsing for us
                        # so we do not need to handle the format kwarg
                        column_expr = (
                            f"CAST({self.format_name(column_name)} AS DATETIME)"
                        )
                    elif cast_from_type in ["float", "int"] and db_type == "DATETIME":
                        column_expr = self.generate_number_to_datetime_cast(
                            column_name, cast_from_type, **kwargs
                        )
                    else:
                        column_expr = (
                            f"CAST({self.format_name(column_name)} AS "
                            + self.pandas_type_to_bigquery_type_map[
                                cast_to_map[column_name]
                            ]
                            + ")"
                        )
            else:
                column_expr = f"{self.format_name(column_name)}"
            ret_column_expressions.append(column_expr)
        return ret_column_expressions

    def generate_truthy_bool_expression(self, column_name, column_type):
        if is_string_dtype(column_type):
            falsy_check = f"LENGTH(TRIM({column_name})) = 0"
        elif is_numeric_dtype(column_type) and not is_bool_dtype(column_type):
            falsy_check = f"{column_name} = 0"
        else:
            falsy_check = f"{column_name} IS FALSE"

        return f"""
            IF({column_name} IS NULL OR {falsy_check}, false, true)
            """

    def generate_reduction_column_transformation(
        self,
        function,
        formatted_col: str,
        percentile=None,
        params_list=None,
        formatted_other_col: str = None,
    ):
        if function in (REDUCE_FUNCTION.SUM, GROUPBY_FUNCTIONS.SUM):
            return f"SUM({formatted_col})"
        elif function is REDUCE_FUNCTION.BOOL_COUNT:
            return f"COUNTIF({formatted_col})"
        elif function in (REDUCE_FUNCTION.COUNT, GROUPBY_FUNCTIONS.COUNT):
            return f"COUNT({formatted_col})"
        elif function is REDUCE_FUNCTION.COUNT_UNIQUE_INCLUDING_NULL:
            return f"ARRAY_LENGTH(ARRAY_AGG(DISTINCT {formatted_col}))"
        elif function is REDUCE_FUNCTION.COUNT_UNIQUE_EXCLUDING_NULL:
            # ARRAY_AGG with IGNORE NULLS filters out nulls, but if the column is all
            # nulls, ARRAY_AGG returns null and ARRAY_LENGTH returns null. pandas
            # considers the count to be 0, not null, in that case.
            return (
                "IFNULL("
                + f"ARRAY_LENGTH(ARRAY_AGG(DISTINCT {formatted_col} IGNORE NULLS)),"
                + "0)"
            )
        elif function is GROUPBY_FUNCTIONS.UNIQUE:
            return f"ARRAY_AGG({formatted_col})"
        elif function in (REDUCE_FUNCTION.MEAN, GROUPBY_FUNCTIONS.MEAN):
            return f"AVG({formatted_col})"
        elif function in (REDUCE_FUNCTION.MEDIAN, GROUPBY_FUNCTIONS.MEDIAN):
            return f"APPROX_QUANTILES({formatted_col}, 100) [OFFSET(50)]"
        elif function is REDUCE_FUNCTION.MODE:
            return f"MODE({formatted_col})"
        elif function in (
            REDUCE_FUNCTION.STANDARD_DEVIATION,
            GROUPBY_FUNCTIONS.STD,
        ):
            return f"STDDEV({formatted_col})"
        elif function is REDUCE_FUNCTION.KURTOSIS:
            return f"KURTOSIS({formatted_col})"
        elif function in (REDUCE_FUNCTION.SEM, GROUPBY_FUNCTIONS.SEM):
            return f"STDDEV({formatted_col})/SQRT(COUNT({formatted_col}))"
        elif function in (REDUCE_FUNCTION.SKEW, GROUPBY_FUNCTIONS.SKEW):
            return f"SKEW({formatted_col})"
        elif function in (REDUCE_FUNCTION.VARIANCE, GROUPBY_FUNCTIONS.VAR):
            return f"VARIANCE({formatted_col})"
        elif function in (REDUCE_FUNCTION.CORR, GROUPBY_FUNCTIONS.CORR):
            return f"CORR({formatted_other_col},{formatted_col})"
        elif function in (REDUCE_FUNCTION.COV, GROUPBY_FUNCTIONS.COV):
            return f"COVAR_SAMP({formatted_other_col},{formatted_col})"
        elif function in (REDUCE_FUNCTION.MIN, GROUPBY_FUNCTIONS.MIN):
            return f"MIN({formatted_col})"
        elif function in (REDUCE_FUNCTION.MAX, GROUPBY_FUNCTIONS.MAX):
            return f"MAX({formatted_col})"
        elif function == GROUPBY_FUNCTIONS.PROD:
            # TODO: Handle cases with zeros POND-825
            # Results in Invalid floating point operation: log(e,0)
            return (
                f"IF(MOD(COUNTIF({formatted_col} < 0), 2) = 0, 1, -1) "
                + f"* EXP(SUM(LN(ABS({formatted_col}))))"
            )
        elif function in (REDUCE_FUNCTION.LOGICAL_OR, GROUPBY_FUNCTIONS.ANY):
            return f"LOGICAL_OR({formatted_col})"
        elif function in (REDUCE_FUNCTION.LOGICAL_AND, GROUPBY_FUNCTIONS.ALL):
            return f"LOGICAL_AND({formatted_col})"
        elif function in (REDUCE_FUNCTION.PERCENTILE, GROUPBY_FUNCTIONS.QUANTILE):
            if percentile is None:
                raise make_exception(
                    RuntimeError,
                    PonderError.BIGQUERY_REDUCE_NODE_MISSING_PERCENTILE,
                    "Reduce node must have a percentile value for the PERCENTILE "
                    + "reduce function.",
                )
            if get_execution_configuration().bigquery_approximate_quantiles:
                warnings.warn("Calculating approximate quantiles")
                return (
                    f"APPROX_QUANTILES({formatted_col}, 100)"
                    + f"[OFFSET(CAST(TRUNC({percentile} * 100) as INT64))]"
                )
            return f"PERCENTILE_CONT({formatted_col}, {percentile}) OVER ()"
        elif function is REDUCE_FUNCTION.STR_CAT:
            if params_list is None:
                raise make_exception(
                    RuntimeError,
                    PonderError.BIGQUERY_STR_CAT_REDUCE_MISSING_PARAMS_LIST,
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
            return (
                f"ARRAY_TO_STRING(ARRAY_AGG(IFNULL({formatted_col},{na_rep})"
                + f" ORDER BY {__PONDER_ORDER_COLUMN_NAME__}),{sep})"
            )
        elif function is GROUPBY_FUNCTIONS.NOOP:
            return formatted_col
        elif function is GROUPBY_FUNCTIONS.SIZE:
            return "COUNT(*)"
        elif function is REDUCE_FUNCTION.CONSTANT_ZERO:
            return "SUM(0)"
        else:
            raise make_exception(
                RuntimeError,
                PonderError.BIGQUERY_COLUMN_WISE_REDUCE_INVALID_FUNCTION,
                "Internal error: cannot execute column-wise reduce function "
                + f"{function}",
            )

    def generate_column_wise_reduce_node_command(
        self,
        function: REDUCE_FUNCTION,
        labels_to_apply_over: list[str],
        input_node_sql: str,
        percentile: Optional[float] = None,
        params_list: Optional[object] = None,
        other_col_id: str = None,
    ) -> str:
        # the reductions should give just one row, but add "MIN(0)" instead of "0" as a
        # hack to get just 1 row even when there are no columns to reduce.
        selects = (
            f"0 AS {__PONDER_ORDER_COLUMN_NAME__}",
            f"0 AS {__PONDER_ROW_LABELS_COLUMN_NAME__}",
        )
        formatted_other_col = None
        if other_col_id is not None:
            # Special case to add columns that will later become an index
            other_col = labels_to_apply_over[other_col_id]
            formatted_other_col = self.format_name(other_col)
            selects = (
                *selects,
                f"MIN({other_col_id}) AS {__PONDER_AGG_OTHER_COL_ID__}",
                f"MIN('{other_col}') AS {__PONDER_AGG_OTHER_COL_NAME__}",
            )
        selects = (
            *selects,
            *(
                f"""
            {self.generate_reduction_column_transformation(function,
                self.format_name(col),
                percentile=percentile,
                params_list=params_list,
                formatted_other_col=formatted_other_col)}
            AS {self.format_name(col)}
            """
                for col in labels_to_apply_over
            ),
        )
        return f"SELECT {', '.join(selects)} FROM ({input_node_sql}) LIMIT 1"

    def generate_row_wise_reduce_node_command(
        self,
        input_column_names: list[str],
        input_column_types,
        function: REDUCE_FUNCTION,
        input_node_sql: str,
        order_and_labels_column_strings: str,
        result_column_name: str,
    ) -> str:
        # All column references in an array need to be of a common subclass
        # in GBQ. If they are all numeric we want to keep them that way.
        # otherwise we have to turn them into strings to be compared. Some
        # operations, such as nunique do not work well with this approach.
        all_numeric = all(is_numeric_dtype(t) for t in input_column_types)
        if all_numeric:
            cols = ",".join(self.format_names_list(input_column_names))
        else:
            if (
                function == REDUCE_FUNCTION.COUNT_UNIQUE_EXCLUDING_NULL
                or function == REDUCE_FUNCTION.COUNT_UNIQUE_INCLUDING_NULL
            ):
                raise make_exception(
                    NotImplementedError,
                    PonderError.BIGQUERY_NUNIQUE_AXIS1_MIXED_TYPES_NOT_IMPLEMENTED,
                    "BigQuery does not support row-wise nunique with mixed types",
                )

            cols = ",".join(
                [
                    f"CAST({self.format_name(name)} AS STRING)"
                    for name in input_column_names
                ]
            )
        if function is REDUCE_FUNCTION.COUNT_UNIQUE_INCLUDING_NULL:
            function_call = (
                f"ARRAY_LENGTH(ARRAY(SELECT DISTINCT X FROM UNNEST([{cols}]) AS X))"
            )
        elif function is REDUCE_FUNCTION.COUNT_UNIQUE_EXCLUDING_NULL:
            function_call = (
                f"ARRAY_LENGTH(ARRAY(SELECT DISTINCT X FROM UNNEST([{cols}]) AS X"
                + " WHERE X IS NOT NULL))"
            )
        elif function is REDUCE_FUNCTION.MIN:
            function_call = f"LEAST({cols})"
        elif function is REDUCE_FUNCTION.MAX:
            function_call = f"GREATEST({cols})"
        elif function is REDUCE_FUNCTION.SUM:
            function_call = " + ".join(self.format_names_list(input_column_names))
        else:
            raise make_exception(
                ValueError,
                PonderError.BIGQUERY_ROW_WISE_REDUCE_INVALID_FUNCTION,
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
        for value in values:
            # if the value translates to null in sql for this column type, tell bigquery
            # to look for null.
            if is_numeric_dtype(column_type):
                if value is np.nan:
                    value_strings.append("NULL")
                    continue
            elif is_datetime64_any_dtype(column_type):
                if value is pandas.NaT:
                    value_strings.append("NULL")
                    continue
            elif value is None:
                value_strings.append("NULL")
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
                    PonderError.BIGQUERY_ISIN_COLLECTION_UNSUPPORTED_VALUE,
                    f"Cannot apply isin to value {value} of type "
                    + f"{type(value).__name__}",
                )
        # isin(empty_list) is false in pandas. I think "IN" didn't work for that in
        # bigquery.
        if len(value_strings) == 0:
            return "FALSE"
        json_string_values = [f"TO_JSON_STRING({v})" for v in value_strings]
        return (
            f"TO_JSON_STRING({self.format_name(column_name)}) IN "
            + f"({', '.join(json_string_values)})"
        )

    def generate_dataframe_isin_series(
        self,
        column_name,
    ):
        return (
            f"{self.format_name(column_name)} IS NOT NULL AND "
            + f"TO_JSON_STRING({self.format_name(column_name)}) = "
            + f"TO_JSON_STRING({self.format_name(__ISIN_SERIES_VALUES_COLUMN_NAME__)})"
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
            EXTRACT(MICROSECOND FROM {datetime_expression}) +
            1000000 * (
                60 * 60 * EXTRACT(HOUR FROM {datetime_expression}) +
                60 * EXTRACT(MINUTE FROM {datetime_expression}) +
                EXTRACT(SECOND FROM {datetime_expression})
            )"""

        start_compare_time_maybe_timezone_adjusted = time_micros(
            f"TIMESTAMP(DATETIME({formatted_index_name}, 'UTC'))"
            if compare_start_to_utc_time
            else formatted_index_name
        )
        end_compare_time_maybe_timezone_adjusted = time_micros(
            f"TIMESTAMP(DATETIME({formatted_index_name}, 'UTC'))"
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

    def generate_union_all_query(
        self,
        node_data_list: list[UnionAllDataForDialect],
        column_names,
        row_labels_column_names,
        order_column_name,
        new_dtypes,
    ):
        # for now the only casting is UNION is to cast to VARIANT if column c has non-
        # object dtype A in one subquery, and the caller of this function wants column
        # to be of dtype object after the union. this covers cases where we union a
        # string column with a numeric column and the resulting column must have both
        # strings and numbers, e.g. when we union a subquery with the integer count of a
        # string column with a subquery with the string mode of that column in
        # implementing `pandas.DataFrame.describe`.
        # TODO(FIX[POND-823]): Implement and test more general mixed type concats.
        # we may need to e.g. figure out how to downcast appropriately when we combine
        # an int and a string in a column. For now we just upcast to VARIANT in a
        # particular case.
        #
        # If we're going to cast anything in a column to VARIANT, we have to cast
        # everything in that column to variant. Otherwise we get SQL compilation error
        # like "inconsistent data type for result columns for set operator input
        # branches, expected VARCHAR(16777216), got VARIANT for expression [{2}] branch
        # {3}"
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
            # https://docs.snowflake.com/en/sql-reference/operators-query.html#general-usage-notes
            node_column_names_set = set(node.dtypes.keys())
            final_column_names_set = set(column_names)
            if node_column_names_set != final_column_names_set:
                raise make_exception(
                    RuntimeError,
                    PonderError.BIGQUERY_UNION_ALL_COLUMN_NAME_MISMATCH,
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
                        {self.format_name(c)}::VARIANT AS
                        {self.format_name(c)}
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

    def generate_groupby_head_predicate(self, by, order_column, n):
        # If we have a negative number, we have enumerate in the
        # other direction.
        if n < 0:
            return f"""
                QUALIFY
                    ROW_NUMBER() OVER (
                        PARTITION BY {by}
                        ORDER BY {order_column} DESC
                    ) > {abs(n)}
                """
        return f"""
                QUALIFY
                    ROW_NUMBER() OVER (
                        PARTITION BY {by}
                        ORDER BY {order_column} ASC
                    ) <= {n}
                """

    def generate_groupby_tail_predicate(self, by, order_column, n):
        if n < 0:
            return f"""
                QUALIFY
                    ROW_NUMBER() OVER (
                        PARTITION BY {by}
                        ORDER BY {order_column} ASC
                    ) > {abs(n)}
                """
        return f"""
                QUALIFY
                    ROW_NUMBER() OVER (
                        PARTITION BY {by}
                        ORDER BY {order_column} DESC
                    ) <= {n}
                """

    def generate_row_value_not_equals_predicate(
        self, column_name: str, values: Iterable
    ) -> str:
        return f"""
            WHERE {self.format_name(column_name)} NOT IN (
                {', '.join(map(str, values))})
            """

    def generate_row_value_equals_group_by_key_predicate(
        self, by_columns: Iterable, lookup_key: Iterable
    ):
        # by_columns and lookup_key have to match in order
        predicates = []
        for by, key in zip(by_columns, lookup_key):
            predicates.append(f"{self.format_name(by)} = {self.format_value(key)}")

        return f"""
            WHERE
                {" AND ".join(predicates)}
        """

    def generate_column_is_min_predicate(self, column_name, by_columns):
        if by_columns:
            keys = ",".join(self.format_names_list(by_columns))
            partition_by_clause = f"PARTITION BY {keys}"
        else:
            partition_by_clause = ""
        formatted_column_name = self.format_name(column_name)
        return f"""
            QUALIFY {formatted_column_name} = MIN({formatted_column_name})
                                                OVER ({partition_by_clause})
        """

    def generate_column_is_max_predicate(self, column_name, by_columns):
        if by_columns:
            keys = ",".join(self.format_names_list(by_columns))
            partition_by_clause = f"PARTITION BY {keys}"
        else:
            partition_by_clause = ""
        formatted_column_name = self.format_name(column_name)
        return f"""
            QUALIFY {formatted_column_name} = MAX({formatted_column_name})
                                                OVER ({partition_by_clause})
        """

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
                    IF(
                        (
                            SELECT COUNT({self.format_name(col)})
                            FROM INNER_QUERY{where_clause}
                        ) >= {thresh},
                        TRUE,
                        FALSE
                    ) AS {self.format_name(col)}
                    """
                    for col in columns
                )
            )
        elif how == "any":
            columns_selection = ", ".join(
                f"""
                    IF(
                        (
                            SELECT COUNTIF({self.format_name(col)} IS NULL)
                            FROM INNER_QUERY{where_clause}
                        ) = 0,
                        TRUE,
                        FALSE
                    ) AS {self.format_name(col)}
                    """
                for col in columns
            )
        else:
            columns_selection = ", ".join(
                (
                    f"""
                        IF(
                            (
                                SELECT COUNT({self.format_name(col)})
                                FROM INNER_QUERY{where_clause}
                            ) = 0,
                            FALSE,
                            TRUE
                        ) AS {self.format_name(col)}
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
                f"IF({self.format_name(col)} IS NULL, 0, 1)" for col in columns
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

    def _generate_dates_within_offset_of_min_or_max_predicate(
        self,
        column_name: str,
        offset: pandas.DateOffset,
        min: bool,
    ):
        n, sql_unit = _pandas_offset_object_to_n_and_sql_unit(offset)
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

        diff_func = (
            "TIMESTAMP_DIFF" if sql_unit in ("minute", "second") else "DATE_DIFF"
        )

        return f"""
            QUALIFY {diff_func}(
                {diff_arg2},
                {diff_arg1},
                {sql_unit.upper()}
            ) < {n}
        """

    def generate_dates_within_offset_of_min_predicate(
        self, column_name: str, offset: pandas.DateOffset
    ):
        return self._generate_dates_within_offset_of_min_or_max_predicate(
            column_name, offset, min=True
        )

    def generate_dates_within_offset_of_max_predicate(
        self, column_name: str, offset: pandas.DateOffset
    ):
        return self._generate_dates_within_offset_of_min_or_max_predicate(
            column_name, offset, min=False
        )

    def generate_dt_nanosecond(self, params_list):
        # BigQuery does not track nanoseconds.
        return "0"

    def generate_dt_microsecond(self, params_list):
        col_name_quoted = params_list[0]
        return f"EXTRACT(MICROSECOND FROM CAST({col_name_quoted} AS TIMESTAMP))"

    def generate_dt_second(self, params_list):
        col_name_quoted = params_list[0]
        return f"EXTRACT(SECOND FROM CAST({col_name_quoted} AS TIMESTAMP))"

    def generate_dt_minute(self, params_list):
        col_name_quoted = params_list[0]
        return f"EXTRACT(MINUTE FROM CAST({col_name_quoted} AS TIMESTAMP))"

    def generate_dt_hour(self, params_list):
        col_name_quoted = params_list[0]
        return f"EXTRACT(HOUR FROM CAST({col_name_quoted} AS TIMESTAMP))"

    def generate_dt_day(self, params_list):
        col_name_quoted = params_list[0]
        return f"EXTRACT(DAY FROM CAST({col_name_quoted} AS TIMESTAMP))"

    def generate_dt_dayofweek(self, params_list):
        col_name_quoted = params_list[0]
        # ISO-standard has Monday as 1, BigQuery has Sunday as 1, thus we
        # do some modulo math to get it to wrap around correctly
        return f"""MOD(
                    EXTRACT(
                        DAYOFWEEK FROM CAST({col_name_quoted} AS TIMESTAMP)
                    ) + 5, 7)"""

    def generate_dt_day_name(self, params_list):
        col_name_quoted = params_list[0]
        return f"FORMAT_TIMESTAMP('%A', CAST({col_name_quoted} AS TIMESTAMP))"

    def generate_dt_dayofyear(self, params_list):
        col_name_quoted = params_list[0]
        return f"EXTRACT(DAYOFYEAR FROM CAST({col_name_quoted} AS TIMESTAMP))"

    def generate_dt_week(self, params_list):
        col_name_quoted = params_list[0]
        return f"EXTRACT(ISOWEEK FROM CAST({col_name_quoted} AS TIMESTAMP))"

    def generate_dt_month(self, params_list):
        col_name_quoted = params_list[0]
        return f"EXTRACT(MONTH FROM CAST({col_name_quoted} AS TIMESTAMP))"

    def generate_dt_month_name(self, params_list):
        col_name_quoted = params_list[0]
        return f"FORMAT_TIMESTAMP('%B', CAST({col_name_quoted} AS TIMESTAMP))"

    def generate_dt_quarter(self, params_list):
        col_name_quoted = params_list[0]
        return f"EXTRACT(QUARTER FROM CAST({col_name_quoted} AS TIMESTAMP))"

    def generate_dt_year(self, params_list):
        col_name_quoted = params_list[0]
        return f"EXTRACT(YEAR FROM CAST({col_name_quoted} AS TIMESTAMP))"

    def generate_dt_tz_convert(self, params_list):
        col_name_quoted, tz = params_list

        return (
            f"TIMESTAMP(DATETIME({col_name_quoted}), 'UTC')"
            if tz is None
            else (
                f"TIMESTAMP(DATETIME({col_name_quoted}, "
                f"{self.format_value(tz)}),{self.format_value(tz)})"
            )
        )

    def generate_dt_tz_localize(self, params_list):
        col_name_quoted, tz = params_list
        return (
            f"TIMESTAMP({col_name_quoted})"
            if tz is None
            else f"""TIMESTAMP({col_name_quoted}, {self.format_value(tz)})"""
        )

    def generate_str_center(self, params_list):
        col_name_quoted, width, fillchar = params_list
        return f"""
        RPAD(
            LPAD(
                {col_name_quoted},
                GREATEST(
                    LENGTH({col_name_quoted}),
                    (
                        LENGTH({col_name_quoted}) +
                        CAST(
                            CEIL(({width} - LENGTH({col_name_quoted}) - 1) / 2)
                            AS INT64
                        )
                    )
                ),
                '{fillchar}'
            ),
            GREATEST(
                LENGTH({col_name_quoted}),
                {width}
            ),
            '{fillchar}'
        )
        """

    def generate_str_contains(self, params_list):
        col_name_quoted, pat, case, flags, na, regex = params_list
        if not regex and case:
            if pandas.isnull(na):
                exp = f"({col_name_quoted} LIKE '{pat}')"
            else:
                exp = f"IFNULL(({col_name_quoted} LIKE '{pat}'),{na})"
        else:
            pat = f"CONCAT('.*',REPLACE('{pat}','.','\\\\.'),'.*')"
            if not case or (regex and (flags & re.IGNORECASE != 0)):
                col_name_quoted = f"UPPER({col_name_quoted})"
                pat = f"UPPER({pat})"
            if pandas.isnull(na):
                exp = f"REGEXP_CONTAINS({col_name_quoted},{pat})"
            else:
                exp = f"IFNULL(REGEXP_CONTAINS({col_name_quoted},{pat}),{na})"
        return exp

    def generate_str_count(self, params_list):
        col_name_quoted, pat, flags = tuple(params_list)
        if flags & re.IGNORECASE != 0:
            col_name_quoted = f"UPPER({col_name_quoted})"
            pat = f"UPPER('{pat}')"
        else:
            pat = f"'{pat}'"
        exp = f"ARRAY_LENGTH(REGEXP_EXTRACT_ALL({col_name_quoted},{pat}))"
        return exp

    def generate_str_decode(self, params_list):
        col_name_quoted, encoding, errors = tuple(params_list)
        pat = re.compile("^utf[ _\\-]*8")
        if encoding.lower() == "ascii" or pat.fullmatch(encoding.lower()):
            encoding = "utf-8"
        if encoding != "utf-8":
            raise make_exception(
                NotImplementedError,
                PonderError.BIGQUERY_STR_DECODE_UNSUPPORTED_ENCODING,
                "str.decode() only supports 'ascii' and 'utf-8' encodings currently",
            )
        exp = f"CAST({col_name_quoted} AS STRING)"
        return exp

    def generate_str_encode(self, params_list):
        col_name_quoted, encoding, errors = tuple(params_list)
        pat = re.compile("^utf[ _\\-]*8")
        if encoding.lower() == "ascii" or pat.fullmatch(encoding.lower()):
            encoding = "utf8"
        if encoding != "utf8":
            raise make_exception(
                NotImplementedError,
                PonderError.BIGQUERY_STR_ENCODE_UNSUPPORTED_ENCODING,
                "str.encode() only supports 'ascii' and 'utf-8' encodings currently",
            )
        exp = f"CAST({col_name_quoted} AS BYTES)"
        return exp

    def generate_str_endswith(self, params_list):
        col_name_quoted, pat, na = params_list
        pat = f"%{pat}"
        if pandas.isnull(na):
            exp = f"({col_name_quoted} LIKE '{pat}')"
        else:
            exp = f"IFNULL({col_name_quoted} LIKE '{pat}',{na})"
        return exp

    def generate_str_extract(self, column_name, pat, flags):
        if re.compile(pat).groups > 1:
            # REGEXP_EXTRACT and REGEXP_EXTRACT_ALL throw an error if the regex has > 1
            # capturing group
            # TODO: Maybe we could parse the regex with sre_parse, then create a
            # separate regex with one capturing group to capture each group?
            raise make_exception(
                NotImplementedError,
                PonderError.BIGQUERY_REGEX_EXTRACT_MULTIPLE_GROUPS_NOT_SUPPORTED,
                "str.extract() with multiple groups is not supported on bigquery",
            )
        col_name_quoted = self.format_name(column_name)
        pat = f"""(?{"i" if (flags & re.IGNORECASE) != 0 else ""}:{pat})"""
        return [
            f"""REGEXP_EXTRACT(
                {col_name_quoted},
                {self.format_value(pat)}
            )"""
        ]

    def generate_str_find(self, params_list):
        col_name_quoted, sub, start, end = tuple(params_list)
        if start < 0:
            start_str = f"(GREATEST({start}+LENGTH({col_name_quoted}),0)+1)"
        else:
            start_str = f"{max(start,0)+1}"
        if end is None:
            exp = f"STRPOS(SUBSTR({col_name_quoted},{start_str}),'{sub}')"
        else:
            if end < 0:
                end_str = f"GREATEST({end}+LENGTH({col_name_quoted}),0)"
            else:
                end_str = f"(LEAST(LENGTH({col_name_quoted}),{end}))"
            exp = f"""
                STRPOS(
                    SUBSTR(
                        {col_name_quoted},
                        {start_str},
                        GREATEST({end_str} - {start_str}+1,0)
                    ),
                    '{sub}'
                )
            """
        exp = f"IF({exp}=0,-1,{exp}+{start_str}-2)"
        return exp

    def generate_str_findall(self, params_list):
        col_name_quoted, pat, flags = params_list
        if flags & re.IGNORECASE != 0:
            col_name_quoted = f"UPPER({col_name_quoted})"
            pat = f"UPPER('{pat}')"
        else:
            pat = f"'{pat}'"
        exp = f"REGEXP_EXTRACT_ALL({col_name_quoted},{pat})"
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
            return f"REGEXP_CONTAINS({col_name_quoted},{pat})"
        return f"IFNULL(REGEXP_CONTAINS({col_name_quoted},{pat}),{na})"

    def generate_str_get(self, params_list):
        col_name_quoted, i = params_list
        # Need to cast to keep SQL compiler happy
        col_name_quoted = f"TO_JSON({col_name_quoted})"
        if i >= 0:
            str_exp = f"SUBSTR(JSON_VALUE({col_name_quoted}),{i+1},1)"
            arr_exp = f"JSON_VALUE_ARRAY({col_name_quoted})[SAFE_OFFSET({i})]"
        else:
            str_exp = f"""SUBSTR(JSON_VALUE({col_name_quoted}),
                                {i+1}+LENGTH(JSON_VALUE({col_name_quoted})),1)"""
            arr_exp = f"""
            IF({abs(i)} > ARRAY_LENGTH(JSON_VALUE_ARRAY({col_name_quoted})),
                NULL,
                JSON_VALUE_ARRAY({col_name_quoted})[
                    SAFE_OFFSET(
                        ARRAY_LENGTH(JSON_VALUE_ARRAY({col_name_quoted}))-{abs(i)}
                    )
                ]
            )
            """
        str_exp = f"IF({str_exp}='',NULL,{str_exp})"
        return f"IF(JSON_TYPE({col_name_quoted})='string',{str_exp},{arr_exp})"

    def generate_str_join(self, params_list):
        col_name_quoted, sep = params_list
        exp1 = f"ARRAY_TO_STRING([{col_name_quoted}],'{sep}')"
        exp2 = f"""
            CONCAT(
                REGEXP_REPLACE(
                    SUBSTR(
                        {col_name_quoted},
                        1,
                        LENGTH({col_name_quoted})-1
                    ),
                    '(.)','\\\\1{sep}'
                ),
                SUBSTR({col_name_quoted}, LENGTH({col_name_quoted}))
            )"""
        exp = f"IF(IS_ARRAY(TO_VARIANT({col_name_quoted})),{exp1},{exp2})"
        return exp

    def generate_str_ljust(self, params_list):
        col_name_quoted, width, fillchar = params_list
        exp = f"""
            RPAD(
                {col_name_quoted},
                GREATEST(
                    LENGTH({col_name_quoted}),
                    {width}
                ),
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
            exp = f"REGEXP_CONTAINS({col_name_quoted},{pat})"
        else:
            exp = f"IFNULL(REGEXP_CONTAINS({col_name_quoted},{pat}),{na})"
        return exp

    # Unlike most other string functions, this method returns a list of strings because
    # it takes one column as input and returns three columns as output, each requiring
    # its own SQL expression.
    def generate_str_partition(self, column_name, sep, expand):
        col_name_quoted = self.format_name(column_name)
        sep_start = f"STRPOS({col_name_quoted},'{sep}')"
        if len(sep) == 1:
            sep_end = sep_start
        else:
            sep_end = f"{sep_start}+{len(sep)-1}"
        pre_sep = f"{sep_start}-1"
        post_sep = f"{sep_start}+{len(sep)}"
        part1 = f"SUBSTR({col_name_quoted},1,{pre_sep})"
        part2 = f"SUBSTR({col_name_quoted},{sep_start},{len(sep)})"
        part3 = (
            f"SUBSTR({col_name_quoted},{post_sep},LENGTH({col_name_quoted})-{sep_end})"
        )
        if expand:
            return [
                f"IF({col_name_quoted} IS NULL,NULL,{part1})",
                f"IF({col_name_quoted} IS NULL,NULL,{part2})",
                f"IF({col_name_quoted} IS NULL,NULL,{part3})",
            ]
        return [
            f"""
                IF(
                    {col_name_quoted} IS NULL,
                    NULL,
                    [{part1},{part2},{part3}]
                )
            """
        ]

    def generate_str_removeprefix(self, params_list):
        col_name_quoted, prefix = params_list
        exp = f"""
                IF(
                    SUBSTR({col_name_quoted},1,{len(prefix)})='{prefix}',
                    SUBSTR({col_name_quoted},{len(prefix)+1}),
                    {col_name_quoted}
                )
            """
        return exp

    def generate_str_removesuffix(self, params_list):
        col_name_quoted, suffix = params_list
        exp = f"""
                IF(
                    SUBSTR(
                        {col_name_quoted},
                        LENGTH({col_name_quoted})-{len(suffix)}+1
                    )='{suffix}',
                    SUBSTR({col_name_quoted},1,LENGTH({col_name_quoted})-{len(suffix)}),
                    {col_name_quoted}
                )
            """
        return exp

    def generate_str_repeat(self, params_list):
        col_name_quoted, repeats = params_list
        if repeats <= 0:
            exp = "''"
        else:
            exp = f"REPEAT({col_name_quoted},{repeats})"
        exp = f"IF({col_name_quoted} IS NULL,NULL,{exp})"
        return exp

    def generate_str_replace(self, params_list):
        col_name_quoted, pat, repl, n, case, flags, regex = params_list
        if callable(repl):
            raise make_exception(
                NotImplementedError,
                PonderError.BIGQUERY_STR_REPLACE_CALLABLE_REPL,
                "str.replace() does not support callable `repl` param yet",
            )
        if isinstance(pat, Pattern):
            raise make_exception(
                NotImplementedError,
                PonderError.BIGQUERY_STR_REPLACE_COMPILED_REGEX,
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
                exp = f"REGEXP_REPLACE({col_name_quoted},{pat},'{repl}')"
            else:
                split_idx = f"""
                        IF(
                            REGEXP_INSTR({col_name_quoted},{pat},1,1,1)=0,
                            0,
                            IF(
                                REGEXP_INSTR({col_name_quoted},{pat},1,{n},1)=0,
                                LENGTH({col_name_quoted})+1,
                                REGEXP_INSTR({col_name_quoted},{pat},1,{n},1)
                            )-1
                        )
                    """
                exp = f"""
                        CONCAT(
                            REGEXP_REPLACE(
                                SUBSTR({col_name_quoted},1,{split_idx}),
                                {pat},
                                '{repl}'
                            ),
                            SUBSTR({col_name_quoted},{split_idx}+1)
                        )
                    """
        else:
            exp = f"REPLACE({col_name_quoted},'{pat}','{repl}')"
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
                end_str = f"(GREATEST({end}+LENGTH({col_name_quoted}),0)+1)"
            else:
                end_str = f"(LEAST(LENGTH({col_name_quoted}),{end})+1)"
        exp = f"""
        IF(
            {start_str} > LENGTH({col_name_quoted}) OR
            STRPOS(
                REVERSE(
                    SUBSTR(
                        {col_name_quoted},
                        {start_str},
                        GREATEST({end_str} - {start_str},0)
                    )
                ),
                '{sub}'
            ) = 0,
            -1,
            {end_str} - STRPOS(
                REVERSE(
                    SUBSTR(
                        {col_name_quoted},
                        {start_str},
                        GREATEST({end_str} - {start_str},0)
                    )
                ),
                '{sub}'
            ) - 1
        )
        """
        return exp

    generate_str_rindex = generate_str_rfind

    def generate_str_rjust(self, params_list):
        col_name_quoted, width, fillchar = params_list
        exp = f"""
        LPAD(
            {col_name_quoted},
            GREATEST(
                LENGTH({col_name_quoted}),
                {width}
            ),
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
                    LENGTH({col_name_quoted})-STRPOS(
                        REVERSE({col_name_quoted}),
                        '{sep[::-1]}'
                    )+1
                )
            """
        if len(sep) == 1:
            sep_start = sep_end
        else:
            sep_start = f"{sep_end}-{len(sep)-1}"
        pre_sep = f"{sep_end}-{len(sep)}"
        post_sep = f"{sep_start}+1"
        part1 = f"SUBSTR({col_name_quoted},1,{pre_sep})"
        part2 = f"SUBSTR({col_name_quoted},{sep_start},{len(sep)})"
        part3 = (
            f"SUBSTR({col_name_quoted},{post_sep},LENGTH({col_name_quoted})-{sep_end})"
        )
        if expand:
            return [
                f"IF({col_name_quoted} IS NULL,NULL,{part1})",
                f"IF({col_name_quoted} IS NULL,NULL,{part2})",
                f"IF({col_name_quoted} IS NULL,NULL,{part3})",
            ]
        return [
            f"""
                IF(
                    {col_name_quoted} IS NULL,
                    NULL,
                    [{part1},{part2},{part3}]
                )
            """
        ]

    def generate_str_rsplit(self, params_list):
        col_name_quoted, pat, n, expand = params_list
        if pat is None:
            regex_pat = f"'[ \t\r\n]+'"  # noqa F541
            regex_pat_extended = f"'.*[ \t\r\n]+'"  # noqa F541
            exp = f"REGEXP_REPLACE(TRIM({col_name_quoted},{regex_pat}),{regex_pat},' ')"
            pat = " "
            n_for_split_idx = (
                f"IF(REGEXP_CONTAINS({col_name_quoted},{regex_pat_extended}),{n+1},{n})"
            )
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
            IF({n+1} > ARRAY_LENGTH(SPLIT({exp},'{pat}')),
                SPLIT({exp},'{pat}'),
                ARRAY_CONCAT(
                    [SUBSTR(
                        {col_name_quoted},
                        1,
                        {split_idx}
                    )],
                    ARRAY(
                        SELECT X[SAFE_OFFSET(index)]
                        FROM
                            (SELECT SPLIT({exp},'{pat}') AS X)
                        CROSS JOIN
                            UNNEST(
                                GENERATE_ARRAY(
                                    0,
                                    ARRAY_LENGTH(SPLIT({exp},'{pat}')) - 1
                                )
                            ) AS index
                        WHERE index > ARRAY_LENGTH(SPLIT({exp},'{pat}')) - {n}
                    )
                )
            )
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
            stop_str = f"(LEAST(LENGTH({column_name_quoted}),{stop})+1)"
        if step is None or step == 1:
            exp = f"SUBSTR({column_name_quoted},{start_str},{stop_str}-{start_str})"
        else:
            if start * stop < 0 or stop is None:
                raise make_exception(
                    NotImplementedError,
                    PonderError.BIGQUERY_STR_SLICE_UNSUPPORTED_START_STOP_STEP_COMBINATION,  # noqa: E501
                    "str.slice() does not support step > 1 along with (a) no stop, "
                    + "or (b) start and stop with different signs",
                )
            n = int((stop - start) / step)
            exp = f"CONCAT("  # noqa F541
            for i in range(n):
                exp = f"{exp}SUBSTR({column_name_quoted},{start_str}+{i*step},1)"
                if i < n - 1:
                    exp = f"{exp},"
            exp = f"{exp})"
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
            stop_str = f"(LEAST(LENGTH({column_name_quoted}),{stop})+1)"
        if repl is None:
            repl = ""
        exp = f"""
        CONCAT(
            SUBSTR(
                {column_name_quoted},
                1,
                {start_str} - 1
            ),
            '{repl}',
            SUBSTR(
                {column_name_quoted},
                {stop_str}
            )
        )"""
        return exp

    def generate_str_split(self, params_list):
        col_name_quoted, pat, n, expand = params_list
        if pat is None:
            regex_pat = f"'[ \t\r\n]+'"  # noqa F541
            regex_pat_extended = f"'[ \t\r\n]+.*'"  # noqa F541
            exp = f"REGEXP_REPLACE(TRIM({col_name_quoted},{regex_pat}),{regex_pat},' ')"
            pat = " "
            n_for_split_idx = (
                f"IF(REGEXP_CONTAINS({col_name_quoted},{regex_pat_extended}),{n+1},{n})"
            )
        else:
            regex_pat = f"'{pat}'"
            exp = f"{col_name_quoted}"  # noqa F541
            n_for_split_idx = n
        if n <= 0:
            exp = f"SPLIT({exp},'{pat}')"
        else:
            split_idx = (
                f"REGEXP_INSTR({col_name_quoted},{regex_pat},1,{n_for_split_idx},1)"
            )
            exp = f"""
            IF({n+1} > ARRAY_LENGTH(SPLIT({exp},'{pat}')),
                SPLIT({exp},'{pat}'),
                ARRAY_CONCAT(
                    ARRAY(
                        SELECT X[SAFE_OFFSET(index)]
                        FROM
                            (SELECT SPLIT({exp},'{pat}') AS X)
                        CROSS JOIN
                            UNNEST(
                                GENERATE_ARRAY(
                                    0,
                                    ARRAY_LENGTH(SPLIT({exp},'{pat}')) - 1
                                )
                            ) AS index
                        WHERE index < {n}
                    ),
                    [SUBSTR(
                        {col_name_quoted},
                        {split_idx}
                    )]
                )
            )"""
        return exp

    def generate_str_startswith(self, params_list):
        col_name_quoted, pat, na = params_list
        pat = f"{pat}%"
        if pandas.isnull(na):
            exp = f"({col_name_quoted} LIKE '{pat}')"
        else:
            exp = f"IFNULL({col_name_quoted} LIKE '{pat}',{na})"
        return exp

    def generate_str_wrap(self, params_list):
        col_name_quoted, width = params_list
        exp = f"""
                IF(
                    MOD(LENGTH({col_name_quoted}),{width})=0,
                    SUBSTR(REGEXP_REPLACE(
                        {col_name_quoted},
                        '(.{{{{{width}}}}})',
                        '\\\\1\\n'),
                        1,
                        CAST(FLOOR(LENGTH({col_name_quoted})*(1+1/{width})-1) AS INT64
                    )),
                    REGEXP_REPLACE({col_name_quoted},'(.{{{{{width}}}}})','\\\\1\\n')
                )
            """
        return exp

    def generate_str_capitalize(self, params_list):
        col_name_quoted = params_list[0]
        return f"""
        CONCAT(
            UPPER(
                SUBSTR(
                    {col_name_quoted},
                    1,
                    1
                )
            ),
            LOWER(
                SUBSTR(
                    {col_name_quoted},
                    2
                )
            )
        )"""

    def generate_str_isalnum(self, params_list):
        col_name_quoted = params_list[0]
        return f"""
            IF(
                {col_name_quoted} IS NULL,
                NULL,
                REGEXP_CONTAINS({col_name_quoted},'^[a-zA-Z0-9]+$')
            )
        """

    def generate_str_isalpha(self, params_list):
        col_name_quoted = params_list[0]
        return f"""
            IF(
                {col_name_quoted} IS NULL,
                NULL,
                REGEXP_CONTAINS({col_name_quoted},'^[a-zA-Z]+$')
            )
        """

    def generate_str_isdecimal(self, params_list):
        col_name_quoted = params_list[0]
        return f"""
            IF(
                {col_name_quoted} IS NULL,
                NULL,
                REGEXP_CONTAINS({col_name_quoted},'^[0-9]+$')
            )
        """

    def generate_str_isdigit(self, params_list):
        col_name_quoted = params_list[0]
        return f"""
            IF(
                {col_name_quoted} IS NULL,
                NULL,
                REGEXP_CONTAINS({col_name_quoted},'^[0-9]+$'))
        """

    def generate_str_islower(self, params_list):
        col_name_quoted = params_list[0]
        return f"""
            IF(
                {col_name_quoted} IS NULL,
                NULL,
                REGEXP_CONTAINS(
                    {col_name_quoted},
                    '.*[a-zA-Z]+.*'
                ) AND
                {col_name_quoted} = LOWER({col_name_quoted})
            )
        """

    def generate_str_isnumeric(self, params_list):
        col_name_quoted = params_list[0]
        return f"""
            IF(
                {col_name_quoted} IS NULL,
                NULL,
                REGEXP_CONTAINS({col_name_quoted},'^[0-9]+$')
            )
        """

    def generate_str_istitle(self, params_list):
        col_name_quoted = params_list[0]
        return f"""
            IF(
                {col_name_quoted} IS NULL,
                NULL,
                REGEXP_CONTAINS(
                    {col_name_quoted},
                    '^.*[a-zA-Z]+.*$'
                ) AND
                {col_name_quoted} = INITCAP({col_name_quoted})
            )
        """

    def generate_str_isupper(self, params_list):
        col_name_quoted = params_list[0]
        return f"""
            IF(
                {col_name_quoted} IS NULL,
                NULL,
                REGEXP_CONTAINS({col_name_quoted}, '^.*[a-zA-Z]+.*$') AND
                {col_name_quoted} = UPPER({col_name_quoted})
            )
        """

    def generate_new_row_labels_columns_command(
        self, new_row_label_column_names, column_names, input_node_sql, new_row_labels
    ):
        if len(new_row_label_column_names) > 1:
            raise make_exception(
                NotImplementedError,
                PonderError.BIGQUERY_NEW_ROW_LABELS_MULTIPLE_COLUMNS,
                "Ponder Internal Error: cannot create multiindex from python objects",
            )
        new_row_label_column_name = new_row_label_column_names[0]
        left_formatted_column_names = ", ".join(
            f"LEFT_TABLE.{self.format_name(col)}" for col in column_names
        )
        return f"""
            SELECT
                LEFT_TABLE.{__PONDER_ORDER_COLUMN_NAME__},
                RIGHT_TABLE.{new_row_label_column_name}, {left_formatted_column_names}
            FROM ({input_node_sql}) AS LEFT_TABLE
            INNER JOIN (
                SELECT
                    _ROW_ORDER_VALS_,
                    {new_row_label_column_name}
                FROM
                   UNNEST([STRUCT<_ROW_ORDER_VALS_ INT64,
                        {new_row_label_column_name}
                        {self.pandas_type_to_bigquery_type_map[
                            type(list(new_row_labels.values())[0]).__name__]}>
                        {", ".join(str((k, v)) for k,
                        v in new_row_labels.items())}])
            ) AS RIGHT_TABLE
            ON LEFT_TABLE.{__PONDER_ORDER_COLUMN_NAME__} = RIGHT_TABLE._ROW_ORDER_VALS_
        """

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
                f"""IF(
                        EQUAL_NULL({formatted_self_name}, {formatted_other_name}),
                        NULL,
                        {formatted_self_name})"""
            )
            column_types.append(type)
            column_names.append(f"{column}_other")
            column_expressions.append(
                f"""IF(
                        EQUAL_NULL({formatted_self_name}, {formatted_other_name}),
                        NULL,
                        {formatted_other_name})"""
            )
            column_types.append(type)
        return column_names, column_expressions, column_types

    def generate_with_cross_join_col_exp(self, col, kwargs):
        purpose = kwargs.get("purpose", "rolling")

        if purpose not in ["rolling", "expanding"]:
            raise make_exception(
                NotImplementedError,
                PonderError.BIGQUERY_CROSS_JOIN_PURPOSE_NOT_IMPLEMENTED,
                f"Cross join for the purpose {purpose} not implemented yet",
            )

        view_names = kwargs.get("view_names", None)
        if view_names is None:
            view_names = ["", ""]
        elif len(view_names) != 2:
            raise make_exception(
                TypeError,
                PonderError.BIGQUERY_CROSS_JOIN_VIEW_NAMES_LENGTH_NOT_2,
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
                PonderError.BIGQUERY_CROSS_JOIN_WIN_TYPE_NOT_IMPLEMENTED,
                f"Cross join with {win_type} not implemented yet",
            )

        # COMMENT: Add other win_types under here if the templates fits
        # them as well
        common_exp_prefix = f"""
            IF(COUNT({view_names[1]}{self.format_name(col)}) < {window},
            NULL, {win_func}
        """

        if win_type is not None and win_type.lower() == "gaussian":
            # This is deliberately made as a list instead of equality check
            # to make it extendable
            if win_func not in ["SUM", "AVG", "STDDEV", "VARIANCE"]:
                raise make_exception(
                    NotImplementedError,
                    PonderError.BIGQUERY_GAUSSIAN_AGGREGATION_FUNCTION_NOT_IMPLEMENTED,
                    f"Gaussian aggregation function {win_func} not implemented yet",
                )

            std = kwargs.get("std", None)
            weight = f"""
                EXP(-0.5 * POW(({window - (window+1)/2} -
                    {view_names[0]}{__PONDER_ORDER_COLUMN_NAME__} +
                    {view_names[1]}{__PONDER_ORDER_COLUMN_NAME__})/{std}, 2))"""
            if win_func == "SUM":
                return f"""
                    IF(
                        COUNT({view_names[1]}{self.format_name(col)}) < {window},
                        NULL,
                        SUM({weight} * {view_names[1]}{self.format_name(col)})
                    )
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

                window_specs = f"""
                    OVER (
                        ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                        ROWS BETWEEN {window} PRECEDING AND CURRENT ROW
                    )
                """
                window_specs = ""
                if win_func == "AVG":
                    return f"""
                        IF(
                            COUNT({view_names[1]}{self.format_name(col)}) < {window},
                            NULL,
                            SUM({weight} * {view_names[1]}{self.format_name(col)}) /
                            {sum_weights}
                        )
                    """
                elif win_func == "VARIANCE":
                    if math.isinf(weighting_ratio):
                        return "NULL"
                    return f"""
                        IF(
                            COUNT({view_names[1]}{self.format_name(col)}) {window_specs}
                            < {window},
                            NULL,
                            {weighting_ratio} *
                            SUM({weight} *
                                POW(
                                    {view_names[1]}{self.format_name(col)} -
                                    {view_names[0]}{self.format_name(col+'_MU')},
                                    2
                                )
                            ) {window_specs}
                        )
                    """
                elif win_func == "STDDEV":
                    if math.isinf(weighting_ratio):
                        return "NULL"
                    return f"""
                        IF(
                            COUNT({view_names[1]}{self.format_name(col)}) {window_specs}
                            < {window},
                            NULL,
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
                        )
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
            IF(COUNT({view_names[1]}{self.format_name(col)}) < {window},
            NULL,
            APPROX_QUANTILES({view_names[1]}{self.format_name(col)}, 100)
            [OFFSET(CAST(TRUNC({quantile} * 100) as INT64))])
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
                +(COUNTIF(
                    {view_names[1]}{self.format_name(col)}=
                    {view_names[0]}{self.format_name(col)}
                )+1)/2
                """
            return f"""
            IF(COUNT({view_names[1]}{self.format_name(col)}) < {window},
            NULL, IF({view_names[0]}{self.format_name(col)} IS NULL, NULL, COUNTIF(
                {view_names[1]}{self.format_name(col)}{comp}
                {view_names[0]}{self.format_name(col)}
            )){addend})
            """
        elif win_func == "MEDIAN":
            return f"""
            APPROX_QUANTILES({view_names[1]}{self.format_name(col)}, 100) [OFFSET(50)]
            """
        elif win_func in ["KURTOSIS", "SKEW"]:
            return f"""
            {common_exp_prefix}({view_names[1]}{self.format_name(col)}))
            """
        else:
            raise make_exception(
                NotImplementedError,
                PonderError.BIGQUERY_WINDOW_FUNCTION_NOT_IMPLEMENTED,
                f"Window function {win_func} not implemented yet",
            )

    def generate_with_cross_join_full_command(
        self,
        input_node_sql,
        column_names,
        column_expressions,
        order_column_name,
        row_labels_column_names,
        kwargs,
    ):
        column_select_strings = (
            f"{self.format_name(expr) if expr == name else expr} AS "
            + self.format_name(name)
            for name, expr in zip(column_names, column_expressions)
        )

        purpose = kwargs.get("purpose", "rolling")
        if purpose not in ["rolling", "expanding"]:
            raise make_exception(
                NotImplementedError,
                PonderError.BIGQUERY_CROSS_JOIN_FULL_NOT_IMPLEMENTED,
                f"Cross join for the purpose {purpose} not implemented yet",
            )

        view_names = kwargs.get("view_names", None)
        if view_names is None or len(view_names) != 2:
            raise make_exception(
                TypeError,
                PonderError.BIGQUERY_CROSS_JOIN_FULL_VIEW_NAMES_INCORRECT,
                f"View names {view_names} has problems",
            )

        order_columns_list = []
        if order_column_name not in column_names:
            order_columns_list.append(
                "MIN("
                + view_names[0]
                + "."
                + self.format_name(order_column_name)
                + ") AS "
                + self.format_name(order_column_name)
            )

        row_labels_columns_list = []
        for row_labels_column_name in row_labels_column_names:
            if row_labels_column_name not in column_names:
                row_labels_columns_list.append(
                    "MIN("
                    + view_names[0]
                    + "."
                    + self.format_name(row_labels_column_name)
                    + ") AS "
                    + self.format_name(row_labels_column_name)
                )

        formatted_cols = [
            view_names[0] + "." + self.format_name(col)
            for col in column_names
            if not col.endswith("_MU")
        ]
        groupby_cols = ", ".join(formatted_cols)

        # COMMENT: This node essentially does a self join on the input table.
        # The where clause combined with the groupby creates
        # increasing sizes of groups of values from the same columns
        # but has them __side-by-side__ due to the self-cross join.
        # Then the grouping clause allows to group them with sizes of
        # 1, 2, 3.... <window_size>, <window_size>, <window_size>
        # The size of the group never goes beyond <window_size> because we
        # have an inequality join condition of type
        # T1.rownum - T2.rownum < window_size. The window is ensured to be rolling
        # forward always by the clause T1.rownum - T2.rownum >= 0.
        # The aggregation with IF statement which comes from our
        # 'generate_with_cross_join_col_exp' function above ensures
        # that we consider groups of only <window_size> and then applies
        # grouping function on them. In this case, the grouping function
        # has to be applied by doing some mathematical (gaussian) transformations
        # on the column values first and then applying the aggregation on them.
        # However, in the future, we can extend this node to be more generic
        # by making 'generate_with_cross_join_col_exp' function more generic
        # With this we can potentially support rolling.median
        # (not within win_type) which currently does not have native Snowflake
        # support.

        window_size = kwargs.get("window", None)
        if purpose == "rolling":
            condition = f"""
                {view_names[0]}.{__PONDER_ORDER_COLUMN_NAME__} -
                {view_names[1]}.{__PONDER_ORDER_COLUMN_NAME__} < {window_size}
                AND {view_names[0]}.{__PONDER_ORDER_COLUMN_NAME__} -
                {view_names[1]}.{__PONDER_ORDER_COLUMN_NAME__} >= 0
            """
        else:
            condition = f"""
                {view_names[0]}.{__PONDER_ORDER_COLUMN_NAME__} >=
                {view_names[1]}.{__PONDER_ORDER_COLUMN_NAME__}
            """
        return f"""
            SELECT
                {", ".join(
                    (*column_select_strings,
                    *row_labels_columns_list,
                    *order_columns_list))}
            FROM
                ({input_node_sql}) AS {view_names[0]},
                ({input_node_sql}) AS {view_names[1]}
             WHERE {condition}
              GROUP BY {view_names[0]}.{__PONDER_ORDER_COLUMN_NAME__}, {groupby_cols}
              ORDER BY {view_names[0]}.{__PONDER_ORDER_COLUMN_NAME__}
            """

    def generate_upsample_command(
        self,
        col,
        offset: pandas.DateOffset,
        start_val: pandas.Timestamp,
        end_val: pandas.Timestamp,
        sum_interval: float,
        interval: float,
    ):
        # Use GENERATE_TIMESTAMP_ARRAY to create rows based on the start_val
        n, unit = _pandas_offset_object_to_n_and_sql_unit(offset)
        start_val = _pandas_start_val_to_end_period(start_val, unit)
        end_val = _pandas_start_val_to_end_period(end_val, unit)
        if unit in ("second", "minute", "hour", "day"):
            return (
                f"SELECT TIMESTAMP_SECONDS(DIV(UNIX_SECONDS(TIMESTAMP("
                f"{self.format_name('generate_series')})), {int(interval)}) "
                f"* {int(interval)}) AS {self.format_name(col)}, "
                f"{self.format_name('generate_series')} "
                f"FROM (SELECT * FROM UNNEST(GENERATE_TIMESTAMP_ARRAY( "
                f"{self.format_value(start_val)}, {self.format_value(end_val)}, "
                f"INTERVAL {n} {unit})) AS {self.format_name('generate_series')})"
            )
        else:
            # We need to convert start_val from a TIMESTAMP to DATE
            # in order to use GENERATE_DATE_ARRAY which supports
            # intervals week, month, quarter, year
            return (
                f"SELECT LAST_DAY(DATETIME(TIMESTAMP_SECONDS(DIV(UNIX_SECONDS("
                f"TIMESTAMP({self.format_name('generate_series')})), {int(interval)}) "
                f"* {int(interval)} + {int(interval)})), {unit}) AS "
                f"{self.format_name(col)}, {self.format_name('generate_series')} FROM "
                f"(SELECT * FROM UNNEST(GENERATE_DATE_ARRAY("
                f"DATE_FROM_UNIX_DATE(CAST(FLOOR(UNIX_SECONDS("
                f"{self.format_value(start_val)}) / 86400) AS INT64)), "
                f"DATE_FROM_UNIX_DATE(CAST(FLOOR(UNIX_SECONDS("
                f"{self.format_value(end_val)}) / 86400) AS INT64)), "
                f"INTERVAL {n} {unit})) AS {self.format_name('generate_series')})"
            )

    def generate_simple_unpivot(
        self, input_node_query, input_query_cols, transposed=False
    ):
        formatted_input_query_cols = [self.format_name(col) for col in input_query_cols]
        input_cols_str = ", ".join(formatted_input_query_cols)
        if not transposed:
            return f"""
                SELECT {__PONDER_ORDER_COLUMN_NAME__} AS R, C, V
                FROM ({input_node_query})
                UNPIVOT(V FOR C IN ({input_cols_str}))
            """
        else:
            return f"""
                SELECT R, {__PONDER_ORDER_COLUMN_NAME__} AS C, V
                FROM ({input_node_query})
                UNPIVOT(V FOR R IN ({input_cols_str}))
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
        int_output_columns = [str(int(col)) for col in output_columns]
        int_output_col_str = ", ".join(iter(int_output_columns))
        return f"""
        SELECT R AS "{__PONDER_ORDER_COLUMN_NAME__}",
        "{__PONDER_ORDER_COLUMN_NAME__}" AS "{__PONDER_ROW_LABELS_COLUMN_NAME__}",
        {formatted_output_col_str}
        FROM
        ({input_query}) AS MATMUL
        PIVOT(SUM(MATMUL.V) FOR MATMUL.C IN ({int_output_col_str})) AS P
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
            where_clause = where_clause + " TO_NUMBER(LEFT_TABLE.C) = "

        if transposed_right:
            where_clause = where_clause + "TO_NUMBER(RIGHT_TABLE.R) "
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
        if periods < 0:
            lag_or_lead = f"LEAD({column_name}, {abs(periods)})"
        else:
            lag_or_lead = f"LAG({column_name}, {periods})"
        window = f"""{lag_or_lead} OVER (
            {partition_by_clause}
            ORDER BY {order_col}
            )"""

        return f"({column_name} - {window}) / ({window})"

    def generate_diff(self, column_name, periods, partition_by_clause=""):
        column_name = self.format_name(column_name)
        order_col = __PONDER_ORDER_COLUMN_NAME__

        if periods < 0:
            lag_or_lead = f"LEAD({column_name}, {abs(periods)})"
        else:
            lag_or_lead = f"LAG({column_name}, {periods})"

        window = f"""{lag_or_lead} OVER (
        {partition_by_clause}
        ORDER BY {order_col}
        )"""

        return f"({column_name} - {window})"

    def generate_timedelta_to_datetime_addend(self, timedelta: pandas.Timedelta) -> str:
        return str(int(timedelta / np.timedelta64(1, "us")))

    def generate_scalar_timestamp_for_subtraction(
        self, timestamp: pandas.Timestamp
    ) -> str:
        return f'DATETIME "{timestamp}"'

    def generate_datetime_plus_timedelta(
        self, datetime_sql: str, timedelta_sql: str
    ) -> str:
        return f"TIMESTAMP_ADD({datetime_sql}, INTERVAL {timedelta_sql} MICROSECOND)"

    def generate_datetime_minus_timedelta(self, left_sql: str, right_sql: str) -> str:
        return f"TIMESTAMP_ADD({left_sql}, INTERVAL -{right_sql} MICROSECOND)"

    def generate_datetime_minus_datetime(self, left_sql: str, right_sql: str) -> str:
        return f"TIMESTAMP_DIFF({left_sql}, {right_sql}, MICROSECOND)"

    def generate_pandas_timestamp_to_date(self, timestamp: pandas.Timestamp):
        return f"DATE('{self.format_value(timestamp)}')"

    def generate_bitwise_and(self, op_1, op_2) -> str:
        return f"{str(op_1)} & {str(op_2)}"

    def generate_bitwise_or(self, op_1, op_2) -> str:
        return f"{str(op_1)} | {str(op_2)}"

    def generate_bitwise_xor(self, op_1, op_2) -> str:
        return f"{str(op_1)} ^ {str(op_2)}"

    def generate_map_column_expressions(self, labels_to_apply_over, n):
        return [
            f"""
            IF(ARRAY_LENGTH({labels_to_apply_over[0]})>{i},
                CAST({labels_to_apply_over[0]}[OFFSET({i})] AS STRING),
                NULL)
            """
            for i in range(n)
        ]

    def generate_value_dict_fill_na(
        self, label, value_dict, limit, group_cols: list[str], upcast_to_object
    ):
        if upcast_to_object:
            raise make_exception(
                NotImplemented,
                PonderError.BIGQUERY_FILLNA_MIXED_TYPES_NOT_IMPLEMENTED,
                message="fillna with mixed types not implemented for bigquery",
            )
        if label not in value_dict:
            return label
        formatted_value = self.format_value_by_type(value_dict[label])
        if group_cols is None:
            partition_by_sql = ""
        else:
            partition_by_sql = (
                f" PARTITION BY "
                f"({','.join(self.format_name(c) for c in group_cols)})"
            )

        if limit is not None:
            return f"""
                IF(
                        COUNTIF({self.format_name(label)} IS NULL)
                        OVER (
                            {partition_by_sql}
                            ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                        ) <= {limit}
                    AND
                        {self.format_name(label)} IS NULL,
                    {formatted_value},
                    {self.format_name(label)})
                """
        else:
            return f"IFNULL({self.format_name(label)},{formatted_value})"

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
                PonderError.BIGQUERY_FILLNA_INVALID_METHOD,
                "Ponder Internal Error: received method from fillna that is not "
                + "ffill or bfill",
            )
        return columns_selection

    def generate_cast_to_type_command(self, col, cast_type):
        return (
            f"CAST({self.format_name(col)} AS "
            f"{self.pandas_type_to_bigquery_type_map[cast_type]})"
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
            code=PonderError.BIGQUERY_MASK_NOT_IMPLEMENTED,
            message="Mask not yet supported in BigQuery dialect",
        )
