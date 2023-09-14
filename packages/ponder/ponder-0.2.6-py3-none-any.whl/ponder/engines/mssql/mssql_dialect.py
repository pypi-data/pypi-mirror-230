from __future__ import annotations

import hashlib
import logging
import math
import random
import re
import string
import uuid
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
    __ROWID_VALUE_SIZE_TO_MATERIALIZE__,
    GROUPBY_FUNCTIONS,
    REDUCE_FUNCTION,
    UnionAllDataForDialect,
)
from ponder.core.error_codes import PonderError, make_exception
from ponder.core.sql_dialect import SQLDialect, _pandas_offset_object_to_n_and_sql_unit

logger = logging.getLogger(__name__)


def _regex_params(flags=0):
    if flags == 0:
        return "c"
    params = ""
    if flags & re.IGNORECASE:
        params = params + "i"
    else:
        params = params + "c"
    if flags & re.MULTILINE:
        params = params + "m"
    if flags & re.DOTALL:
        params = params + "s"
    return params


class MSSQLDialect(SQLDialect):
    pandas_type_to_mssql_type_map = {
        "bool": "BIT",
        "date": "DATETIME",
        "datetime64[ms]": "DATETIME",
        "datetime64[ns]": "DATETIME2",
        "datetime": "DATETIME",
        "float": "FLOAT",
        "float64": "REAL",
        "int": "INT",
        "int8": "BIGINT",
        "int16": "BIGINT",
        "int32": "BIGINT",
        "int64": "BIGINT",
        "uint8": "BIGINT",
        "str": "TEXT",
        "string": "TEXT",
        "object": "TEXT",
    }

    # hilariously incomplete type mappings
    mssql_type_to_pandas_type_map = {
        "bigint": "int64",
        "bit": "bool",
        "numeric": "float64",
        "smallint": "int16",
        "decimal": "float64",
        "smallmoney": "object",
        "int": "int64",
        "tinyint": "int16",
        "money": "object",
        "float": "float64",
        "real": "float64",
        "date": "datetime64[ns]",
        "timestamp": "datetime64[ns]",
        "datetimeoffset": "object",
        "smalldatetime": "datetime64[ns]",
        "datetime": "datetime64[ms]",
        "datetime2": "datetime64[ns]",
        "datetime2(7)": "datetime64[ns]",
        "time": "object",
        "char": "string",
        "varchar": "string",
        "text": "string",
        "nchar": "object",
        "nvarchar": "object",
        "ntext": "object",
        "binary": "object",
        "varbinary": "object",
        "image": "object",
    }

    valid_name_regex_pattern = re.compile("^[A-Z_][A-Z0-9_\\$]*")

    def __init__(self):
        self._obfuscate = False
        self._salt = uuid.uuid4().hex
        self._valid_name_regex_pattern = re.compile("^[A-Z_][A-Z0-9_\\$]*")
        super().__init__()

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
            return table_or_query
        return f"{table_or_query}"

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
        if '"' in name:
            name = name.replace('"', '""')
        return f'"{name}"'

    def format_name_thrice(self, name):
        if self._obfuscate:
            # just doing something random to obfuscate.
            return self.format_name(name)

        return (
            self.format_name(name)
            if self._valid_name_regex_pattern.fullmatch(name)
            else f'"""{name}"""'
        )

    def format_name_quarce(self, name):
        if self._obfuscate:
            # just doing something random to obfuscate.
            return self.format_name(name)

        return (
            self.format_name(name)
            if self._valid_name_regex_pattern.fullmatch(name)
            else f'""""{name}""""'
        )

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
                "OBJECT_CONSTRUCT('_ponder_python_object_type', "
                + "'pandas.Interval', 'data', OBJECT_CONSTRUCT('left', "
                + f"{self.format_value_by_type(value.left)}, 'right', "
                + f"{self.format_value_by_type(value.right)}, 'closed', "
                + f"{self.format_value_by_type(value.closed)}))"
            )
        return f"{value}"

    def format_datetime_format(self, time_column, datetime_format):
        return f"TO_TIMESTAMP({self.format_name(time_column)}, " f"'{datetime_format}')"

    def set_obfuscate(self):
        self._obfuscate = True

    def generate_datetime_minus_timedelta(self, left_sql: str, right_sql: str) -> str:
        return f"TIMESTAMPADD('nanosecond', -({right_sql}), {left_sql})"

    def generate_datetime_minus_datetime(self, left_sql: str, right_sql: str) -> str:
        return f"TIMESTAMPDIFF('nanosecond', {right_sql}, {left_sql})"

    def generate_datetime_plus_timedelta(
        self, datetime_sql: str, timedelta_sql: str
    ) -> str:
        return f"TIMESTAMPADD('nanosecond', {timedelta_sql}, {datetime_sql})"

    def generate_downsample_command(
        self,
        col,
        offset: pandas.DateOffset,
        start_val: pandas.Timestamp,
        end_val: pandas.Timestamp,
        sum_interval: float,
    ):
        raise make_exception(
            NotImplementedError,
            PonderError.PONDER_POSTGRES_PROTOTYPE_NOT_IMPLEMENTED,
            "Ponder Internal Error: PostgreSQL downsample not implemented",
        )

    def generate_downsample_index_command(
        self,
        col,
        offset: pandas.DateOffset,
        start_val: pandas.Timestamp,
        end_val: pandas.Timestamp,
    ):
        raise make_exception(
            NotImplementedError,
            PonderError.PONDER_POSTGRES_PROTOTYPE_NOT_IMPLEMENTED,
            "Ponder Internal Error: PostgreSQL downsample not implemented",
        )

    def generate_map_column_expressions(self, labels_to_apply_over, n):
        return [
            f"""
            IFF(ARRAY_SIZE({labels_to_apply_over[0]})>{i},
                GET({labels_to_apply_over[0]},{i})::STRING,
                NULL)
            """
            for i in range(n)
        ]

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
        raise make_exception(
            NotImplementedError,
            PonderError.PONDER_POSTGRES_PROTOTYPE_NOT_IMPLEMENTED,
            "Ponder Internal Error: PostgreSQL pivot not implemented",
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
        raise make_exception(
            NotImplementedError,
            PonderError.PONDER_POSTGRES_PROTOTYPE_NOT_IMPLEMENTED,
            "Ponder Internal Error: PostgreSQL upsample not implemented",
        )

    def generate_get_current_database_command(self):
        return "SELECT CURRENT_DATABASE()"

    def generate_get_current_schema_command(self):
        return "SELECT CURRENT_SCHEMA()"

    def generate_put_command(self, file_path, table_name):
        command = "put file://" + file_path + " @%" + table_name
        return command

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
        date_format=None,
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
                if (self.pandas_type_to_mssql_type_map[str(column_type)] != "BOOLEAN")
                else f"TO_BOOLEAN(${column_index})"
                for column_index, column_type in zip(
                    [i for i in range(1, len(column_types) + 1)], column_types
                )
            ]
        )
        from_clause = (
            f" FROM ( SELECT {from_clause} FROM @%{table_name} ) AS PONDER_INPUT "
        )

        on_error_fragment = "ON_ERROR=CONTINUE" if on_bad_lines == "skip" else ""

        command = (
            f"COPY INTO {table_name} ( {columns_clause} ) {from_clause} purge = true"
            f" file_format = (type = csv NULL_IF='{na_values}'"
            f" FIELD_OPTIONALLY_ENCLOSED_BY='\"' FIELD_DELIMITER='{sep}' "
            f"DATE_FORMAT='{date_format}' SKIP_HEADER={skip_header}, "
            f"ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE) {on_error_fragment}"
        )
        return command

    def generate_select_count_star_statement(self, table):
        formatted_table_name = self.format_table_name(table)
        return f"""SELECT COUNT(*) AS COUNT_PONDER FROM ({formatted_table_name})
                AS PONDER_INPUT;"""

    # mssql creates a different type of metadata call from other databases
    # because we cannot depend on a to_pandas operation to do the correct
    # typing for a dataset with nulls
    def generate_read_table_metadata_statement(self, table_or_query):
        formatted_table_or_query = self.format_table_name(table_or_query)
        return f"""SELECT name, system_type_name
        FROM sys.dm_exec_describe_first_result_set
        (N'SELECT * FROM  {formatted_table_or_query};',NULL,1);"""

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
                IFF(COUNT(*) OVER (ORDER BY
                {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                ROWS BETWEEN {window-1} PRECEDING AND CURRENT ROW)={window},
                COUNT({formatted_col}) OVER (ORDER BY
                {self.format_name(__PONDER_ORDER_COLUMN_NAME__)} ROWS BETWEEN {window-1}
                PRECEDING AND CURRENT ROW), NULL)
                """

        # Standard error of mean (SEM) does not have native postgres support
        # thus calculated as STDDEV/SQRT(N-1)
        if cumulative_function == "SEM":
            if non_numeric_col:
                return "NULL"
            return f"""
                IFF(COUNT({formatted_col}) OVER (ORDER BY
                {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                ROWS BETWEEN {window-1} PRECEDING AND CURRENT ROW)={window},
                (STDEV({formatted_col}) OVER (ORDER BY
                {self.format_name(__PONDER_ORDER_COLUMN_NAME__)} ROWS BETWEEN {window-1}
                PRECEDING AND CURRENT ROW))/SQRT({window-1}), NULL)
                """

        if cumulative_function == "CORR":
            assert formatted_other_col is not None
            if non_numeric_col or window < 2:
                return "NULL"

            count_exp = f"""
            COUNT_IF({formatted_col} IS NOT NULL AND {formatted_other_col} IS NOT NULL)
             OVER (ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
             ROWS BETWEEN {window-1} PRECEDING AND CURRENT ROW)"""

            sigmas_exp = f"""
                    STDDEV_POP(IFF({formatted_col} IS NULL,NULL,{formatted_other_col}))
                    OVER (ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                    ROWS BETWEEN
                    {window-1} PRECEDING AND CURRENT ROW) *
                    STDDEV_POP(IFF({formatted_other_col} IS NULL,NULL,{formatted_col}))
                    OVER (ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                    ROWS BETWEEN
                    {window-1} PRECEDING AND CURRENT ROW)"""

            return f"""
                IFF({count_exp}={window} AND {count_exp} * {sigmas_exp} > 0, (
                    SUM({formatted_other_col}*{formatted_col}) OVER (ORDER BY
                    {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                    ROWS BETWEEN {window-1}
                    PRECEDING AND CURRENT ROW) - (
                        SUM(IFF({formatted_col} IS NULL,NULL,{formatted_other_col}))
                        OVER (ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                        ROWS BETWEEN
                        {window-1} PRECEDING AND CURRENT ROW) *
                        SUM(IFF({formatted_other_col} IS NULL,NULL,{formatted_col}))
                        OVER (ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                        ROWS BETWEEN
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
            COUNT_IF({formatted_col} IS NOT NULL AND {formatted_other_col} IS NOT NULL)
             OVER (ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
             ROWS BETWEEN {window-1} PRECEDING AND CURRENT ROW)"""

            return f"""
                IFF({count_exp}={window}, (
                    SUM({formatted_other_col}*{formatted_col}) OVER (ORDER BY
                    {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                    ROWS BETWEEN {window-1}
                    PRECEDING AND CURRENT ROW) - (
                        SUM(IFF({formatted_col} IS NULL,NULL,{formatted_other_col}))
                        OVER (ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                        ROWS BETWEEN
                        {window-1} PRECEDING AND CURRENT ROW) *
                        SUM(IFF({formatted_other_col} IS NULL,NULL,{formatted_col}))
                        OVER (ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                        ROWS BETWEEN
                        {window-1} PRECEDING AND CURRENT ROW) / {count_exp}
                    )
                ) / (
                    {count_exp}-1
                ), NULL)
                """

        return f"""
        IFF(COUNT({formatted_col}) OVER (ORDER BY
        {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
         ROWS BETWEEN {window - 1} PRECEDING AND CURRENT ROW)={window},
            {cumulative_function}({formatted_col}) OVER (ORDER BY
            {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
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
                IFF(COUNT({self.format_name(__PONDER_ORDER_COLUMN_NAME__)}) OVER
                 (ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)} ROWS
                 BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)>={min_window},
                 COUNT({formatted_col}) OVER (ORDER BY
                 {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                 ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), NULL)
                """

        if cumulative_function == "SEM":
            if non_numeric_col:
                return "NULL"

            count_expression = f"""COUNT({formatted_col})
             OVER (ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)"""

            return f"""
            IFF({count_expression}>={min_window},
             (STDEV({formatted_col}) OVER (ORDER BY
             {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
              ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW))
             /SQRT({count_expression}-1), NULL)
            """

        if cumulative_function == "CORR":
            assert formatted_other_col is not None
            if non_numeric_col:
                return "NULL"

            count_exp = f"""
            COUNT_IF({formatted_col} IS NOT NULL AND {formatted_other_col} IS NOT NULL)
             OVER (ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)"""

            sigmas_exp = f"""
                    STDDEV_POP(IFF({formatted_col} IS NULL,NULL,{formatted_other_col}))
                    OVER (ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                    ROWS BETWEEN
                    UNBOUNDED PRECEDING AND CURRENT ROW) *
                    STDDEV_POP(IFF({formatted_other_col} IS NULL,NULL,{formatted_col}))
                    OVER (ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                    ROWS BETWEEN
                    UNBOUNDED PRECEDING AND CURRENT ROW)"""

            return f"""
                IFF({count_exp}>={min_window} AND {count_exp} * {sigmas_exp} > 0, (
                    SUM({formatted_other_col}*{formatted_col}) OVER (ORDER BY
                    {self.format_name(__PONDER_ORDER_COLUMN_NAME__)} ROWS BETWEEN
                    UNBOUNDED
                    PRECEDING AND CURRENT ROW) - (
                        SUM(IFF({formatted_col} IS NULL,NULL,{formatted_other_col}))
                        OVER (ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                        ROWS BETWEEN
                        UNBOUNDED PRECEDING AND CURRENT ROW) *
                        SUM(IFF({formatted_other_col} IS NULL,NULL,{formatted_col}))
                        OVER (ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                        ROWS BETWEEN
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
            COUNT_IF({formatted_col} IS NOT NULL AND {formatted_other_col} IS NOT NULL)
             OVER (ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)"""

            return f"""
                IFF({count_exp}>=GREATEST({min_window}, 2), (
                    SUM({formatted_other_col}*{formatted_col}) OVER (ORDER BY
                    {self.format_name(__PONDER_ORDER_COLUMN_NAME__)} ROWS BETWEEN
                    UNBOUNDED
                    PRECEDING AND CURRENT ROW) - (
                        SUM(IFF({formatted_col} IS NULL,NULL,{formatted_other_col}))
                        OVER (ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                        ROWS BETWEEN
                        UNBOUNDED PRECEDING AND CURRENT ROW) *
                        SUM(IFF({formatted_other_col} IS NULL,NULL,{formatted_col}))
                        OVER (ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                        ROWS BETWEEN
                        UNBOUNDED PRECEDING AND CURRENT ROW) / {count_exp}
                    )
                ) / (
                    {count_exp}-1
                ), NULL)
                """

        return f"""
            IFF(COUNT({formatted_col}) OVER (ORDER BY
            {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)>={min_window},
            {cumulative_function}({formatted_col}) OVER (ORDER BY
            {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW),
                NULL)"""

    def generate_get_first_element_by_row_label_rank_command(
        self, col, row_labels_column_name
    ):
        return (
            f"IFF(RANK() OVER "
            f"(PARTITION BY {self.format_name(col)} "
            f"ORDER BY {self.format_name(row_labels_column_name)})=1, "
            f"{self.format_name(col)}, NULL)"
        )

    def generate_replace_nan_with_0(self, col):
        return f"ZEROIFNULL({self.format_name(col)})"

    def generate_use_admin_role_command(self):
        return "USE ROLE SYSADMIN;"

    def generate_query_timeout_command(self, query_timeout):
        return f"ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS={query_timeout}"

    def generate_temp_table_for_subquery(self, temp_table_name, query):
        if not temp_table_name.startswith("#"):
            raise make_exception(
                RuntimeError,
                PonderError.MSSQL_TEMP_TABLE_NAME_FORMAT_ERROR,
                f"MSSQL Temp Table names must start with '#': {temp_table_name}",
            )
        return (
            f"""
            CREATE TABLE {self.format_table_name(temp_table_name)} AS
            ({query})
            """,
            f"""
            SELECT * FROM {self.format_table_name(temp_table_name)}
            """,
        )

    def generate_create_temp_table_with_rowid_command(self, temp_table_name, sql_query):
        if not temp_table_name.startswith("#"):
            raise make_exception(
                RuntimeError,
                PonderError.MSSQL_TEMP_TABLE_NAME_FORMAT_ERROR,
                f"MSSQL Temp Table names must start with '#': {temp_table_name}",
            )
        formatted_sql_query = self.format_table_name(sql_query)
        # SQL Server does not allow integer indices in a window function, so
        #   "ROW_NUMBER() OVER (ORDER BY 1) -1" would not work here. You can
        # also not use a literal. The expectation is that you need to use
        # a column name, but since we have been passed a query we cannot use
        # that either. We circumvent this by using "user" in the ORDER BY
        # https://learn.microsoft.com/en-us/sql/t-sql/functions/user-transact-sql
        row_num_sql = " ROW_NUMBER() OVER (ORDER BY user) -1 "

        return (
            f"SELECT *,"
            f" {row_num_sql} AS {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}"
            f" INTO {self.format_table_name(temp_table_name)}"
            f" FROM {formatted_sql_query}"
        )

    def generate_create_temp_table_for_wherein(self, temp_table_name, rowids):
        if not temp_table_name.startswith("#"):
            raise make_exception(
                RuntimeError,
                PonderError.MSSQL_TEMP_TABLE_NAME_FORMAT_ERROR,
                f"MSSQL Temp Table names must start with '#': {temp_table_name}",
            )

        rowid_insert_exp = []
        for i in range(0, len(rowids), __ROWID_VALUE_SIZE_TO_MATERIALIZE__):
            rowids_to_insert = ", ".join(
                [
                    f"({rowid})"
                    for rowid in rowids[
                        i : (i + __ROWID_VALUE_SIZE_TO_MATERIALIZE__)  # noqa: E203
                    ]  # noqa: E203
                ]
            )
            rowid_insert_exp.append(rowids_to_insert)

        formatted_temp_table_name = self.format_table_name(temp_table_name)
        return_arr = [
            f"""
            CREATE TABLE {formatted_temp_table_name} AS SELECT
            {self.format_name(__PONDER_TEMP_TABLE_ROWID_COLUMN__)} FROM VALUES
            {rowid_insert_exp[0]} AS
             TEMPVAL({self.format_name(__PONDER_TEMP_TABLE_ROWID_COLUMN__)})
            """,
        ]
        for i in range(1, len(rowid_insert_exp)):
            return_arr.append(
                f"""
                INSERT INTO {formatted_temp_table_name}
                SELECT {self.format_name(__PONDER_TEMP_TABLE_ROWID_COLUMN__)} FROM
                VALUES {rowid_insert_exp[i]}  AS
                TEMPVAL({self.format_name(__PONDER_TEMP_TABLE_ROWID_COLUMN__)})
                """
            )
        return_arr.append(
            f"""
            SELECT {self.format_name(__PONDER_TEMP_TABLE_ROWID_COLUMN__)}
            FROM {formatted_temp_table_name}
            """,
        )
        logger.debug(f"Postgres dialect return array size {len(return_arr)}")
        return return_arr

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
        nulls_equal=True,
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
                (
                    # nulls count as matching in pandas joins:
                    # pandas.DataFrame([[None, 1]], columns=['a', 'b']).merge(
                    #   pandas.DataFrame([[None, 2]], columns=['a', 'b']),
                    #   on='a',
                    #   how='left',
                    #   indicator=True)
                    # )
                    # the _merge column in result is 'both' for the above.
                    (
                        f"(LEFT_TABLE.{self.format_name(left_clause)} = "
                        f"RIGHT_TABLE.{self.format_name(right_clause)} OR "
                        f"(LEFT_TABLE.{self.format_name(left_clause)} IS NULL AND "
                        f"RIGHT_TABLE.{self.format_name(right_clause)} IS NULL))"
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
                    f"THEN 'left_only' ELSE 'both' END AS \"_merge\" "
                )
            elif how == "right":
                indicator_clause = (
                    f"CASE WHEN {self.format_name(left_order_column_name)} IS NULL "
                    f"THEN 'right_only' ELSE 'both' END AS \"_merge\" "
                )
            elif how == "outer":
                indicator_clause = (
                    f"CASE WHEN {self.format_name(left_order_column_name)} IS NULL "
                    f"THEN 'right_only' "
                    f"WHEN {self.format_name(right_order_column_name)} IS NULL "
                    f"THEN 'left_only' ELSE 'both' END AS \"_merge\" "
                )
            elif how == "inner":
                indicator_clause = "'both' AS \"_merge\" "
            else:
                raise make_exception(
                    NotImplementedError,
                    PonderError.POSTGRES_JOIN_INDICATOR_UNSUPPORTED_JOIN_TYPE,
                    "Ponder Internal Error: Indicator Clause only "
                    + "supported for left joins currently",
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
                row_labels = ", ".join(
                    [
                        f"""LEFT_TABLE.{self.format_name(col_name)}
                                        AS {self.format_name(col_name)}"""
                        for col_name in db_index_column_name
                    ]
                )

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
                # We coalese the columns from the order in case the merge
                # is from unbalanced tables.
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
            result_order_column_expression = (
                ", ROW_NUMBER() OVER (ORDER BY"
                f" {self.format_name(right_order_column_name)},"
                f" {self.format_name(left_order_column_name)}) - 1 AS"
                f" {self.format_name(result_order_column_name)},"
                f" {self.format_name(result_order_column_name)} AS"
                f" {self.format_name(__PONDER_ROW_LABELS_COLUMN_NAME__)}"
            )
        if how == "outer":
            how = "full outer"
        select_clause += result_order_column_expression
        ret_val = (
            f"SELECT {select_clause} FROM ({left_node_query}) AS LEFT_TABLE"
            f" {how.upper()} JOIN ({right_node_query}) AS RIGHT_TABLE"
            f" {on_clause}"
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
                    f" AND ABS(TIMESTAMPDIFF(MICROSECOND, {left_on_formatted[0]}, "
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
            FROM
                {self.generate_subselect_expression(right_node_query)}
        ) AS RIGHT_TABLE
        ON
            {on_fragment} {tolerance_fragment} {where_fragment}
        ORDER BY
            {self.format_name(result_order_column_name)}
        """
        return ret_val

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
            FROM {self.generate_subselect_expression(input_query)}
            """

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
            f" {result_order_column_name}"
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
            result_order_column_expression = self.generate_groupby_result_order_expr(
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
                {self.generate_subselect_expression(input_query)}
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
            select_clauses.append(
                f"{other_col_id} AS {self.format_name(__PONDER_AGG_OTHER_COL_ID__)}"
            )
            select_clauses.append(
                f"'{other_col}' AS {self.format_name(__PONDER_AGG_OTHER_COL_NAME__)}"
            )
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
                {self.generate_subselect_expression(input_query)}
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
                f"""MIN({other_col_id}) AS
                {self.format_name(__PONDER_AGG_OTHER_COL_ID__)}"""
            )
            select_clauses.append(
                f"MIN('{other_col}') AS "
                f"{self.format_name(__PONDER_AGG_OTHER_COL_NAME__)}"
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
        result_order_column_expression = self.generate_groupby_result_order_expr(
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
                {self.generate_subselect_expression(input_query)}
            {where_clause}
            GROUP BY
                {",".join(formatted_group_by_columns)}
            """

    def generate_groupby_window_first_expression(
        self, formatted_col, partition_by_clause
    ):
        return f"""
            FIRST_VALUE({formatted_col})
            OVER (
                {partition_by_clause}
                ORDER BY CASE WHEN {formatted_col} IS NOT NULL THEN 0 ELSE 1 END ASC,
                {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            )"""

    def generate_groupby_window_last_expression(
        self, formatted_col, partition_by_clause
    ):
        return f"""
            LAST_VALUE({formatted_col})
            OVER (
                {partition_by_clause}
                ORDER BY CASE WHEN {formatted_col} IS NOT NULL THEN 0 ELSE 1 END ASC,
                {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
            )"""

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
                        ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                    )"""
            else:
                return f"""
                    IFF({formatted_col} IS NULL, NULL, SUM({formatted_col})
                    OVER (
                        {partition_by_clause}
                        ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
                    )"""
        elif function in (
            CUMULATIVE_FUNCTIONS.PROD,
            GROUPBY_FUNCTIONS.CUMPROD,
        ):
            if skipna is False:
                return f"""
                    IFF(
                        (
                            COUNT_IF({formatted_col} < 0)
                            OVER (
                                {partition_by_clause}
                                ORDER BY
                                {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                            ) % 2
                        ) = 0,
                        1,
                        -1)
                    *
                    EXP(
                        SUM(LN(ABS({formatted_col})))
                        OVER (
                            {partition_by_clause}
                            ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                        )
                    )"""
            else:
                return f"""
                    IFF({formatted_col} IS NULL,
                        NULL,
                        IFF
                            (
                            COUNT_IF({formatted_col} < 0)
                            OVER (
                                {partition_by_clause}
                                ORDER BY
                                {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                            )
                            % 2 = 0,
                            1,
                            -1) *
                        EXP(
                            SUM(LN(ABS({formatted_col})))
                            OVER (
                                {partition_by_clause}
                                ORDER BY
                                {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
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
                    ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                )"""
            else:
                return f"""
                IFF({formatted_col} IS NULL,
                    NULL,
                    (
                        MAX({formatted_col})
                        OVER (
                            {partition_by_clause}
                            ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
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
                    ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                )"""
            else:
                return f"""
                IFF({formatted_col} IS NULL,
                    NULL,
                    (
                        MIN({formatted_col})
                        OVER (
                            {partition_by_clause}
                            ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                        )
                    )
                )"""
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
                ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
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
                    ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
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
                    PonderError.POSTGRES_GROUPBY_DIFF_AXIS_1_NOT_IMPLEMENTED,
                    "groupby.diff() with axis=1 not implemented yet",
                )
            return self.generate_diff(col, agg_kwargs["periods"], partition_by_clause)
        raise make_exception(
            RuntimeError,
            PonderError.POSTGRES_WINDOW_UNKNOWN_FUNCTION,
            f"Unknown function {function}",
        )

    def generate_autoincrement_type(self):
        return "int IDENTITY(0,1)"

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
        if is_temp is True and is_global_temp is False:
            if not table_name.startswith("#"):
                raise make_exception(
                    RuntimeError,
                    PonderError.MSSQL_TEMP_TABLE_NAME_FORMAT_ERROR,
                    f"MSSQL Temp Table names must start with '#': {table_name}",
                )

        create_statement += table_name + " ( "

        # TODO: Fix setting the col label to a data column without
        # updating the list of row label names
        try:
            columns_clause = ", ".join(
                [
                    self.format_name(column_name)
                    + " "
                    + self.pandas_type_to_mssql_type_map[str(column_type)]
                    for column_name, column_type in zip(column_names, column_types)
                ]
            )
        except Exception as e:
            raise make_exception(
                RuntimeError,
                PonderError.MSSQL_CREATE_TABLE_FAILED,
                """Create table failed possibly because
                column types are not mapped correctly""",
            ) from e
        # add the row order/row labels columns only for temp tables.
        if is_temp or is_global_temp:
            columns_clause += (
                f", {self.format_name(__PONDER_ROW_LABELS_COLUMN_NAME__)} "
                f" {self.generate_autoincrement_type()}"
            )

            if len(order_column_name or "") > 0:
                # Create the order column off of the row labels column
                columns_clause += f", {self.format_name(order_column_name)} "
                columns_clause += (
                    f" AS {self.format_name(__PONDER_ROW_LABELS_COLUMN_NAME__)} "
                    "PERSISTED "
                )

        else:
            if len(order_column_name or "") > 0:
                columns_clause += (
                    f", {self.format_name(order_column_name)} "
                    + self.pandas_type_to_mssql_type_map[str(order_column_type)]
                )

        create_statement += columns_clause + " )"

        return create_statement

    def generate_create_table_for_sp_command(
        self,
        table_name,
        column_names,
        column_types,
        order_column_name,
        order_column_type,
    ):
        table_name = self.format_table_name(table_name)

        if not table_name.startswith("#"):
            raise make_exception(
                RuntimeError,
                PonderError.MSSQL_TEMP_TABLE_NAME_FORMAT_ERROR,
                f"MSSQL Temp Table names must start with '#': {table_name}",
            )

        create_statement = f"CREATE TABLE {table_name} ( "

        # TODO: Fix setting the col label to a data column without
        # updating the list of row label names
        try:
            columns_clause = ", ".join(
                [
                    self.format_name(column_name)
                    + " "
                    + self.pandas_type_to_mssql_type_map[str(column_type)]
                    for column_name, column_type in zip(column_names, column_types)
                ]
            )
        except Exception as e:
            raise make_exception(
                RuntimeError,
                PonderError.POSTGRES_CREATE_TABLE_FAILED,
                """Create table failed possibly because
                column types are not mapped correctly""",
            ) from e

        if len(order_column_name or "") > 0:
            columns_clause += (
                f", {self.format_name(order_column_name)} "
                + self.pandas_type_to_mssql_type_map[str(order_column_type)]
            )

        if __PONDER_ORDER_COLUMN_NAME__ not in column_names:
            columns_clause += f""", {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
            {self.generate_autoincrement_type()}"""

        create_statement += columns_clause + " )"

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
            f" {select_columns_text} FROM "
            f"{self.generate_subselect_expression(input_query)}"
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

    def generate_find_last_altered_time_command(
        self, database_name, schema_name, table_name
    ):
        raise make_exception(
            NotImplementedError,
            PonderError.PONDER_POSTGRES_PROTOTYPE_NOT_IMPLEMENTED,
            "There is no reliable way to get the last modified time on PostgreSQL",
        )

    def generate_abort_detached_queries_command(self):
        return "ALTER SESSION SET ABORT_DETACHED_QUERY=TRUE;"

    def generate_category_list_object(self, column_name, category_list):
        return (
            "OBJECT_CONSTRUCT('_ponder_category', "
            + f"IFNULL(ARRAY_POSITION({self.format_name(column_name)}, "
            + f"{category_list}), -1))"
        )

    def generate_category_object(self, column_name):
        return (
            "OBJECT_CONSTRUCT('_ponder_category', "
            + "DENSE_RANK() OVER (ORDER BY "
            + f"{self.format_name(column_name)}) - 1)"
        )

    def generate_casted_columns(
        self, column_names, cast_from_map, cast_to_map, **kwargs
    ):
        # TODO: The DATETIME type casting is specific to Snowflake
        # but the rest of the types are generic to PostgreSQL dialects
        ret_column_expressions = []
        for column_name in column_names:
            if column_name in cast_to_map:
                if (
                    isinstance(cast_to_map[column_name], pandas.CategoricalDtype)
                    or cast_to_map[column_name] == "category"
                ):
                    column_expr = self.format_name(column_name)
                else:
                    db_type = self.pandas_type_to_mssql_type_map[
                        cast_to_map[column_name]
                    ]
                    cast_from_type = cast_from_map[column_name]
                    if cast_from_type == "float" and db_type == "INT":
                        column_expr = f"FLOOR({self.format_name(column_name)})::INT"
                    elif cast_from_type == "str" and db_type == "DATETIME":
                        datetime_format = kwargs.get("format", None)
                        if datetime_format is not None:
                            column_expr = self.format_datetime_format(
                                column_name, datetime_format
                            )
                        else:
                            column_expr = f"{self.format_name(column_name)}::TIMESTAMP"
                    else:
                        column_expr = (
                            f"{self.format_name(column_name)}::"
                            + self.pandas_type_to_mssql_type_map[
                                cast_to_map[column_name]
                            ]
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
            falsy_check = f"{column_name} = false"

        return f"""
            IFF({column_name} IS NULL OR {falsy_check}, false, true)
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
            return f"COUNT_IF({formatted_col})"
        elif function in (REDUCE_FUNCTION.COUNT, GROUPBY_FUNCTIONS.COUNT):
            return f"COUNT({formatted_col})"
        elif function is REDUCE_FUNCTION.COUNT_UNIQUE_INCLUDING_NULL:
            return f"ARRAY_LENGTH(ARRAY_AGG(DISTINCT {formatted_col}), 1)"
        elif function is REDUCE_FUNCTION.COUNT_UNIQUE_EXCLUDING_NULL:
            # TODO: Fix this to not include NULL values
            return f"ARRAY_LENGTH(ARRAY_AGG(DISTINCT {formatted_col}), 1)"
        elif function is GROUPBY_FUNCTIONS.UNIQUE:
            return f"ARRAY_AGG(DISTINCT {formatted_col})"
        elif function in (REDUCE_FUNCTION.MEAN, GROUPBY_FUNCTIONS.MEAN):
            return f"AVG({formatted_col})"
        elif function in (REDUCE_FUNCTION.MEDIAN, GROUPBY_FUNCTIONS.MEDIAN):
            # TODO: Fix for PostgreSQL as MEDIAN does not exist
            return f"MEDIAN({formatted_col})"
        elif function is REDUCE_FUNCTION.MODE:
            return f"MODE({formatted_col})"
        elif function in (
            REDUCE_FUNCTION.STANDARD_DEVIATION,
            GROUPBY_FUNCTIONS.STD,
        ):
            return f"STDEV({formatted_col})"
        elif function is REDUCE_FUNCTION.KURTOSIS:
            return f"KURTOSIS({formatted_col})"
        elif function in (REDUCE_FUNCTION.SEM, GROUPBY_FUNCTIONS.SEM):
            return f"STDEV({formatted_col})/SQRT(COUNT({formatted_col}))"
        elif function in (REDUCE_FUNCTION.SKEW, GROUPBY_FUNCTIONS.SKEW):
            # TODO: Fix for PostgreSQL as SKEW does not exist
            return f"SKEW({formatted_col})"
        elif function in (REDUCE_FUNCTION.VARIANCE, GROUPBY_FUNCTIONS.VAR):
            return f"VAR({formatted_col})"
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
                f"CASE WHEN (SUM(CASE WHEN {formatted_col} < 0 THEN 1 ELSE 0 END)"
                f" % 2 = 0) THEN 1 ELSE -1 END "
                f"* EXP(SUM(LN(ABS({formatted_col}))))"
            )
        elif function in (REDUCE_FUNCTION.LOGICAL_OR, GROUPBY_FUNCTIONS.ANY):
            return f"BOOLOR_AGG({formatted_col})"
        elif function in (REDUCE_FUNCTION.LOGICAL_AND, GROUPBY_FUNCTIONS.ALL):
            return f"BOOLAND_AGG({formatted_col})"
        elif function in (REDUCE_FUNCTION.PERCENTILE, GROUPBY_FUNCTIONS.QUANTILE):
            if percentile is None:
                raise make_exception(
                    RuntimeError,
                    PonderError.POSTGRES_REDUCE_NODE_MISSING_PERCENTILE,
                    "Reduce node must have a percentile value for the PERCENTILE "
                    + "reduce function.",
                )
            return (
                f"PERCENTILE_CONT({percentile}) WITHIN GROUP "
                + f"(ORDER BY {formatted_col})"
            )
        elif function is REDUCE_FUNCTION.STR_CAT:
            if params_list is None:
                raise make_exception(
                    RuntimeError,
                    PonderError.POSTGRES_REDUCE_NODE_MISSING_PARAMS_LIST,
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
            return f"ARRAY_TO_STRING(ARRAY_AGG(IFNULL({formatted_col},{na_rep})),{sep})"
        elif function is GROUPBY_FUNCTIONS.NOOP:
            return formatted_col
        elif function is GROUPBY_FUNCTIONS.SIZE:
            return "COUNT(*)"
        elif function is REDUCE_FUNCTION.CONSTANT_ZERO:
            return "SUM(0)"
        else:
            raise make_exception(
                RuntimeError,
                PonderError.POSTGRES_COLUMN_WISE_REDUCE_INVALID_FUNCTION,
                f"Internal error: cannot execute column-wise reduce function {function}",  # noqa: E501
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
            f"MIN(0) AS {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}",
            f"MIN(0) AS {self.format_name(__PONDER_ROW_LABELS_COLUMN_NAME__)}",
        )
        formatted_other_col = None
        if other_col_id is not None:
            # Special case to add columns that will later become an index
            other_col = labels_to_apply_over[other_col_id]
            formatted_other_col = self.format_name(other_col)
            selects = (
                *selects,
                f"""MIN({other_col_id}) AS
                  {self.format_name(__PONDER_AGG_OTHER_COL_ID__)}""",
                f"""MIN('{other_col}') AS
                  {self.format_name(__PONDER_AGG_OTHER_COL_NAME__)}""",
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
        return (
            f"SELECT {', '.join(selects)} "
            f"FROM {self.generate_subselect_expression(input_node_sql)}"
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
            function_call = f"ARRAY_SIZE(ARRAY_DISTINCT(ARRAY_CONSTRUCT({cols})))"
        elif function is REDUCE_FUNCTION.COUNT_UNIQUE_EXCLUDING_NULL:
            function_call = (
                "ARRAY_SIZE(ARRAY_EXCEPT(ARRAY_DISTINCT("
                + f"ARRAY_CONSTRUCT({cols})), [NULL]))"
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
                PonderError.POSTGRES_ROW_WISE_REDUCE_INVALID_FUNCTION,
                f"Cannot execute row-wise reduce function {function}",
            )
        query = f"SELECT {order_and_labels_column_strings}"
        query += f", {function_call} AS {self.format_name(result_column_name)}"
        query += f" FROM {self.generate_subselect_expression(input_node_sql)}"
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
            # if the value translates to null in sql for this column type, tell postgres
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
                    PonderError.POSTGRES_ISIN_COLLECTION_UNSUPPORTED_VALUE,
                    f"Cannot apply isin to value {value} of type {type(value).__name__}",  # noqa: E501
                )
        # ARRAY_CONTAINS returns NULL for empty arrays, whereas pandas considers
        # isin(empty_array) to be vacuously false.
        return f"""
                IFNULL(
                    ARRAY_CONTAINS(
                        {self.format_name(column_name)}::variant,
                        ARRAY_CONSTRUCT({", ".join(value_strings)})
                    ),
                    FALSE
                )
            """

    def generate_dataframe_isin_series(
        self,
        column_name,
    ):
        return f"""
            IFNULL(
                {self.format_name(column_name)}::variant =
                    {self.format_name(__ISIN_SERIES_VALUES_COLUMN_NAME__)},
                FALSE
            )
        """

    def generate_dataframe_isin_dataframe(
        self,
        column_name,
    ):
        return f"""
            IFNULL(
                {self.format_name(column_name +
                    __ISIN_DATAFRAME_LEFT_PREFIX__)}::variant =
                    {self.format_name(column_name +
                        __ISIN_DATAFRAME_RIGHT_PREFIX__)}::variant,
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
            FLOOR(DATE_PART(nanosecond, {datetime_expression}) / 1000) +
            1000000 * (
                60 * 60 * DATE_PART(hour, {datetime_expression}) +
                60 * DATE_PART(minute, {datetime_expression}) +
                DATE_PART(second, {datetime_expression})
            )"""

        start_compare_time_maybe_timezone_adjusted = time_micros(
            f"convert_timezone('UTC', {formatted_index_name})"
            if compare_start_to_utc_time
            else formatted_index_name
        )
        end_compare_time_maybe_timezone_adjusted = time_micros(
            f"convert_timezone('UTC', {formatted_index_name})"
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
            # https://docs.postgres.com/en/sql-reference/operators-query.html#general-usage-notes
            node_column_names_set = set(node.dtypes.keys())
            final_column_names_set = set(column_names)
            if node_column_names_set != final_column_names_set:
                raise make_exception(
                    RuntimeError,
                    PonderError.POSTGRES_UNION_ALL_COLUMN_NAME_MISMATCH,
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
                FROM
                    {self.generate_subselect_expression(node.sql)}
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
        predicates = (
            f"{self.format_name(by)} = {self.format_value(key)}"
            for by, key in zip(by_columns, lookup_key)
        )
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
                    IFF(
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
                    IFF(
                        (
                            SELECT COUNT_IF({self.format_name(col)} IS NULL)
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
                        IFF(
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
        if columns is None or len(columns) == 0:
            return "WHERE FALSE"
        if thresh is not None:
            col_conditions = [
                f"IFF({self.format_name(col)} IS NULL, 0, 1)" for col in columns
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
                {postgres_unit},
                {diff_arg1},
                {diff_arg2}
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
        col_name_quoted = params_list[0]
        return f"DATE_PART(ns,{col_name_quoted}::timestamp)%1000"

    def generate_dt_microsecond(self, params_list):
        col_name_quoted = params_list[0]
        return f"FLOOR(DATE_PART(ns,{col_name_quoted}::timestamp)/1000)"

    def generate_dt_second(self, params_list):
        col_name_quoted = params_list[0]
        return f"SECOND({col_name_quoted}::timestamp)"

    def generate_dt_minute(self, params_list):
        col_name_quoted = params_list[0]
        return f"MINUTE({col_name_quoted}::timestamp)"

    def generate_dt_hour(self, params_list):
        col_name_quoted = params_list[0]
        return f"HOUR({col_name_quoted}::timestamp)"

    def generate_dt_day(self, params_list):
        col_name_quoted = params_list[0]
        return f"DAY({col_name_quoted}::timestamp)"

    def generate_dt_dayofweek(self, params_list):
        col_name_quoted = params_list[0]
        return f"DAYOFWEEKISO({col_name_quoted}::timestamp)-1"

    def generate_dt_day_name(self, params_list):
        col_name_quoted = params_list[0]
        return f"""
        IFF(
            DAYOFWEEK({col_name_quoted}::timestamp) = 0,
            'Sunday',
            IFF(
                DAYOFWEEK({col_name_quoted}::timestamp)=1,
                'Monday',
                IFF(
                    DAYOFWEEK({col_name_quoted}::timestamp)=2,
                    'Tuesday',
                    IFF(
                        DAYOFWEEK({col_name_quoted}::timestamp)=3,
                        'Wednesday',
                        IFF(
                            DAYOFWEEK({col_name_quoted}::timestamp)=4,
                            'Thursday',
                            IFF(
                                DAYOFWEEK({col_name_quoted}::timestamp)=5,
                                'Friday',
                                IFF(
                                    DAYOFWEEK({col_name_quoted}::timestamp)=6,
                                    'Saturday',
                                    NULL
                                )
                            )
                        )
                    )
                )
            )
        )"""

    def generate_dt_dayofyear(self, params_list):
        col_name_quoted = params_list[0]
        return f"DATE_PART(dy,{col_name_quoted}::timestamp)"

    def generate_dt_week(self, params_list):
        col_name_quoted = params_list[0]
        return f"WEEKISO({col_name_quoted}::timestamp)"

    def generate_dt_month(self, params_list):
        col_name_quoted = params_list[0]
        return f"MONTH({col_name_quoted}::timestamp)"

    def generate_dt_month_name(self, params_list):
        # the first param is the quoted column name.
        c = params_list[0]
        return f"""
        IFF(
            MONTH({c}::timestamp)=1,
            'January',
            IFF(
                MONTH({c}::timestamp)=2,
                'February',
                IFF(
                    MONTH({c}::timestamp)=3,
                    'March',
                    IFF(
                        MONTH({c}::timestamp)=4,
                        'April',
                        IFF(
                            MONTH({c}::timestamp)=5,
                            'May',
                            IFF(
                                MONTH({c}::timestamp)=6,
                                'June',
                                IFF(
                                    MONTH({c}::timestamp)=7,
                                    'July',
                                    IFF(
                                        MONTH({c}::timestamp)=8,
                                        'August',
                                        IFF(
                                            MONTH({c}::timestamp)=9,
                                            'September',
                                            IFF(
                                                MONTH({c}::timestamp)=10,
                                                'October',
                                                IFF(
                                                    MONTH({c}::timestamp)=11,
                                                    'November',
                                                    IFF(
                                                        MONTH({c}::timestamp)=12,
                                                        'December',
                                                        NULL
                                                    )
                                                )
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )"""

    def generate_dt_quarter(self, params_list):
        col_name_quoted = params_list[0]
        return f"DATE_PART(q,{col_name_quoted}::timestamp)"

    def generate_dt_year(self, params_list):
        col_name_quoted = params_list[0]
        return f"YEAR({col_name_quoted}::timestamp)"

    def generate_dt_tz_convert(self, params_list):
        col_name_quoted, tz = params_list

        return (
            f"CONVERT_TIMEZONE('UTC', {col_name_quoted})::TIMESTAMP_NTZ"
            if tz is None
            else f"CONVERT_TIMEZONE({self.format_value(tz)}, {col_name_quoted})"
        )

    def generate_dt_tz_localize(self, params_list):
        col_name_quoted, tz = params_list
        return (
            # If this column is already a TIMESTAMP_NTZ, this cast does nothing.
            # If the column is a TIMESTAMP_TZ, the cast drops the timezone and converts
            # to TIMESTAMP_NTZ.
            f"{col_name_quoted}::TIMESTAMP_NTZ"
            if tz is None
            # this seems to be the way to coerce a TIMESTAMP_NTZ to a particular
            # timezone. souce:
            # https://community.postgres.com/s/question/0D50Z00008xAmsUSAS/how-to-convert-timestampntz-to-timestamptz-independent-of-session-timezone
            # note that earlier layers should ensure we aren not trying to do this
            # conversion with a timestamp that is already timezone-aware.
            else f"""TIMESTAMP_TZ_FROM_PARTS(
                year({col_name_quoted}), month({col_name_quoted}),
                day({col_name_quoted}), hour({col_name_quoted}),
                minute({col_name_quoted}), second({col_name_quoted}),
                date_part(nanosecond, {col_name_quoted}), {self.format_value(tz)})"""
        )

    def generate_str_center(self, params_list):
        col_name_quoted, width, fillchar = params_list
        return f"""
        RPAD(
            LPAD(
                {col_name_quoted},
                GREATEST(
                    LEN({col_name_quoted}),
                    (
                        LEN({col_name_quoted}) +
                        ({width} - LEN({col_name_quoted}) - 1) / 2
                    )
                ),
                '{fillchar}'
            ),
            GREATEST(
                LEN({col_name_quoted}),
                {width}
            ),
            '{fillchar}'
        )
        """

    def generate_str_contains(self, params_list):
        col_name_quoted, pat, case, flags, na, regex = params_list
        if regex:
            pat = f".*{pat}.*"
            fn = "RLIKE"
            if flags & re.IGNORECASE == 0 and not case:
                flags = flags | re.IGNORECASE
            params = f", '{_regex_params(flags)}'"
        else:
            pat = f"%{pat}%"
            fn = "LIKE" if case else "ILIKE"
            params = ""
        if pandas.isnull(na):
            exp = f"{fn}({col_name_quoted},'{pat}'{params})"
        else:
            exp = f"IFNULL({fn}({col_name_quoted},'{pat}'{params}), '{na}')"
        return exp

    def generate_str_count(self, params_list):
        col_name_quoted, pat, flags = tuple(params_list)
        exp = f"REGEXP_COUNT({col_name_quoted},'{pat}',1,'{_regex_params(flags)}')"
        return exp

    def generate_str_decode(self, params_list):
        col_name_quoted, encoding, errors = tuple(params_list)
        pat = re.compile("^utf[ _\\-]*8")
        if encoding.lower() == "ascii" or pat.fullmatch(encoding.lower()):
            encoding = "utf-8"
        if encoding != "utf-8":
            raise make_exception(
                NotImplementedError,
                PonderError.POSTGRES_STR_DECODE_UNSUPPORTED_ENCODING,
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
                PonderError.POSTGRES_STR_ENCODE_UNSUPPORTED_ENCODING,
                "str.encode() only supports 'ascii' and 'utf8' encodings currently",
            )
        exp = f"TO_BINARY({col_name_quoted},'{encoding}')"
        return exp

    def generate_str_endswith(self, params_list):
        col_name_quoted, pat, na = params_list
        pat = f"%{pat}"
        if pandas.isnull(na):
            exp = f"LIKE({col_name_quoted},'{pat}')"
        else:
            exp = f"IFNULL(LIKE({col_name_quoted},'{pat}'), '{na}')"
        return exp

    def generate_str_extract(self, column_name, pat, flags):
        params = _regex_params(flags)
        return [
            f"""
                REGEXP_SUBSTR(
                    {self.format_name(column_name)},
                    {self.format_value(pat)},
                    1,
                    1,
                    {self.format_value(params)},
                    {i+1}
                )
                """
            for i in range(re.compile(pat).groups)
        ]

    def generate_str_find(self, params_list):
        col_name_quoted, sub, start, end = tuple(params_list)
        if start < 0:
            start_str = f"(GREATEST({start}+LEN({col_name_quoted}),0)+1)"
        else:
            start_str = f"{max(start,0)+1}"
        if end is None:
            exp = f"CHARINDEX('{sub}',{col_name_quoted},{start_str})-1"
        else:
            if end < 0:
                end_str = f"({end}+LEN({col_name_quoted}))"
            else:
                end_str = f"(LEAST(LEN({col_name_quoted}),{end}))"
            exp = f"CHARINDEX('{sub}',LEFT({col_name_quoted},{end_str}),{start_str})-1"
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
        params = f", '{_regex_params(flags)}'"
        if pandas.isnull(na):
            return f"RLIKE({col_name_quoted},'{pat}'{params})"
        return f"IFNULL(RLIKE({col_name_quoted},'{pat}'{params}), '{na}')"

    def generate_str_get(self, params_list):
        col_name_quoted, i = params_list
        # Need to cast to keep SQL compiler happy
        col_name_quoted = f"{col_name_quoted}::variant"
        if i >= 0:
            str_exp = f"SUBSTR({col_name_quoted},{i+1},1)"
            arr_exp = f"GET({col_name_quoted}, {i})"
        else:
            str_exp = f"""SUBSTR({col_name_quoted},
                                {i+1}+LEN({col_name_quoted}),1)"""
            arr_exp = f"""
            IFF({abs(i)} > ARRAY_SIZE({col_name_quoted}),
                NULL,
                GET({col_name_quoted}, ARRAY_SIZE({col_name_quoted})-{abs(i)})
            )
            """
        str_exp = f"IFF({str_exp}='',NULL,{str_exp})"
        return f"""
        CASE
            WHEN IS_ARRAY({col_name_quoted}) THEN {arr_exp}
            WHEN IS_VARCHAR({col_name_quoted}) THEN {str_exp}
        END
        """

    def generate_str_join(self, params_list):
        col_name_quoted, sep = params_list
        exp1 = f"ARRAY_TO_STRING(TO_ARRAY({col_name_quoted}),'{sep}')"
        exp2 = f"""
            CONCAT(
                REGEXP_REPLACE(
                    LEFT(
                        GET(
                            TO_ARRAY(
                                {col_name_quoted}
                            ),
                            0
                        ),
                        LEN(
                            GET(
                                TO_ARRAY(
                                    {col_name_quoted}
                                ),
                                0
                            )
                        ) -1
                    ),
                    '(.)','\\\\1{sep}'
                ),
                RIGHT(
                    GET(
                        TO_ARRAY(
                            {col_name_quoted}
                        ),
                    0),
                1)
            )"""
        exp = f"IFF(IS_ARRAY(TO_VARIANT({col_name_quoted})),{exp1},{exp2})"
        return exp

    def generate_str_ljust(self, params_list):
        col_name_quoted, width, fillchar = params_list
        exp = f"""
            RPAD(
                {col_name_quoted},
                GREATEST(
                    LEN({col_name_quoted}),
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
        params = f", '{_regex_params(flags)}'"
        if pandas.isnull(na):
            exp = f"RLIKE({col_name_quoted},'{pat}'{params})"
        else:
            exp = f"IFNULL(RLIKE({col_name_quoted},'{pat}'{params}), '{na}')"
        return exp

    # Unlike most other string functions, this method returns a list of strings because
    # it takes one column as input and returns three columns as output, each requiring
    # its own SQL expression.
    def generate_str_partition(self, column_name, sep, expand):
        col_name_quoted = self.format_name(column_name)
        sep_start = f"CHARINDEX('{sep}',{col_name_quoted})"
        if len(sep) == 1:
            sep_end = sep_start
        else:
            sep_end = f"{sep_start}+{len(sep)-1}"
        pre_sep = f"{sep_start}-1"
        post_sep = f"{sep_start}+{len(sep)}"
        part1 = f"LEFT({col_name_quoted},{pre_sep})"
        part2 = f"SUBSTR({col_name_quoted},{sep_start},{len(sep)})"
        part3 = f"SUBSTR({col_name_quoted},{post_sep},LEN({col_name_quoted})-{sep_end})"
        if expand:
            return [
                f"IFF({col_name_quoted} IS NULL,NULL,{part1})",
                f"IFF({col_name_quoted} IS NULL,NULL,{part2})",
                f"IFF({col_name_quoted} IS NULL,NULL,{part3})",
            ]
        return [
            f"""
                IFF(
                    {col_name_quoted} IS NULL,
                    NULL,
                    ARRAY_CONSTRUCT({part1},{part2},{part3})
                )
            """
        ]

    def generate_str_removeprefix(self, params_list):
        col_name_quoted, prefix = params_list
        exp = f"""
                IFF(
                    LEFT({col_name_quoted},{len(prefix)})='{prefix}',
                    SUBSTR({col_name_quoted},{len(prefix)+1}),
                    {col_name_quoted}
                )
            """
        return exp

    def generate_str_removesuffix(self, params_list):
        col_name_quoted, suffix = params_list
        exp = f"""
                IFF(
                    RIGHT({col_name_quoted},{len(suffix)})='{suffix}',
                    LEFT({col_name_quoted},LEN({col_name_quoted})-{len(suffix)}),
                    {col_name_quoted}
                )
            """
        return exp

    def generate_str_repeat(self, params_list):
        col_name_quoted, repeats = params_list
        exp = f"REPEAT({col_name_quoted},{repeats})"
        return exp

    def generate_str_replace(self, params_list):
        col_name_quoted, pat, repl, n, case, flags, regex = params_list
        if callable(repl):
            raise make_exception(
                NotImplementedError,
                PonderError.POSTGRES_STR_REPLACE_CALLABLE_REPL_NOT_IMPLEMENTED,
                "str.replace() does not support callable `repl` param yet",
            )
        if isinstance(pat, Pattern):
            raise make_exception(
                NotImplementedError,
                PonderError.POSTGRES_STR_REPLACE_COMPILED_REGEX_NOT_IMPLEMENTED,
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
            if flags == 0:
                params = ""
            else:
                params = f",'{_regex_params(flags)}'"
            if n <= 0:
                exp = f"REGEXP_REPLACE({col_name_quoted},'{pat}','{repl}',1,0{params})"
            else:
                split_idx = f"""
                        IFF(
                            REGEXP_INSTR({col_name_quoted},'{pat}',1,1,1{params})=0,
                            0,
                            IFF(
                                REGEXP_INSTR({col_name_quoted},'{pat}',1,{n},1{params})=0,
                                LEN({col_name_quoted})+1,
                                REGEXP_INSTR({col_name_quoted},'{pat}',1,{n},1{params})
                            )-1
                        )
                    """
                exp = f"""
                        CONCAT(
                            REGEXP_REPLACE(
                                LEFT({col_name_quoted},{split_idx}),
                                '{pat}',
                                '{repl}',
                                1,
                                0{params}
                            ),
                            RIGHT({col_name_quoted},LEN({col_name_quoted})-{split_idx})
                        )
                    """
        else:
            exp = f"REPLACE({col_name_quoted},'{pat}','{repl}')"
        return exp

    def generate_str_rfind(self, params_list):
        col_name_quoted, sub, start, end = params_list
        if start < 0:
            start_str = f"(GREATEST({start}+LEN({col_name_quoted}),0)+1)"
        else:
            start_str = f"{max(start,0)+1}"
        if end is None:
            end_str = f"LEN({col_name_quoted})+1"  # noqa F541
        else:
            if end < 0:
                end_str = f"({end}+LEN({col_name_quoted})+1)"
            else:
                end_str = f"(-1*GREATEST(-1*LEN({col_name_quoted}),{-1*end})+1)"
        exp = f"""
        IFF(
            {start_str} > LEN({col_name_quoted}) OR
            CHARINDEX(
                '{sub}',
                REVERSE(
                    SUBSTR(
                        {col_name_quoted},
                        {start_str},
                        {end_str} - {start_str}
                    )
                )
            ) = 0,
            -1,
            {end_str} - CHARINDEX(
                '{sub}',
                REVERSE(
                    SUBSTR(
                        {col_name_quoted},
                        {start_str},
                        {end_str} - {start_str}
                    )
                )
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
                LEN({col_name_quoted}),
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
                    LEN({col_name_quoted})-CHARINDEX(
                        '{sep[::-1]}',
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
        part3 = f"SUBSTR({col_name_quoted},{post_sep},LEN({col_name_quoted})-{sep_end})"
        if expand:
            return [
                f"IFF({col_name_quoted} IS NULL,NULL,{part1})",
                f"IFF({col_name_quoted} IS NULL,NULL,{part2})",
                f"IFF({col_name_quoted} IS NULL,NULL,{part3})",
            ]
        return [
            f"""
                IFF(
                    {col_name_quoted} IS NULL,
                    NULL,
                    ARRAY_CONSTRUCT({part1},{part2},{part3})
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
                f"IFF(REGEXP_LIKE({col_name_quoted},{regex_pat_extended}),{n+1},{n})"
            )
        else:
            regex_pat = f"REVERSE('{pat}')"
            exp = f"{col_name_quoted}"  # noqa F541
            n_for_split_idx = n
        if n <= 0:
            exp = f"SPLIT({exp},'{pat}')"
        else:
            split_idx = f"""
            1 + LEN(
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
            IFF({n+1} > ARRAY_SIZE(SPLIT({exp},'{pat}')),
                SPLIT({exp},'{pat}'),
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
            )
            """
        return exp

    def generate_str_slice(self, params_list):
        column_name_quoted, start, stop, step = params_list
        if start is None:
            start = 1
            start_str = f"1"  # noqa F541
        elif start < 0:
            start_str = f"(GREATEST({start}+LEN({column_name_quoted}),0)+1)"
        else:
            start_str = f"{max(start,0)+1}"
        if stop is None:
            stop_str = f"(LEN({column_name_quoted})+1)"  # noqa F541
        elif stop < 0:
            stop_str = f"({stop}+LEN({column_name_quoted})+1)"
        else:
            stop_str = f"(-1*GREATEST(-1*LEN({column_name_quoted}),{-1*stop})+1)"
        if step is None or step == 1:
            exp = f"SUBSTR({column_name_quoted},{start_str},{stop_str}-{start_str})"
        else:
            if start * stop < 0 or stop is None:
                raise make_exception(
                    NotImplementedError,
                    PonderError.POSTGRES_STR_SLICE_UNSUPPORTED_START_STOP_STEP_COMBINATION,  # noqa: E501
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
            start_str = f"(GREATEST({start}+LEN({column_name_quoted}),0)+1)"
        else:
            start_str = f"{max(start,0)+1}"
        if stop is None:
            stop_str = f"(LEN({column_name_quoted})+1)"  # noqa F541
        elif stop < 0:
            stop_str = f"({stop}+LEN({column_name_quoted})+1)"
        else:
            stop_str = f"(-1*GREATEST(-1*LEN({column_name_quoted}),{-1*stop})+1)"
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
                LEN(
                    {column_name_quoted}
                ) - {stop_str} + 1
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
                f"IFF(REGEXP_LIKE({col_name_quoted},{regex_pat_extended}),{n+1},{n})"
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
            IFF({n+1} > ARRAY_SIZE(SPLIT({exp},'{pat}')),
                SPLIT({exp},'{pat}'),
                ARRAY_APPEND(
                    ARRAY_SLICE(
                        SPLIT({exp},'{pat}'),
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
            exp = f"LIKE({col_name_quoted},'{pat}')"
        else:
            exp = f"IFNULL(LIKE({col_name_quoted},'{pat}'), '{na}')"
        return exp

    def generate_str_wrap(self, params_list):
        col_name_quoted, width = params_list
        exp = f"""
                IFF(
                    LEN({col_name_quoted})%{width}=0,
                    LEFT(REGEXP_REPLACE({col_name_quoted},'(.{{{{{width}}}}})','\\\\1\\n',1,0),LEN({col_name_quoted})*(1+1/{width})-1),
                    REGEXP_REPLACE({col_name_quoted},'(.{{{{{width}}}}})','\\\\1\\n',1,0)
                )
            """
        return exp

    def generate_str_capitalize(self, params_list):
        col_name_quoted = params_list[0]
        return f"""
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
                    LEN({col_name_quoted}) - 1
                )
            )
        )"""

    def generate_str_isalnum(self, params_list):
        col_name_quoted = params_list[0]
        return f"RLIKE({col_name_quoted}, '[a-zA-Z0-9]+')"

    def generate_str_isalpha(self, params_list):
        col_name_quoted = params_list[0]
        return f"RLIKE({col_name_quoted}, '[a-zA-Z]+')"

    def generate_str_isdecimal(self, params_list):
        col_name_quoted = params_list[0]
        return f"RLIKE({col_name_quoted}, '[0-9]+')"

    def generate_str_isdigit(self, params_list):
        col_name_quoted = params_list[0]
        return f"RLIKE({col_name_quoted}, '[0-9]+')"

    def generate_str_islower(self, params_list):
        col_name_quoted = params_list[0]
        return f"""
            RLIKE(
                {col_name_quoted},
                '.*[a-zA-Z]+.*'
            ) AND
            {col_name_quoted} = LOWER({col_name_quoted})"""

    def generate_str_isnumeric(self, params_list):
        col_name_quoted = params_list[0]
        return f"RLIKE({col_name_quoted}, '[0-9]+')"

    def generate_str_istitle(self, params_list):
        col_name_quoted = params_list[0]
        return f"""
        RLIKE(
            {col_name_quoted},
            '.*[a-zA-Z]+.*'
        ) AND
        {col_name_quoted} = INITCAP({col_name_quoted})"""

    def generate_str_isupper(self, params_list):
        col_name_quoted = params_list[0]
        return f"""
        RLIKE({col_name_quoted}, '.*[a-zA-Z]+.*') AND
        {col_name_quoted} = UPPER({col_name_quoted})"""

    def generate_new_row_labels_columns_command(
        self, new_row_label_column_names, column_names, input_node_sql, new_row_labels
    ):
        if len(new_row_label_column_names) > 1:
            raise make_exception(
                NotImplementedError,
                PonderError.POSTGRES_NEW_ROW_LABELS_MULTIPLE_COLUMNS,
                "Ponder Internal Error: cannot create multiindex from python objects",
            )
        new_row_label_column_name = new_row_label_column_names[0]
        left_formatted_column_names = ", ".join(
            f"LEFT_TABLE.{self.format_name(col)}" for col in column_names
        )
        return f"""
                SELECT
                    LEFT_TABLE.{self.format_name(__PONDER_ORDER_COLUMN_NAME__)},
                    RIGHT_TABLE.{self.format_name(new_row_label_column_name)},
                    {left_formatted_column_names}
                FROM ({input_node_sql}) AS LEFT_TABLE
                INNER JOIN (
                    SELECT
                        _ROW_ORDER_VALS_,
                        {self.format_name(new_row_label_column_name)}
                    FROM (
                        VALUES{", ".join(str((k, v))
                                         for k, v in new_row_labels.items())})
                        AS RIGHT_TABLE(_ROW_ORDER_VALS_,
                          {self.format_name(new_row_label_column_name)})
                ) AS RIGHT_TABLE
                ON
                    LEFT_TABLE.{self.format_name(__PONDER_ORDER_COLUMN_NAME__)} =
                        RIGHT_TABLE._ROW_ORDER_VALS_
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
                f"""IFF(
                        EQUAL_NULL({formatted_self_name}, {formatted_other_name}),
                        NULL,
                        {formatted_self_name})"""
            )
            column_types.append(type)
            column_names.append(f"{column}_other")
            column_expressions.append(
                f"""IFF(
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
                PonderError.POSTGRES_CROSS_JOIN_PURPOSE_NOT_IMPLEMENTED,
                f"Cross join for the purpose {purpose} not implemented yet",
            )

        view_names = kwargs.get("view_names", None)
        if view_names is None:
            view_names = ["", ""]
        elif len(view_names) != 2:
            raise make_exception(
                TypeError,
                PonderError.POSTGRES_CROSS_JOIN_VIEW_NAMES_LENGTH_NOT_2,
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
                PonderError.POSTGRES_CROSS_JOIN_WIN_TYPE_NOT_IMPLEMENTED,
                f"Cross join with {win_type} not implemented yet",
            )

        # COMMENT: Add other win_types under here if the templates fits
        # them as well
        common_exp_prefix = f"""
            IFF(COUNT({view_names[1]}{self.format_name(col)}) < {window},
            NULL, {win_func}
        """

        if win_type is not None and win_type.lower() == "gaussian":
            # This is deliberately made as a list instead of equality check
            # to make it extendable
            if win_func not in ["SUM", "AVG", "STDEV", "VAR"]:
                raise make_exception(
                    NotImplementedError,
                    PonderError.POSTGRES_GAUSSIAN_AGGREGATION_FUNCTION_NOT_IMPLEMENTED,
                    f"Gaussian aggregation function {win_func} not implemented yet.",
                )
            std = kwargs.get("std", None)
            weight = f"""
                EXP(-0.5 * POW(({window - (window+1)/2} -
                    {view_names[0]}{self.format_name(__PONDER_ORDER_COLUMN_NAME__)} +
                    {view_names[1]}{self.format_name(__PONDER_ORDER_COLUMN_NAME__)})/{std}, 2))"""  # noqa
            if win_func == "SUM":
                return f"""
                    IFF(
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
                if math.isinf(weighting_ratio):
                    weighting_ratio = "NULL"

                window_specs = f"""
                    OVER (
                        ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                        ROWS BETWEEN {window} PRECEDING AND CURRENT ROW
                    )
                """
                window_specs = ""
                if win_func == "AVG":
                    return f"""
                        IFF(
                            COUNT({view_names[1]}{self.format_name(col)}) < {window},
                            NULL,
                            SUM({weight} * {view_names[1]}{self.format_name(col)}) /
                            {sum_weights}
                        )
                    """
                elif win_func == "VAR":
                    return f"""
                        IFF(
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
                    return f"""
                        IFF(
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
            IFF(COUNT({view_names[1]}{self.format_name(col)}) < {window},
            NULL, PERCENTILE_CONT({quantile})
            WITHIN GROUP (ORDER BY ({view_names[1]}{self.format_name(col)})))
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
                +(COUNT_IF(
                    {view_names[1]}{self.format_name(col)}=
                    {view_names[0]}{self.format_name(col)}
                )+1)/2
                """
            return f"""
            IFF(COUNT({view_names[1]}{self.format_name(col)}) < {window},
            NULL, IFF({view_names[0]}{self.format_name(col)} IS NULL, NULL, COUNT_IF(
                {view_names[1]}{self.format_name(col)}{comp}
                {view_names[0]}{self.format_name(col)}
            )){addend})
            """
        elif win_func in ["MEDIAN", "KURTOSIS", "SKEW"]:
            return f"""
            {common_exp_prefix}({view_names[1]}{self.format_name(col)}))
            """
        else:
            raise make_exception(
                NotImplementedError,
                PonderError.POSTGRES_WINDOW_FUNCTION_NOT_IMPLEMENTED,
                f"Aggregation function {win_func} not implemented yet.",
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
                PonderError.POSTGRES_CROSS_JOIN_FULL_NOT_IMPLEMENTED,
                f"Cross join for the purpose {purpose} not implemented yet",
            )

        view_names = kwargs.get("view_names", None)
        if view_names is None or len(view_names) != 2:
            raise make_exception(
                TypeError,
                PonderError.BIGQUERY_CROSS_JOIN_VIEW_NAMES_LENGTH_NOT_2,
                f"{view_names} has problems.",
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
        # The aggregation with IFF statement which comes from our
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
                {view_names[0]}.{self.format_name(__PONDER_ORDER_COLUMN_NAME__)} -
                {view_names[1]}.{self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                 < {window_size}
                AND {view_names[0]}.{self.format_name(__PONDER_ORDER_COLUMN_NAME__)} -
                {view_names[1]}.{self.format_name(__PONDER_ORDER_COLUMN_NAME__)} >= 0
            """
        else:
            condition = f"""
                {view_names[0]}.{self.format_name(__PONDER_ORDER_COLUMN_NAME__)} >=
                {view_names[1]}.{self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
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
              GROUP BY {view_names[0]}.{self.format_name(__PONDER_ORDER_COLUMN_NAME__)},
               {groupby_cols}
              ORDER BY {view_names[0]}.{self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
            """

    def generate_diff(self, column_name, periods, partition_by_clause=""):
        column_name = self.format_name(column_name)
        order_col = __PONDER_ORDER_COLUMN_NAME__
        # periods can be negative in Snowflake and DuckDB, but may need to use LEAD
        # for other DBs.
        lag_window = f"""LAG({column_name}, {periods}) OVER (
            {partition_by_clause}
            ORDER BY {self.format_name(order_col)}
            )"""

        return f"({column_name} - {lag_window})"

    def generate_subselect_expression(self, input_sql):
        return f"({input_sql}) AS PONDER_INPUT"

    def generate_cast_to_type_command(self, col, cast_type):
        return (
            f"CAST({self.format_name(col)} AS "
            f"{self.pandas_type_to_mssql_type_map[cast_type]})"
        )
