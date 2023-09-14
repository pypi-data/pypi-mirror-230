from __future__ import annotations

import hashlib
from typing import Any, Dict, Optional

import pandas
from pandas.core.computation.parsing import tokenize_string

from ponder.core.error_codes import PonderError, make_exception

from .abstract_dialect import AbstractDialect
from .common import (
    __PONDER_ORDER_COLUMN_NAME__,
    __PONDER_ROW_LABELS_COLUMN_NAME__,
    MAP_FUNCTION,
    generate_column_name_from_value,
)


def _pandas_offset_object_to_n_and_sql_unit(
    offset: pandas.DateOffset,
) -> tuple[int, str]:
    try:
        rule_code = offset.rule_code
    except NotImplementedError:
        # It seems that DateOffset has a rule code if and only if it comes from a string
        # like "3T" from the user. In fact because resample() uses rule code to decide
        # the offsets, it raises NotImplementedError if you pass it some DateOffsets
        # like DateOffset(days=1): https://github.com/pandas-dev/pandas/issues/31697
        # first() and last() take DateOffset but seem to be buggy:
        # https://github.com/pandas-dev/pandas/issues/51284
        raise make_exception(
            NotImplementedError,
            PonderError.CANNOT_CONVERT_PANDAS_OFFSET_TO_N_AND_SQL_UNIT_BECAUSE_NO_RULE_CODE,  # noqa: E501
            f"Ponder Internal Error: Cannot handle offset rule code {offset}",
        )
    else:
        n = offset.n
        # TODO(FIX): there is likely some innacuracy with "quarter start" versus
        # "quarter end", and other such offsets pairs.
        if rule_code == "S":
            unit = "second"
        elif rule_code == "T":
            unit = "minute"
        elif rule_code == "H":
            unit = "hour"
        elif rule_code == "D":
            unit = "day"
        elif rule_code[0] == "W":
            # treat codes like W-MON and W-SUN as "week":
            # https://github.com/pandas-dev/pandas/blob/6b27de318619ab7524e24976c31adf20e59c25f5/pandas/_libs/tslibs/dtypes.pyx#L103-L109
            # it's probably a bug that we treat all these the same
            unit = "week"
        elif rule_code == "M":
            unit = "month"
        elif rule_code[0] == "Q":
            # treat codes like Q-DEC and Q-JAN as "quarter":
            # https://github.com/pandas-dev/pandas/blob/6b27de318619ab7524e24976c31adf20e59c25f5/pandas/_libs/tslibs/dtypes.pyx#L88C5-L99
            # it's probably a bug that we treat all these the same
            unit = "quarter"
        elif rule_code[0] in ("A", "Y"):
            # treat codes like A-DEC and A-JAN as "year":
            # https://github.com/pandas-dev/pandas/blob/6b27de318619ab7524e24976c31adf20e59c25f5/pandas/_libs/tslibs/dtypes.pyx#L73-L84
            # it's probably a bug that we treat all these the same
            unit = "year"
        else:
            raise make_exception(
                NotImplementedError,
                PonderError.CANNOT_CONVERT_PANDAS_OFFSET_TO_N_AND_SQL_UNIT_BECAUSE_CANNOT_HANDLE_RULE_CODE,  # noqa: E501
                f"Ponder Internal Error: Cannot handle offset unit {offset}",
            )

    return n, unit


