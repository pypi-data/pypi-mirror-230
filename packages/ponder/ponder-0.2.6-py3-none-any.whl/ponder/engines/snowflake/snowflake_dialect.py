import hashlib
import math
import re
import uuid
from datetime import datetime

import pandas
from pandas._libs.lib import no_default

from ponder.core.common import (
    __PONDER_ORDER_COLUMN_NAME__,
    __PONDER_ROW_LABELS_COLUMN_NAME__,
    APPLY_FUNCTION,
    GROUPBY_FUNCTIONS,
    REDUCE_FUNCTION,
    generate_column_name_from_value,
)
from ponder.core.error_codes import PonderError, make_exception
from ponder.core.sql_dialect import (
    _pandas_offset_object_to_n_and_sql_unit,
    _pandas_offset_object_to_seconds,
    _pandas_start_val_to_end_period,
)

from ..postgres.postgres_dialect import postgres_dialect


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


class snowflake_dialect(postgres_dialect):
    pandas_type_to_snowflake_type_map = {
        "bool": "BOOLEAN",
        "date": "DATETIME",
        "datetime64[ms]": "TIMESTAMP",
        "datetime64[ns]": "TIMESTAMP",
        "datetime": "TIMESTAMP",
        "float": "FLOAT",
        "float64": "REAL",
        "uint8": "INT",
        "int": "INT",
        "int8": "BIGINT",
        "int16": "BIGINT",
        "int32": "BIGINT",
        "int64": "BIGINT",
        "str": "STRING",
        "object": "TEXT",
        "<class 'list'>": "ARRAY",
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
            return f"({table_or_query})"
        if "." in table_or_query:
            return table_or_query
        return f'"{table_or_query}"'

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
        # TODO(REFACTOR): Should deal with no_default at API layer
        if value is no_default or value is None or pandas.isnull(value):
            return "NULL"
        if isinstance(value, pandas.Timestamp):
            return f"'{value}'"
        if isinstance(value, str):
            new_value = value.replace("\\", "\\\\").replace("'", "\\'")
            return f"'{new_value}'"
        return f"{value}"

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
        return (
            f"TO_TIMESTAMP({self.format_name(time_column)}, "
            f"'{datetime_format}')::DATETIME"
        )

    def set_obfuscate(self):
        self._obfuscate = True

    def generate_autoincrement_type(self):
        return "NUMBER AUTOINCREMENT(0, 1)"

    def generate_get_current_database_command(self):
        return "SELECT CURRENT_DATABASE()"

    def generate_get_current_schema_command(self):
        return "SELECT CURRENT_SCHEMA()"

    def generate_put_command(self, file_path, table_name):
        changed_file_path = file_path.replace("\\", "/")
        command = f"put 'file://{changed_file_path}' @%{table_name}"
        return command

    def generate_get_command(self, stage_path, local_path):
        command = "get " + "@" + stage_path + " file://" + local_path + ";"
        return command

    def generate_remove_file_from_staging_command(self, stage_path):
        return f"REMOVE @{stage_path}"

    def generate_use_warehouse_command(self, warehouse_name):
        return "USE WAREHOUSE " + self.format_name(warehouse_name) + ";"

    def generate_use_database_command(self, database_name):
        return "USE DATABASE " + self.format_name(database_name) + ";"

    def generate_use_schema_command(self, schema_name):
        return "USE SCHEMA " + self.format_name(schema_name) + ";"

    def generate_use_role_command(self, role_name):
        return "USE ROLE " + self.format_name(role_name) + ";"

    def generate_use_admin_role_command(self):
        return "USE ROLE SYSADMIN;"

    def generate_query_tag_command(self):
        return 'ALTER SESSION SET QUERY_TAG="PONDER QUERY"'

    def generate_query_timeout_command(self, query_timeout):
        return f"ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS={query_timeout}"

    def generate_read_table_metadata_statement(self, table_or_query):
        formatted_table_or_query = self.format_table_name(table_or_query)
        return f"SELECT * FROM ({formatted_table_or_query}) LIMIT 1"

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
        if header is not None and isinstance(header, int):
            skip_header = header + 1
        columns_clause = ", ".join(
            [self.format_name(column_name) for column_name in column_names]
        )

        from_clause = ", ".join(
            [
                f"${column_index}"
                if (
                    self.pandas_type_to_snowflake_type_map[str(column_type)]
                    != "BOOLEAN"
                )
                else f"TO_BOOLEAN(${column_index})"
                for column_index, column_type in zip(
                    [i for i in range(1, len(column_types) + 1)], column_types
                )
            ]
        )
        from_clause = f" FROM ( SELECT {from_clause} FROM @%{table_name} )"

        on_error_fragment = "ON_ERROR=CONTINUE" if on_bad_lines == "skip" else ""

        command = (
            f"COPY INTO {table_name} ( {columns_clause} ) {from_clause} purge = true"
            f" file_format = (type = csv NULL_IF=('{na_values}', '')"
            f" FIELD_OPTIONALLY_ENCLOSED_BY='\"' FIELD_DELIMITER='{sep}' "
            f"DATE_FORMAT='{date_format}' SKIP_HEADER={skip_header}, "
            f"ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE) {on_error_fragment}"
        )
        return command

    def generate_copy_into_stage_command(
        self,
        columns_list,
        query,
        file_name,
        sep=",",
        header=True,
        date_format=None,
        na_rep="",
    ):
        formatted_columns_list = [
            self.format_name(col_name) for col_name in columns_list
        ]
        input_sql_query = (
            f"""SELECT {",".join(formatted_columns_list)} FROM ({query})"""
        )
        snowflake_na_value_option = "{" + f"'{na_rep}'" + "}" if len(na_rep) > 0 else ""
        null_if = (
            f"NULL_IF = {snowflake_na_value_option}"
            if len(snowflake_na_value_option) > 0
            else "NULL_IF = ''"
        )
        date_format_fragment = (
            f"DATE_FORMAT = {date_format}"
            if date_format is not None and len(date_format) > 0
            else ""
        )
        header_fragment = ""

        if header:
            header_fragment = " HEADER = TRUE "
        file_format_fragment = f"""FILE_FORMAT = (TYPE = csv {null_if}
            COMPRESSION='gzip'
            FIELD_DELIMITER='{sep}' FIELD_OPTIONALLY_ENCLOSED_BY='\"'
            {date_format_fragment})"""

        command = f"""COPY INTO @~/{file_name} FROM ({input_sql_query})
            {file_format_fragment} {header_fragment}
            MAX_FILE_SIZE = 5000000000 SINGLE = TRUE"""
        return command

    def generate_copy_into_table_parquet_command(
        self,
        table_name,
        column_names,
    ):
        formatted_cols = [self.format_name(column_name) for column_name in column_names]

        columns_clause = ",".join(formatted_cols)
        parquet_cols = "$1:" + ",$1:".join(formatted_cols)
        from_clause = f" FROM ( SELECT {parquet_cols} FROM @%{table_name} )"

        command = (
            f"COPY INTO {table_name} ( {columns_clause} ) {from_clause}"
            f" FILE_FORMAT=(TYPE=PARQUET COMPRESSION=AUTO)"
            f" PURGE=TRUE ON_ERROR=ABORT_STATEMENT"
        )
        return command

    def get_database_type_for_pandas_type(self, pandas_type):
        return self.pandas_type_to_snowflake_type_map[str(pandas_type)]

    def generate_apply_command(
        self,
        input_node_sql,
        function_name,
        input_column_names,
        input_column_types,
        output_column_names,
        output_alias_map,
    ):
        # We need to rename output columns from the UDTF back to whatever they were
        # we could use ChangeColumns or something but that seems unnecessary.
        renamed_output_cols = []
        for output_col in output_column_names:
            if output_col not in output_alias_map:
                raise make_exception(
                    KeyError,
                    PonderError.SNOWFLAKE_APPLY_OUTPUT_ALIAS_MAP_MISSING_KEYS,
                    f"columns {output_col} was not found in the alias map",
                )
            renamed_output_cols.append(
                f"""
                {self.format_name(output_col)} AS
                {self.format_name(output_alias_map[output_col])}
                """
            )

        select_columns_fragment = ", ".join(renamed_output_cols)

        input_column_names_types = zip(
            input_column_names,
            [
                self.get_database_type_for_pandas_type(input_col_type)
                for input_col_type in input_column_types
            ],
        )

        input_columns_fragment = ", ".join(
            [
                f"{self.format_name(input_column_name)}::{input_column_type}"
                for (input_column_name, input_column_type) in input_column_names_types
            ]
        )

        return f"""
                SELECT
                    {select_columns_fragment}
                FROM
                    ({input_node_sql}),
                TABLE({function_name}
                    ({input_columns_fragment}))
                """

    def generate_udf_function_body(self, apply_type, na_action, func_args, func_kwargs):
        arg_list = []
        for arg in func_args:
            arg_list.append(arg)
        for arg, val in func_kwargs.items():
            arg_list.append(f"{arg}={val}")

        arg_list_str = ", ".join(map(str, arg_list))

        if apply_type == APPLY_FUNCTION.ELEMENT_WISE:
            na_action_str = f"'{na_action}'" if na_action else na_action
            if len(arg_list_str) == 0:
                return f"""def func(x):
            return x.map(self._func, na_action={na_action_str})
                """
            else:
                return f"""def func(x):
            return x.map(self._func, na_action={na_action_str}, {arg_list_str})
                """
        elif apply_type == APPLY_FUNCTION.ROW_WISE:
            if len(arg_list_str) == 0:
                return """def func(x):
            return self._func(x)
                """
            else:
                return f"""def func(x):
            return self._func(x, {arg_list_str})
                """
        else:
            raise make_exception(
                NotImplementedError,
                PonderError.SNOWFLAKE_APPLY_TYPE_NOT_SUPPORTED,
                f"apply() with {apply_type} is not implemented yet",
            )

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
        formatted_thrice_pivot_column_name = self.format_name_thrice(pivot_column_name)

        str_unique_values = [
            generate_column_name_from_value(unique_value)
            for unique_value in unique_values
        ]

        # Snowflake adds quotes around names that have non-capital letters. For example
        # 'JAN_a' would be a quoted name, where as 'JAN_A' would not have any quotes.
        # In order to handle these cases, we need to see if each col_name matches the
        # regex pattern and then format them once or thrice as needed.
        formatted_once_or_thrice_col_expressions = []
        formatted_once_final_values_column_names = []
        new_columns_prefix = (
            values_column_name + "_" if add_qualifier_to_new_column_names else ""
        )
        for v in str_unique_values:
            col_name = new_columns_prefix + v
            if self._valid_name_regex_pattern.fullmatch(col_name):
                final_col = self.format_name(col_name)
            else:
                final_col = self.format_name_thrice(col_name)
            formatted_once_or_thrice_col_expressions.append(
                f"{final_col} as {self.format_name(col_name)}"
            )
            formatted_once_final_values_column_names.append(self.format_name(col_name))

        """
        When the user doesn't specify a column over which aggregation can be done,
        Pandas doesn't do any aggregation.  But the PIVOT command supported
        by databases always will.  In this case the result will be reduced to
        one record which is the result of the aggregation over the entire input
        dataset.  To prevent the aggregation from happening, use the row number
        column from the input node.  Since the row number column will have unique values
        in every row (think group by where the group by column has a unique value
        for every record), the Pandas behavior can be effective mimic'ed.
        """
        grouping_column_expression = f"""{formatted_thrice_pivot_column_name},
            {formatted_thrice_pivot_column_name} AS {__PONDER_ORDER_COLUMN_NAME__}, """
        with_expression_fragment = f"""WITH _PONDER_PIVOT_GB_ AS (
                SELECT
                    {self.format_name(values_column_name)},
                    {input_node_order_column_name},
                    {formatted_pivot_column_name}
                FROM (
                    {input_node_query}
                )
            )"""
        formatted_once_final_values_column_names.insert(
            0, f"{formatted_pivot_column_name}"
        )

        ret_val = f"""
            SELECT
                {grouping_column_expression}
                {", ".join(formatted_once_or_thrice_col_expressions)}
            FROM (
                {with_expression_fragment}
                SELECT
                    *
                FROM
                    _PONDER_PIVOT_GB_
                    PIVOT(
                        {aggregation_call}
                        FOR {formatted_pivot_column_name} in (
                        {", ".join([f"{self.format_value(val)}"
                        for val in unique_values])})
                    )
                AS P(
                    {", ".join(formatted_once_final_values_column_names)}
                )
            )
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
                PonderError.SNOWFLAKE_PIVOT_UNSUPPORTED_AGGREGATION_FUNCTION,
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

        # Snowflake adds quotes around names that have non-capital letters. For example
        # 'JAN_a' would be a quoted name, where as 'JAN_A' would not have any quotes.
        # In order to handle these cases, we need to see if each col_name matches the
        # regex pattern and then format them once or thrice as needed.
        formatted_once_or_thrice_col_expressions = []
        formatted_once_final_values_column_names = []
        if add_qualifier_to_new_column_names:
            qualifier = values_column_name + "_"
        else:
            qualifier = ""
        for v in str_unique_values:
            col_name = qualifier + v
            if self._valid_name_regex_pattern.fullmatch(col_name):
                final_col = self.format_name(col_name)
            else:
                final_col = self.format_name_thrice(col_name)
            formatted_once_or_thrice_col_expressions.append(
                f"{final_col} as {self.format_name(col_name)}"
            )
            formatted_once_final_values_column_names.append(self.format_name(col_name))

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
                {", ".join(formatted_once_or_thrice_col_expressions)}
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
                        {", ".join([f"{self.format_value(val)}"
                        for val in unique_values])})
                    )
                AS P(
                    {formatted_group_col_name_once},
                    {", ".join(formatted_once_final_values_column_names)}
                )
            )
        """

    def generate_downsample_command(
        self,
        col,
        offset: pandas.DateOffset,
        start_val: pandas.Timestamp,
        end_val: pandas.Timestamp,
        sum_interval: float,
    ):
        n, unit = _pandas_offset_object_to_n_and_sql_unit(offset)
        if unit in ("second", "minute", "hour", "day"):
            return (
                f"TIME_SLICE({self.format_name(col)}, {n}, {self.format_value(unit)})"
            )
        else:
            # Case week/month/quarter/year returns the end of the
            # specified sampling period
            n_sec = _pandas_offset_object_to_seconds(offset)
            if n_sec > sum_interval or n == 1:
                # Case where we only have a single bin or the sampling
                # frequency is 1, so we do need need to shift to special
                # case the first value
                return (
                    f"LAST_DAY(TIME_SLICE({self.format_name(col)}, {n}, "
                    f"{self.format_value(unit)}), {self.format_value(unit)})"
                )
            start_val = _pandas_start_val_to_end_period(start_val, unit)
            return (
                f"LAG(LAST_DAY(TIME_SLICE({self.format_name(col)}, {n},"
                f"{self.format_value(unit)}, 'end'), {self.format_value(unit)}),"
                f" 1, {self.format_value(start_val)})"
                f"OVER (ORDER BY {__PONDER_ORDER_COLUMN_NAME__})"
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

        start_val_dt = datetime.strptime(start_val, "%Y-%m-%d %H:%M:%S")
        end_val_dt = datetime.strptime(end_val, "%Y-%m-%d %H:%M:%S")
        sum_seconds = (end_val_dt - start_val_dt).total_seconds()

        # Get number of seconds in the offset on average
        n_sec = _pandas_offset_object_to_seconds(offset, average_seconds=True)
        row_count = math.floor((sum_seconds / n_sec) + 1)
        if unit in ("second", "minute", "hour", "day"):
            return (
                f"(SELECT TIMEADD({self.format_value(unit)}, SEQ4() * {n}, "
                f"{self.format_value(start_val)}) AS"
                f"{self.format_name('generate_series')} "
                f"FROM TABLE(GENERATOR(rowcount => {row_count})))"
            )
        else:
            return (
                f"(SELECT LAST_DAY(TIMEADD({self.format_value(unit)}, SEQ4() * {n}, "
                f"{self.format_value(start_val)}), "
                f"{self.format_value(unit)}) AS "
                f"{self.format_name('generate_series')} "
                f"FROM TABLE(GENERATOR(rowcount => {row_count})))"
            )

    def generate_select_count_star_statement(self, table):
        formatted_table_name = self.format_table_name(table)
        return f"SELECT COUNT(*) FROM ({formatted_table_name});"

    def generate_upsample_command(
        self,
        col,
        offset: pandas.DateOffset,
        start_val: pandas.Timestamp,
        end_val: pandas.Timestamp,
        sum_interval: float,
        interval: float,
    ):
        # Use GENERATOR to create rows based on the start_val
        n, unit = _pandas_offset_object_to_n_and_sql_unit(offset)
        n_sec = _pandas_offset_object_to_seconds(offset)
        row_count = math.floor((sum_interval / n_sec) + 1)
        start_val = _pandas_start_val_to_end_period(start_val, unit)
        return (
            f"SELECT TIME_SLICE({self.format_name('generate_series')}, "
            f"{interval}, {self.format_value('second')}) "
            f"AS {self.format_name(col)}, {self.format_name('generate_series')} FROM "
            f"(SELECT TIMEADD({self.format_value(unit)}, SEQ4() * {n}, "
            f"{self.format_value(start_val)}) AS "
            f"{self.format_name('generate_series')} "
            f"FROM TABLE(GENERATOR(rowcount => {row_count})))"
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
        group_by_column_string_for_order_fragment = (
            f" ARRAY_CONSTRUCT({group_by_column_string_for_order})"
        )
        result_order_column_expression = (
            f"{group_by_column_string_for_order_fragment} AS"
            f" {result_order_column_name}"
        )

        return result_order_column_expression

    def generate_groupby_window_first_expression(
        self, formatted_col, partition_by_clause
    ):
        return f"""
            FIRST_VALUE({formatted_col})
            IGNORE NULLS
            OVER (
                {partition_by_clause}
                ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            )"""

    def generate_groupby_window_last_expression(
        self, formatted_col, partition_by_clause
    ):
        return f"""
            LAST_VALUE({formatted_col})
            IGNORE NULLS
            OVER (
                {partition_by_clause}
                ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
                ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
            )"""

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
            # this hack is from here:
            # https://stackoverflow.com/a/15040616/17554722
            # ARRAY_UNIQUE_AGG ignores nulls, so the first summand gets
            # the count of distinct non-null values. The second summand
            # replaces null values with placeholder 1 and non-null
            # values with null, so the second `ARRAY_UNIQUE_AGG`
            # returns 1 if there's anything not null and 0 otherwise.
            transformed = f"ARRAY_SIZE(ARRAY_UNIQUE_AGG({formatted_col}))"
            transformed += (
                f" + ARRAY_SIZE(ARRAY_UNIQUE_AGG(IFF({formatted_col} IS NULL, "
                + "1, NULL)))"
            )
            return transformed
        elif function is REDUCE_FUNCTION.COUNT_UNIQUE_EXCLUDING_NULL:
            # snowflake docs say that computing unique count this way can be
            # faster than COUNT(DISTINCT):
            # https://docs.snowflake.com/en/user-guide/querying-arrays-for-distinct-counts.html#example-1-counting-the-distinct-values-in-a-single-table
            return f"ARRAY_SIZE(ARRAY_UNIQUE_AGG({formatted_col}))"
        elif function is GROUPBY_FUNCTIONS.UNIQUE:
            # TODO: FIX-[POND-931] ARRAY_UNIQUE_AGG does not account for NULL values
            return f"ARRAY_UNIQUE_AGG({formatted_col})"
        elif function in (REDUCE_FUNCTION.MEAN, GROUPBY_FUNCTIONS.MEAN):
            return f"AVG({formatted_col})"
        elif function in (REDUCE_FUNCTION.MEDIAN, GROUPBY_FUNCTIONS.MEDIAN):
            return f"MEDIAN({formatted_col})"
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
                f"IFF((COUNT_IF({formatted_col} < 0) % 2) = 0, 1, -1) "
                + f"* EXP(SUM(LN(ABS({formatted_col}))))"
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

    def generate_timedelta_to_datetime_addend(self, timedelta: pandas.Timedelta):
        return timedelta / pandas.Timedelta("1ns")

    def generate_scalar_timestamp_for_subtraction(
        self, timestamp: pandas.Timestamp
    ) -> str:
        return f"'{timestamp}'"

    def generate_datetime_plus_timedelta(
        self, datetime_sql: str, timedelta_sql: str
    ) -> str:
        return f"TIMESTAMPADD('nanosecond', {timedelta_sql}, {datetime_sql})"

    def generate_datetime_minus_timedelta(self, left_sql: str, right_sql: str) -> str:
        # can pass numbers to TIMESTAMPADD, but not to TIMESTAMPDIFF. Instead of
        # subtracting `self._rhs` seconds, add `-self._rhs` seconds.
        return f"TIMESTAMPADD('nanosecond', -({right_sql}), {left_sql})"

    def generate_datetime_minus_datetime(self, left_sql: str, right_sql: str) -> str:
        return f"TIMESTAMPDIFF('nanosecond', {right_sql}, {left_sql})"

    def generate_number_to_datetime_cast(self, column_name, column_type, **kwargs):
        unit = kwargs.get("unit", "ns")
        unit = unit if unit is not None else "ns"
        column_name = self.format_name(column_name)
        if column_type == "float":
            if unit == "ns":
                column_name = f"FLOOR({column_name})"
            else:
                if unit in ["s", "ms", "us"]:
                    scale = {"s": 1e9, "ms": 1e6, "us": 1e3}[unit]
                    column_name = f"FLOOR({column_name} * {scale})"
                    unit = "ns"
        origin = kwargs.get("origin", "unix")
        if origin == "unix":
            operand1 = "TO_TIMESTAMP('1970-01-01')"
        elif isinstance(origin, (int, float)):
            epoch_time = "TO_TIMESTAMP('1970-01-01 00:00:00')"
            if column_type == "float":
                origin = f"FLOOR({origin})"
            operand1 = f"TIMESTAMPADD('millisecond', {origin}, {epoch_time})"
        else:
            timestamp_str = pandas.Timestamp(origin).strftime("%Y-%m-%d %H:%M:%S.%f")
            operand1 = f"TO_TIMESTAMP('{timestamp_str}')"
        if unit != "D" or column_type != "float":
            return f"TIMESTAMPADD({unit.lower()}, {column_name}, {operand1})"
        else:
            decimal_part = f"{column_name} - FLOOR({column_name})"
            days = f"FLOOR({column_name})"
            seconds = f"({decimal_part}) * 86400"
            nanoseconds = f"FLOOR((({seconds}) - FLOOR({seconds}))*1e9)"
            plus_days = f"TIMESTAMPADD(d, {days}, {operand1})"
            plus_seconds = f"TIMESTAMPADD(s, FLOOR({seconds}), {plus_days})"
            return f"TIMESTAMPADD(ns, {nanoseconds}, {plus_seconds})"

    def generate_map_column_expressions(self, labels_to_apply_over, n):
        return [
            f"""
            IFF(ARRAY_SIZE({labels_to_apply_over[0]})>{i},
                GET({labels_to_apply_over[0]},{i})::STRING,
                NULL)
            """
            for i in range(n)
        ]

    def generate_stored_procedure_call(
        self,
        input_query,
        function_name,
        output_table_name,
        row_labels_column_name,
    ):
        return f"""CALL {function_name}('{input_query}', '{output_table_name}',
            '{row_labels_column_name}')"""

    # Duplicates code in DuckDB, but it's not enough to
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
            f"{self.pandas_type_to_snowflake_type_map[cast_type]})"
        )

    def generate_bitwise_negation(self, op) -> str:
        return f"BITNOT({self.format_name(op)})"

    def generate_pandas_mask(
        self,
        binary_pred_str,
        dbcolumn,
        value_dict,
        upcast_to_object,
    ):
        if value_dict is None:
            return (
                f"CASE WHEN {binary_pred_str} "
                + "THEN NULL "
                + f"ELSE {self.format_name(dbcolumn)} END"
            )
        else:
            formatted_col = self.format_name(dbcolumn) + (
                "::VARIANT" if upcast_to_object else ""
            )
            return (
                f"CASE WHEN {binary_pred_str} "
                + f"THEN '{value_dict[dbcolumn]}' "
                + f"ELSE {formatted_col} END"
            )
