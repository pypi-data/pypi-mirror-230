"""This module contains objects that multiple layers in the pushdown service
use."""

import copy
import functools
import os
from collections import namedtuple
from datetime import date
from enum import Enum, auto
from functools import cached_property

import numpy as np
import pandas

from ponder.core.error_codes import PonderError, make_exception

__UNNAMED_INDEX_COLUMN__ = "_PONDER_IDX_COL_NAME_"

UnionAllDataForDialect = namedtuple("UnionAllDataForDialect", ["sql", "dtypes"])
UnionAllDataForDialect.__doc__ = """\
Container for data about a node that will be unioned with other nodes.

Attributes:
    sql (str): The SQL to execute for this node.
    dtypes (pandas.Series): The dtypes for this node.
"""


# TODO(https://ponderdata.atlassian.net/browse/POND-1003): make configuration more
# dynamic.
ExecutionConfiguration = namedtuple(
    "Configuration",
    [
        "row_transfer_limit",
        # mask_with_temp_table enables an experimental internal feature that will
        # use intermediate temporary tables to shorten SQL queries. This should not
        # affect correctness but it may be useful if queries are too large.
        "mask_with_temp_table",
        "query_timeout",
        "bigquery_dataset",
        "bigquery_approximate_quantiles",
    ],
)

_execution_configuration = None


def get_execution_configuration():
    return _execution_configuration


def set_execution_configuration(config):
    global _execution_configuration
    _execution_configuration = config


class MAP_FUNCTION(Enum):
    COUNT = auto()
    ISNA = auto()
    NOTNA = auto()

    dt_nanosecond = auto()
    dt_microsecond = auto()
    dt_second = auto()
    dt_minute = auto()
    dt_hour = auto()
    dt_day = auto()
    dt_dayofweek = auto()
    dt_day_name = auto()
    dt_dayofyear = auto()
    dt_week = auto()
    dt_month = auto()
    dt_month_name = auto()
    dt_quarter = auto()
    dt_year = auto()
    dt_tz_convert = auto()
    dt_tz_localize = auto()

    str_cat = auto()
    str_center = auto()
    str_contains = auto()
    str_count = auto()
    str_encode = auto()
    str_decode = auto()
    str_endswith = auto()
    str_capitalize = auto()
    str_find = auto()
    str_findall = auto()
    str_fullmatch = auto()
    str_get = auto()
    str_isalnum = auto()
    str_isalpha = auto()
    str_isdecimal = auto()
    str_isdigit = auto()
    str_isnumeric = auto()
    str_isspace = auto()
    str_istitle = auto()
    str_isupper = auto()
    str_islower = auto()
    str_len = auto()
    str_title = auto()
    str_lower = auto()
    str_upper = auto()
    str_split = auto()
    str_rsplit = auto()
    str_rfind = auto()
    str_join = auto()
    str_ljust = auto()
    str_rjust = auto()
    str_strip = auto()
    str_lstrip = auto()
    str_rstrip = auto()
    str_match = auto()
    str_slice = auto()
    str_slice_replace = auto()
    str_startswith = auto()
    str_partition = auto()
    str_removeprefix = auto()
    str_removesuffix = auto()
    str_repeat = auto()
    str_replace = auto()
    str_rpartition = auto()
    str_swapcase = auto()
    str_translate = auto()
    str_wrap = auto()


class MapFunction(object):
    def __init__(
        self,
        id: MAP_FUNCTION,
        params_list,
        return_type="object",
    ):
        self._id = id
        self._params_list = params_list
        self._return_type = return_type

    def generate_sql(self, conn):
        return conn.generate_map_function(self._id, self._params_list)


class CUMULATIVE_FUNCTIONS(Enum):
    MIN = auto()
    MAX = auto()
    SUM = auto()
    PROD = auto()


class REDUCE_FUNCTION(Enum):
    SUM = auto()
    COUNT = auto()
    COUNT_UNIQUE_INCLUDING_NULL = auto()
    COUNT_UNIQUE_EXCLUDING_NULL = auto()
    KURTOSIS = auto()
    MEAN = auto()
    MEDIAN = auto()
    SEM = auto()
    SKEW = auto()
    STANDARD_DEVIATION = auto()
    CORR = auto()
    COV = auto()
    STR_CAT = auto()
    MIN = auto()
    MAX = auto()
    LOGICAL_OR = auto()
    LOGICAL_AND = auto()
    PERCENTILE = auto()
    VARIANCE = auto()
    MODE = auto()
    BOOL_COUNT = auto()
    # this function reduces a column to 0. It's hack to get a single
    # row with 0s for every column for `memory_usage()`.
    CONSTANT_ZERO = auto()


class APPLY_FUNCTION(Enum):
    ROW_WISE = auto()
    COLUMN_WISE = auto()
    ELEMENT_WISE = auto()


# TODO: we should see if we can just use the frozen list from service.py
# But should do this after we implement everything
groupby_funcs = (
    "corr",
    "cov",
    "cumcount",
    "cummin",
    "cummax",
    "cumsum",
    "cumprod",
    "head",
    "tail",
    "nth",
    "ngroup",
    "get_group",
    "sum",
    "count",
    "mean",
    "median",
    "sem",
    "skew",
    "std",
    "min",
    "max",
    "any",
    "all",
    "unique",
    "nunique",
    "quantile",
    "var",
    "size",
    "prod",
    "noop",
    "first",
    "last",
    "asfreq",
    "pct_change",
    "diff",
    "idxmax",
    "idxmin",
)
GROUPBY_FUNCTIONS = Enum("GROUPBY_FUNCTIONS", [f.upper() for f in groupby_funcs])
groupby_func_str_to_enum = {
    func: GROUPBY_FUNCTIONS[func.upper()] for func in groupby_funcs
}