def _pandas_offset_object_to_seconds(
    offset: pandas.DateOffset,
    average_seconds=False,
) -> tuple[int, str]:
    try:
        rule_code = offset.rule_code
    except NotImplementedError:
        # It seems that DateOffset has a rule code if and only if it comes from a string
        # like "3T" from the user. In fact because resample() uses rule code to decide
        # the offsets, it raises NotImplementedError if you pass it some DateOffsets
        # like DateOffset(days=1): https://github.com/pandas-dev/pandas/issues/31697
        # first() and last() take DateOffset but seem to be buggy:
        # https://github.com/pandas-dev/pandas/issues/51284
        raise make_exception(
            NotImplementedError,
            PonderError.CANNOT_CONVERT_PANDAS_OFFSET_TO_SECONDS_BECAUSE_NO_RULE_CODE,
            f"Ponder Internal Error: Cannot handle offset rule code {offset}",
        )
    else:
        # TODO: Resolve seconds calculation accounting for
        # leap years, 28-day, 30-day months
        n = offset.n
        if rule_code == "S":
            pass
        elif rule_code == "T":
            n *= 60
        elif rule_code == "H":
            n *= 3600
        elif rule_code == "D":
            n *= 86400
        elif rule_code[0] == "W":
            n *= 604800
        elif rule_code == "M":
            if average_seconds:
                # Assume average 30.42 day month
                n *= 2628288
            else:
                # Assume 31 day months as an upper bound
                n *= 2678400
        elif rule_code[0] == "Q":
            if average_seconds:
                # Assume average 30.42 day month over 3 months
                n *= 7884864
            else:
                # Assume 31 day months as an upper bound
                n *= 8035200
        elif rule_code[0] in ("A", "Y"):
            if average_seconds:
                # Assume 365 day year
                n *= 31536000
            else:
                # Assume 366 day year as an upper bound
                # to account for leap years
                n *= 31622400
        else:
            raise make_exception(
                NotImplementedError,
                PonderError.CANNOT_CONVERT_PANDAS_OFFSET_TO_SECONDS_BECAUSE_CANNOT_HANDLE_RULE_CODE,  # noqa: E501
                f"Ponder Internal Error: Cannot handle offset unit {offset}",
            )

    return n


def _pandas_start_val_to_end_period(start_val: pandas.Timestamp, unit: str) -> str:
    if unit == "week":
        # Set week start_val to Sunday of given week
        week_end_val = start_val.to_period("W-SUN").end_time
        start_val = week_end_val.strftime("%Y-%m-%d") + start_val.strftime(" %X")
    elif unit == "month":
        # Set month start_val to last day of the given month
        month_end_val = start_val.to_period("M").end_time
        start_val = month_end_val.strftime("%Y-%m-%d") + start_val.strftime(" %X")
    elif unit == "quarter":
        quarter_end_val = start_val.to_period("Q").end_time
        start_val = quarter_end_val.strftime("%Y-%m-%d") + start_val.strftime(" %X")
    elif unit == "year":
        # Set year start_val to last day of the given year
        year_end_val = start_val.to_period("A-DEC").end_time
        start_val = year_end_val.strftime("%Y-%m-%d") + start_val.strftime(" %X")
    else:
        start_val = start_val.strftime("%Y-%m-%d %X")
    return start_val


class SQLDialect(AbstractDialect):
    def generate_sanitized_name(self, col_name):
        # The parameter 6 below ensures that we get back a hash of 12 characters
        # You get very long strings without it.
        ret_val = hashlib.shake_256(str(col_name).encode("utf-8")).hexdigest(6).upper()
        return f"F{ret_val}"

    def format_name_cast_to_type(self, name, type):
        if type.__name__ == pandas.Timestamp.__name__:
            return f"{self.format_name(name)}::timestamp"
        return self.format_name(name)

    def pandas_datetime_format_to_db_datetime_format(self, pandas_format: str) -> str:
        # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
        # Only support: %m, %d, %y, %Y, %H, %M, %S, %f, %z for now
        # '%m/%d/%y %H:%M:%S.%f %z' -> 'mm/dd/yy hh24:mi:ss.ff9 TZHTZM'
        # '%Z' is deprecated, and not supported by many databases
        db_format = ""
        for char_pos in range(len(pandas_format)):
            cur_char = pandas_format[char_pos]
            prev_char = pandas_format[char_pos - 1]
            if cur_char in ("/", "-", " ", ":", ".", ","):
                # Append any delimiter value
                db_format += cur_char
            elif cur_char == "%":
                pass
            elif cur_char in ("m", "d", "y", "Y", "H", "M", "S", "f", "z"):
                # Check the last character is a '%'
                if prev_char == "%":
                    if cur_char in ("m", "d", "y"):
                        db_format += cur_char.lower() * 2
                    elif cur_char in ("Y"):
                        db_format += cur_char.lower() * 4
                    elif pandas_format[char_pos] == "H":
                        db_format += "hh24"
                    elif pandas_format[char_pos] == "M":
                        db_format += "mi"
                    elif pandas_format[char_pos] == "S":
                        db_format += "ss"
                    elif pandas_format[char_pos] == "f":
                        # This rounds to the nearest millisecond
                        # as Snowflake does not support microseconds
                        db_format += "ff9"
                    elif pandas_format[char_pos] == "z":
                        # TODO: Accurate time/date handling will continue
                        # to need refinement and testing.
                        # Timezone offsets can be parsed, but the results
                        # can be... different depending on the locale
                        db_format += "TZHTZM"
                else:
                    raise make_exception(
                        TypeError,
                        PonderError.DATETIME_FORMAT_STRING_INVALID,
                        "to_datetime() has invalid format parameter!",
                    )
            else:
                raise make_exception(
                    NotImplementedError,
                    PonderError.DATETIME_FORMAT_STRING_NOT_SUPPORTED,
                    f"{cur_char} not yet supported in to_datetime() format parameter!",
                )
        return db_format

    def generate_map_function(self, function, params_list):
        if function == MAP_FUNCTION.COUNT:
            return self.generate_count(params_list)

        if function == MAP_FUNCTION.ISNA:
            return self.generate_isna(params_list)

        if function == MAP_FUNCTION.NOTNA:
            return self.generate_notna(params_list)

        if function == MAP_FUNCTION.dt_nanosecond:
            return self.generate_dt_nanosecond(params_list)

        if function == MAP_FUNCTION.dt_microsecond:
            return self.generate_dt_microsecond(params_list)

        if function == MAP_FUNCTION.dt_second:
            return self.generate_dt_second(params_list)

        if function == MAP_FUNCTION.dt_minute:
            return self.generate_dt_minute(params_list)

        if function == MAP_FUNCTION.dt_hour:
            return self.generate_dt_hour(params_list)

        if function == MAP_FUNCTION.dt_day:
            return self.generate_dt_day(params_list)

        if function == MAP_FUNCTION.dt_dayofweek:
            return self.generate_dt_dayofweek(params_list)

        if function == MAP_FUNCTION.dt_day_name:
            return self.generate_dt_day_name(params_list)

        if function == MAP_FUNCTION.dt_dayofyear:
            return self.generate_dt_dayofyear(params_list)

        if function == MAP_FUNCTION.dt_week:
            return self.generate_dt_week(params_list)

        if function == MAP_FUNCTION.dt_month:
            return self.generate_dt_month(params_list)

        if function == MAP_FUNCTION.dt_month_name:
            return self.generate_dt_month_name(params_list)

        if function == MAP_FUNCTION.dt_quarter:
            return self.generate_dt_quarter(params_list)

        if function == MAP_FUNCTION.dt_year:
            return self.generate_dt_year(params_list)

        if function == MAP_FUNCTION.dt_tz_convert:
            return self.generate_dt_tz_convert(params_list)

        if function == MAP_FUNCTION.dt_tz_localize:
            return self.generate_dt_tz_localize(params_list)

        if function == MAP_FUNCTION.str_center:
            return self.generate_str_center(params_list)

        if function == MAP_FUNCTION.str_contains:
            return self.generate_str_contains(params_list)

        if function == MAP_FUNCTION.str_count:
            return self.generate_str_count(params_list)

        if function == MAP_FUNCTION.str_encode:
            return self.generate_str_encode(params_list)

        if function == MAP_FUNCTION.str_decode:
            return self.generate_str_decode(params_list)

        if function == MAP_FUNCTION.str_endswith:
            return self.generate_str_endswith(params_list)

        if function == MAP_FUNCTION.str_capitalize:
            return self.generate_str_capitalize(params_list)

        if function == MAP_FUNCTION.str_find:
            return self.generate_str_find(params_list)

        if function == MAP_FUNCTION.str_findall:
            return self.generate_str_findall(params_list)

        if function == MAP_FUNCTION.str_fullmatch:
            return self.generate_str_fullmatch(params_list)

        if function == MAP_FUNCTION.str_get:
            return self.generate_str_get(params_list)

        if function == MAP_FUNCTION.str_isalnum:
            return self.generate_str_isalnum(params_list)

        if function == MAP_FUNCTION.str_isalpha:
            return self.generate_str_isalpha(params_list)

        if function == MAP_FUNCTION.str_isdecimal:
            return self.generate_str_isdecimal(params_list)

        if function == MAP_FUNCTION.str_isdigit:
            return self.generate_str_isdigit(params_list)

        if function == MAP_FUNCTION.str_isnumeric:
            return self.generate_str_isnumeric(params_list)

        if function == MAP_FUNCTION.str_isspace:
            return self.generate_str_isspace(params_list)

        if function == MAP_FUNCTION.str_istitle:
            return self.generate_str_istitle(params_list)

        if function == MAP_FUNCTION.str_isupper:
            return self.generate_str_isupper(params_list)

        if function == MAP_FUNCTION.str_islower:
            return self.generate_str_islower(params_list)

        if function == MAP_FUNCTION.str_len:
            return self.generate_str_len(params_list)

        if function == MAP_FUNCTION.str_lower:
            return self.generate_str_lower(params_list)

        if function == MAP_FUNCTION.str_title:
            return self.generate_str_title(params_list)

        if function == MAP_FUNCTION.str_upper:
            return self.generate_str_upper(params_list)

        if function == MAP_FUNCTION.str_split:
            return self.generate_str_split(params_list)

        if function == MAP_FUNCTION.str_rsplit:
            return self.generate_str_rsplit(params_list)

        if function == MAP_FUNCTION.str_join:
            return self.generate_str_join(params_list)

        if function == MAP_FUNCTION.str_rfind:
            return self.generate_str_rfind(params_list)

        if function == MAP_FUNCTION.str_ljust:
            return self.generate_str_ljust(params_list)

        if function == MAP_FUNCTION.str_strip:
            return self.generate_str_strip(params_list)

        if function == MAP_FUNCTION.str_lstrip:
            return self.generate_str_lstrip(params_list)

        if function == MAP_FUNCTION.str_rstrip:
            return self.generate_str_rstrip(params_list)

        if function == MAP_FUNCTION.str_match:
            return self.generate_str_match(params_list)

        if function == MAP_FUNCTION.str_removeprefix:
            return self.generate_str_removeprefix(params_list)

        if function == MAP_FUNCTION.str_removesuffix:
            return self.generate_str_removesuffix(params_list)

        if function == MAP_FUNCTION.str_repeat:
            return self.generate_str_repeat(params_list)

        if function == MAP_FUNCTION.str_replace:
            return self.generate_str_replace(params_list)

        if function == MAP_FUNCTION.str_rjust:
            return self.generate_str_rjust(params_list)

        if function == MAP_FUNCTION.str_slice:
            return self.generate_str_slice(params_list)

        if function == MAP_FUNCTION.str_slice_replace:
            return self.generate_str_slice_replace(params_list)

        if function == MAP_FUNCTION.str_startswith:
            return self.generate_str_startswith(params_list)

        if function == MAP_FUNCTION.str_swapcase:
            return self.generate_str_swapcase(params_list)

        if function == MAP_FUNCTION.str_translate:
            return self.generate_str_translate(params_list)

        if function == MAP_FUNCTION.str_wrap:
            return self.generate_str_wrap(params_list)

    def generate_false_constant(self):
        return "FALSE"

    def generate_map_node_command(
        self,
        conn,
        function_sql: str,
        labels_to_apply_over: list[str],
        all_columns: list[str],
        input_node_sql: str,
    ) -> str:
        column_selects = [
            f"""{function_sql.format(conn.format_name(c))
                    if c in labels_to_apply_over else conn.format_name(c)}
                 AS {conn.format_name(c)}"""
            for c in all_columns
        ]
        return f"""
            SELECT
                {", ".join(column_selects)}
            FROM {self.generate_subselect_expression(input_node_sql)}
        """

    def generate_groupby_nth_predicate(self, by, order_column, n):
        neg_idx = []
        pos_idx = []
        row_predicates = []
        for val in n:
            if val < 0:
                neg_idx.append(abs(val))
            else:
                # Increment by 1 because ROW_NUMBER() is 1-indexed.
                pos_idx.append(val + 1)

        # If we have an empty list then we want to just return an empty
        # dataframe. This is only possible if we check with a row number
        # that can never exist (e.g. -1).
        if len(n) == 0:
            row_predicates.append(
                f"""
                ROW_NUMBER() OVER (
                    PARTITION BY {by}
                    ORDER BY {order_column} DESC
                ) in (-1)
                """
            )

        if neg_idx:
            neg_idx = ",".join([str(i) for i in neg_idx])
            row_predicates.append(
                f"""
                ROW_NUMBER() OVER (
                    PARTITION BY {by}
                    ORDER BY {order_column} DESC
                ) in ({neg_idx})
                """
            )

        if pos_idx:
            pos_idx = ",".join([str(i) for i in pos_idx])
            row_predicates.append(
                f"""
                ROW_NUMBER() OVER (
                    PARTITION BY {by}
                    ORDER BY {order_column} ASC
                ) in ({pos_idx})
                """
            )

        joined_row_predicates = " OR ".join(row_predicates)
        return f"""
                QUALIFY
                    {joined_row_predicates}
                """

    def generate_new_row_labels_columns_command(
        self, new_row_label_column_names, column_names, input_node_sql, new_row_labels
    ):
        if len(new_row_label_column_names) > 1:
            raise make_exception(
                NotImplementedError,
                PonderError.GENERIC_SQL_MULTI_INDEX_JOIN_NOT_SUPPORTED,
                "Ponder Internal Error: Multiindex joins are not supported yet",
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
                        {new_row_label_column_name} INT64>{", ".join(str((k, v)) for k,
                        v in new_row_labels.items())}])
            ) AS RIGHT_TABLE
            ON LEFT_TABLE.{__PONDER_ORDER_COLUMN_NAME__} = RIGHT_TABLE._ROW_ORDER_VALS_
        """

    def generate_count(self, params_list):
        col_name_quoted = params_list[0]
        return f"CASE WHEN {col_name_quoted} IS NULL THEN 0 ELSE 1 END"

    def generate_isna(self, params_list):
        col_name_quoted = params_list[0]
        return f"CASE WHEN {col_name_quoted} IS NULL THEN true ELSE false END"

    def generate_notna(self, params_list):
        col_name_quoted = params_list[0]
        return f"CASE WHEN {col_name_quoted} IS NOT NULL THEN true ELSE false END"

    def generate_str_title(self, params_list):
        col_name_quoted = params_list[0]
        return f"INITCAP({col_name_quoted})"

    def generate_str_lower(self, params_list):
        col_name_quoted = params_list[0]
        return f"LOWER({col_name_quoted})"

    def generate_str_upper(self, params_list):
        col_name_quoted = params_list[0]
        return f"UPPER({col_name_quoted})"

    def generate_str_lstrip(self, params_list):
        col_name_quoted, to_strip = params_list
        if to_strip is None:
            exp = f"LTRIM({col_name_quoted})"  # noqa F541
        else:
            exp = f"LTRIM({col_name_quoted},'{to_strip}')"  # noqa F541
        return exp

    def generate_str_rstrip(self, params_list):
        column_name_quoted, to_strip = params_list
        if to_strip is None:
            exp = f"RTRIM({column_name_quoted})"  # noqa F541
        else:
            exp = f"RTRIM({column_name_quoted},'{to_strip}')"
        return exp

    def generate_str_strip(self, params_list):
        col_name_quoted, to_strip = params_list
        if to_strip is None:
            exp = f"TRIM({col_name_quoted})"  # noqa F541
        else:
            exp = f"TRIM({col_name_quoted},'{to_strip}')"
        return exp

    def generate_str_index(self, params_list):
        return self.generate_str_find(params_list)

    def generate_str_swapcase(self, params_list):
        col_name_quoted = params_list[0]
        exp = f"""
                TRANSLATE(
                    {col_name_quoted},
                    'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
                    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
                )
            """
        return exp

    def generate_str_translate(self, params_list):
        col_name_quoted, table = params_list
        table = dict({k: "" if v is None else v for k, v in table.items()})
        table = dict(sorted(table.items(), key=lambda x: x[1], reverse=True))
        keys = list(table.keys())
        values = list(table.values())
        keys_str = f"CONCAT({','.join(map(f'CHR({{}})'.format, keys))})"
        values_str = "".join(values)
        exp = f"TRANSLATE({col_name_quoted},{keys_str},'{values_str}')"
        return exp

    def generate_str_isspace(self, params_list):
        col_name_quoted = params_list[0]
        return f"'' = TRIM({col_name_quoted})"

    def generate_str_len(self, params_list):
        col_name_quoted = params_list[0]
        return f"LENGTH({col_name_quoted})"

    def generate_reassign_order_post_union_command(self, column_names, input_node_sql):
        formatted_column_names = self.format_names_list(column_names)
        return f"""
            SELECT
                {self.format_name(__PONDER_ORDER_COLUMN_NAME__)} AS
                {self.format_name(__PONDER_ROW_LABELS_COLUMN_NAME__)},
                ROW_NUMBER() OVER (
                    ORDER BY {self.format_name("_TABLE_ORDER_")},
                    {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}) -1
                    AS {self.format_name(__PONDER_ORDER_COLUMN_NAME__)},
                {", ".join(formatted_column_names)}
            FROM {self.generate_subselect_expression(input_node_sql)}
        """

    def generate_abs(self, col):
        formatted_col = self.format_name(col)
        return f"ABS({formatted_col})"

    def generate_round(self, col, decimals):
        formatted_col = self.format_name(col)
        return f"ROUND({formatted_col}, {decimals})"

    def generate_cut_expression(self, column_name, categories, bins):
        if len(bins) < 2:
            raise make_exception(
                NotImplementedError,
                PonderError.CUT_BINS_LESS_THAN_2_NOT_SUPPORTED,
                "cut() does not support bins < 2",
            )
        formatted_name = self.format_name(column_name)
        return f"""
            CASE
                {" ".join(
                    (f'WHEN {formatted_name} <= {bin} THEN ' +
                     self.format_value_by_type(category)
                    for bin, category in zip(bins[1:], categories)))}
                ELSE NULL
            END
        """

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
        formatted_column = self.format_name(column)
        non_dummy_cols_list = self.format_names_list(non_dummy_cols)
        formatted_order_column_name_fragment = (
            f"{self.format_name(order_column_name)} AS "
            + self.format_name(order_column_name)
        )
        formatted_row_labels_column_names_fragment = ", ".join(
            f"{self.format_name(c)} AS {c}" for c in row_labels_column_names
        )
        input_node_columns_list = self.format_names_list(input_node_column_names)
        input_node_columns_list.extend(
            self.format_name(c)
            for c in input_node_row_labels_column_names
            if c not in input_node_column_names
        )
        if input_node_order_column_name not in input_node_column_names:
            input_node_columns_list.append(
                self.format_name(input_node_order_column_name)
            )

        str_unique_vals = [
            generate_column_name_from_value(value) for value in unique_vals
        ]
        new_column_names_fragment = ", ".join(
            f"""CASE WHEN {formatted_column} = '{val}' THEN TRUE ELSE FALSE
                END AS {self.format_name(f"{prefix}{prefix_sep}{val}")}"""
            for val in str_unique_vals
        )
        get_dummies_query = f"""
        SELECT {",".join(non_dummy_cols_list)}, {formatted_order_column_name_fragment},
        {formatted_row_labels_column_names_fragment}, {new_column_names_fragment}
        FROM {self.generate_subselect_expression(input_node_query)}
        """
        return get_dummies_query

    def generate_pandas_timestamp_to_date(self, timestamp: pandas.Timestamp):
        return f"DATE({self.format_value(timestamp)})"

    def generate_monotonic_intermediate(
        self, increasing, lag_val_column_name, column_name
    ) -> str:
        return f"""
            CASE
                WHEN
                (
                    {self.format_name(lag_val_column_name)} IS NULL OR
                    {self.format_name(lag_val_column_name)}
                    {" <= " if increasing else " >= "}
                    {self.format_name(column_name)}
                )
                THEN TRUE
                ELSE FALSE
            END
        """

    def generate_create_temp_table_with_rowid_command(self, temp_table_name, sql_query):
        # PONDER_ROW_ID may already be present in the underlying table in some
        # cases - fix soon(ish).
        formatted_sql_query = self.format_table_name(sql_query)
        row_num_sql = " ROW_NUMBER() OVER (ORDER BY 1) -1 "

        return (
            f"CREATE TEMP TABLE {self.format_table_name(temp_table_name)} AS SELECT *,"
            f" {row_num_sql} AS {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}"
            f" FROM {formatted_sql_query}"
        )

    def generate_read_table_command(self, table_name, column_list=None, skipfooter=0):
        formatted_table_name = self.format_name(table_name)
        if skipfooter > 0:
            column_name_for_skip_footer = (
                __PONDER_ORDER_COLUMN_NAME__
                if column_list is not None
                else __PONDER_ROW_LABELS_COLUMN_NAME__
            )
            column_name_for_skip_footer = self.format_name(column_name_for_skip_footer)
            skip_footer_fragment = f"""WHERE ({column_name_for_skip_footer}
            < (SELECT COUNT(*) AS COUNT_PONDER FROM {formatted_table_name})
             - {skipfooter})"""
        else:
            skip_footer_fragment = ""

        if column_list is not None:
            formatted_columns_list = self.format_names_list(column_list)
            selected_columns_list = ", ".join(formatted_columns_list)
            if __PONDER_ORDER_COLUMN_NAME__ not in column_list:
                selected_columns_list = (
                    selected_columns_list
                    + f", {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}"
                )
            if __PONDER_ROW_LABELS_COLUMN_NAME__ not in column_list:
                selected_columns_list = (
                    selected_columns_list
                    + f""", {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
                        AS {self.format_name(__PONDER_ROW_LABELS_COLUMN_NAME__)}"""
                )
            return (
                f"SELECT {selected_columns_list} FROM {formatted_table_name} "
                f"{skip_footer_fragment}"
            )

        return f"SELECT * FROM ({formatted_table_name}) " f"{skip_footer_fragment}"

    def generate_row_ge_value_predicate(self, column_name: str, value) -> str:
        return f"""
            WHERE {self.format_name_cast_to_type(column_name, type(value))}
            >= {self.format_value_by_type(value)}
            """

    def generate_row_le_value_predicate(self, column_name: str, value) -> str:
        return f"""
            WHERE {self.format_name_cast_to_type(column_name, type(value))}
            <= {self.format_value_by_type(value)}
            """

    def generate_row_between_inclusive_predicate(
        self, column_name: str, value_start, value_stop
    ) -> str:
        start = self.format_value_by_type(value_start)
        stop = self.format_value_by_type(value_stop)

        return f"""
            WHERE {self.format_name_cast_to_type(column_name, type(value_start))}
            <= {stop}
            AND {self.format_name_cast_to_type(column_name, type(value_stop))}
            >= {start}
            """

    def generate_equal_null_predicate(self, lhs: str, rhs: str) -> str:
        # TODO(REFACTOR, FIX): there are probably bugs with how we format literals for
        # binary comparison. The query tree should tell the connection layer whether the
        # sides of the comparison are literals or not.
        # https://github.com/ponder-org/soda/blob/2791d16b5101e98c38fcd0b5fa4196171bdb6ae7/ponder/pushdown_service/common/query_tree.py#L70-L95
        return f"{lhs} IS NOT DISTINCT FROM {rhs}"

    def generate_bitwise_and(self, op_1, op_2) -> str:
        return f"BITAND({str(op_1)},{str(op_2)})"

    def generate_bitwise_or(self, op_1, op_2) -> str:
        return f"BITOR({str(op_1)},{str(op_2)})"

    def generate_bitwise_xor(self, op_1, op_2) -> str:
        return f"BITXOR({str(op_1)},{str(op_2)})"

    def generate_bitwise_negation(self, op) -> str:
        return f"~{self.format_name(op)}"

    def generate_read_sp_temp_table(
        self, table_name, column_names, row_labels_column_name
    ):
        columns_list = [self.format_name(column_name) for column_name in column_names]
        columns_list.append(row_labels_column_name)

        if __PONDER_ORDER_COLUMN_NAME__ not in column_names:
            columns_list.append(__PONDER_ORDER_COLUMN_NAME__)

        return f"SELECT {', '.join(columns_list)} FROM {table_name}"

    def generate_coalesce(self, column_list) -> str:
        return f"""COALESCE({', '.join([self.format_name(column_name)
                                        for column_name in column_list])})"""

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
                LAST_VALUE({self.format_name(col)}) IGNORE NULLS
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
                FIRST_VALUE({self.format_name(col)}) IGNORE NULLS
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
                PonderError.GENERIC_SQL_FILLNA_INVALID_METHOD,
                "received method from fillna that is not ffill or bfill",
            )
        return columns_selection

    def generate_value_dict_fill_na(
        self,
        label,
        value_dict,
        limit,
        group_cols: list[str],
        upcast_to_object,
    ):
        if label not in value_dict:
            return label

        formatted_value = self.format_value(value_dict[label]) + (
            "::VARIANT" if upcast_to_object else ""
        )
        if group_cols is None:
            partition_by_sql = ""
        else:
            partition_by_sql = (
                f" PARTITION BY "
                f"({','.join(self.format_name(c) for c in group_cols)})"
            )

        if limit is not None:
            return f"""
                IFF(
                        COUNT_IF({self.format_name(label)} IS NULL)
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
        return (
            f"IFNULL({self.format_name(label)}"
            + ("::VARIANT" if upcast_to_object else "")
            + f",{formatted_value})"
        )

    def generate_pandas_query_predicate(
        self,
        query: str,
        local_dict: Dict[str, Any],
        global_dict: Dict[str, Any],
        input_columns: list[str],
        column_name_mapper,
    ):
        is_variable = False
        parsed_list = []
        for _, v in tokenize_string(query):
            if v == "" or v == " ":
                continue
            if is_variable:
                if v in local_dict:
                    value = local_dict[v]
                elif v in global_dict:
                    value = global_dict[v]
                else:
                    # TODO this error does not quite match pandas
                    raise make_exception(
                        ValueError,
                        PonderError.DATABASE_PANDAS_QUERY_VARIABLE_NOT_FOUND,
                        f"{v} not found",
                    )
                if isinstance(value, list):
                    value = tuple(value)
                parsed_list.append(value)
                is_variable = False
            elif v == "@":
                is_variable = True
                continue
            else:
                if " " in v:
                    raise make_exception(
                        NotImplementedError,
                        PonderError.DATABASE_PANDAS_QUERY_SPACES_IN_COLUMN_NAMES_NOT_SUPPORTED,  # noqa: E501
                        "Columns with spaces are not supported yet",
                    )
                if v == "&":
                    v = "AND"
                elif v == "|":
                    v = "OR"
                elif v == "[":
                    v = "("
                elif v == "]":
                    v = ")"
                elif column_name_mapper.get_db_name_from_df_name(v) in input_columns:
                    v = column_name_mapper.get_db_name_from_df_name(v)
                    if v[0] != '"' and v[-1] != '"':
                        v = self.format_name(v)
                elif v[0] == '"' and v[-1] == '"':
                    if len(v) > 1:
                        v = "'" + v[1:-1] + "'"
                parsed_list.append(v)
        return f'WHERE {" ".join(map(str, parsed_list))}'

    def generate_subselect_expression(self, input_sql):
        return f"({input_sql})"

    def generate_autoincrement_type(self):
        pass

    def generate_reorder_columns_statement(self, input_node_sql, column_list):
        select_col_list = [self.format_name(col_name) for col_name in column_list]

        return f'SELECT {", ".join(select_col_list)} from ({input_node_sql})'

    def generate_replace_values_statement(
        self,
        input_node_sql,
        column_list,
        replace_values_column_name,
        replace_values_dict,
    ):
        formatted_replace_values_column_name = self.format_name(
            replace_values_column_name
        )
        if replace_values_dict is not None and len(replace_values_dict) > 0:
            when_then_fragments = "\n".join(
                [
                    f"""WHEN {formatted_replace_values_column_name} =
                        {self.format_value(key)} THEN {self.format_value(value)}"""
                    for key, value in replace_values_dict.items()
                ]
            )
            when_then_fragments = f"""CASE {when_then_fragments} \n
                ELSE {self.format_value('Unmapped Value')} END
                AS {formatted_replace_values_column_name}"""
        else:
            when_then_fragments = f"{formatted_replace_values_column_name}"

        column_list_fragment = ", ".join(
            [
                self.format_name(col_name)
                if col_name != replace_values_column_name
                else when_then_fragments
                for col_name in column_list
            ]
        )

        return f"SELECT {column_list_fragment} FROM ({input_node_sql})"

    def generate_get_unique_values(self, input_node_sql, column_name):
        sql = f"""
            SELECT DISTINCT {self.format_name(column_name)}
            FROM
                {self.generate_subselect_expression(input_node_sql)}
            """
        return sql

    def is_query_like(self, table_or_query):
        left_stripped = table_or_query.lstrip(" \n")
        if (
            "SELECT " in left_stripped
            or "SELECT\n" in left_stripped
            or " SELECT\n" in left_stripped
            or ("WITH ") in left_stripped
            or (" WITH\n") in left_stripped
        ):
            return True
        return False

    def generate_boolean_negation(self, op) -> str:
        # need parens when the NOT applies to a boolean expression instead of just a
        # column name
        return f"NOT ({self.format_name(op)})"

    def generate_pandas_mask(
        self,
        binary_pred_str,
        dbcolumn,
        value_dict,
        upcast_to_object,
    ):
        pass