groupby_window_funcs = [
    GROUPBY_FUNCTIONS.CUMSUM,
    GROUPBY_FUNCTIONS.CUMMAX,
    GROUPBY_FUNCTIONS.CUMMIN,
    GROUPBY_FUNCTIONS.CUMPROD,
    GROUPBY_FUNCTIONS.CUMCOUNT,
    GROUPBY_FUNCTIONS.FIRST,
    GROUPBY_FUNCTIONS.LAST,
    GROUPBY_FUNCTIONS.ASFREQ,
    GROUPBY_FUNCTIONS.NGROUP,
    GROUPBY_FUNCTIONS.PCT_CHANGE,
    GROUPBY_FUNCTIONS.DIFF,
]

groupby_view_funcs = [
    GROUPBY_FUNCTIONS.HEAD,
    GROUPBY_FUNCTIONS.TAIL,
    GROUPBY_FUNCTIONS.NTH,
    GROUPBY_FUNCTIONS.GET_GROUP,
]

__PONDER_ORDER_COLUMN_NAME__ = "_PONDER_ROW_NUMBER_"
__PONDER_ROW_LABELS_COLUMN_NAME__ = "_PONDER_ROW_LABELS_"
__PONDER_REDUCED_COLUMN_NAME__ = "__reduced__"
__PONDER_AGG_OTHER_COL_ID__ = "_PONDER_AGG_OTHER_COL_ID_"
__PONDER_AGG_OTHER_COL_NAME__ = "_PONDER_AGG_OTHER_COL_"
__ISIN_SERIES_VALUES_COLUMN_NAME__ = "_PONDER_ISIN_VALUES_"
__ISIN_DATAFRAME_LEFT_PREFIX__ = "_isin_left"
__ISIN_DATAFRAME_RIGHT_PREFIX__ = "_isin_right"
__PONDER_TEMP_TABLE_ROWID_COLUMN__ = "_PONDER_TEMP_ROW_ID_"
__ROWID_VALUE_SIZE_TO_MATERIALIZE__ = int(
    os.environ.get("ROWID_VALUE_SIZE_TO_MATERIALIZE", 2000)
)
__SQL_QUERY_LEN_LIMIT__ = int(os.environ.get("SQL_QUERY_LEN_LIMIT", 800_000))
__PONDER_STORED_PROC_ROW_LABEL_COLUMN_NAME__ = "_PONDER_SP_ROW_LABEL_COLUMN_NAME_"


def generate_column_name_from_value(value, source_column_name=None):
    if value is None:
        return_value = "na"
    elif isinstance(value, date):
        return_value = value.strftime("%Y-%m-%d %H:%M:%S")
    elif not isinstance(value, str):
        return_value = str(value)
    else:
        return_value = value

    if source_column_name is not None:
        return f"{source_column_name}_{return_value}"

    return return_value


def copying_cache(func):
    """Cache a function result, but copy the result each time.

    This method is useful for caching mutable function results. functools.cache would
    return a mutable result that's shared across invocations.

    Note that there is some cost for the copy. If it's possible for your method to
    return an immutable object, e.g. a frozenlist or frozendict, it may be better to do
    that instead.

    Parameters
    ----------
    func: Callable
        Function to cache

    Returns
    -------
    Callable
        The wrapped function.
    """
    import sys

    # python versions older than 3.9 do not support the cache function,
    # which per the docs is the same thing as lru_cache(maxsize=None).
    if sys.version_info < (3, 9):
        cached_func = functools.lru_cache(maxsize=None)(func)
    else:
        cached_func = functools.cache(func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return copy.deepcopy(cached_func(*args, **kwargs))

    return wrapper


def groupby_function_to_reduce_enum(func) -> GROUPBY_FUNCTIONS:
    # Have to map the func, which could be a string or a callable, to a snowflake
    # aggregate function.
    # np.max has name "amax" and np.min has name "amin", so hardcode the names of
    # those two.
    if func is np.max:
        func = "max"
    elif func is np.min:
        func = "min"
    elif callable(func):
        if hasattr(np, func.__name__):
            func = func.__name__
        else:
            raise make_exception(
                NotImplementedError,
                PonderError.GROUPBY_REDUCE_WITH_NON_NUMPY_CALLABLE,
                "groupby() aggregation with a callable that is not a numpy "
                + f"method is not implemented yet: {func.__name__}",
            )
    if not isinstance(func, str):
        raise make_exception(
            TypeError,
            PonderError.GROUPBY_REDUCE_WITH_NON_STR_OR_CALLABLE,
            f"{type(func).__name__} object is not callable",
        )
    if not hasattr(pandas.core.groupby.generic.DataFrameGroupBy, func):
        raise make_exception(
            AttributeError,
            PonderError.GROUPBY_REDUCE_WITH_INVALID_FUNCTION,
            f"'{func}' is not a valid function for 'DataFrameGroupBy' object",
        )
    if not hasattr(GROUPBY_FUNCTIONS, func.upper()):
        raise make_exception(
            NotImplementedError,
            PonderError.GROUPBY_REDUCE_WITH_UNIMPLEMENTED_FUNCTION,
            f"groupby() aggregatation with '{func}' is not implemented yet",
        )
    return getattr(GROUPBY_FUNCTIONS, func.upper())


# Temporary wrapper class to handle list-like by parameters for groupby
class ByParams:
    def __init__(self, by_map):
        self.by_map = by_map

    @cached_property
    def columns(self):
        by_columns = []
        for k in self.by_map.keys():
            if isinstance(k, pandas.Grouper):
                by_columns.append(k.key)
            else:
                by_columns.extend(list(k.columns))
        return by_columns

    def get_map(self):
        return self.by_map
