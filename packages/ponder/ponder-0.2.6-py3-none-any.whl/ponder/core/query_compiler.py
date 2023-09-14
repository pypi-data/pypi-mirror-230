from __future__ import annotations

import copy
import datetime
import logging
import pickle
import sys
import warnings
from enum import Enum, auto
from functools import reduce
from typing import Any, Hashable, Optional

import cloudpickle
import modin.pandas as pd
import numpy as np
import pandas
import pytz
from modin.core.dataframe.base.dataframe.utils import Axis
from modin.core.storage_formats.base.query_compiler import BaseQueryCompiler
from pandas._libs.lib import NoDefault, no_default
from pandas._libs.tslibs import to_offset
from pandas._typing import Frequency
from pandas.api.types import (
    is_bool_dtype,
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_datetime64_dtype,
    is_datetime64tz_dtype,
    is_dict_like,
    is_list_like,
    is_string_dtype,
)
from pandas.core.common import is_bool_indexer
from pandas.core.dtypes.common import (
    is_float_dtype,
    is_integer_dtype,
    is_number,
    is_numeric_dtype,
    is_scalar,
    pandas_dtype,
)
from pandas.io.formats.format import format_percentiles
from pandas.util._validators import validate_inclusive

from ponder.core.common import ByParams, get_execution_configuration
from ponder.core.error_codes import PonderError, make_exception

from .common import (
    __PONDER_ORDER_COLUMN_NAME__,
    __PONDER_REDUCED_COLUMN_NAME__,
    __UNNAMED_INDEX_COLUMN__,
    APPLY_FUNCTION,
    CUMULATIVE_FUNCTIONS,
    GROUPBY_FUNCTIONS,
    MAP_FUNCTION,
    REDUCE_FUNCTION,
    MapFunction,
    groupby_func_str_to_enum,
    groupby_function_to_reduce_enum,
)
from .dataframe import TransposedDBMSDataframe
from .index import DBMSDateTimeIndex, DBMSIndex, DBMSPositionMapping
from .query_tree import RowWiseFilterPredicates
from .sql_dialect import _pandas_offset_object_to_seconds

__MAX_INT__ = 2147483647

_unnamed_column_ = "__REDUCED__"
__WINDOW_AGGREGATE_MAP__ = "_AGGDICTMAP_"

logger = logging.getLogger(__name__)


def _get_types(values):
    return list(
        map(
            lambda x: np.dtype(type(x)) if not is_list_like(x) else _get_types(x),
            values,
        )
    )


def _generalize_types(types, use_num=True):
    types = list(
        map(
            lambda x: "date"
            if is_datetime64_dtype(x) and not is_list_like(x)
            else _generalize_types(x, use_num)
            if is_list_like(x)
            else x,
            types,
        )
    )
    types = list(
        map(
            lambda x: "str"
            if is_string_dtype(x) and not is_datetime64_dtype(x) and not is_list_like(x)
            else _generalize_types(x, use_num)
            if is_list_like(x)
            else x,
            types,
        )
    )
    types = list(
        map(
            lambda x: "bool"
            if is_bool_dtype(x) and not is_list_like(x)
            else _generalize_types(x, use_num)
            if is_list_like(x)
            else x,
            types,
        )
    )
    types = list(
        map(
            lambda x: "category"
            if is_categorical_dtype(x) and not is_list_like(x)
            else _generalize_types(x, use_num)
            if is_list_like(x)
            else x,
            types,
        )
    )
    if use_num:
        types = list(
            map(
                lambda x: "num"
                if is_numeric_dtype(x) and not is_bool_dtype(x) and not is_list_like(x)
                else _generalize_types(x, use_num)
                if is_list_like(x)
                else x,
                types,
            )
        )
    else:
        types = list(
            map(
                lambda x: "int"
                if is_integer_dtype(x) and not is_bool_dtype(x) and not is_list_like(x)
                else _generalize_types(x, use_num)
                if is_list_like(x)
                else x,
                types,
            )
        )
        types = list(
            map(
                lambda x: "float"
                if is_float_dtype(x) and not is_bool_dtype(x) and not is_list_like(x)
                else _generalize_types(x, use_num)
                if is_list_like(x)
                else x,
                types,
            )
        )
    return types


def _add_quotes(values):
    return list(
        map(
            lambda x: f"'{x}'"
            if (
                is_datetime64_dtype(np.dtype(type(x)))
                or is_string_dtype(np.dtype(type(x)))
            )
            and not is_list_like(x)
            else _add_quotes(x)
            if is_list_like(x)
            else x,
            values,
        )
    )


def _binary_op(sql_infix, self_on_right=False):
    def op(
        self,
        other,
        broadcast: bool = False,
        axis=None,
        level: Any = None,
        sort_columns: bool = True,
        **kwargs,
    ):
        if not is_scalar(other):
            # if the relevant dimension - row or column has only one row or column we
            # have to do an outer join which effectively mimics a numpy broadcast.
            if axis == 0 and len(other._dataframe.index) == 1:
                join_type = "cross"
            elif axis == 1 and len(other._dataframe.columns) == 1:
                join_type = "cross"
            else:
                join_type = "outer"
            return self.__constructor__(
                self._dataframe.binary_op(
                    sql_infix,
                    other._dataframe,
                    join_type=join_type,
                    axis=axis,
                    sort_columns=sort_columns,
                )
            )
        return new_func(self, other)

    def new_func(self, other):
        return self.__constructor__(
            self._dataframe.binary_op_with_scalar(sql_infix, other, self_on_right)
        )

    return op


def _cast_to_int_if_needed(qc):
    types = _generalize_types(list(qc.dtypes))
    columns_df = pandas.DataFrame(
        zip(types, list(qc.columns)),
        index=pandas.RangeIndex(len(qc.columns)),
        columns=["column_type", "column"],
    )
    bool_cols = columns_df.query("column_type == 'bool'")["column"].to_list()
    if len(bool_cols) > 0:
        return qc.astype(dict(zip(bool_cols, [int] * len(bool_cols))))
    else:
        return qc


def _time_to_micros(time_obj: datetime.time) -> int:
    """Convert a datetime object to microseconds since midnight."""
    # this is copied from an internal pandas function.
    seconds = time_obj.hour * 60 * 60 + 60 * time_obj.minute + time_obj.second
    return 1_000_000 * seconds + time_obj.microsecond


def _timetz_to_tz(t: datetime.time, tz_out: datetime.tzinfo):
    # implementation is from https://stackoverflow.com/a/49475901/17554722
    return (
        datetime.datetime.combine(datetime.datetime.today(), t)
        .astimezone(tz_out)
        .timetz()
    )


class _TzConvertOrLocalize(Enum):
    CONVERT = auto()
    LOCALIZE = auto()


class DBMSQueryCompiler(BaseQueryCompiler):
    lazy_execution = True

    def __init__(self, dataframe):
        self._dataframe = dataframe

    def _set_columns(self, new_columns):
        old_len = len(self.columns)
        new_len = len(new_columns)
        if new_len != old_len:
            raise make_exception(
                ValueError,
                PonderError.QUERY_COMPILER_SET_COLUMNS_LENGTH_MISMATCH,
                f"Length mismatch: Expected axis has {old_len} elements, new values "
                + f"have {new_len} elements",
            )
        new_dataframe = self._dataframe.rename(new_col_labels=new_columns)
        self._dataframe = new_dataframe

    def _get_columns(self):
        return self._dataframe.columns

    def _set_index(self, new_index):
        old_len = len(self.index)
        new_len = len(new_index)
        if new_len != old_len:
            raise make_exception(
                ValueError,
                PonderError.QUERY_COMPILER_SET_INDEX_LENGTH_MISMATCH,
                f"Length mismatch: Expected axis has {old_len} elements, new values "
                + f"have {new_len} elements",
            )
        if isinstance(new_index, DBMSIndex):
            # TODO(https://ponderdata.atlassian.net/browse/POND-875): rewrite this so
            # we don't hae to do a self join on the order column.
            self_without_index_column = (
                self.reset_index(drop=True)
                if isinstance(self.index, DBMSIndex)
                else self
            )
            # for cases where index name same as name of a column
            if new_index.name in self_without_index_column.columns:
                raise make_exception(
                    NotImplementedError,
                    PonderError.QUERY_COMPILER_SET_INDEX_TO_EXISTING_COLUMN_NAME,
                    "Ponder Internal Error: cannot set index to a DBMSIndex "
                    "with the same name as a column yet",
                )
            concatenated = self_without_index_column.concat(
                axis=1,
                # easier to concat to another query compiler than to a DBMSDataframe
                other=self.__constructor__(new_index._dataframe)
                .reset_index(drop=False)
                .getitem_column_array(new_index.names),
            )
            new_dataframe = concatenated.set_index_from_columns(
                keys=new_index.names
            )._dataframe
        elif isinstance(new_index, DBMSPositionMapping):
            raise make_exception(
                NotImplementedError,
                PonderError.QUERY_COMPILER_SET_INDEX_TO_POSITION_MAPPING,
                "Cannot set index to a DBMSPositionMapping yet",
            )
        else:
            new_dataframe = self._dataframe.rename(new_row_labels=new_index)
        self._dataframe = new_dataframe

    def _get_index(self):
        return self._dataframe.index

    columns = property(_get_columns, _set_columns)  # mutable!
    index = property(_get_index, _set_index)

    @property
    def dtypes(self):
        return self._dataframe.dtypes

    @classmethod
    def from_pandas(cls, df, data_cls):
        # hopefully shouldn't end up here anyway because our I/O classes shouldn't call
        # this method. We have to implement it becaue it's an abstract method of the
        # base query compiler class.
        raise make_exception(
            NotImplementedError,
            PonderError.QUERY_COMPILER_FROM_PANDAS,
            "Cannot create a query compiler from pandas",
        )

    def to_sql(self):
        return self._dataframe.to_sql()

    def to_pandas(self, ignore_warning=False):
        try:
            pandas_df = self._dataframe.to_pandas()
            if pandas_df.index.name == __UNNAMED_INDEX_COLUMN__:
                pandas_df.index.name = None
        except Exception:
            import traceback

            traceback.print_exc()
            raise
        if (
            not ignore_warning
            and len(pandas_df) > get_execution_configuration().row_transfer_limit
        ):
            warnings.warn(
                "Switching away from database execution mode."
                + " A limited sample of"
                + f" {get_execution_configuration().row_transfer_limit}"
                + " rows was loaded into memory for local execution."
                + " To change this limit, run"
                + " ponder.configure(row_transfer_limit=X) with"
                + " a different value."
            )
            pandas_df = pandas_df[0:-1]
        return pandas_df

    def to_csv(self, **kwargs):
        qc = self
        if "index" in kwargs:
            if kwargs["index"]:
                qc = self.reset_index()
        qc._dataframe.to_csv(**kwargs)

    def to_numpy(self, **kwargs):
        return self.to_pandas().to_numpy(**kwargs)

    def default_to_pandas(self, pandas_op, *args, **kwargs):
        raise make_exception(
            NotImplementedError,
            PonderError.QUERY_COMPILER_DEFAULT_TO_PANDAS,
            (
                f"The pandas function {getattr(pandas_op, '__name__', pandas_op)} "
                "has not been implemented yet"
            ),
        )

    def transpose(self, *args, **kwargs):
        return self.__constructor__(self._dataframe.transpose())

    def copy(self):
        return self.__constructor__(self._dataframe)

    def add_prefix(self, prefix, axis=1):
        if axis == 1:
            new_columns = self.columns.map(lambda c: f"{prefix}{c}")
            result = self.copy()
            result.columns = new_columns
            return result
        else:
            raise make_exception(
                NotImplementedError,
                PonderError.ADD_PREFIX_AXIS_0,
                "add_prefix() on axis=0 is not supported yet",
            )

    def add_suffix(self, suffix, axis=1):
        if axis == 1:
            new_columns = self.columns.map(lambda c: f"{c}{suffix}")
            result = self.copy()
            result.columns = new_columns
            return result
        else:
            raise make_exception(
                NotImplementedError,
                PonderError.ADD_SUFFIX_AXIS_0,
                "add_suffix() on axis=0 is not supported yet",
            )

    def insert(self, loc, column, value):
        if isinstance(value, (list, np.ndarray)):
            # Need to add this in-memory object to DBMS as a table
            pandas_df = pandas.DataFrame(value, columns=[column])

            return self.__constructor__(
                self._dataframe.insert_pandas_df(pandas_df, add_col_last=True)
            )

        if isinstance(value, DBMSQueryCompiler):
            self_leaves = self._dataframe.get_query_tree().data_hash()
            value_leaves = value._dataframe.get_query_tree().data_hash()
            # if the leaf nodes of the two sides are the same use
            # derived column. Otherwise use a join.
            if self_leaves == value_leaves:
                inserted = self.__constructor__(
                    self._dataframe.derived_column(value._dataframe, column)
                )
            else:
                value = value.copy()
                value.columns = [column]
                inserted = self.concat(
                    axis=Axis.ROW_WISE,
                    other=[value],
                    how="outer",
                )

            if loc < len(self.columns):
                new_columns = self.columns.insert(loc, column)
                return self.__constructor__(
                    inserted._dataframe.mask(col_labels=new_columns)
                )
            else:
                return inserted

        elif is_scalar(value):
            return self.__constructor__(
                self._dataframe.setitem_scalar_broadcast(column, value)
            )

        if loc != 0:
            # loc != 0 can be handled, but, it requires more code.
            # For to_sql we only need to handle loc=0. So adding code
            # only for that now.
            raise make_exception(
                NotImplementedError,
                PonderError.QUERY_COMPILER_INSERT_NONZERO_LOC,
                f"Cannot insert column at nonzero position {loc} yet",
            )
        if isinstance(value, DBMSPositionMapping):
            return self.__constructor__(
                self._dataframe.insert_pandas_df(
                    value._to_pandas().to_frame(index=False, name=column)
                )
            )
        elif hasattr(value, "to_frame"):
            try:
                pandas_df = value.to_frame(index=False, name=column)
                # have to drop the index from the current dataframe - otherwise
                # concat won't work
                self_df = self._dataframe.from_labels(drop=True)
                return self.__constructor__(self_df.insert_pandas_df(pandas_df))
            except Exception:
                raise make_exception(
                    NotImplementedError,
                    PonderError.QUERY_COMPILER_INSERT_TO_FRAME_FAILED,
                    "Ponder Internal Error: failed to use to_frame() to insert "
                    + f"value of type {type(value).__name__}",
                )
        raise make_exception(
            NotImplementedError,
            PonderError.QUERY_COMPILER_INSERT_UNSUPPORTED_TYPE,
            f"Cannot insert column of type {type(value).__name__} yet",
        )

    def setitem(self, axis, key, value):
        if axis != 0:
            raise make_exception(
                NotImplementedError,
                PonderError.QUERY_COMPILER_SETITEM_AXIS_1,
                "Inserting rows is not supported yet",
            )
        if isinstance(value, DBMSQueryCompiler):
            if key not in self.columns:
                return self.insert(len(self.columns), key, value)
            new_loc = self.columns.get_indexer_for([key])[0]
            result = self.insert(new_loc, key + "_", value).drop(columns=[key])
            result.columns = list(self.columns.copy())
            return result
        if not is_scalar(value):
            raise make_exception(
                NotImplementedError,
                PonderError.QUERY_COMPILER_SETITEM_NON_SCALAR_OR_QUERY_COMPILER,
                f"Cannot insert column of type {type(value).__name__} yet",
            )
        if key in self.columns:
            raise make_exception(
                NotImplementedError,
                PonderError.QUERY_COMPILER_SETITEM_EXISTING_COLUMN_WITH_SCALAR,
                "Replacing existing column with a scalar is not supported yet",
            )
        return self.insert(len(self.columns), key, value)

    def getitem_array(self, key):
        if isinstance(key, type(self)):
            root_node = key._dataframe._query_tree._root
            predicates = root_node.get_predicates()
            if len(predicates) > 0:
                if (
                    # Getitem with 2d bool array is equivalent to mask
                    # and has a different implementation.
                    len(root_node.get_column_names())
                    == 1
                ):
                    new_df = self._dataframe.get_from_binary_comparison(root_node)
                    return self.__constructor__(new_df)
        if isinstance(key, BaseQueryCompiler):
            # TODO: in case key is a snowflake query compiler with predicates
            # like col1 == 3, pull the predicates up to our query.
            key = key.to_pandas().squeeze(axis=1)
        if is_bool_indexer(key):
            if isinstance(key, pandas.Series) and not key.index.equals(self.index):
                warnings.warn(
                    "Boolean Series key will be reindexed to match DataFrame index.",
                    PendingDeprecationWarning,
                    stacklevel=3,
                )
            raise make_exception(
                NotImplementedError,
                PonderError.QUERY_COMPILER_GETITEM_BOOL_INDEXER,
                "Cannot select rows with bool indexer yet",
            )
        else:
            extra_columns = [k for k in key if k not in self.columns]
            if len(extra_columns) > 0:
                raise make_exception(
                    KeyError,
                    PonderError.QUERY_COMPILER_GETITEM_KEY_ERROR,
                    f"{str(extra_columns).replace(',', '')} not in columns",
                )
            return self.getitem_column_array(key)

    def getitem_column_array(self, key, numeric=False):
        # Convert to list for type checking
        if isinstance(key, slice) and key == slice(None):
            return self.copy()
        elif isinstance(key, slice):
            key = self.columns[key]
            numeric = False
        elif not is_list_like(key):
            key = [key]
        elif is_bool_indexer(key):
            key = self.columns[key]
        if not numeric:
            key = self.columns.get_indexer_for(key)
        return self.take_2d_positional(columns=key)

    def take_2d_labels(
        self,
        index,
        columns,
    ):
        """Take the given labels.

        Parameters
        ----------
        index : slice, scalar, list-like, or BaseQueryCompiler
            Labels of rows to grab.
        columns : slice, scalar, list-like, or BaseQueryCompiler
            Labels of columns to grab.

        Returns
        -------
        BaseQueryCompiler
            Subset of this QueryCompiler.
        """
        return self.getitem_row_labels_array(index).getitem_column_array(columns)

    def getitem_row_labels_array(self, labels):
        if isinstance(self.index, DBMSDateTimeIndex):
            # Assume this is a valid period in string format
            if isinstance(labels, str):
                labels = pandas.Period(labels)
            if isinstance(labels, pandas.Period):
                labels = slice(labels.to_timestamp(), (labels + 1).to_timestamp())
        if isinstance(labels, slice):
            # edge case where we are not filtering by anything
            if labels == slice(None):
                return self.copy()
            label_start = labels.start
            label_stop = labels.stop

            # Convert the values within an existing timeslice to timestamps
            if isinstance(self.index, DBMSDateTimeIndex):
                if isinstance(label_start, str):
                    label_start = pandas.Period(label_start).to_timestamp()
                if isinstance(label_stop, str):
                    label_stop = pandas.Period(label_stop).to_timestamp()

            if label_start is not None and label_stop is not None:
                df_filtered = self._dataframe.filter_rows(
                    RowWiseFilterPredicates.RowValueBetweenInclusive(
                        self.index.name, label_start, label_stop
                    )
                )
            if label_start is not None and label_stop is None:
                df_filtered = self._dataframe.filter_rows(
                    RowWiseFilterPredicates.RowValueGE(self.index.name, label_start)
                )
            if label_start is None and label_stop is not None:
                df_filtered = self._dataframe.filter_rows(
                    RowWiseFilterPredicates.RowValueLE(self.index.name, label_stop)
                )
            return self.__constructor__(df_filtered)
        if labels is not None and not isinstance(labels, list):
            labels = [labels]
        return self.__constructor__(self._dataframe.mask(row_labels=labels))

    def getitem_row_array(self, key):
        if not is_list_like(key):
            key = [key]
        else:
            key = list(key)
        return self.__constructor__(self._dataframe.mask(row_positions=key))

    def pivot(self, index, columns, values, add_qualifier_to_new_column_names=True):
        # TODO: raise an error if groupby(index+columns).size() is not all ones, pandas
        # raises ValueError: Index contains duplicate entries, cannot reshape
        # and we just pick the min value.
        return self.pivot_table(
            index=index,
            columns=columns,
            values=values,
            aggfunc="min",
            fill_value=None,
            margins=False,
            dropna=True,
            margins_name="All",
            observed=False,
            sort=True,
            add_qualifier_to_new_column_names=add_qualifier_to_new_column_names,
        )

    def pivot_table(
        self,
        index,
        values,
        columns,
        aggfunc,
        fill_value,
        margins,
        dropna,
        margins_name,
        observed,
        sort,
        add_qualifier_to_new_column_names=True,
    ):
        """Create a spreadsheet-style pivot table from underlying data.

        Parameters
        ----------
        index : label, pandas.Grouper, array or list of such
        values : label, optional
        columns : column, pandas.Grouper, array or list of such
        aggfunc : callable(pandas.Series) -> scalar, dict of list of such
        fill_value : scalar, optional
        margins : bool
        dropna : bool
        margins_name : str
        observed : bool
        sort : bool

        Returns
        -------
        BaseQueryCompiler
        """
        if (isinstance(index, list) and len(index) > 1) or (
            isinstance(columns, list) and len(columns) > 1
        ):
            raise make_exception(
                NotImplementedError,
                PonderError.PIVOT_TABLE_EITHER_AXIS_HAS_LENGTH_GREATER_THAN_ONE,
                "pivot_table() does not support frames with multiindex yet",
            )
        if fill_value is not None:
            raise make_exception(
                NotImplementedError,
                PonderError.PIVOT_TABLE_FILL_VALUE_NOT_NONE,
                "pivot_table() does not support non-None param fill_value yet",
            )
        if margins:
            raise make_exception(
                NotImplementedError,
                PonderError.PIVOT_TABLE_MARGINS_TRUE,
                "pivot_table() does not support margins=True yet",
            )
        if not dropna:
            raise make_exception(
                NotImplementedError,
                PonderError.PIVOT_TABLE_DROPNA_FALSE,
                "pivot_table() does not support dropna=False yet",
            )
        if margins_name != "All":
            raise make_exception(
                NotImplementedError,
                PonderError.PIVOT_TABLE_MARGINS_NAME_NOT_ALL,
                "pivot_table() does not support margins_name != 'All' yet",
            )
        if observed:
            raise make_exception(
                NotImplementedError,
                PonderError.PIVOT_TABLE_OBSERVED_TRUE,
                "pivot_table() does not support observed=True yet",
            )
        if not sort:
            raise make_exception(
                NotImplementedError,
                PonderError.PIVOT_TABLE_SORT_FALSE,
                "pivot_table() does not support sort=False yet",
            )

        if not isinstance(index, list):
            index = [index]
        if not isinstance(columns, list):
            columns = [columns]
        values_list = values if isinstance(values, list) else [values]
        # make an aggfunc dict regardless of what the user's aggfunc looks like, so we
        # can always use a dict in the next step.
        if is_dict_like(aggfunc):
            if len(aggfunc) == 0:
                # cryptic, but this matches pandas error
                raise make_exception(
                    ValueError,
                    PonderError.PIVOT_TABLE_DICT_AGGFUNC_EMPTY,
                    "No objects to concatenate",
                )
            nonexistent_keys = [k for k in aggfunc.keys() if k not in values_list]
            if len(nonexistent_keys) > 0:
                raise make_exception(
                    KeyError,
                    PonderError.PIVOT_TABLE_DICT_AGGFUNC_NONEXISTENT_KEYS,
                    f"Column(s) {nonexistent_keys} do not exist",
                )
            aggfunc_dict = aggfunc
        else:
            aggfunc_dict = {value: aggfunc for value in values_list}
        # aggregate each column and concatenate the results column-wise because
        # snowflake pivot() can only aggregate one column.
        # TODO(https://community.snowflake.com/s/ideas): If snowflake ever supports
        # aggregating multiple values with one PIVOT query, do that instead of doing
        # each pivot separately.
        if add_qualifier_to_new_column_names:
            add_qualifier_to_new_column_names = (
                isinstance(values, list) or len(columns) != 1
            )

        if len(aggfunc_dict) > 1:
            add_qualifier_to_new_column_names = True

        aggregations = [
            self.__constructor__(
                self._dataframe.pivot(
                    index=index,
                    columns=columns,
                    values_column_name=value,
                    aggfunc=groupby_function_to_reduce_enum(func),
                    add_qualifier_to_new_column_names=add_qualifier_to_new_column_names,
                )
            )
            for value, func in aggfunc_dict.items()
        ]
        all_pivoted = aggregations[0].concat(axis=1, other=aggregations[1:])
        return all_pivoted

    def get_dummies(self, columns, **kwargs):
        # TODO(https://github.com/modin-project/modin/issues/3108): should explicitly
        # list args instead of using kwargs in this method's signature.
        prefix = kwargs.get("prefix")
        prefix_sep = kwargs.get("prefix_sep")
        dummy_na = kwargs.get("dummy_na", False)
        if not is_list_like(columns):
            columns = [columns]
        else:
            columns = list(columns)

        # TODO(https://github.com/modin-project/modin/issues/5792): do this validation
        # at API layer.
        for arg_name, arg in (("prefix", prefix), ("prefix_sep", prefix_sep)):
            if is_list_like(arg):
                if len(arg) != len(columns):
                    len_msg = (
                        f"Length of '{arg_name}' ({len(arg)}) did not match the "
                        "length of the columns being encoded "
                        f"({len(columns)})."
                    )
                    raise make_exception(
                        ValueError,
                        PonderError.GET_DUMMIES_PREFIX_OR_PREFIX_SEP_LENGTH_MISMATCH,
                        len_msg,
                    )

        dummy_compilers = []
        for i, col in enumerate(columns):
            if prefix is None:
                column_prefix = col
            elif is_dict_like(prefix):
                column_prefix = prefix[col]
            elif is_list_like(prefix):
                column_prefix = prefix[i]
            else:
                column_prefix = prefix
            if is_dict_like(prefix_sep):
                column_prefix_sep = prefix_sep[col]
            elif is_list_like(prefix_sep):
                column_prefix_sep = prefix_sep[i]
            else:
                column_prefix_sep = prefix_sep
            dummy_compilers.append(
                self.__constructor__(
                    self._dataframe.get_dummies(
                        col, dummy_na, column_prefix, column_prefix_sep
                    )
                )
            )
        return dummy_compilers[0].concat(axis=1, other=dummy_compilers[1:])

    def take_2d_positional(self, index=None, columns=None):
        return self.__constructor__(
            self._dataframe.mask(row_positions=index, col_positions=columns)
        )

    def dot(self, other, *args, **kwargs):
        if len(self.columns) != len(other.index):
            raise make_exception(
                ValueError,
                PonderError.DOT_DIMENSION_MISMATCH,
                "matrices are not aligned",
            )

        def prepare_df(qc):
            numeric_cols = []
            new_cast_type = None
            transposed = False

            if isinstance(qc._dataframe, TransposedDBMSDataframe):
                transposed = True
                true_columns = qc._dataframe.transpose().columns
                true_dtypes = list(qc._dataframe.transpose().dtypes)
            else:
                true_columns = qc.columns
                true_dtypes = list(qc.dtypes)

            if len(set(true_dtypes)) > 1:
                for coltype in true_dtypes:
                    if "float" in str(coltype).lower():
                        new_cast_type = str(coltype)
                        break

            if new_cast_type is None:
                new_cast_type = str(true_dtypes[0])

            for idx, col in enumerate(true_columns):
                numeric_cols.append(str(idx))
            # The way QC has set columns property, it can accept a dict
            # as a part of _set_columns method
            if not transposed:
                qc._dataframe = qc._astype_with_rename(
                    col_dtypes=new_cast_type,
                    new_col_names=numeric_cols,
                    df=qc._dataframe,
                    reset_order=True,
                )
            else:
                # TODO: Needs debugging as the SQL of rename is not
                # getting generated correctly
                qc._dataframe._untransposed_frame = self._astype_with_rename(
                    col_dtypes=new_cast_type,
                    new_col_names=numeric_cols,
                    df=qc._dataframe._untransposed_frame,
                    reset_order=True,
                )
            return transposed

        transposed = prepare_df(self)
        transposed_other = prepare_df(other)
        if transposed:
            if transposed_other:
                return self.__constructor__(
                    self._dataframe.transpose().dot(
                        other._dataframe.transpose(),
                        transposed=True,
                        transposed_other=True,
                    )
                )
            else:
                return self.__constructor__(
                    self._dataframe.transpose().dot(
                        other._dataframe, transposed=True, transposed_other=False
                    )
                )
        else:
            if transposed_other:
                return self.__constructor__(
                    self._dataframe.dot(
                        other._dataframe.transpose(),
                        transposed=False,
                        transposed_other=True,
                    )
                )
            else:
                return self.__constructor__(
                    self._dataframe.dot(
                        other._dataframe, transposed=False, transposed_other=False
                    )
                )

    def drop(self, index=None, columns=None, errors: str = "raise"):
        if index is not None and len(index) > 0:
            index = [str(i) if not isinstance(i, str) else f"'{i}'" for i in index]
            new_obj = self.__constructor__(
                self._dataframe.filter_rows(
                    RowWiseFilterPredicates.RowValueNotEquals(self.index.name, index)
                )
            )
        else:
            new_obj = self
        if columns is None:
            return new_obj.copy()
        return new_obj.getitem_column_array(
            new_obj.columns[~new_obj.columns.isin(columns)], numeric=False
        )

    def isna(self):
        # built in function in snowflake
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.ISNA,
                    ["{0}"],
                    np.bool_,
                )
            )
        )

    def notna(self):
        # built in function in snowflake
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.NOTNA,
                    ["{0}"],
                    np.bool_,
                )
            )
        )

    def invert(self):
        # TODO(https://github.com/modin-project/modin/issues/6489): do this check in
        # modin
        for d in self.dtypes:
            if not (is_integer_dtype(d) or is_bool_dtype(d)):
                raise TypeError(f"bad operand type for unary ~: '{d}'".format(d))
        # can't do this as dataframe.map because `invert` can mean a different bitwise
        # operation on each column, e.g. bitwise not for integers, but boolean negation
        # for booleans.
        return self.__constructor__(self._dataframe.invert())

    def astype(self, col_dtypes, **kwargs):
        if is_scalar(col_dtypes) or is_categorical_dtype(col_dtypes):
            col_dtypes = [col_dtypes] * len(self.columns)
            col_dtypes = dict(zip(list(self.columns), col_dtypes))
        generalized_current_types_dict = dict(
            zip(
                self.dtypes.keys(), _generalize_types(self.dtypes.values, use_num=False)
            )
        )
        generalized_target_types_dict = dict(
            zip(
                col_dtypes.keys(), _generalize_types(col_dtypes.values(), use_num=False)
            )
        )
        correct_cols = []
        for col in generalized_target_types_dict.keys():
            if (
                generalized_target_types_dict[col]
                == generalized_current_types_dict[col]
                and generalized_target_types_dict[col] != "date"
            ):
                # We exclude dates since date conversion is trickier
                # than casting for other types.
                correct_cols += [col]
        for col in correct_cols:
            generalized_target_types_dict.pop(col, None)
            col_dtypes.pop(col, None)
        if len(col_dtypes) == 0:
            return self.copy()
        # TODO: Make sure the `errors` argument is being passed down to this
        # layer.
        errors = "raise"
        generalized_target_types = generalized_target_types_dict.values()
        generalized_current_types = generalized_current_types_dict.values()
        current_types_df = pandas.DataFrame(
            zip(list(self.columns), generalized_current_types),
            index=pandas.RangeIndex(len(self.columns)),
            columns=["column", "gen_type"],
        )
        target_types_df = pandas.DataFrame(
            zip(col_dtypes.keys(), col_dtypes.values(), generalized_target_types),
            index=pandas.RangeIndex(len(col_dtypes)),
            columns=["target_column", "target_type", "target_generalized_type"],
        )
        # TODO: Use Enums instead of string literals.
        if len(
            target_types_df.query(
                "target_generalized_type in ('date', 'str', 'bool', 'int', 'float', "
                + "'category')"
            )
        ) != len(target_types_df):
            raise make_exception(
                NotImplementedError,
                PonderError.ASTYPE_TO_TYPE_NOT_SUPPORTED,
                "Casting to desired type is not supported yet",
            )
        current_types_df = current_types_df.join(
            target_types_df.set_index("target_column"), on="column", how="inner"
        )
        if current_types_df.empty:
            if errors == "raise":
                raise make_exception(
                    KeyError,
                    PonderError.ASTYPE_NO_MATCHING_FROM_COLUMN,
                    "Only a column name can be used for the key in "
                    + "a dtype mappings argument.",
                )
            return self
        # TODO: Use Enums instead of string literals.
        if len(
            current_types_df.query(
                "gen_type in ('date', 'str', 'bool', 'int', 'float')"
            )
        ) != len(current_types_df):
            raise make_exception(
                NotImplementedError,
                PonderError.ASTYPE_FROM_TYPE_NOT_SUPPORTED,
                "Casting from desired column type is not supported yet",
            )
        type_comp_dict = {
            "date": ["date", "str", "category"],
            "str": [
                "date",
                "str",
                "bool",
                "int",
                "float",
                "category",
            ],
            "bool": [
                "str",
                "bool",
                "int",
                "float",
                "category",
            ],
            "int": [
                "date",
                "str",
                "bool",
                "int",
                "float",
                "category",
            ],
            "float": [
                "date",
                "str",
                "bool",
                "int",
                "float",
                "category",
            ],
        }
        type_comp_dict_keys = sum(
            list(map(lambda x: [x[0]] * len(x[1]), type_comp_dict.items())), []
        )
        type_comp_dict_values = sum(type_comp_dict.values(), [])
        type_comp_df = pandas.DataFrame(
            zip(type_comp_dict_keys, type_comp_dict_values),
            index=pandas.RangeIndex(len(type_comp_dict_keys)),
            columns=["gen_type", "target_generalized_type"],
        )
        type_conversion_df = current_types_df.merge(
            type_comp_df, on=["gen_type", "target_generalized_type"], how="inner"
        )
        if type_conversion_df.empty:
            if errors == "raise":
                raise make_exception(
                    ValueError,
                    PonderError.ASTYPE_NO_MATCHING_TO_TYPE,
                    (
                        f"Column type {generalized_current_types} cannot "
                        + f"be cast to desired type {generalized_target_types}."
                    ),
                )
            return self
        # Build new dtypes from existing ones, but use a deep copy of the
        # original so we don't change this object's dtypes.
        new_dtypes = self.dtypes.copy(deep=True)
        changed_columns_gen_target_types_dict = type_conversion_df.set_index(
            "column"
        ).to_dict()["target_generalized_type"]
        changed_columns_gen_types_dict = type_conversion_df.set_index(
            "column"
        ).to_dict()["gen_type"]
        for col in changed_columns_gen_target_types_dict:
            target_type = type_conversion_df.set_index("column").to_dict()[
                "target_type"
            ][col]
            if is_string_dtype(target_type):
                new_dtypes[col] = pandas.StringDtype()
            elif is_bool_dtype(target_type):
                new_dtypes[col] = pandas.BooleanDtype()
            elif isinstance(target_type, pandas.CategoricalDtype):
                # e.g. the user has passed pd.Categorical([1, 2, 3])
                changed_columns_gen_target_types_dict[col] = new_dtypes[
                    col
                ] = target_type
            elif target_type == "category":
                # n.b every CategoricalDtype is equal to the string "category", so we
                # have to put this condition after the check for CategoricalDtype
                # have to materialize the unique values to get the dtype itself
                new_dtypes[col] = pandas.CategoricalDtype(
                    self.getitem_column_array([col])
                    .unique()
                    .to_pandas()
                    .squeeze(axis=1)
                    .sort_values()
                    .rename(None)
                    # categories cannot include nulls.
                    .dropna()
                )
            else:
                new_dtypes[col] = np.dtype(target_type)

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}\n
            changed_columns_gen_types_dict -->\n
            {changed_columns_gen_types_dict}\n
            changed_columns_gen_target_types_dict -->\n
            {changed_columns_gen_target_types_dict}\n
            self._dataframe.columns -->\n
            {self._dataframe.columns}\n
            new_dtypes -->\n
            {new_dtypes}
            self.columns -->\n
            {self.columns}
            kwargs -->\n
            {kwargs}
            """
        )

        return self.__constructor__(
            self._dataframe.cast_func(
                changed_columns_gen_types_dict,
                changed_columns_gen_target_types_dict,
                self._dataframe.columns,
                new_dtypes.tolist(),
                **kwargs,
            )
        )

    def _astype_with_rename(self, col_dtypes, new_col_names, df=None, reset_order=True):
        errors = "raise"
        if df is None:
            raise make_exception(
                ValueError,
                PonderError.ASTYPE_DF_NONE,
                "DF should not be none",
            )
        cols_to_consider = df.columns
        dtypes_to_consider = df.dtypes

        if is_scalar(col_dtypes):
            col_dtypes = [col_dtypes] * len(cols_to_consider)
            col_dtypes = dict(zip(list(cols_to_consider), col_dtypes))
        types = _generalize_types(list(dtypes_to_consider), use_num=False)
        columns_df = pandas.DataFrame(
            zip(list(cols_to_consider), types),
            index=pandas.RangeIndex(len(cols_to_consider)),
            columns=["column", "gen_type"],
        )
        types = _generalize_types(list(col_dtypes.values()), use_num=False)
        target_types_df = pandas.DataFrame(
            zip(col_dtypes.keys(), col_dtypes.values(), types),
            index=pandas.RangeIndex(len(col_dtypes)),
            columns=["target_column", "target_type", "target_gen_type"],
        )
        # TODO: Use Enums instead of string literals.
        if len(
            target_types_df.query(
                "target_gen_type in ('date', 'str', 'bool', 'int', 'float')"
            )
        ) != len(target_types_df):
            raise make_exception(
                NotImplementedError,
                PonderError.ASTYPE_TO_TYPE_NOT_SUPPORTED,
                "Casting to desired type is not supported yet",
            )
        columns_df = columns_df.join(
            target_types_df.set_index("target_column"), on="column", how="inner"
        )
        if columns_df.empty:
            if errors == "raise":
                raise make_exception(
                    KeyError,
                    PonderError.ASTYPE_NO_MATCHING_FROM_COLUMN,
                    "Only a column name can be used for the key in "
                    + "a dtype mappings argument.",
                )
            return self
        # TODO: Use Enums instead of string literals.
        if len(
            columns_df.query("gen_type in ('date', 'str', 'bool', 'int', 'float')")
        ) != len(columns_df):
            raise make_exception(
                NotImplementedError,
                PonderError.ASTYPE_FROM_TYPE_NOT_SUPPORTED,
                "Casting from desired column type is not supported yet",
            )
        type_comp_dict = {
            "date": ["date", "str"],
            "str": ["date", "str", "bool", "int", "float"],
            "bool": ["str", "bool", "int", "float"],
            "int": ["str", "bool", "int", "float"],
            "float": ["str", "bool", "int", "float"],
        }
        type_comp_dict_keys = sum(
            list(map(lambda x: [x[0]] * len(x[1]), type_comp_dict.items())), []
        )
        type_comp_dict_values = sum(type_comp_dict.values(), [])
        type_comp_df = pandas.DataFrame(
            zip(type_comp_dict_keys, type_comp_dict_values),
            index=pandas.RangeIndex(len(type_comp_dict_keys)),
            columns=["gen_type", "target_gen_type"],
        )
        columns_df = columns_df.merge(
            type_comp_df, on=["gen_type", "target_gen_type"], how="inner"
        )
        if columns_df.empty:
            if errors == "raise":
                raise make_exception(
                    ValueError,
                    PonderError.ASTYPE_NO_MATCHING_TO_TYPE,
                    "Column type cannot be cast to desired type.",
                )
            return self
        # Build new dtypes from existing ones, but use a deep copy of the
        # original so we don't change this object's dtypes.
        new_dtypes = dtypes_to_consider.copy(deep=True)
        changed_columns_gen_target_types_dict = columns_df.set_index(
            "column"
        ).to_dict()["target_gen_type"]
        changed_columns_gen_types_dict = columns_df.set_index("column").to_dict()[
            "gen_type"
        ]
        for col in changed_columns_gen_target_types_dict:
            target_type = columns_df.set_index("column").to_dict()["target_type"][col]
            if is_string_dtype(target_type):
                new_dtypes[col] = pandas.StringDtype()
            elif is_bool_dtype(target_type):
                new_dtypes[col] = pandas.BooleanDtype()
            else:
                new_dtypes[col] = np.dtype(target_type)

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}\n
            changed_columns_gen_types_dict -->\n
            {changed_columns_gen_types_dict}\n
            changed_columns_gen_target_types_dict -->\n
            {changed_columns_gen_target_types_dict}\n
            cols_to_consider -->\n
            {cols_to_consider}\n
            new_dtypes -->\n
            {new_dtypes}\n
            new_col_names -->\n
            {new_col_names}
            """
        )
        return df.cast_func(
            cast_from_map=changed_columns_gen_types_dict,
            cast_to_map=changed_columns_gen_target_types_dict,
            column_names=cols_to_consider,
            return_types=new_dtypes.tolist(),
            new_col_names=new_col_names,
            reset_order=reset_order,
        )

    def clip(self, lower, upper, axis, inplace=False):
        if lower is None and upper is None:
            return self
        if axis == 0:
            raise make_exception(
                NotImplementedError,
                PonderError.CLIP_AXIS_0_NOT_SUPPORTED,
                "clip() does not support axis=0 yet",
            )
        if isinstance(lower, type(self)) or isinstance(upper, type(self)):
            raise make_exception(
                NotImplementedError,
                PonderError.CLIP_LOWER_OR_UPPER_BOUNDS_MODIN_PANDAS_OBJECTS_NOT_SUPPORTED,  # noqa: E501
                "clip() cannot take modin.pandas objects as `lower` or `upper` "
                + "bounds yet",
            )

        lower_is_scalar = is_scalar(lower)
        upper_is_scalar = is_scalar(upper)
        if lower is not None and is_scalar(lower):
            lower = np.full(shape=len(self.columns), fill_value=lower)
        if upper is not None and is_scalar(upper):
            upper = np.full(shape=len(self.columns), fill_value=upper)
        lower_fixed = lower
        upper_fixed = upper
        # correct for inverted values. While these
        # inputs do not make sense, pandas produces
        # results from these inputs without error
        # https://github.com/pandas-dev/pandas/issues/52147
        if lower is not None and upper is not None:
            for i, (l, u) in enumerate(zip(lower, upper)):
                if u < l:
                    if upper_is_scalar and lower_is_scalar:
                        lower_fixed[i] = min(l, u)
                        upper_fixed[i] = max(l, u)
                    if upper_is_scalar and not lower_is_scalar:
                        lower_fixed[i] = u
                        upper_fixed[i] = u
                    if not upper_is_scalar:
                        # POND-941
                        # We do not match the pandas
                        # behavior here; though it is
                        # undocumented.
                        lower_fixed[i] = l
                        upper_fixed[i] = l

        return self.__constructor__(
            self._dataframe.clip(lower_fixed, upper_fixed, axis)
        )

    def replace(
        self,
        to_replace=None,
        value=no_default,
        inplace=False,
        limit=None,
        regex=False,
        method: "str | NoDefault" = no_default,
    ):
        # Apply some rules to conform with Pandas requirements,
        # and also to perform early pruning and merging of various cases
        # to reduce the size of the parameter space.

        # Guess we have to pay the piper sometime. We're generating dialect
        # specific code here in this layer. It was done for speed of execution,
        # but, now needs to be refactored.  Refactoring will be time consuming
        # so putting dataframe column names into query tree column for now.
        df = self._dataframe.pushdown_df_names_to_query_tree()
        if value is not no_default and method is not no_default:
            value = no_default
        if (
            value is no_default
            and method is no_default
            and not is_dict_like(to_replace)
        ):
            method = "ffill"
        if method == "pad":
            method = "ffill"
        if method == "backfill":
            method = "bfill"
        if is_dict_like(to_replace):
            method = no_default
        if (
            is_dict_like(to_replace)
            and not is_dict_like(list(to_replace.values())[0])
            and value is no_default
        ):
            value = list(
                map(
                    lambda x: x[0] if is_list_like(x) else x,
                    to_replace.values(),
                )
            )
            to_replace = to_replace.keys()
        if (
            is_dict_like(to_replace)
            and is_dict_like(list(to_replace.values())[0])
            and value is not no_default
        ):
            raise make_exception(
                ValueError,
                PonderError.REPLACE_VALUE_CANNOT_BE_SET_WHEN_TO_REPLACE_IS_A_NESTED_DICT,  # noqa: E501
                "value cannot be set when to_replace is a nested dictionary",
            )
        if method is not no_default:
            regex = False
        if (
            not is_list_like(to_replace)
            and is_list_like(value)
            and not is_dict_like(value)
        ):
            raise make_exception(
                ValueError,
                PonderError.REPLACE_VALUE_CANNOT_BE_A_LIST_WHEN_TO_REPLACE_IS_NOT_A_LIST,  # noqa: E501
                "value cannot be a list when to_replace is not a list",
            )
        if (
            is_list_like(to_replace)
            and not is_dict_like(to_replace)
            and is_dict_like(value)
        ):
            value = list(value)
        if (
            is_list_like(to_replace)
            and not is_dict_like(to_replace)
            and is_list_like(value)
            and not is_dict_like(value)
            and len(to_replace) != len(value)
        ):
            raise make_exception(
                ValueError,
                PonderError.TO_REPLACE_AND_VALUE_LISTS_MUST_MATCH_IN_LENGTH,
                "to_replace and value lists must match in length",
            )
        if is_scalar(to_replace):
            to_replace = [to_replace]
        if (
            is_scalar(value)
            and is_list_like(to_replace)
            and not is_dict_like(to_replace)
        ):
            value = [value] * len(to_replace)

        # For every possible parameter combination, try to generate a cananonical
        # representation in the form of a Pandas dataframe whose columns are 'column',
        # 'to_replace', and optionally 'value'. 'value' will only be present if the
        # replacement values are provided. Both 'to_replace' and 'value' contain
        # corresponding lists of values capturing those to be replaced and those to use
        # for replacement, respectively. 'to_replace' may also contain lists of patterns
        # to be matched during replacement. Along the way, perform type checking across
        # column types, to_replace types, and value types.
        types = _generalize_types(list(self.dtypes))
        column_df = pandas.DataFrame(
            zip(types, list(self.columns)),
            index=pandas.RangeIndex(len(self.columns)),
            columns=["column_type", "column"],
        )
        if is_list_like(to_replace) and not is_dict_like(to_replace):
            types = _generalize_types(_get_types(to_replace))
            to_replace = _add_quotes(to_replace)
            to_replace_df = pandas.DataFrame(
                zip(types, to_replace),
                index=pandas.RangeIndex(len(to_replace)),
                columns=["to_replace_type", "to_replace"],
            )
            to_replace_df["to_replace"] = to_replace_df["to_replace"].apply(
                lambda x: [x]
            )

            def list_agg(series):
                return reduce(
                    lambda x, y: [x, y]
                    if is_scalar(x) and is_scalar(y)
                    else [x] + y
                    if is_scalar(x)
                    else x + [y]
                    if is_scalar(y)
                    else x + y,
                    series,
                )

            agg_columns = []
            if is_list_like(value):
                types = _generalize_types(_get_types(value))
                value = _add_quotes(value)
                value_df = pandas.DataFrame(
                    zip(types, value),
                    index=pandas.RangeIndex(len(value)),
                    columns=["value_type", "value"],
                )
                value_df["value"] = value_df["value"].apply(lambda x: [x])
                to_replace_df = pandas.concat([to_replace_df, value_df], axis=1)
                if (
                    not to_replace_df["to_replace_type"]
                    .eq(to_replace_df["value_type"])
                    .all()
                ):
                    raise make_exception(
                        NotImplementedError,
                        PonderError.TYPE_MISMATCH_BETWEEN_TO_REPLACE_AND_VALUE_NOT_SUPPORTED,  # noqa: E501
                        "Type mismatches between to_replace values and replacement"
                        + " values are not supported yet",
                    )
                agg_columns = ["column_type", "to_replace", "value"]
            else:
                assert value is no_default
                assert method is not no_default
                agg_columns = ["column_type", "to_replace"]
            column_df = column_df.join(
                to_replace_df.set_index("to_replace_type"),
                on="column_type",
                how="inner",
            )
            if column_df.empty:
                return self
            column_df = column_df.groupby(by=["column"], as_index=False)[
                agg_columns
            ].agg(list_agg)
            for col in agg_columns[1::]:
                column_df[col] = column_df[col].apply(
                    lambda x: [x] if is_scalar(x) else x
                )
        elif is_dict_like(to_replace) and is_dict_like(list(to_replace.values())[0]):
            assert value is no_default
            assert method is no_default
            value = {k: list(v.values()) for k, v in to_replace.items()}
            to_replace = {k: list(v.keys()) for k, v in to_replace.items()}
        if is_dict_like(to_replace) and not is_dict_like(list(to_replace.values())[0]):
            types = _generalize_types(_get_types(to_replace.values()))
            to_replace_values = _add_quotes(to_replace.values())
            to_replace_df = pandas.DataFrame(
                zip(types, to_replace.keys(), to_replace_values),
                index=pandas.RangeIndex(len(to_replace)),
                columns=["to_replace_type", "to_replace_column", "to_replace"],
            )
            to_replace_df["to_replace"] = to_replace_df["to_replace"].apply(
                lambda x: [x] if is_scalar(x) else x
            )
            if (
                not to_replace_df["to_replace_type"]
                .apply(lambda x: len(set(x)) == 1 if not is_scalar(x) else True)
                .all()
            ):
                raise make_exception(
                    NotImplementedError,
                    PonderError.TYPE_MISMATCH_BETWEEN_TO_REPLACE_VALUES_SAME_COLUMN_NOT_SUPPORTED,  # noqa: E501
                    "Mixed types for to_replace values for the same column are not"
                    + " supported yet",
                )
            to_replace_df["to_replace_type"] = to_replace_df["to_replace_type"].apply(
                lambda x: x[0] if is_list_like(x) else x
            )
            if is_scalar(value):
                value = [value]
                types = _generalize_types(_get_types(value))
                value_df = pandas.DataFrame(
                    zip(types, value),
                    index=pandas.RangeIndex(len(value)),
                    columns=["value_type", "value"],
                )
                value_df["value"] = value_df["value"].apply(lambda x: [x])
                to_replace_df = to_replace_df.join(
                    value_df.set_index("value_type"),
                    on="to_replace_type",
                    how="inner",
                )
                if to_replace_df.empty:
                    return self
                to_replace_df = to_replace_df[
                    ["to_replace_type", "to_replace_column", "to_replace"]
                ]
                value = value[0]
                value = {col: value for col in to_replace_df["to_replace_column"]}
            if is_dict_like(value):
                for key, val in to_replace.items():
                    if key in value:
                        if (
                            is_list_like(val)
                            and not is_dict_like(val)
                            and is_list_like(value[key])
                            and not is_dict_like(value[key])
                            and len(val) != len(value[key])
                        ):
                            raise make_exception(
                                ValueError,
                                PonderError.TO_REPLACE_AND_VALUE_LISTS_MUST_MATCH_IN_LENGTH_2,  # noqa: E501
                                "to_replace and value lists must match in length",
                            )
                        if (
                            is_list_like(val)
                            and not is_dict_like(val)
                            and is_scalar(value[key])
                        ):
                            value[key] = [value[key]] * len(val)
                types = _generalize_types(_get_types(value.values()))
                value_values = _add_quotes(value.values())
                value_df = pandas.DataFrame(
                    zip(types, value.keys(), value_values),
                    index=pandas.RangeIndex(len(value)),
                    columns=["value_type", "value_column", "value"],
                )
                value_df["value"] = value_df["value"].apply(
                    lambda x: [x] if is_scalar(x) else x
                )
                if (
                    not value_df["value_type"]
                    .apply(lambda x: len(set(x)) == 1 if not is_scalar(x) else True)
                    .all()
                ):
                    raise make_exception(
                        NotImplementedError,
                        PonderError.TYPE_MISMATCH_BETWEEN_VALUE_VALUES_SAME_COLUMN_NOT_SUPPORTED_2,  # noqa: E501
                        "Mixed types for replacement values for the same column are not"
                        + " supported yet",
                    )
                value_df["value_type"] = value_df["value_type"].apply(
                    lambda x: x[0] if is_list_like(x) else x
                )
                to_replace_df = to_replace_df.join(
                    value_df.set_index("value_column"),
                    on="to_replace_column",
                    how="inner",
                )
                if to_replace_df.empty:
                    return self
                if (
                    not to_replace_df["to_replace_type"]
                    .eq(to_replace_df["value_type"])
                    .all()
                ):
                    raise make_exception(
                        NotImplementedError,
                        PonderError.TYPE_MISMATCH_BETWEEN_TO_REPLACE_VALUES_AND_REPLACEMENT_VALUES_NOT_SUPPORTED,  # noqa: E501
                        "Type mismatches between to_replace values and replacement"
                        + " values are not supported yet",
                    )
            else:
                assert value is no_default
                assert method is not no_default
            column_df = column_df.join(
                to_replace_df.set_index("to_replace_column"),
                on="column",
                how="inner",
            )
            if column_df.empty:
                return self
            if not column_df["column_type"].eq(column_df["to_replace_type"]).all():
                raise make_exception(
                    NotImplementedError,
                    PonderError.TYPE_MISMATCH_BETWEEN_TO_REPLACE_VALUES_AND_COLUMN_NOT_SUPPORTED,  # noqa: E501
                    "Type mismatches between to_replace values and corresponding column"
                    + " are not supported yet",
                )

        # Use the generated Pandas dataframe to generate the sql framgents to be passed
        # to the appropriate query tree nodes.
        changed_columns = column_df["column"].to_list()
        unchanged_columns = [
            col for col in self.columns.to_list() if col not in changed_columns
        ]
        changed_str_columns = column_df["column"][
            column_df["column_type"] == "str"
        ].to_list()
        to_replace_dict = column_df.set_index("column").to_dict()["to_replace"]
        if "value" in column_df.columns:
            value_dict = column_df.set_index("column").to_dict()["value"]
            exp_dict = {}
            for col, v1 in to_replace_dict.items():
                v2 = value_dict[col]
                if col in changed_str_columns and regex:
                    exp = f"{col}"
                    for i in range(len(v1)):
                        exp = f"REGEXP_REPLACE({exp},{v1[i]},{v2[i]})"
                elif len(set(v2)) == 1:
                    exp = (
                        f"IFF({col} in ({', '.join([f'{x}' for x in v1])}), {v2[0]},"
                        f" {col})"
                    )
                else:
                    whens = "WHEN ".join(
                        [f"{col}={x} THEN {y} " for (x, y) in zip(v1, v2)]
                    )
                    exp = f"CASE WHEN {whens} ELSE {col} END"
                exp_dict[col] = exp

            columns_selection = ", ".join(
                f"{col if col in unchanged_columns else exp_dict[col]} AS {col}"
                for col in self.columns
            )
            return self.__constructor__(
                df.project(
                    axis=1,
                    columns_selection=columns_selection,
                    project_column_names=df.columns,
                    project_column_types=None,
                )
            )
        else:
            assert method is not no_default
            assert regex is False

            suffix = "_PONDER_ORIG"
            project_column_types = df._query_tree._root.get_column_types()
            exp_dict = {}
            for col in changed_columns:
                project_column_types.append(
                    dict(
                        zip(
                            self.columns,
                            df._query_tree._root.get_column_types(),
                        )
                    )[col]
                )
                inner_exp = (
                    f"IFF({col} IN"
                    f" ({', '.join([f'{x}' for x in to_replace_dict[col]])}), NULL,"
                    f" IFNULL({col}, {to_replace_dict[col][0]}))"
                )
                if method == "ffill" and limit is None:
                    exp_dict[col] = (
                        f"LAST_VALUE({inner_exp}) IGNORE NULLS OVER (ORDER BY"
                        f" {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN UNBOUNDED"
                        " PRECEDING AND CURRENT ROW)"
                    )
                elif method == "ffill" and limit is not None:
                    exp_dict[col] = (
                        f"LAST_VALUE({inner_exp}) IGNORE NULLS OVER (ORDER BY"
                        f" {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN"
                        f" {limit} PRECEDING AND 0 FOLLOWING)"
                    )
                elif method == "bfill" and limit is None:
                    exp_dict[col] = (
                        f"FIRST_VALUE({inner_exp}) IGNORE NULLS OVER (ORDER BY"
                        f" {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN CURRENT ROW AND"
                        " UNBOUNDED FOLLOWING)"
                    )
                elif method == "bfill" and limit is not None:
                    exp_dict[col] = (
                        f"FIRST_VALUE({inner_exp}) IGNORE NULLS OVER (ORDER BY"
                        f" {__PONDER_ORDER_COLUMN_NAME__} ROWS BETWEEN 0 PRECEDING AND"
                        f" {limit} FOLLOWING)"
                    )

            columns_selection = ", ".join(
                [
                    f"{col if col in unchanged_columns else exp_dict[col]} AS {col}"
                    for col in self.columns
                ]
            )
            columns_selection = (
                f"{columns_selection},"
                f' {", ".join([f"{col} AS {col}{suffix}" for col in changed_columns])}'
            )
            df1 = self.__constructor__(
                df.project(
                    axis=1,
                    columns_selection=columns_selection,
                    project_column_names=df.columns.to_list()
                    + list(map(lambda x: f"{x}{suffix}", changed_columns)),
                    project_column_types=project_column_types,
                )
            )

            exp_dict = {}
            for col in changed_columns:
                exp_dict[col] = (
                    f"IFF({col} IS NULL, {col}{suffix}, IFF({col} ="
                    f" {to_replace_dict[col][0]}, NULL, {col}))"
                )

            columns_selection = ", ".join(
                [
                    f"{col if col in unchanged_columns else exp_dict[col]} AS {col}"
                    for col in self.columns
                ]
            )
            return self.__constructor__(
                df1._dataframe.project(
                    axis=1,
                    columns_selection=columns_selection,
                    project_column_names=df.columns,
                    project_column_types=None,
                )
            )

    def mask(self, cond, other, **kwargs):
        if isinstance(cond, pd.Series) and cond.shape[0] == len(self.index):
            root_node = cond._query_compiler._dataframe._query_tree._root
            predicates = root_node.get_predicates()
            columns_to_upcast_to_object = None
            value_dict = None
            if is_scalar(other):
                if other is not np.nan:
                    value_dict = {c: other for c in self.columns}
                    columns_to_upcast_to_object = [
                        col
                        for col, value in value_dict.items()
                        if (
                            is_numeric_dtype(self.dtypes[col])
                            and isinstance(value, str)
                        )
                        or (is_number(value) and is_string_dtype(self.dtypes[col]))
                        or (
                            is_datetime64_dtype(self.dtypes[col])
                            and isinstance(value, str)
                        )
                    ]
            elif other is NoDefault or other is no_default:
                pass
            elif isinstance(other, pd.Series):
                raise make_exception(
                    exception_class=NotImplementedError,
                    code=PonderError.MASK_WITH_OTHER_AS_SERIES_NOT_IMPLEMENTED,
                    message="Mask with other as a type of "
                    + f"{type(other)} not implemented",
                )
            else:
                raise make_exception(
                    exception_class=NotImplementedError,
                    code=PonderError.MASK_OTHER_TYPE_UNKNOWN_NOT_IMPLEMENTED,
                    message="Mask with other as a type of "
                    + f"{type(other)} not implemented",
                )

            return self.__constructor__(
                self._dataframe.pandas_mask(
                    mask_predicate=predicates[0],
                    value_dict=value_dict,
                    columns_to_upcast_to_object=columns_to_upcast_to_object,
                )
            )
        else:
            raise make_exception(
                exception_class=NotImplementedError,
                code=PonderError.MASK_WITH_COND_AS_BOOL_NOT_IMPLEMENTED,
                message="Mask with cond as boolean not supported",
            )

    def fillna(
        self,
        squeeze_self,
        squeeze_value,
        value=None,
        method=None,
        axis=None,
        inplace=False,
        limit=None,
        downcast=None,
        group_cols=None,
    ):
        if value is None and method is None:
            raise make_exception(
                ValueError,
                PonderError.FILLNA_NO_VALUE_OR_METHOD,
                "Must specify either a fill method or a value",
            )

        if value is not None and method is not None:
            raise make_exception(
                ValueError,
                PonderError.FILLNA_BOTH_VALUE_AND_METHOD,
                "Cannot specify both a fill method and value",
            )

        if isinstance(value, BaseQueryCompiler):
            raise make_exception(
                NotImplementedError,
                PonderError.FILLNA_QUERY_COMPILER,
                "Series and Dataframe values are not supported for fillna() yet",
            )
        if is_scalar(value):
            value_dict = {c: value for c in self.columns}
        elif not isinstance(value, dict):
            raise TypeError(
                '"value" parameter must be a scalar or dict, but '
                + f'you passed a "{type(value).__name__}"'
            )
        else:
            value_dict = {c: v for c, v in value.items() if c in self.columns}

        for c, value in value_dict.items():
            if (
                is_categorical_dtype(self.dtypes[c])
                and value not in self.dtypes[c].categories
            ):
                raise make_exception(
                    TypeError,
                    PonderError.FILLNA_CATEGORY_WITH_VALUE_NOT_IN_CATEGORIES,
                    f"Cannot setitem on a Categorical with a new category {value}, "
                    + "set the categories first",
                )

        columns_to_upcast_to_object = [
            col
            for col, value in value_dict.items()
            if (is_numeric_dtype(self.dtypes[col]) and isinstance(value, str))
            or (is_number(value) and is_string_dtype(self.dtypes[col]))
        ]

        if method is not None:
            if method == "backfill":
                method = "bfill"
            if method == "pad":
                method = "ffill"
            return self.__constructor__(
                self._dataframe.fillna(
                    value, method, limit, group_cols, columns_to_upcast_to_object
                )
            )
        # TODO: should do some preemptive type checking here, but it may depend on the
        # DB and the particular type. pandas lets you fillna() with any type you want,
        # possibly changing the type of the column thereby. snowflake will raise a
        # ProgrammingError for fillna() that changes type from number to string. duckdb
        # is quite flexible with types. All 3 DBMSs seem to be fine with filling a
        # decimal column with an integer value and vice versa.
        return self.__constructor__(
            self._dataframe.fillna(
                value_dict, method, limit, group_cols, columns_to_upcast_to_object
            )
        )

    def dropna(self, **kwargs):
        axis = kwargs.get("axis", 0)
        how = kwargs["how"]
        if how is no_default:
            how = "any"
        thresh = kwargs["thresh"]
        if thresh is no_default:
            thresh = None
        subset = kwargs.get("subset", None)
        new_df = self._dataframe.dropna(axis, how, thresh, subset, self.index.name)
        return self.__constructor__(new_df)

    def sum(self, **kwargs):
        if kwargs.get("min_count", 0) > 1:
            raise make_exception(
                NotImplementedError,
                PonderError.SUM_MIN_COUNT_NOT_SUPPORTED,
                "sum() does not support the `min_count` parameter yet",
            )
        new_self = _cast_to_int_if_needed(self)
        if kwargs.get("axis", 0) == 1:
            start = None
            for i in range(0, len(new_self.columns)):
                if is_numeric_dtype(new_self.dtypes.iloc[i]):
                    start = new_self.getitem_column_array([i], True)
                    break
            for j in range(i + 1, len(new_self.columns)):
                if is_numeric_dtype(new_self.dtypes.iloc[j]):
                    start = start.add(new_self.getitem_column_array([j], True))
            if start is None:
                raise make_exception(
                    ValueError,
                    PonderError.SUM_NO_NUMERIC_TYPES,
                    "No numeric types to sum!",
                )
            # This is really convoluted, but it's the only way to ensure that we skip
            # the join altogether because this will ensure the join gets rewritten into
            # a <col> <op> <col> syntax. The SQL statement is shorter after this as
            # well!
            return new_self.insert(
                len(new_self.columns), __PONDER_REDUCED_COLUMN_NAME__, start
            ).getitem_column_array(__PONDER_REDUCED_COLUMN_NAME__, False)
        else:
            new_dtypes = new_self.dtypes
            return new_self.__constructor__(
                new_self._dataframe.reduce(
                    REDUCE_FUNCTION.SUM, Axis.COL_WISE, new_dtypes
                )
            )

    def prod(self, **kwargs):
        if kwargs.get("min_count", 0) > 1:
            raise make_exception(
                NotImplementedError,
                PonderError.PROD_MIN_COUNT_NOT_SUPPORTED,
                "prod() does not support the `min_count` parameter yet",
            )
        new_self = _cast_to_int_if_needed(self)
        if kwargs.get("axis", 0) == 0:
            raise make_exception(
                NotImplementedError,
                PonderError.PROD_AXIS_0_NOT_SUPPORTED,
                "prod() does not support axis=0 yet",
            )
        start = None
        for i in range(0, len(new_self.columns)):
            if is_numeric_dtype(new_self.dtypes.iloc[i]):
                start = new_self.getitem_column_array([i], True)
                break
        for j in range(i + 1, len(new_self.columns)):
            if is_numeric_dtype(new_self.dtypes.iloc[j]):
                start = start.mul(new_self.getitem_column_array([j], True))
        if start is None:
            raise make_exception(
                ValueError,
                PonderError.PROD_NO_NUMERIC_TYPES,
                "No numeric types to prod!",
            )
        # This is really convoluted, but it's the only way to ensure that we skip
        # the join altogether because this will ensure the join gets rewritten into
        # a <col> <op> <col> syntax. The SQL statement is shorter after this as
        # well!
        return new_self.insert(
            len(new_self.columns), __PONDER_REDUCED_COLUMN_NAME__, start
        ).getitem_column_array([__PONDER_REDUCED_COLUMN_NAME__], False)

    def count(self, **kwargs):
        if kwargs.get("numeric_only", None) is True:
            count_obj = self.getitem_column_array(
                [
                    self.columns[i]
                    for i in range(len(self.dtypes))
                    if is_numeric_dtype(self.dtypes.iloc[i])
                ]
            )
        else:
            count_obj = self
        if kwargs.get("axis", 0) == 1:
            new_dtypes = pandas.Series(
                {c: np.int64 for c in count_obj.columns}, dtype=object
            )
            return count_obj.__constructor__(
                count_obj._dataframe.map(
                    MapFunction(
                        MAP_FUNCTION.COUNT,
                        ["{0}"],
                        np.int64,
                    )
                )
            ).sum(axis=1)
        else:
            new_dtypes = pandas.Series(
                {c: np.int64 for c in count_obj.columns}, dtype=object
            )
            return count_obj.__constructor__(
                count_obj._dataframe.reduce(
                    REDUCE_FUNCTION.COUNT, Axis.COL_WISE, new_dtypes
                )
            )

    def nunique(self, axis=0, dropna=True):  # noqa: PR01, RT01, D200
        if axis == 1:
            new_dtypes = pandas.Series({_unnamed_column_: np.int64}, dtype=object)
        else:
            new_dtypes = pandas.Series(
                {c: np.int64 for c in self.columns}, dtype=object
            )
        return self.__constructor__(
            self._dataframe.reduce(
                REDUCE_FUNCTION.COUNT_UNIQUE_EXCLUDING_NULL
                if dropna
                else REDUCE_FUNCTION.COUNT_UNIQUE_INCLUDING_NULL,
                axis,
                new_dtypes,
            )
        )

    def mean(self, **kwargs):
        if kwargs.get("min_count", 0) > 1:
            raise make_exception(
                NotImplementedError,
                PonderError.MEAN_MIN_COUNT_NOT_SUPPORTED,
                "mean() does not support the `min_count` parameter yet",
            )
        if kwargs.get("axis", 0) == 1:
            colsums = self.sum(**kwargs)
            return colsums.truediv(
                len(
                    [
                        i
                        for i in range(len(self.dtypes))
                        if is_numeric_dtype(self.dtypes.iloc[i])
                    ]
                )
            )
        else:
            new_dtypes = self.dtypes
            return self.__constructor__(
                self.astype("float")._dataframe.reduce(
                    REDUCE_FUNCTION.MEAN, Axis.COL_WISE, new_dtypes
                )
            )

    def median(self, **kwargs):
        new_dtypes = self.dtypes
        return self.__constructor__(
            self._dataframe.reduce(REDUCE_FUNCTION.MEDIAN, Axis.COL_WISE, new_dtypes)
        )

    def std(self, **kwargs):
        new_dtypes = self.dtypes
        return self.__constructor__(
            self._dataframe.reduce(
                REDUCE_FUNCTION.STANDARD_DEVIATION, Axis.COL_WISE, new_dtypes
            )
        )

    def kurtosis(self, **kwargs):
        new_dtypes = pandas.Series({c: np.float_ for c in self.columns}, dtype=object)
        return self.__constructor__(
            self._dataframe.reduce(REDUCE_FUNCTION.KURTOSIS, Axis.COL_WISE, new_dtypes)
        )

    kurt = kurtosis

    def sem(self, **kwargs):
        new_dtypes = pandas.Series({c: np.float_ for c in self.columns}, dtype=object)
        return self.__constructor__(
            self._dataframe.reduce(REDUCE_FUNCTION.SEM, Axis.COL_WISE, new_dtypes)
        )

    def skew(self, **kwargs):
        new_dtypes = pandas.Series({c: np.float_ for c in self.columns}, dtype=object)
        return self.__constructor__(
            self._dataframe.reduce(REDUCE_FUNCTION.SKEW, Axis.COL_WISE, new_dtypes)
        )

    def var(self, **kwargs):
        new_dtypes = pandas.Series({c: np.float_ for c in self.columns}, dtype=object)
        return self.__constructor__(
            self._dataframe.reduce(REDUCE_FUNCTION.VARIANCE, Axis.COL_WISE, new_dtypes)
        )

    def corr(self, **kwargs):
        if kwargs.get("method", "pearson") != "pearson":
            raise make_exception(
                NotImplementedError,
                PonderError.CORR_METHOD_NOT_SUPPORTED,
                "corr() currently only supports method='pearson'",
            )
        if kwargs.get("min_periods", 1) != 1:
            raise make_exception(
                NotImplementedError,
                PonderError.CORR_MIN_PERIODS_NOT_SUPPORTED,
                "corr() currently only supports min_periods=1",
            )

        if kwargs.get("numeric_only", True):
            df = self._dataframe.mask(
                col_labels=[
                    i for i in self.dtypes.index if is_numeric_dtype(self.dtypes[i])
                ]
            )
        else:
            df = self._dataframe
        new_dtypes = df.dtypes
        return self.__constructor__(
            df.reduce(REDUCE_FUNCTION.CORR, Axis.COL_WISE, new_dtypes)
        )

    def cov(self, **kwargs):
        if kwargs.get("ddof", 1) not in [None, 1]:
            raise make_exception(
                NotImplementedError,
                PonderError.COV_DDOF_NOT_SUPPORTED,
                "cov() currently only supports ddof=1 or ddof=None",
            )
        if kwargs.get("numeric_only", True):
            df = self._dataframe.mask(
                col_labels=[
                    i for i in self.dtypes.index if is_numeric_dtype(self.dtypes[i])
                ]
            )
        else:
            df = self._dataframe
        new_dtypes = df.dtypes
        return self.__constructor__(
            df.reduce(REDUCE_FUNCTION.COV, Axis.COL_WISE, new_dtypes)
        )

    def min(self, **kwargs):
        if kwargs.get("axis", 0) == 1:
            numeric_only = kwargs.get("numeric_only", True)
            if numeric_only or numeric_only is None:
                new_dtypes = pandas.Series({_unnamed_column_: np.float64}, dtype=object)
                query_obj = self._dataframe.mask(
                    col_labels=[
                        i for i in self.dtypes.index if is_numeric_dtype(self.dtypes[i])
                    ]
                )
            else:
                new_dtypes = pandas.Series({_unnamed_column_: object}, dtype=object)
                query_obj = self._dataframe
            return self.__constructor__(
                query_obj.reduce(REDUCE_FUNCTION.MIN, Axis.ROW_WISE, new_dtypes)
            )
        else:
            new_dtypes = self.dtypes
            return self.__constructor__(
                self._dataframe.reduce(REDUCE_FUNCTION.MIN, Axis.COL_WISE, new_dtypes)
            )

    def max(self, **kwargs):
        if kwargs.get("axis", 0) == 1:
            numeric_only = kwargs.get("numeric_only", True)
            if numeric_only or numeric_only is None:
                new_dtypes = pandas.Series({_unnamed_column_: np.float64}, dtype=object)
                query_obj = self._dataframe.mask(
                    col_labels=[
                        i for i in self.dtypes.index if is_numeric_dtype(self.dtypes[i])
                    ]
                )
            else:
                new_dtypes = pandas.Series({_unnamed_column_: object}, dtype=object)
                query_obj = self._dataframe
            return self.__constructor__(
                query_obj.reduce(REDUCE_FUNCTION.MAX, Axis.ROW_WISE, new_dtypes)
            )
        else:
            new_dtypes = self.dtypes
            return self.__constructor__(
                self._dataframe.reduce(REDUCE_FUNCTION.MAX, Axis.COL_WISE, new_dtypes)
            )

    def any(self, **kwargs):
        if kwargs.get("axis", 0) == 0:
            new_dtypes = pandas.Series({c: bool for c in self.columns}, dtype=object)
            return self.__constructor__(
                self._dataframe.reduce(
                    REDUCE_FUNCTION.LOGICAL_OR, Axis.COL_WISE, new_dtypes
                )
            )
        else:
            start = self.getitem_column_array([0], True)
            for i in range(1, len(self.columns)):
                start = start.__or__(self.getitem_column_array([i], True))
            # This is really convoluted, but it's the only way to ensure that we skip
            # the join altogether because this will ensure the join gets rewritten into
            # a <col> <op> <col> syntax. The SQL statement is shorter after this as
            # well!
            return self.insert(
                len(self.columns), __PONDER_REDUCED_COLUMN_NAME__, start
            ).getitem_column_array([__PONDER_REDUCED_COLUMN_NAME__], False)

    def all(self, **kwargs):
        if kwargs.get("axis", 0) == 0:
            new_dtypes = pandas.Series({c: bool for c in self.columns}, dtype=object)
            return self.__constructor__(
                self._dataframe.reduce(
                    REDUCE_FUNCTION.LOGICAL_AND, Axis.COL_WISE, new_dtypes
                )
            )
        else:
            start = self.getitem_column_array([0], True)
            for i in range(1, len(self.columns)):
                start = start.__and__(self.getitem_column_array([i], True))
            # This is really convoluted, but it's the only way to ensure that we skip
            # the join altogether because this will ensure the join gets rewritten into
            # a <col> <op> <col> syntax. The SQL statement is shorter after this as
            # well!
            return self.insert(
                len(self.columns), __PONDER_REDUCED_COLUMN_NAME__, start
            ).getitem_column_array([__PONDER_REDUCED_COLUMN_NAME__], False)

    def quantile_for_single_value(self, **kwargs):
        if kwargs.get("numeric_only", True):
            df = self._dataframe.mask(
                col_labels=[
                    i for i in self.dtypes.index if is_numeric_dtype(self.dtypes[i])
                ]
            )
        else:
            df = self._dataframe
        new_dtypes = df.dtypes
        return self.__constructor__(
            df.reduce(
                REDUCE_FUNCTION.PERCENTILE,
                Axis.COL_WISE,
                new_dtypes,
                percentile=kwargs.get("q"),
            )
        )

    def quantile_for_list_of_values(self, **kwargs):
        if kwargs.get("numeric_only", True):
            df = self._dataframe.mask(
                col_labels=[
                    i for i in self.dtypes.index if is_numeric_dtype(self.dtypes[i])
                ]
            )
        else:
            df = self._dataframe
        new_dtypes = df.dtypes

        quantiles = [
            self.__constructor__(
                df.reduce(
                    REDUCE_FUNCTION.PERCENTILE, Axis.COL_WISE, new_dtypes, percentile=q
                )
            )
            for q in kwargs.get("q")
        ]
        if len(quantiles) == 1:
            quants = quantiles[0]
        else:
            quants = quantiles[0].concat(Axis.COL_WISE, quantiles[1:])
        return self.__constructor__(
            quants._dataframe.rename(
                new_row_labels=list(kwargs.get("q")),
                new_row_labels_names=[__UNNAMED_INDEX_COLUMN__],
            )
        )

    def describe(
        self,
        percentiles: np.ndarray[Any, np.dtype[np.float64]],
    ):
        stats_by_name = {}
        stats_by_name["count"] = self.count()

        ordered_stat_names_per_column_type = []

        numeric_self = self.getitem_column_array(
            [n for n, t in self.dtypes.items() if is_numeric_dtype(t)]
        )
        if len(numeric_self.columns) > 0:
            float64_self = numeric_self.astype("float64")
            stats_by_name["mean"] = float64_self.mean()
            stats_by_name["std"] = float64_self.std()
            stats_by_name["min"] = float64_self.min()
            percentile_names = format_percentiles(percentiles)
            for q, name in zip(percentiles, percentile_names):
                stats_by_name[name] = float64_self.quantile_for_single_value(q=q)
            stats_by_name["max"] = float64_self.max()
            ordered_stat_names_per_column_type.append(
                ["count", "mean", "std", "min", *percentile_names, "max"]
            )

        non_numeric_self = self.getitem_column_array(
            [
                n
                for n, t in self.dtypes.items()
                if not is_numeric_dtype(t) and not is_datetime64_any_dtype(t)
            ]
        )
        if len(non_numeric_self.columns) > 0:
            # Casting all the non-numeric stats is a hack to allow mixed types in the
            # resulting dataframe. e.g if we need to describe a string column, the
            # description for that column contains both the integer count and the string
            # `top`, the most frequent value. The only way to represent such a column
            # in snowflake is with a variant type, so we cast everything to a variant
            # type
            # TODO(FIX[POND-823]): concat should handle casting to variant before for
            # the union all and then downcasting back to appropriate types.
            stats_by_name["unique"] = non_numeric_self.nunique()
            # TODO(REFACTOR): this is a hack to get the mode to work. Alternatively, we
            # could use value_counts() on each column and get `top` and `freq` from the
            # first row of that, then concat each column's `top` and `freq` column-wise.
            # this way seemed like it might produce less SQL and @mvashishtha hit some
            # bugs with the value_counts() approach.
            # N.B. mode in pandas returns all the most common values if there are ties,
            # so we haven't implemented it yet. Can use SnowflakeDataFrame.redue with
            # MODE to get an arbitrary mode. (pandas documentation for mode says the
            # mode can be any of the most common values)
            mode = self.__constructor__(
                non_numeric_self._dataframe.reduce(
                    REDUCE_FUNCTION.MODE, Axis.COL_WISE, non_numeric_self.dtypes
                )
            )
            stats_by_name["top"] = mode
            # this eq() is like doing df == df.mode(). have to transpose to get query
            # compiler representation of series.
            equal_to_mode = non_numeric_self.eq(mode.transpose())
            # count the rows where df == df.mode().
            stats_by_name["freq"] = self.__constructor__(
                equal_to_mode._dataframe.reduce(
                    REDUCE_FUNCTION.BOOL_COUNT,
                    Axis.COL_WISE,
                    pandas.Series(
                        {n: int for n in equal_to_mode.columns}, dtype=object
                    ),
                )
            )

            ordered_stat_names_per_column_type.append(
                ["count", "unique", "top", "freq"]
            )

        final_stat_names = []
        # this is how pandas chooses the order of rows. See reorder_columns in
        # pandas.core.describe:
        # https://github.com/pandas-dev/pandas/blob/ca60aab7340d9989d9428e11a51467658190bb6b/pandas/core/describe.py#L213
        for stat_names in sorted(ordered_stat_names_per_column_type, key=len):
            for name in stat_names:
                if name not in final_stat_names:
                    final_stat_names.append(name)
        aggregated: DBMSQueryCompiler = stats_by_name[final_stat_names[0]].concat(
            axis=Axis.COL_WISE,
            other=[stats_by_name[n] for n in final_stat_names[1:]],
        )
        return self.__constructor__(
            aggregated._dataframe.rename(
                new_row_labels=final_stat_names,
                new_row_labels_names=[__UNNAMED_INDEX_COLUMN__],
            )
        )

    def set_index_from_columns(self, keys, drop=True, append=False):
        # TODO: support drop and append
        assert drop and not append, "Not yet supported"
        if len(keys) > 0 and isinstance(keys[0], DBMSIndex):
            return self.__constructor__(self._dataframe.index_to_labels(keys))
        return self.__constructor__(self._dataframe.to_labels(keys))

    def reset_index(
        self,
        level=None,
        drop=False,
        col_level=0,
        col_fill="",
        allow_duplicates=no_default,
        names=None,
    ):
        if (
            isinstance(self.index, DBMSPositionMapping)
            and drop
            and self.index.is_true_labels()
        ):
            return self.copy()
        if level is not None:
            raise make_exception(
                NotImplementedError,
                PonderError.RESET_INDEX_LEVEL_NOT_SUPPORTED,
                "Resetting a specific level of an index is not yet supported",
            )
        if allow_duplicates is not no_default:
            raise make_exception(
                NotImplementedError,
                PonderError.RESET_INDEX_ALLOW_DUPLICATES_NOT_SUPPORTED,
                "reset_index() does not support `allow_duplicates`",
            )
        return self.__constructor__(self._dataframe.from_labels(drop=drop))

    def concat(self, axis, other, **kwargs):
        # TODO(REFACTOR): it's annoying that the base query compiler concat() takes
        # arbitrary kwargs instead of an explicit list of args. Clean this up.
        # TODO(FIX[POND-823]): concat should handle casting to variant before for the
        # union all and then downcasting back to appropriate types.
        if not isinstance(other, list):
            other = [other]
        assert all(
            isinstance(o, type(self)) for o in other
        ), "Different Manager objects are being used. This is not allowed"
        join = kwargs.get("join", "outer")
        sort = kwargs.get("sort", False)
        other_frames = [o._dataframe for o in other]
        new_frame = self._dataframe.concat(axis, other_frames, join, sort)
        result = self.__constructor__(new_frame)
        if kwargs.get("ignore_index", False):
            if axis == 0:
                return result.reset_index(drop=True)
            else:
                result.columns = pandas.RangeIndex(len(result.columns))
        return result

    _equal_null = _binary_op("equal_null")
    eq = _binary_op("==")
    lt = _binary_op("<")
    le = _binary_op("<=")
    gt = _binary_op(">")
    ge = _binary_op(">=")
    ne = _binary_op("!=")
    __and__ = _binary_op("&")
    __rand__ = _binary_op("&")
    __or__ = _binary_op("|")
    __ror__ = _binary_op("|")
    __xor__ = _binary_op("^")
    __rxor__ = _binary_op("^")

    add = _binary_op("+")
    radd = _binary_op("+", True)
    truediv = _binary_op("/")
    rtruediv = _binary_op("/", True)
    floordiv = _binary_op("//")
    rfloordiv = _binary_op("//", True)
    mod = _binary_op("%")
    rmod = _binary_op("%", True)
    sub = _binary_op("-")
    rsub = _binary_op("-", True)
    mul = _binary_op("*")
    rmul = _binary_op("*")
    pow = _binary_op("**")
    rpow = _binary_op("**", True)

    def sort_rows_by_column_values(
        self, columns, ascending=True, handle_duplicates=None, **kwargs
    ):
        # don't want to mutate user's columns object.
        columns = copy.deepcopy(columns)
        if not is_list_like(columns):
            columns = [columns]
        return self.__constructor__(
            self._dataframe.sort_by(
                Axis.ROW_WISE,
                columns,
                ascending=ascending,
                handle_duplicates=handle_duplicates,
            )
        )

    def nlargest(self, n, columns, keep="first"):
        if keep != "first":
            raise make_exception(
                NotImplementedError,
                PonderError.NLARGEST_KEEP_NOT_SUPPORTED,
                "nlargest() keep != 'first' not supported yet",
            )
        if not isinstance(n, int):
            # NOTE: in pandas the 'int' type here comes from SelectNSeries.compute
            # where we have the expression n <= 0
            raise make_exception(
                TypeError,
                PonderError.NLARGEST_NON_INT,
                f"'<=' not supported between instances of '{type(n)}' and 'int'",
            )
        if n < 0:
            raise make_exception(
                IndexError, PonderError.NLARGEST_NEGATIVE_N, "index -1 is out of bounds"
            )

        return self.sort_rows_by_column_values(
            columns=columns, ascending=False, handle_duplicates=keep
        ).getitem_row_array(range(n))

    def nsmallest(self, n, columns, keep="first"):
        if keep != "first":
            raise make_exception(
                NotImplementedError,
                PonderError.NSMALLEST_KEEP_NOT_SUPPORTED,
                "nsmallest() keep != 'first' not supported yet",
            )
        if not isinstance(n, int):
            # NOTE: in pandas the 'int' type here comes from SelectNSeries.compute
            # where we have the expression n <= 0
            raise make_exception(
                TypeError,
                PonderError.NSMALLEST_NON_INT,
                f"'<=' not supported between instances of '{type(n)}' and 'int'",
            )
        if n < 0:
            raise make_exception(
                IndexError,
                PonderError.NSMALLEST_NEGATIVE_N,
                "index -1 is out of bounds",
            )
        return self.sort_rows_by_column_values(
            columns=columns, ascending=True, handle_duplicates=keep
        ).getitem_row_array(range(n))

    def sort_index(self, **kwargs):
        ascending = kwargs.get("ascending", True)
        level = kwargs.get("level", None)
        if level is not None:
            if is_list_like(level):
                col_names = [self.index.names[lev] for lev in level]
            else:
                col_names = [self.index.names[level]]
        else:
            col_names = (
                [self.index.name]
                if len(self.index.names) == 1
                else list(self.index.names)
            )
        return self.__constructor__(
            self._dataframe.sort_by(Axis.ROW_WISE, col_names, ascending=ascending)
        )

    def str_islower(self):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_islower,
                    ["{0}"],
                    np.bool_,
                )
            )
        )

    def str_isnumeric(self):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_isnumeric,
                    ["{0}"],
                    np.bool_,
                )
            )
        )

    def str_isspace(self):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_isspace,
                    ["{0}"],
                    np.bool_,
                )
            )
        )

    def str_istitle(self):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_istitle,
                    ["{0}"],
                    np.bool_,
                )
            )
        )

    def str_isupper(self):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_isupper,
                    ["{0}"],
                    np.bool_,
                )
            )
        )

    def str_len(self):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_len,
                    ["{0}"],
                    np.int64,
                )
            )
        )

    def str_lower(self):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_lower,
                    ["{0}"],
                )
            )
        )

    def str_title(self):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_title,
                    ["{0}"],
                )
            )
        )

    def str_upper(self):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_upper,
                    ["{0}"],
                )
            )
        )

    def str_capitalize(self):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_capitalize,
                    ["{0}"],
                )
            )
        )

    def str_isalnum(self):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_isalnum,
                    ["{0}"],
                    np.bool_,
                )
            )
        )

    def str_isalpha(self):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_isalpha,
                    ["{0}"],
                    np.bool_,
                )
            )
        )

    def str_isdecimal(self):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_isdecimal,
                    ["{0}"],
                    np.bool_,
                )
            )
        )

    def str_isdigit(self):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_isdigit,
                    ["{0}"],
                    np.bool_,
                )
            )
        )

    def str_cat(self, others=None, sep=None, na_rep=None, join="left"):
        if others is not None:
            raise make_exception(
                NotImplementedError,
                PonderError.STR_CAT_OTHERS_NOT_SUPPORTED,
                "str.cat() does not support the `others` param yet",
            )
        return self.__constructor__(
            self._dataframe.reduce(
                REDUCE_FUNCTION.STR_CAT,
                Axis.COL_WISE,
                self.dtypes,
                None,
                [sep, na_rep],
            )
        )

    def str_center(self, width, fillchar=" "):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_center,
                    ["{0}", width, fillchar],
                )
            )
        )

    def str_contains(self, pat, case=True, flags=0, na=np.NaN, regex=True):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_contains,
                    ["{0}", pat, case, flags, na, regex],
                    np.bool_,
                )
            )
        )

    def str_count(self, pat, flags=0, **kwargs):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_count,
                    ["{0}", pat, flags],
                    np.int64,
                )
            )
        )

    def str_encode(self, encoding, errors, **kwargs):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_encode,
                    ["{0}", encoding, errors],
                    object,
                )
            )
        )

    def str_decode(self, encoding, errors, **kwargs):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_decode,
                    ["{0}", encoding, errors],
                    object,
                )
            )
        )

    def str_endswith(self, pat, na=np.NaN):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_endswith,
                    ["{0}", pat, na],
                    np.bool_,
                )
            )
        )

    def str_extract(self, pat, flags=0, expand=True):
        return self.__constructor__(self._dataframe.str_extract(pat, flags, expand))

    def str_find(self, sub, start=0, end=None):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_find,
                    ["{0}", sub, start, end],
                    np.int64,
                )
            )
        )

    def str_findall(self, pat, flags=0, **kwargs):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_findall,
                    ["{0}", pat, flags],
                )
            )
        )

    def str_fullmatch(self, pat, case=True, flags=0, na=np.NaN):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_fullmatch,
                    ["{0}", pat, case, flags, na],
                    np.bool_,
                )
            )
        )

    def str_get(self, i):
        return self.__constructor__(
            self._dataframe.map(MapFunction(MAP_FUNCTION.str_get, ["{0}", i]))
        )

    str_index = str_find

    def str_join(self, sep):
        return self.__constructor__(
            self._dataframe.map(MapFunction(MAP_FUNCTION.str_join, ["{0}", sep]))
        )

    def str_lstrip(self, to_strip=None):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_lstrip,
                    ["{0}", to_strip],
                )
            )
        )

    def str_ljust(self, width, fillchar=" "):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_ljust,
                    ["{0}", width, fillchar],
                )
            )
        )

    def str_match(self, pat, case=True, flags=0, na=np.NaN):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_match,
                    ["{0}", pat, case, flags, na],
                    np.bool_,
                )
            )
        )

    def str_pad(self, width, side="left", fillchar=" "):
        if side == "left":
            return self.str_rjust(width, fillchar)
        elif side == "right":
            return self.str_ljust(width, fillchar)
        else:  # side == "both"
            return self.str_center(width, fillchar)

    def str_partition(self, sep=" ", expand=True):
        return self.__constructor__(self._dataframe.str_partition(sep, expand))

    def str_repeat(self, repeats):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_repeat,
                    ["{0}", repeats],
                )
            )
        )

    def str_removeprefix(self, prefix):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_removeprefix,
                    ["{0}", prefix],
                )
            )
        )

    def str_removesuffix(self, suffix):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_removesuffix,
                    ["{0}", suffix],
                )
            )
        )

    def str_replace(self, pat, repl, n=-1, case=None, flags=0, regex=True):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_replace,
                    ["{0}", pat, repl, n, case, flags, regex],
                )
            )
        )

    def str_rfind(self, sub, start=0, end=None):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_rfind,
                    ["{0}", sub, start, end],
                    np.int64,
                )
            )
        )

    str_rindex = str_rfind

    def str_rjust(self, width, fillchar=" "):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_rjust,
                    ["{0}", width, fillchar],
                )
            )
        )

    def str_rpartition(self, sep=" ", expand=True):
        return self.__constructor__(self._dataframe.str_rpartition(sep, expand))

    def str_rsplit(self, pat=None, *, n=-1, expand=False):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_rsplit,
                    ["{0}", pat, n, expand],
                )
            )
        )

    def str_rstrip(self, to_strip=None):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_rstrip,
                    ["{0}", to_strip],
                )
            )
        )

    def str_slice(self, start=None, stop=None, step=None):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_slice,
                    ["{0}", start, stop, step],
                )
            )
        )

    def str_slice_replace(self, start=None, stop=None, repl=None):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_slice_replace,
                    ["{0}", start, stop, repl],
                )
            )
        )

    def str_split(self, pat=None, *, n=-1, expand=False, regex=None):
        if regex is not None:
            # We want to error if regex is True OR False, so we need to explicitly
            # check that its not None, rather than just checking its truthyness.
            raise make_exception(
                NotImplementedError,
                PonderError.STRTYPE_REGEX_NOT_IMPLEMENTED,
                "`.str.split` with `regex` not implemented yet.",
            )
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_split,
                    ["{0}", pat, n, expand],
                )
            )
        )

    def str_startswith(self, pat, na=np.NaN):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_startswith,
                    ["{0}", pat, na],
                    np.bool_,
                )
            )
        )

    def str_strip(self, to_strip=None):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_strip,
                    ["{0}", to_strip],
                )
            )
        )

    def str_swapcase(self):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_swapcase,
                    ["{0}"],
                )
            )
        )

    def str_translate(self, table):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_translate,
                    ["{0}", table],
                )
            )
        )

    def str_wrap(self, width, **kwargs):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.str_wrap,
                    ["{0}", width],
                )
            )
        )

    def str_zfill(self, width):
        return self.str_rjust(width, "0")

    def str___getitem__(self, key):
        if isinstance(key, slice):
            return self.str_slice(start=key.start, stop=key.stop, step=key.step)
        return self.str_get(key)

    def dt_nanosecond(self):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.dt_nanosecond,
                    ["{0}"],
                    np.int32,
                )
            )
        )

    def dt_microsecond(self):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.dt_microsecond,
                    ["{0}"],
                    np.int32,
                )
            )
        )

    def dt_second(self):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.dt_second,
                    ["{0}"],
                    np.int32,
                )
            )
        )

    def dt_minute(self):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.dt_minute,
                    ["{0}"],
                    np.int32,
                )
            )
        )

    def dt_hour(self):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.dt_hour,
                    ["{0}"],
                    np.int32,
                )
            )
        )

    def dt_day(self):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.dt_day,
                    ["{0}"],
                    np.int32,
                )
            )
        )

    def dt_dayofweek(self):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.dt_dayofweek,
                    ["{0}"],
                    np.int32,
                )
            )
        )

    dt_day_of_week = dt_dayofweek
    dt_weekday = dt_dayofweek

    def dt_day_name(self):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.dt_day_name,
                    ["{0}"],
                )
            )
        )

    def dt_dayofyear(self):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.dt_dayofyear,
                    ["{0}"],
                    np.int32,
                )
            )
        )

    dt_day_of_year = dt_dayofyear

    def dt_month(self):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.dt_month,
                    ["{0}"],
                    np.int32,
                )
            )
        )

    def dt_month_name(self):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.dt_month_name,
                    ["{0}"],
                )
            )
        )

    def dt_quarter(self):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.dt_quarter,
                    ["{0}"],
                    np.int32,
                )
            )
        )

    def dt_year(self):
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    MAP_FUNCTION.dt_year,
                    ["{0}"],
                    np.int32,
                )
            )
        )

    def _tz_convert_or_localize_columns(
        self, convert_or_localize: _TzConvertOrLocalize, tz, columns: list[str]
    ) -> "DBMSQueryCompiler":
        """Convert the timezone of the columns for tz_convert or tz_localize.

        Parameters
        ----------
        convert_or_localize : _TzConvertOrLocalize
            Whether to do tz_convert or tz_localize.
        tz : str or pytz.timezone or None
            The timezone to convert to.
        columns : list[str]
            The columns to convert.

        Returns
        -------
        DBMSQueryCompiler
            A new query compiler with the converted columns.
        """
        if convert_or_localize is _TzConvertOrLocalize.CONVERT:
            map_function = MAP_FUNCTION.dt_tz_convert
        elif convert_or_localize is _TzConvertOrLocalize.LOCALIZE:
            map_function = MAP_FUNCTION.dt_tz_localize
        else:
            raise make_exception(
                RuntimeError,
                PonderError.TZ_CONVERT_LOCALIZE_INVALID_OPTION,
                "internal error: invalid convert_or_localize",
            )
        if isinstance(tz, str):
            optional_string_tz = tz
            return_type = pandas.DatetimeTZDtype(tz=tz)
        elif isinstance(tz, pytz.tzinfo.BaseTzInfo):
            optional_string_tz = str(tz)
            return_type = pandas.DatetimeTZDtype(tz=tz)
        elif tz is None:
            optional_string_tz = None
            return_type = pandas_dtype("datetime64[ns]")
        else:
            raise make_exception(
                NotImplementedError,
                PonderError.TZ_CONVERT_LOCALIZE_TZ_TYPE_NOT_SUPPORTED,
                "tz_convert() can only take string and pytz timezones",
            )
        return self.__constructor__(
            self._dataframe.map(
                MapFunction(
                    id=map_function,
                    params_list=["{0}", optional_string_tz],
                    return_type=return_type,
                ),
                labels_to_apply_over=columns,
            )
        )

    def _tz_convert_columns(self, tz, columns: list[str]) -> "DBMSQueryCompiler":
        """Convert the timezone of the columns.

        Parameters
        ----------
        tz : str or pytz.timezone or None
            The timezone to convert to.
        columns : list[str]
            The columns to convert.

        Returns
        -------
        DBMSQueryCompiler
            A new query compiler with the converted columns.
        """
        return self._tz_convert_or_localize_columns(
            _TzConvertOrLocalize.CONVERT, tz, columns
        )

    def _tz_localize_columns(self, tz, columns: list[str]) -> "DBMSQueryCompiler":
        """Localize the timezone of the columns.

        Parameters
        ----------
        tz : str or pytz.timezone or None
            The timezone to localize to.
        columns : list[str]
            The columns to localize.

        Returns
        -------
        DBMSQueryCompiler
            A new query compiler with the localized columns.
        """
        return self._tz_convert_or_localize_columns(
            _TzConvertOrLocalize.LOCALIZE, tz, columns
        )

    def tz_convert(self, tz, axis, level, copy):
        if axis not in (0, "index"):
            raise make_exception(
                NotImplementedError,
                PonderError.TZ_CONVERT_AXIS_1_NOT_SUPPORTED,
                "tz_convert() with axis=1 not supported yet",
            )
        if level is not None:
            raise make_exception(
                NotImplementedError,
                PonderError.TZ_CONVERT_LEVEL_NOT_SUPPORTED,
                "tz_convert() with level != None not supported yet",
            )
        if copy is not True:
            raise make_exception(
                ValueError,
                PonderError.TZ_CONVERT_COPY_MUST_BE_TRUE,
                "tz_convert always copies the underlying data",
            )
        if not isinstance(self.index, DBMSDateTimeIndex):
            raise make_exception(
                TypeError,
                PonderError.TZ_CONVERT_INDEX_MUST_BE_DATETIME_OR_PERIOD_INDEX,
                "Index is not a valid DatetimeIndex or PeriodIndex",
            )
        if not is_datetime64tz_dtype(self.index.dtype):
            raise make_exception(
                TypeError,
                PonderError.TZ_CONVERT_INDEX_MUST_BE_TZ_AWARE,
                "Cannot convert tz-naive timestamps, use tz_localize to localize",
            )
        return self._tz_convert_columns(tz, self.index.column_names[0])

    def dt_tz_convert(self, tz):
        return self._tz_convert_columns(tz, list(self.columns))

    def dt_tz_localize(self, tz, ambiguous="raise", nonexistent="raise"):
        if ambiguous != "raise" or nonexistent != "raise":
            raise make_exception(
                NotImplementedError,
                PonderError.DT_TZ_LOCALIZE_AMBIGUOUS_NONEXISTENT_NOT_SUPPORTED,
                "dt_tz_localize() currently only supports "
                + "ambiguous='raise' and nonexistent='raise'",
            )
        return self._tz_localize_columns(tz, list(self.columns))

    def tz_localize(self, tz, axis, level, copy, ambiguous, nonexistent):
        if axis not in (0, "index"):
            raise make_exception(
                NotImplementedError,
                PonderError.TZ_LOCALIZE_AXIS_1_NOT_SUPPORTED,
                "tz_localize() with axis=1 not supported yet",
            )
        if level is not None:
            raise make_exception(
                NotImplementedError,
                PonderError.TZ_LOCALIZE_LEVEL_NOT_SUPPORTED,
                "tz_localize() with level != None not supported yet",
            )
        if ambiguous != "raise" or nonexistent != "raise":
            raise make_exception(
                NotImplementedError,
                PonderError.TZ_LOCALIZE_AMBIGUOUS_NONEXISTENT_NOT_SUPPORTED,
                "tz_localize() only supports ambiguous='raise' and nonexistent='raise'",
            )
        if copy is not True:
            raise make_exception(
                ValueError,
                PonderError.TZ_LOCALIZE_COPY_MUST_BE_TRUE,
                "tz_localize always copies the underlying data",
            )
        if not isinstance(self.index, DBMSDateTimeIndex):
            raise make_exception(
                TypeError,
                PonderError.TZ_LOCALIZE_INDEX_MUST_BE_DATETIME_OR_PERIOD_INDEX,
                "Index is not a valid DatetimeIndex or PeriodIndex",
            )
        if tz is not None and is_datetime64tz_dtype(self.index.dtype):
            raise make_exception(
                TypeError,
                PonderError.TZ_LOCALIZE_INDEX_CANNOT_BE_TZ_AWARE,
                "Already tz-aware, use tz_convert to convert.",
            )
        return self._tz_localize_columns(tz, self.index.column_names[0])

    def between_time(
        self,
        start_time: datetime.time,
        end_time: datetime.time,
        inclusive: str,
        axis: int,
    ):
        if axis == 1:
            raise make_exception(
                NotImplementedError,
                PonderError.BETWEEN_TIME_AXIS_1_NOT_SUPPORTED,
                "between_time() with axis=1 not supported yet",
            )
        # Modin should do `inclusive` argument validation and conversion at API layer,
        # and @mvashishtha made that change and @vnlitvinov upstreamed it but anatoly
        # reverted it in
        # https://github.com/modin-project/modin/commit/1d8a179dc0d775b8601f0586da4b64f9c4f86c0b
        # because the query compiler between_time interface just has **kwargs.
        include_start, include_end = validate_inclusive(inclusive)
        # snowflake allows a timestamp_tz column to have multiple timezones across its
        # entries. While pandas allows columns like that, if such a column is converted
        # to index, you get a regular index instead of DateTimeIndex. This is because
        # DateTimeIndex can only have one timezone.

        # We materialize the first element of the index because:
        # - If the index is not a DatetimeIndex, we need to throw TypeError
        # - If the index doesn't have a timezone, but the start_time or end_time does,
        #   we need to throw ValueError. (this is a pandas constraint, but also, in the
        #   case where start_time or end_time is timezone aware, we need to convert it
        #   and the index to UTC before comparing, and converting index to UTC doesn't
        #   make sense for a non-timezone-aware index, i.e. TIMESTAMP_NTZ or
        #   TIMESTAMP_LTZ in snowflake)
        # self.index isn't a real pandas index, so the simplest way to check the index
        # type is to materialize the first row and column of this dataframe and check
        # the type of the resulting index. We do something similar in get_dummies to
        # get column names. Ways we may be able to avoid materializing data:
        # - Every time we set_index, if the column we're setting as index is a datetime
        #   object, save a variable like self._is_datetime_index. (similarly could
        #   track timezone awareness). This is hard to maintain-- we set index in
        #   multiple places, e.g. groupby, and we also have to remember to set this
        #   variable to False when we reset_index.
        # - Within the SQL that compares the column, uses a python UDF that throws
        #   an error if the column has the wrong type, then catch the error when we
        #   execute the SQL. This is kind of promising but the UDFs may not be
        #   performant enough, and it will take a bit of effort to try this out.
        pandas_index_first_row = (
            self.take_2d_positional(index=[0], columns=[0]).to_pandas().index
        )
        if not isinstance(pandas_index_first_row, pandas.DatetimeIndex):
            raise make_exception(
                TypeError,
                PonderError.BETWEEN_TIME_INDEX_MUST_BE_DATETIME_INDEX,
                "Index must be DatetimeIndex",
            )
        index_has_timezone = pandas_index_first_row.tzinfo is not None
        compare_start_to_utc_time = start_time.tzinfo is not None
        compare_end_to_utc_time = start_time.tzinfo is not None
        if not index_has_timezone and (
            compare_start_to_utc_time or compare_end_to_utc_time
        ):
            raise make_exception(
                ValueError,
                PonderError.BETWEEN_TIME_INDEX_MUST_BE_TZ_AWARE,
                "Index must be timezone aware.",
            )
        return self.__constructor__(
            self._dataframe.filter_rows(
                condition=RowWiseFilterPredicates.TimesInRange(
                    self.index.name,
                    _time_to_micros(
                        _timetz_to_tz(start_time, pytz.UTC)
                        if compare_start_to_utc_time
                        else start_time
                    ),
                    _time_to_micros(
                        _timetz_to_tz(end_time, pytz.UTC)
                        if compare_end_to_utc_time
                        else end_time
                    ),
                    include_start,
                    include_end,
                    compare_start_to_utc_time,
                    compare_end_to_utc_time,
                ),
            )
        )

    # Abstract methods we don't need yet
    @classmethod
    def from_arrow(cls, at, data_cls):
        raise make_exception(
            NotImplementedError,
            PonderError.FROM_ARROW_NOT_SUPPORTED,
            "Creating modin.pandas objects from Arrow objects is not supported yet",
        )

    def finalize(self):
        return

    def free(self):
        return

    def to_dataframe(self, nan_as_null: bool = False, allow_copy: bool = True):
        return self.to_pandas().__dataframe__(nan_as_null, allow_copy)

    @classmethod
    def from_dataframe(cls, df, data_cls):
        raise make_exception(
            NotImplementedError,
            PonderError.FROM_DATAFRAME_NOT_SUPPORTED,
            "Creating modin.pandas objects from the dataframe "
            + "exchange protocol is not supported yet",
        )

    def merge(
        self,
        right_query_compiler,
        how="inner",
        on=None,
        left_on=None,
        right_on=None,
        left_index=False,
        right_index=False,
        sort=False,
        suffixes=("_X", "_Y"),
        copy=False,
        indicator=False,
        validate=None,
    ):
        if on is not None:
            # TODO: POND-888 - Properly fix on= to make sure this is a
            # list type (requires tests)
            left_on = on if is_list_like(on) else on
            right_on = left_on
        # TODO: POND-890 - need to handle multi-index on merge
        if left_index:
            left_on = [self._dataframe.index.name]
        if right_index:
            right_on = [right_query_compiler._dataframe.index.name]

        return self.__constructor__(
            self._dataframe.join(
                right_query_compiler._dataframe,
                how,
                left_on,
                right_on,
                suffixes,
                indicator,
            )
        )

    def df_update(
        self,
        right_query_compiler,
        join="left",
        overwrite=True,
        filter_func=None,
        errors="raise",
    ):
        # Due to lazy evaluation we override the errors
        # parameter to be raise, which conflicts with
        # the pandas api. To account for this, we check
        # for one of the api errors here.
        if errors not in ["raise", "ignore"]:
            raise make_exception(
                ValueError,
                PonderError.DF_UPDATE_INVALID_ERRORS_PARAMETER,
                "errors parameter must be 'raise' or 'ignore'",
            )
        return self.__constructor__(
            self._dataframe.update(
                other=right_query_compiler._dataframe,
                join=join,
                overwrite=overwrite,
                filter_func=filter_func,
                errors="raise",
            )
        )

    def merge_asof(
        self,
        right_query_compiler,
        left_on=None,
        right_on=None,
        left_index=False,
        right_index=False,
        left_by=None,
        right_by=None,
        suffixes=("_x", "_y"),
        tolerance=None,
        allow_exact_matches=True,
        direction="backward",
    ):
        return self.__constructor__(
            self._dataframe.merge_asof(
                right_query_compiler._dataframe,
                left_on,
                right_on,
                left_index,
                right_index,
                left_by,
                right_by,
                suffixes,
                tolerance,
                allow_exact_matches,
                direction,
            )
        )

    def _get_grouper_metadata(self, grouper):
        args = {"graft_predicates": True}
        if grouper.freq:
            index_start = (
                self.getitem_column_array(grouper.key)
                .getitem_row_labels_array([0])
                .to_pandas()
                .squeeze()
            )
            index_length = len(self.index)
            index_end = (
                self.getitem_column_array(grouper.key)
                .getitem_row_labels_array([index_length - 1])
                .to_pandas()
                .squeeze()
            )
            sum_index_interval = (index_end - index_start).total_seconds()
            # (2) Detect whether operation is upsampling or downsampling
            offset = to_offset(grouper.freq)
            offset_sec = _pandas_offset_object_to_seconds(offset)
            index_interval = sum_index_interval / (index_length - 1)

            args.update(
                {
                    "resample_args": {
                        "index_start": index_start,
                        "index_end": index_end,
                        "offset": offset,
                        "offset_sec": offset_sec,
                        "index_interval": index_interval,
                        "sum_index_interval": sum_index_interval,
                    }
                }
            )

        return args

    # The `by` parameter in groupby can be a list of "internal" and "external" objects
    # - internal objects would be columns that exist within the dataframe
    # - external objects would be other pandas Series/DataFrame/list-like objects
    #
    # We handle these changes a bit naively by creating a map of each object to a set
    # of parameters. For now, we really only care about whether we need to graft
    # predicates or not for specific objects that are a part of the current DataFrame.
    def _groupby_clean_by(self, by):
        # by will usually always be just a query compiler, but when we get a mix of
        # internal and external objects, we will always get a list. This is a side
        # effect of how Modin handles these cases.
        # keeps track of objects and whether they should be grafted or not
        by_map = {}
        intermediate_qc = self

        if isinstance(by, list):
            to_concat = []

            for obj in by:
                # If we have a query compiler, let's check and see if the columns exist
                # in the current dataframe
                if isinstance(obj, DBMSQueryCompiler):
                    if all([col in self.columns for col in obj.columns]):
                        by_map[obj._dataframe] = {"graft_predicates": True}
                    else:
                        by_map[obj._dataframe] = {"graft_predicates": False}
                        to_concat.append(obj)
                elif isinstance(obj, str) or isinstance(obj, int):
                    # We handle strings and ints the same as a label lookup, though this
                    # is usually an artifact of how things are preprocessed in Modin.
                    qc_obj = self.getitem_column_array([obj])._dataframe
                    by_map[qc_obj] = {"graft_predicates": True}
                elif isinstance(obj, pandas.Grouper):
                    by_map[obj] = self._get_grouper_metadata(obj)
                else:
                    raise make_exception(
                        NotImplementedError,
                        PonderError.GROUPBY_BY_TYPE_NOT_IMPLEMENTED,
                        f"{type(obj)} not yet supported for groupby by!",
                    )

            if to_concat:
                intermediate_qc = self.concat(axis=1, other=to_concat)
        elif isinstance(by, pandas.Grouper):
            by_map[by] = self._get_grouper_metadata(by)
        else:
            by_df = by._dataframe

            # This is still kind of a hack solution since we still rely on the column
            # names to be the same. We won't properly handle a case where we have the
            # same column name between two DataFrames that could be different. We need
            # a good way of distinguishing the two, which may require the leaf hash.
            if all([col in self._dataframe.columns for col in by_df.columns]):
                by_map[by_df] = {"graft_predicates": True}
            else:
                # We set graft_predicates to false here because we are going to concat
                # "by". If "by" is doing a binary op already, we will end up duplicating
                # that work and get the wrong final result.
                intermediate_qc = self.concat(1, [by])
                by_map[by_df] = {"graft_predicates": False}

        return intermediate_qc, ByParams(by_map)

    def _groupby_func_register(func: str):
        if func not in groupby_func_str_to_enum:
            raise make_exception(
                ValueError,
                PonderError.INVALID_GROUPBY_FUNC_NAME,
                f"{func} is not a valid groupby function",
            )

        def groupby_func(
            self, by, axis, groupby_kwargs, agg_args, agg_kwargs, drop=False
        ):
            if axis == 1:
                raise make_exception(
                    NotImplementedError,
                    PonderError.GROUPBY_AXIS_1_NOT_IMPLEMENTED,
                    f"groupby.{func}() with axis=1 is not supported yet",
                )

            if func == "corr":
                if agg_kwargs.get("method", "pearson") != "pearson":
                    raise make_exception(
                        NotImplementedError,
                        PonderError.GROUPBY_CORR_METHOD_NOT_IMPLEMENTED,
                        "groupby.corr() currently only supports method='pearson'",
                    )
            elif func == "cov":
                if agg_kwargs.get("ddof", 1) not in [None, 1]:
                    raise make_exception(
                        NotImplementedError,
                        PonderError.GROUPBY_COV_DDOF_NOT_IMPLEMENTED,
                        "groupby.cov() currently only supports ddof=1 or ddof=None",
                    )

            # TODO: we can probably do some cleanup with the enums that we have
            # in query_tree.py. There's some code repeat.
            reduction_func = func in (
                "count",
                "min",
                "max",
                "sum",
                "prod",
                "mean",
                "median",
                "var",
                "std",
                "sem",
                "skew",
                "kurt",
                "quantile",
                "unique",
                "nunique",
                "first",
                "last",
                "any",
                "all",
                "size",
                "value_counts",
                "describe",
                "corr",
                "cov",
            )

            # These are functions that are not reductions, and do not drop
            # the by columns from the result.
            view_func = func in (
                "head",
                "tail",
                "nth",
                "get_group",
            )

            intermediate_qc, by_params = self._groupby_clean_by(by)
            by_columns = by_params.columns

            # Reduction functions and nth are the only ones that typically follow
            # the as_index rule.
            if reduction_func:
                as_index = groupby_kwargs.get("as_index", True)
            else:
                as_index = False

            dropna = groupby_kwargs.get("dropna", True)
            sort_by_group_keys = groupby_kwargs.get("sort", True)
            result = self.__constructor__(
                intermediate_qc._dataframe.groupby(
                    by=by_params,
                    operator=groupby_func_str_to_enum[func],
                    as_index=as_index,
                    agg_args=agg_args,
                    agg_kwargs=agg_kwargs,
                    dropna=dropna,
                    sort_by_group_keys=sort_by_group_keys,
                )
            )

            # If we have a reduction function and as_index is False, then pandas
            # orders the by columns first.
            if not as_index and reduction_func:
                new_columns = [
                    *by_columns,
                    *(c for c in result.columns if c not in by_columns),
                ]
                result = result.getitem_column_array(new_columns)
            # View functions don't seem to modify the dataframe, unless any comes
            # from outside of self as in SeriesGroupBy like
            # https://ponderdata.atlassian.net/browse/POND-1180
            # note that if ANY by is from outside self, we need to drop all the bys,
            # e.g.
            # import pandas as pd
            # df = pd.DataFrame([["a", "b"]])
            # df.groupby([0, ['c']])[1].get_group(('a', 'c'))
            # probably the `drop` param is meant for this but modin passes drop=False
            # for series groupby (and that is possibly a bug).
            elif not (
                view_func
                and all(
                    params["graft_predicates"]
                    for params in by_params.get_map().values()
                )
            ):
                columns_without_by = [c for c in result.columns if c not in by_columns]
                result = result.getitem_column_array(columns_without_by)

            return result

        return groupby_func

    # It's possible that in the future some of these reduction functions will
    # need to be handled differently. E.g. we need to handle certain args
    # differently at the query compiler level.
    groupby_mean = _groupby_func_register("mean")
    groupby_median = _groupby_func_register("median")
    groupby_count = _groupby_func_register("count")
    groupby_max = _groupby_func_register("max")
    groupby_min = _groupby_func_register("min")
    groupby_sum = _groupby_func_register("sum")
    groupby_prod = _groupby_func_register("prod")
    groupby_all = _groupby_func_register("all")
    groupby_any = _groupby_func_register("any")
    groupby_std = _groupby_func_register("std")
    groupby_var = _groupby_func_register("var")
    groupby_skew = _groupby_func_register("skew")
    groupby_unique = _groupby_func_register("unique")
    groupby_nunique = _groupby_func_register("nunique")
    groupby_size = _groupby_func_register("size")
    groupby_sem = _groupby_func_register("sem")
    groupby_cummax = _groupby_func_register("cummax")
    groupby_cummin = _groupby_func_register("cummin")
    groupby_cumsum = _groupby_func_register("cumsum")
    groupby_cumprod = _groupby_func_register("cumprod")
    groupby_cumcount = _groupby_func_register("cumcount")
    groupby_first = _groupby_func_register("first")
    groupby_last = _groupby_func_register("last")
    groupby_head = _groupby_func_register("head")
    groupby_tail = _groupby_func_register("tail")
    groupby_nth = _groupby_func_register("nth")
    groupby_ngroup = _groupby_func_register("ngroup")
    groupby_get_group = _groupby_func_register("get_group")
    groupby_pct_change = _groupby_func_register("pct_change")
    groupby_corr = _groupby_func_register("corr")
    groupby_cov = _groupby_func_register("cov")
    groupby_diff = _groupby_func_register("diff")

    # TODO: need to implement support for numeric_only for groupby.quantile
    # and ensure that we match pandas errors for mismatch dtypes. Please see
    # POND-774, POND-775, and POND-776.
    groupby_quantile = _groupby_func_register("quantile")

    def groupby_agg(
        self,
        by,
        agg_func,
        axis,
        groupby_kwargs,
        agg_args,
        agg_kwargs,
        how="axis_wise",
        drop=False,
    ):
        if axis == 1:
            raise make_exception(
                NotImplementedError,
                PonderError.GROUPBY_AGG_AXIS_1_NOT_IMPLEMENTED,
                "groupby.agg() with axis=1 is not supported yet",
            )

        cumulative_funcs = ("cummax", "cummin", "cumsum", "cumprod", "cumcount")
        if isinstance(agg_func, str):
            funcs = [agg_func]
        elif isinstance(agg_func, dict):
            funcs = agg_func.values()
        elif isinstance(agg_func, list):
            funcs = agg_func
        elif hasattr(agg_func, "__call__"):
            raise make_exception(
                NotImplementedError,
                PonderError.GROUPBY_AGG_CALLABLE_NOT_SUPPORTED,
                "groupby.apply not supported ",
            )

        else:
            raise make_exception(
                TypeError,
                PonderError.GROUPBY_AGG_INVALID_FUNC_TYPE,
                "agg_func must be a string, list, callable, or dict",
            )

        # head and tail are not supported in groupby.agg
        # TODO: restructure groupby.agg to call each function individually and then
        # reconstruct the result.
        if any([func in ("head", "tail") for func in funcs]):
            raise make_exception(
                NotImplementedError,
                PonderError.GROUPBY_AGG_HEAD_TAIL_NOT_IMPLEMENTED,
                "head() and tail() are not supported in groupby.agg() yet",
            )

        intermediate_qc, by_params = self._groupby_clean_by(by)
        by_columns = by_params.columns

        # if agg_func is a dict, then we want to filter out all the columns
        # that aren't in by or in agg_func.
        if isinstance(agg_func, dict):
            cols = list(agg_func.keys()) + by_columns
            intermediate_qc = intermediate_qc.getitem_array(cols)

        is_cumulative = any([func in cumulative_funcs for func in funcs])

        # cumulative functions in groupby modify the dataframe in place,
        # so the index should not get changed to the name of the by column(s).
        if is_cumulative:
            as_index = False
        elif isinstance(agg_func, list):
            # matching pandas behavior here, for better or worse
            as_index = True
        else:
            as_index = groupby_kwargs.get("as_index", True)

        dropna = groupby_kwargs.get("dropna", True)
        result = self.__constructor__(
            intermediate_qc._dataframe.groupby(
                by=by_params, operator=agg_func, as_index=as_index, dropna=dropna
            )
        )
        if not as_index:
            result = result.getitem_column_array(
                [
                    *by_columns,
                    *(c for c in result.columns if c not in by_columns),
                ]
            )
        return result

    def groupby_fillna(
        self,
        by,
        axis,
        groupby_kwargs,
        agg_args,
        agg_kwargs,
        drop=False,
    ):
        if axis == 1:
            raise make_exception(
                NotImplementedError,
                PonderError.GROUPBY_FILLNA_AXIS_1_NOT_IMPLEMENTED,
                "groupby.fillna() with axis=1 is not supported yet",
            )
        by_df = by._dataframe
        fillna_value = agg_kwargs.get("value", None)
        fillna_method = agg_kwargs.get("method", None)
        fillna_limit = agg_kwargs.get("limit", None)
        fillna_inplace = agg_kwargs.get("inplace", False)
        group_cols = by_df.columns
        if fillna_value is not None:
            if isinstance(fillna_value, (pandas.Series, pandas.DataFrame)):
                raise make_exception(
                    ValueError,
                    PonderError.GROUPBY_FILLNA_PANDAS_VALUE,
                    "Cannot fillna with a pandas value."
                    + " Did you mean to pass a modin.pandas value?",
                )
        if fillna_inplace:
            raise make_exception(
                NotImplementedError,
                PonderError.GROUPBY_FILLNA_INPLACE_NOT_IMPLEMENTED,
                "groubpy.fillna() with inplace=True is not supported yet",
            )
        # TODO(https://ponderdata.atlassian.net/browse/POND-865): handle dropna
        # groupby kwarg correctly.
        dropna = groupby_kwargs.get("dropna", True)
        new_self = (
            self.dropna(subset=group_cols, how="all", thresh=None) if dropna else self
        )
        return new_self.fillna(
            squeeze_self=None,
            squeeze_value=None,
            value=fillna_value,
            method=fillna_method,
            inplace=fillna_inplace,
            limit=fillna_limit,
            group_cols=group_cols,
        ).drop(columns=group_cols)

    def groupby_ohlc(
        self, by, axis, groupby_kwargs, agg_args, agg_kwargs, is_df, drop=False
    ):
        if is_df:
            raise make_exception(
                NotImplementedError,
                PonderError.GROUPBY_OHLC_DATAFRAME_NOT_IMPLEMENTED,
                "groupby.ohlc() is not supported for dataframes yet",
            )

        # Calculate open, high, low, close
        res_open = self.groupby_first(
            by=by,
            axis=axis,
            groupby_kwargs=copy.deepcopy(groupby_kwargs),
            agg_args=agg_args,
            agg_kwargs=agg_kwargs,
            drop=drop,
        )
        res_high = self.groupby_max(
            by=by,
            axis=axis,
            groupby_kwargs=copy.deepcopy(groupby_kwargs),
            agg_args=agg_args,
            agg_kwargs=agg_kwargs,
            drop=drop,
        )
        res_low = self.groupby_min(
            by=by,
            axis=axis,
            groupby_kwargs=copy.deepcopy(groupby_kwargs),
            agg_args=agg_args,
            agg_kwargs=agg_kwargs,
            drop=drop,
        )
        res_close = self.groupby_last(
            by=by,
            axis=axis,
            groupby_kwargs=copy.deepcopy(groupby_kwargs),
            agg_args=agg_args,
            agg_kwargs=agg_kwargs,
            drop=drop,
        )
        # Change column names inplace
        res_open.columns = ["open"]
        res_high.columns = ["high"]
        res_low.columns = ["low"]
        res_close.columns = ["close"]
        # Aggregate columns into dataframe
        return res_open.concat(
            axis=1,
            other=[res_high, res_low, res_close],
        )

    def _groupby_idx_minmax(
        self,
        func,
        by,
        axis,
        groupby_kwargs,
        agg_args,
        agg_kwargs,
        drop=False,
    ):
        if any(d == np.dtype("O") for d in self.dtypes):
            raise make_exception(
                TypeError,
                PonderError.GROUPBY_IDX_MINMAX_DTYPE_NOT_ALLOWED,
                f"reduce operation 'arg{func[-3:]}' not allowed for this dtype",
            )

        if func not in ("idxmax", "idxmin"):
            raise make_exception(
                ValueError,
                PonderError.INTERNAL_GROUPBY_IDX_MINMAX_FUNC_NOT_VALID,
                "func needs to be either idxmax/idxmin",
            )

        if axis == 1 or agg_kwargs.get("axis", 0) in (1, "columns"):
            raise make_exception(
                NotImplementedError,
                PonderError.GROUPBY_IDX_MINMAX_AXIS_1_NOT_IMPLEMENTED,
                f"groupby.{func}() with axis=1 is not supported yet",
            )

        if not agg_kwargs.get("skipna", True):
            raise make_exception(
                NotImplementedError,
                PonderError.GROUPBY_IDX_MINMAX_SKIPNA_FALSE_NOT_IMPLEMENTED,
                f"groupby.{func}() with skipna=False is not supported yet",
            )

        as_index = groupby_kwargs.get("as_index", True)
        dropna = groupby_kwargs.get("dropna", True)
        sort_by_group_keys = groupby_kwargs.get("sort", True)

        qc_with_by, by_params = self._groupby_clean_by(by)
        by_columns = by_params.columns

        # Since each query selects different chunks of the row labels, we need
        # to do idxmax/idxmin for each column and concat these results together.
        qcs = []
        for col in self.columns:
            if col in by_columns:
                continue

            # We need to include the by column since it might be used in as_index
            intermediate_qc = qc_with_by.getitem_column_array(by_columns + [col])
            qcs.append(
                self.__constructor__(
                    intermediate_qc._dataframe.groupby(
                        by=by_params,
                        operator=groupby_func_str_to_enum[func],
                        as_index=True,  # Always set to true, we can drop it later
                        agg_args=agg_args,
                        agg_kwargs=agg_kwargs,
                        dropna=dropna,
                        sort_by_group_keys=sort_by_group_keys,
                    )
                )
            )

        result = qcs[0].concat(axis=1, other=qcs[1:])
        if not as_index:
            result = result.reset_index()
        return result

    def groupby_idxmax(
        self, by, axis, groupby_kwargs, agg_args, agg_kwargs, drop=False
    ):
        return self._groupby_idx_minmax(
            "idxmax", by, axis, groupby_kwargs, agg_args, agg_kwargs, drop
        )

    def groupby_idxmin(
        self, by, axis, groupby_kwargs, agg_args, agg_kwargs, drop=False
    ):
        return self._groupby_idx_minmax(
            "idxmin", by, axis, groupby_kwargs, agg_args, agg_kwargs, drop
        )

    def unique(self):
        # We can't just do "SELECT DISTINCT" for unique because we need to return rows
        # in their original order. Group by the columns and then just take the key for
        # each group, and let dataframe.groupby order the result by original order. make
        # sure to set sort_by_group_keys=False so we don't make the group key the
        # primary sort key as we usualy do.
        # a little hacky since we're not really doing a groupby explicitly here
        by_params = ByParams({self._dataframe: {"graft_predicates": False}})
        return self.__constructor__(
            self._dataframe.groupby(
                sort_by_group_keys=False,
                columns_to_aggregate=self.columns,
                by=by_params,
                operator=GROUPBY_FUNCTIONS.NOOP,
                as_index=False,
                dropna=False,
            )
        )

    def cummax(self, axis, skipna, *args, **kwargs):
        if axis == 1:
            raise make_exception(
                NotImplementedError,
                PonderError.CUMMAX_AXIS_1_NOT_IMPLEMENTED,
                "cummax() with axis=1 is not supported yet",
            )
        return self.__constructor__(
            self._dataframe.cumulative_func(CUMULATIVE_FUNCTIONS.MAX, skipna)
        )

    def cummin(self, axis, skipna, *args, **kwargs):
        if axis == 1:
            raise make_exception(
                NotImplementedError,
                PonderError.CUMMIN_AXIS_1_NOT_IMPLEMENTED,
                "cummin() with axis=1 is not supported yet",
            )
        return self.__constructor__(
            self._dataframe.cumulative_func(CUMULATIVE_FUNCTIONS.MIN, skipna)
        )

    def cumsum(self, axis, skipna, *args, **kwargs):
        if axis == 1:
            raise make_exception(
                NotImplementedError,
                PonderError.CUMSUM_AXIS_1_NOT_IMPLEMENTED,
                "cumsum() with axis=1 is not supported yet",
            )
        return self.__constructor__(
            self._dataframe.cumulative_func(CUMULATIVE_FUNCTIONS.SUM, skipna)
        )

    def cumprod(self, axis, skipna, *args, **kwargs):
        if axis == 1:
            raise make_exception(
                NotImplementedError,
                PonderError.CUMPROD_AXIS_1_NOT_IMPLEMENTED,
                "cumprod() with axis=1 is not supported yet",
            )
        return self.__constructor__(
            self._dataframe.cumulative_func(CUMULATIVE_FUNCTIONS.PROD, skipna)
        )

    # TODO: Try to unify the implementation of `abs` and `round` along with all other
    # cell-wise operations such as string functions. One current challenge is that each
    # of `abs` and `round` can result in columns with different dtypes (int and float),
    # which is not the case for any of the string functions.
    def abs(self):
        return self.__constructor__(self._dataframe.abs())

    def round(self, decimals, *args, **kwargs):
        return self.__constructor__(self._dataframe.round(decimals))

    def negative(self):
        return self.mul(-1)

    def get_index_names(self, axis=0):
        return []

    def is_monotonic_increasing(self):
        """Return boolean if values in the object are monotonicly increasing.

        Returns
        -------
        bool
        """
        return self._dataframe.is_monotonic_increasing()

    def is_monotonic_decreasing(self):
        """Return boolean if values in the object are monotonicly decreasing.

        Returns
        -------
        bool
        """
        return self._dataframe.is_monotonic_decreasing()

    def idxmin(self, **kwargs):  # noqa: PR02
        if kwargs.get("axis", 0) == 1:
            raise make_exception(
                NotImplementedError,
                PonderError.IDXMIN_AXIS_1_NOT_IMPLEMENTED,
                "idxmin() with axis=1 is not supported yet",
            )
        if not kwargs.get("skipna", True):
            raise make_exception(
                NotImplementedError,
                PonderError.IDXMIN_SKIPNA_FALSE_NOT_IMPLEMENTED,
                "idxmin() with skipna=False is not supported yet",
            )
        result = self.__constructor__(self._dataframe.idx_minmax(min=True))
        result.index.name = None
        return result

    def idxmax(self, **kwargs):  # noqa: PR02
        if kwargs.get("axis", 0) == 1:
            raise make_exception(
                NotImplementedError,
                PonderError.IDXMAX_AXIS_1_NOT_IMPLEMENTED,
                "idxmax() with axis=1 is not supported yet",
            )
        if not kwargs.get("skipna", True):
            raise make_exception(
                NotImplementedError,
                PonderError.IDXMAX_SKIPNA_FALSE_NOT_IMPLEMENTED,
                "idxmax() with skipna=False is not supported yet",
            )
        result = self.__constructor__(self._dataframe.idx_minmax(min=False))
        result.index.name = None
        return result

    def _expanding_pushdown_agg(
        self, axis, operator, expanding_args, agg_args, agg_kwargs
    ):
        [min_periods, arg_axis, method] = expanding_args

        if axis != 0:
            raise make_exception(
                NotImplementedError,
                PonderError.EXPANDING_AXIS_1_NOT_IMPLEMENTED,
                "expanding() with axis=1 is not supported yet",
            )
        if method != "single":
            raise make_exception(
                NotImplementedError,
                PonderError.EXPANDING_METHOD_NOT_IMPLEMENTED,
                f"expanding() with method={method} is not supported yet",
            )
        if axis != arg_axis:
            raise make_exception(
                TypeError,
                PonderError.EXPANDING_AXIS_ARG_AXIS_MISMATCH,
                "Axis and arg_axis must be same",
            )

        non_numeric_cols = [
            col
            for col, col_dtype in self.dtypes.items()
            if not is_numeric_dtype(col_dtype)
        ]

        if operator not in ["COUNT", "SEM", __WINDOW_AGGREGATE_MAP__]:
            select_cols = self.drop(columns=non_numeric_cols)
        elif operator == __WINDOW_AGGREGATE_MAP__:
            col_func_map = agg_kwargs["func_map"]
            cols_to_drop = [
                col
                for col, col_dtype in self.dtypes.items()
                if col not in col_func_map.keys()
            ]
            select_cols = self.drop(columns=cols_to_drop)
            # Change column order to adhere to the one in function-map dictionary
            if list(col_func_map.keys()) != list(select_cols.columns):
                select_cols = select_cols.getitem_column_array(
                    [col for col in col_func_map.keys()]
                )
            for col, col_dtype in select_cols.dtypes.items():
                if not is_numeric_dtype(col_dtype) and col_func_map[col] not in [
                    "COUNT",
                    "SEM",
                ]:
                    raise make_exception(
                        pandas.core.base.DataError,
                        PonderError.EXPANDING_NO_NUMERIC_TYPES_TO_AGGREGATE,
                        "No numeric types to aggregate",
                    )

        else:
            select_cols = self

        return self.__constructor__(
            select_cols._dataframe.expanding(
                axis=axis,
                operator=operator,
                min_window=min_periods,
                non_numeric_cols=non_numeric_cols,
                agg_args=agg_args,
                agg_kwargs=agg_kwargs,
            )
        )

    def expanding_aggregate(self, axis, expanding_args, func, *agg_args, **agg_kwargs):
        new_func_map = self._check_windowing_agg_func_validity(func)
        if isinstance(new_func_map, str):
            return getattr(self, "expanding_" + new_func_map)(
                axis, expanding_args, *agg_args, **agg_kwargs
            )

        non_existing_cols = [col for col in new_func_map if col not in self.columns]

        if len(non_existing_cols) > 0:
            raise make_exception(
                KeyError,
                PonderError.EXPANDING_AGG_NON_EXISTING_COLS,
                f"Column(s) {non_existing_cols} do not exist",
            )

        agg_kwargs["func_map"] = new_func_map
        return self._expanding_pushdown_agg(
            axis, __WINDOW_AGGREGATE_MAP__, expanding_args, agg_args, agg_kwargs
        )

    def expanding_sum(self, axis, expanding_args, *sum_args, **sum_kwargs):
        return self._expanding_pushdown_agg(
            axis, "SUM", expanding_args, sum_args, sum_kwargs
        )

    def expanding_kurt(self, axis, expanding_args, *kurt_args, **kurt_kwargs):
        return self._expanding_pushdown_agg(
            axis, "KURTOSIS", expanding_args, kurt_args, kurt_kwargs
        )

    def expanding_median(self, axis, expanding_args, **median_kwargs):
        return self._expanding_pushdown_agg(
            axis, "MEDIAN", expanding_args, None, median_kwargs
        )

    def expanding_corr(self, axis, expanding_args, *corr_args, **corr_kwargs):
        if corr_kwargs.get("method", "pearson") != "pearson":
            raise make_exception(
                NotImplementedError,
                PonderError.EXPANDING_CORR_METHOD_NOT_IMPLEMENTED,
                "expanding.corr() currently only supports method='pearson'",
            )
        if corr_kwargs.get("pairwise", None) is not None:
            raise make_exception(
                NotImplementedError,
                PonderError.EXPANDING_CORR_PAIRWISE_NOT_IMPLEMENTED,
                "expanding.corr() currently only supports pairwise=None",
            )
        if corr_kwargs.get("ddof", 1) not in [None, 1]:
            raise make_exception(
                NotImplementedError,
                PonderError.EXPANDING_CORR_DDOF_NOT_IMPLEMENTED,
                "expanding.corr() currently only supports ddof=1 or ddof=None",
            )
        return self._expanding_pushdown_agg(
            axis, "CORR", expanding_args, corr_args, corr_kwargs
        )

    def expanding_cov(self, axis, expanding_args, ddof=1, *cov_args, **cov_kwargs):
        cov_kwargs["ddof"] = ddof
        if cov_kwargs.get("pairwise", None) is not None:
            raise make_exception(
                NotImplementedError,
                PonderError.EXPANDING_COV_PAIRWISE_NOT_IMPLEMENTED,
                "expanding.cov() currently only supports pairwise=None",
            )
        if cov_kwargs.get("ddof", 1) not in [None, 1]:
            raise make_exception(
                NotImplementedError,
                PonderError.EXPANDING_COV_DDOF_NOT_IMPLEMENTED,
                "expanding.cov() currently only supports ddof=1 or ddof=None",
            )
        return self._expanding_pushdown_agg(
            axis, "COV", expanding_args, cov_args, cov_kwargs
        )

    def expanding_min(self, axis, expanding_args, *min_args, **min_kwargs):
        return self._expanding_pushdown_agg(
            axis, "MIN", expanding_args, min_args, min_kwargs
        )

    def expanding_max(self, axis, expanding_args, *max_args, **max_kwargs):
        return self._expanding_pushdown_agg(
            axis, "MAX", expanding_args, max_args, max_kwargs
        )

    def expanding_mean(self, axis, expanding_args, *mean_args, **mean_kwargs):
        return self._expanding_pushdown_agg(
            axis, "AVG", expanding_args, mean_args, mean_kwargs
        )

    def expanding_quantile(
        self, axis, expanding_args, *quantile_args, **quantile_kwargs
    ):
        if quantile_kwargs.get("interpolation", "linear") != "linear":
            raise make_exception(
                NotImplementedError,
                PonderError.EXPANDING_QUANTILE_INTERPOLATION_NOT_IMPLEMENTED,
                "expanding.quantile() currently only supports interpolation='linear'",
            )
        return self._expanding_pushdown_agg(
            axis, "QUANTILE", expanding_args, quantile_args, quantile_kwargs
        )

    def expanding_rank(self, axis, expanding_args, *rank_args, **rank_kwargs):
        if rank_kwargs.get("pct", False):
            raise make_exception(
                NotImplementedError,
                PonderError.EXPANDING_RANK_PCT_NOT_IMPLEMENTED,
                "expanding.rank() currently only supports pct=False",
            )
        return self._expanding_pushdown_agg(
            axis, "RANK", expanding_args, rank_args, rank_kwargs
        )

    def expanding_var(self, axis, expanding_args, *var_args, **var_kwargs):
        return self._expanding_pushdown_agg(
            axis, "VARIANCE", expanding_args, var_args, var_kwargs
        )

    def expanding_skew(self, axis, expanding_args, *skew_args, **skew_kwargs):
        return self._expanding_pushdown_agg(
            axis, "SKEW", expanding_args, skew_args, skew_kwargs
        )

    def expanding_std(self, axis, expanding_args, *std_args, **std_kwargs):
        return self._expanding_pushdown_agg(
            axis, "STDDEV", expanding_args, std_args, std_kwargs
        )

    def expanding_count(self, axis, expanding_args, *args, **kwargs):
        return self._expanding_pushdown_agg(axis, "COUNT", expanding_args, args, kwargs)

    def expanding_sem(self, axis, expanding_args, *args, **kwargs):
        return self._expanding_pushdown_agg(axis, "SEM", expanding_args, args, kwargs)

    def _rolling_pushdown_agg(
        self, axis, operator, rolling_kwargs, agg_args, agg_kwargs
    ):
        if rolling_kwargs.pop("min_periods") is not None:
            raise make_exception(
                NotImplementedError,
                PonderError.ROLLING_MIN_PERIODS_NOT_IMPLEMENTED,
                "rolling() with min_periods != None is not supported yet",
            )
        if rolling_kwargs.pop("center") is True:
            raise make_exception(
                NotImplementedError,
                PonderError.ROLLING_CENTER_NOT_IMPLEMENTED,
                "rolling() center=True is not supported yet",
            )
        if (win_type := rolling_kwargs.pop("win_type")) not in ["gaussian", None]:
            raise make_exception(
                NotImplementedError,
                PonderError.ROLLING_WIN_TYPE_NOT_IMPLEMENTED_AT_QUERY_COMPILER,
                f"rolling() with win_type {win_type} is not supported yet",
            )
        if rolling_kwargs.pop("on") is not None:
            raise make_exception(
                NotImplementedError,
                PonderError.ROLLING_ON_NOT_IMPLEMENTED,
                "rolling() with on != None is not supported yet",
            )
        if rolling_kwargs.pop("closed") is not None:
            raise make_exception(
                NotImplementedError,
                PonderError.ROLLING_CLOSED_NOT_IMPLEMENTED,
                "rolling() with closed != None is not supported yet",
            )
        if rolling_kwargs.pop("step") is not None:
            raise make_exception(
                NotImplementedError,
                PonderError.ROLLING_STEP_NOT_IMPLEMENTED,
                "rolling() with step != None is not supported yet",
            )
        if (method := rolling_kwargs.pop("method")) != "single":
            raise make_exception(
                NotImplementedError,
                PonderError.ROLLING_METHOD_NOT_IMPLEMENTED,
                f"rolling() with method {method} is not supported yet",
            )
        if (axis := rolling_kwargs.pop("axis")) != 0:
            raise make_exception(
                NotImplementedError,
                PonderError.ROLLING_AXIS_1_NOT_IMPLEMENTED,
                "rolling() with axis=1 is not supported yet",
            )

        window = rolling_kwargs.pop("window")

        if len(rolling_kwargs) > 0:
            raise make_exception(
                ValueError,
                PonderError.UNKNOWN_ROLLING_KWARGS,
                f"Cannot handle unknown rolling kwargs {rolling_kwargs.keys()}",
            )

        non_numeric_cols = [
            col
            for col, col_dtype in self.dtypes.items()
            if not is_numeric_dtype(col_dtype)
        ]

        if operator not in ["COUNT", "SEM", __WINDOW_AGGREGATE_MAP__]:
            select_cols = self.drop(columns=non_numeric_cols)
        elif operator == __WINDOW_AGGREGATE_MAP__:
            col_func_map = agg_kwargs["func_map"]
            cols_to_drop = [
                col
                for col, col_dtype in self.dtypes.items()
                if col not in col_func_map.keys()
            ]
            select_cols = self.drop(columns=cols_to_drop)
            # Change column order to adhere to the one in function-map dictionary
            if list(col_func_map.keys()) != list(select_cols.columns):
                select_cols = select_cols.getitem_column_array(
                    list(col_func_map.keys())
                )

            for col, col_dtype in select_cols.dtypes.items():
                if not is_numeric_dtype(col_dtype) and col_func_map[col] not in [
                    "COUNT",
                    "SEM",
                ]:
                    raise make_exception(
                        pandas.errors.DataError,
                        PonderError.ROLLING_NO_NUMERIC_TYPES_TO_AGGREGATE,
                        "No numeric types to aggregate",
                    )

        else:
            select_cols = self

        # If window is 1 skip for sum, mean, min, max going all the way to SQL
        # and generating a statement, just short-circuit by choosing only
        # numeric columns
        if window == 1 and operator in [
            "SUM",
            "MEAN",
            "MIN",
            "MAX",
        ]:
            return select_cols

        return self.__constructor__(
            select_cols._dataframe.rolling(
                axis=axis,
                operator=operator,
                window=window,
                non_numeric_cols=non_numeric_cols,
                agg_args=agg_args,
                agg_kwargs=agg_kwargs,
                win_type=win_type,
            )
        )

    def _check_and_replace_windowing_agg_str(self, func, is_dict=False):
        if func == "count":
            return "count" if is_dict is False else "COUNT"
        elif func == "max":
            return "max" if is_dict is False else "MAX"
        elif func == "mean":
            return "mean" if is_dict is False else "AVG"
        elif func == "min":
            return "min" if is_dict is False else "MIN"
        elif func == "sum":
            return "sum" if is_dict is False else "SUM"
        elif func == "std":
            return "std" if is_dict is False else "STDDEV"
        elif func == "var":
            return "var" if is_dict is False else "VARIANCE"
        elif func == "sem":
            return "sem" if is_dict is False else "SEM"
        elif func == "median":
            return "median" if is_dict is False else "MEDIAN"
        elif func == "kurt":
            return "kurt" if is_dict is False else "KURTOSIS"
        elif func == "skew":
            return "skew" if is_dict is False else "SKEW"
        elif func == "quantile":
            return "quantile" if is_dict is False else "QUANTILE"
        elif func == "rank":
            return "rank" if is_dict is False else "RANK"
        else:
            raise make_exception(
                NotImplementedError,
                PonderError.ROLLING_AGG_STR_FUNC_NOT_IMPLEMENTED,
                f"rolling() and expanding() with aggregation {func}"
                + " is not supported yet",
            )

    def _check_and_replace_windowing_agg_func(self, func, is_dict=False):
        if func == np.max:
            return "max" if is_dict is False else "MAX"
        elif func == np.mean:
            return "mean" if is_dict is False else "AVG"
        elif func == np.min:
            return "min" if is_dict is False else "MIN"
        elif func == np.sum:
            return "sum" if is_dict is False else "SUM"
        elif func == np.std:
            return "std" if is_dict is False else "STDDEV"
        elif func == np.var:
            return "var" if is_dict is False else "VARIANCE"
        else:
            raise make_exception(
                NotImplementedError,
                PonderError.ROLLING_AGG_CALLABLE_FUNC_NOT_IMPLEMENTED,
                f"rolling() and expanding() with aggregation {func}"
                + " is not supported yet",
            )

    def _check_windowing_agg_func_validity(self, func, is_dict=False):
        if (
            not isinstance(func, str)
            and not isinstance(func, dict)
            and not callable(func)
        ):
            raise make_exception(
                TypeError,
                PonderError.ROLLING_AGG_FUNC_INVALID_TYPE,
                f"{func} should be either str, dict, or callable.",
            )

        if isinstance(func, str):
            return self._check_and_replace_windowing_agg_str(func, is_dict)
        elif callable(func):
            return self._check_and_replace_windowing_agg_func(func, is_dict)
        elif isinstance(func, dict):
            new_func_map = {
                col: self._check_windowing_agg_func_validity(col_func, is_dict=True)
                for col, col_func in func.items()
            }
            return new_func_map

    def rolling_aggregate(self, axis, rolling_kwargs, func, *agg_args, **agg_kwargs):
        new_func_map = self._check_windowing_agg_func_validity(func)
        if isinstance(new_func_map, str):
            if new_func_map == "count":
                return self.rolling_count(axis, rolling_kwargs)
            return getattr(self, "rolling_" + new_func_map)(
                axis, rolling_kwargs, *agg_args, **agg_kwargs
            )

        non_existing_cols = [
            col for col, col_func in new_func_map.items() if col not in self.columns
        ]

        if len(non_existing_cols) != 0:
            raise make_exception(
                KeyError,
                PonderError.ROLLING_AGG_NON_EXISTING_COLS,
                f"Column(s) {non_existing_cols} do not exist",
            )

        agg_kwargs["func_map"] = new_func_map
        return self._rolling_pushdown_agg(
            axis, __WINDOW_AGGREGATE_MAP__, rolling_kwargs, agg_args, agg_kwargs
        )

    def rolling_corr(self, axis, rolling_kwargs, *corr_args, **corr_kwargs):
        if corr_kwargs.get("method", "pearson") != "pearson":
            raise make_exception(
                NotImplementedError,
                PonderError.ROLLING_CORR_METHOD_NOT_IMPLEMENTED,
                "rolling.corr() currently only supports method='pearson'",
            )
        if corr_kwargs.get("pairwise", None) is not None:
            raise make_exception(
                NotImplementedError,
                PonderError.ROLLING_CORR_PAIRWISE_NOT_IMPLEMENTED,
                "rolling.corr() currently only supports pairwise=None",
            )
        if corr_kwargs.get("ddof", 1) not in [None, 1]:
            raise make_exception(
                NotImplementedError,
                PonderError.ROLLING_CORR_DDOF_NOT_IMPLEMENTED,
                "rolling.corr() currently only supports ddof=1 or ddof=None",
            )
        return self._rolling_pushdown_agg(
            axis, "CORR", rolling_kwargs, corr_args, corr_kwargs
        )

    def rolling_count(self, axis, rolling_kwargs):
        return self._rolling_pushdown_agg(axis, "COUNT", rolling_kwargs, None, None)

    def rolling_kurt(self, axis, rolling_kwargs, *kurt_args, **kurt_kwargs):
        return self._rolling_pushdown_agg(
            axis, "KURTOSIS", rolling_kwargs, kurt_args, kurt_kwargs
        )

    def rolling_cov(self, axis, rolling_kwargs, ddof=1, *cov_args, **cov_kwargs):
        cov_kwargs["ddof"] = ddof
        if cov_kwargs.get("pairwise", None) is not None:
            raise make_exception(
                NotImplementedError,
                PonderError.ROLLING_COV_PAIRWISE_NOT_IMPLEMENTED,
                "rolling.cov() currently only supports pairwise=None",
            )
        if cov_kwargs.get("ddof", 1) not in [None, 1]:
            raise make_exception(
                NotImplementedError,
                PonderError.ROLLING_COV_DDOF_NOT_IMPLEMENTED,
                "rolling.cov() currently only supports ddof=1 or ddof=None",
            )
        return self._rolling_pushdown_agg(
            axis, "COV", rolling_kwargs, cov_args, cov_kwargs
        )

    def rolling_max(self, axis, rolling_kwargs, *max_args, **max_kwargs):
        return self._rolling_pushdown_agg(
            axis, "MAX", rolling_kwargs, max_args, max_kwargs
        )

    def rolling_mean(self, axis, rolling_kwargs, *mean_args, **mean_kwargs):
        return self._rolling_pushdown_agg(
            axis, "AVG", rolling_kwargs, mean_args, mean_kwargs
        )

    def rolling_median(self, axis, rolling_kwargs, **median_kwargs):
        return self._rolling_pushdown_agg(
            axis, "MEDIAN", rolling_kwargs, None, median_kwargs
        )

    def rolling_min(self, axis, rolling_kwargs, *sum_args, **sum_kwargs):
        return self._rolling_pushdown_agg(
            axis, "MIN", rolling_kwargs, sum_args, sum_kwargs
        )

    def rolling_quantile(self, axis, rolling_kwargs, *quantile_args, **quantile_kwargs):
        if quantile_kwargs.get("interpolation", "linear") != "linear":
            raise make_exception(
                NotImplementedError,
                PonderError.ROLLING_QUANTILE_INTERPOLATION_NOT_IMPLEMENTED,
                "rolling.quantile() currently only supports interpolation='linear'",
            )
        return self._rolling_pushdown_agg(
            axis, "QUANTILE", rolling_kwargs, quantile_args, quantile_kwargs
        )

    def rolling_rank(self, axis, rolling_kwargs, *rank_args, **rank_kwargs):
        if rank_kwargs.get("pct", False):
            raise make_exception(
                NotImplementedError,
                PonderError.ROLLING_RANK_PCT_NOT_IMPLEMENTED,
                "rolling.rank() currently only supports pct=False",
            )
        return self._rolling_pushdown_agg(
            axis, "RANK", rolling_kwargs, rank_args, rank_kwargs
        )

    def rolling_sem(self, axis, rolling_kwargs, *sem_args, **sem_kwargs):
        return self._rolling_pushdown_agg(
            axis, "SEM", rolling_kwargs, sem_args, sem_kwargs
        )

    def rolling_skew(self, axis, rolling_kwargs, *skew_args, **skew_kwargs):
        return self._rolling_pushdown_agg(
            axis, "SKEW", rolling_kwargs, skew_args, skew_kwargs
        )

    def rolling_std(self, axis, rolling_kwargs, ddof=1, *std_args, **std_kwargs):
        std_kwargs["ddof"] = ddof
        return self._rolling_pushdown_agg(
            axis, "STDDEV", rolling_kwargs, std_args, std_kwargs
        )

    def rolling_sum(self, axis, rolling_kwargs, *sum_args, **sum_kwargs):
        return self._rolling_pushdown_agg(
            axis, "SUM", rolling_kwargs, sum_args, sum_kwargs
        )

    def window_mean(self, axis, window_args, *mean_args, **mean_kwargs):
        return self.rolling_mean(axis, window_args, *mean_args, **mean_kwargs)

    def window_sum(self, axis, window_args, *sum_args, **sum_kwargs):
        return self.rolling_sum(axis, window_args, *sum_args, **sum_kwargs)

    def window_var(self, axis, window_args, *var_args, **var_kwargs):
        return self.rolling_var(axis, window_args, *var_args, **var_kwargs)

    def window_std(self, axis, window_args, *std_args, **std_kwargs):
        return self.rolling_std(axis, window_args, *std_args, **std_kwargs)

    def rolling_var(
        self, axis, rolling_kwargs, ddof=1, *variance_args, **variance_kwargs
    ):
        variance_kwargs["ddof"] = ddof
        return self._rolling_pushdown_agg(
            axis, "VARIANCE", rolling_kwargs, variance_args, variance_kwargs
        )

    def to_datetime(self, *args, **kwargs):
        pandas_datetime_format = kwargs.get("format")
        if pandas_datetime_format is not None:
            # TODO: We might need to consider a different
            # way of reaching all the way into the dialect from the QC
            dialect = self._dataframe._query_tree._conn._dialect
            db_datetime_format = dialect.pandas_datetime_format_to_db_datetime_format(
                pandas_datetime_format
            )
            kwargs["format"] = db_datetime_format
        if kwargs.get("origin", None) == "julian":
            raise make_exception(
                ValueError,
                PonderError.PONDER_DOES_NOT_SUPPORT_JULIAN_DATES,
                "Ponder does not support Julian dates.",
            )
        if kwargs.get("unit", "ns") not in [None, "D", "s", "ms", "us", "ns"]:
            raise TypeError(
                f"Invalid datetime unit in metadata string \"[{kwargs.get('unit')}]\""
            )
        return self.astype("datetime64", **kwargs)

    # TODO(REFACTOR): Spread **kwargs into actual arguments (Modin issue #3108).
    def isin(self, values, ignore_indices=False, **kwargs):  # noqa: PR02
        self_is_series = kwargs.pop("shape_hint", None) == "column"
        if isinstance(values, type(self)):
            if self_is_series:
                values_type = values.dtypes.iloc[0]
                self_type = self.dtypes.iloc[0]
                if is_numeric_dtype(self_type):
                    comparable_types = is_numeric_dtype(values_type)
                elif is_datetime64_any_dtype(self_type):
                    comparable_types = is_datetime64_any_dtype(values_type)
                else:
                    comparable_types = not (
                        is_numeric_dtype(values_type)
                        or is_datetime64_any_dtype(values_type)
                    )
                if not comparable_types:
                    # if we try joining on non-comparable types, e.g. string to float,
                    # some engines will raise an exception. Within the join SQL code, we
                    # could use a new dialect function to a comparable type like
                    # ":variant" for snowflake and "TO_JSON_STRING" for bigquery and a
                    # struct with {"value": <value>} for duckdb, but that's extra work
                    # for a corner case that @mvashishtha doesn't want to improve right
                    # now. If the types don't match, sin is always false. Just return
                    # false.
                    return self._replace_all(False)
                # 1. get unique values so we only get match per row in self.
                # 2. merge self to values and check _merge indicator to see whether
                #    each value in self was in `values`. merge should preserve `self`'s
                #    order.
                result = (
                    self.merge(
                        values.unique(),
                        how="left",
                        left_on=self.columns[0],
                        right_on=values.columns[0],
                        indicator=True,
                    )
                    .getitem_column_array(["_merge"])
                    .eq("both")
                )
                result.columns = self.columns
                return result
            values_for_dataframe = values._dataframe
        else:
            # TODO: this error checking code should go into API layer (it's not too much
            # work to do it before merging the soda PR)
            if not isinstance(values, dict) and not is_list_like(values):
                # This error message comes straight from pandas code.
                raise make_exception(
                    TypeError,
                    PonderError.ISN_INVALID_VALUE_TYPE,
                    "only list-like or dict-like objects are allowed "
                    "to be passed to isin(), "
                    f"you passed a '{type(values).__name__}'",
                )

            if isinstance(values, dict):
                # make a copy of values so we can modify it
                values_for_dataframe = dict(values)
                for c in self.columns.unique():
                    if c not in values_for_dataframe:
                        values_for_dataframe[c] = values
            else:
                values_for_dataframe = {c: values for c in self.columns.unique()}
        return self.__constructor__(
            self._dataframe.isin(
                values_for_dataframe, ignore_indices, self_is_series=self_is_series
            )
        )

    def _resample_pushdown_agg(self, operator, resample_kwargs, agg_args, agg_kwargs):
        # Should probably have a method like _get_pandas_type() on the indexes, but
        # checking their dtypes works for now.
        invalid_index_type = None
        if not isinstance(self.index, DBMSIndex):
            invalid_index_type = "'RangeIndex'"
        elif len(self.index.column_names) > 1:
            invalid_index_type = "'MultiIndex'"
        elif not pandas.api.types.is_datetime64_any_dtype(self.index.dtype):
            # type here might be like "Int64Index" but that's a little hard to
            # generate.
            invalid_index_type = f"an index class with type {self.index.dtype}"
        if invalid_index_type is not None:
            raise make_exception(
                TypeError,
                PonderError.RESAMPLE_INVALID_INDEX_TYPE,
                f"Only valid with DatetimeIndex, TimedeltaIndex or PeriodIndex, but "
                f"got an instance of {invalid_index_type}",
            )

        # Certain resample aggregations only support numeric columns.
        # In future pandas versions, numeric_only will default to False
        # so we should modify this check to directly throw a TypeError
        if operator in (
            GROUPBY_FUNCTIONS.SUM,
            GROUPBY_FUNCTIONS.MEAN,
            GROUPBY_FUNCTIONS.MEDIAN,
            GROUPBY_FUNCTIONS.STD,
            GROUPBY_FUNCTIONS.VAR,
            GROUPBY_FUNCTIONS.SEM,
            GROUPBY_FUNCTIONS.QUANTILE,
            GROUPBY_FUNCTIONS.PROD,
        ):
            resample_obj = self.getitem_column_array(
                [
                    self.columns[i]
                    for i in range(len(self.dtypes))
                    if is_numeric_dtype(self.dtypes.iloc[i])
                ]
            )
            if len(resample_obj.columns) == 0:
                raise make_exception(
                    TypeError,
                    PonderError.RESAMPLE_NON_NUMERIC_AGGREGATION_INVALID,
                    "resample() cannot be performed against 'object' dtypes!",
                )
        else:
            resample_obj = self

        rule = resample_kwargs.pop("rule")
        axis = resample_kwargs.pop("axis")
        closed = resample_kwargs.pop("closed")
        label = resample_kwargs.pop("label")
        convention = resample_kwargs.pop("convention")
        kind = resample_kwargs.pop("kind")
        on = resample_kwargs.pop("on")
        level = resample_kwargs.pop("level")
        origin = resample_kwargs.pop("origin")
        offset = resample_kwargs.pop("offset")
        group_keys = resample_kwargs.pop("group_keys")
        if len(resample_kwargs) > 0:
            raise make_exception(
                RuntimeError,
                PonderError.RESAMPLE_UNKNOWN_ARGS,
                f"Unknown resample args {resample_kwargs}",
            )

        if axis not in (0, "index"):
            raise make_exception(
                NotImplementedError,
                PonderError.RESAMPLE_AXIS_1_NOT_IMPLEMENTED,
                "resample() with axis=1 is not supported yet",
            )
        if closed is not None:
            raise make_exception(
                NotImplementedError,
                PonderError.RESAMPLE_CLOSED_NOT_IMPLEMENTED,
                "resample() with closed != None is not supported yet",
            )
        if label is not None:
            raise make_exception(
                NotImplementedError,
                PonderError.RESAMPLE_LABEL_NOT_IMPLEMENTED,
                "resample() with label != None is not supported yet",
            )
        if convention != "start":
            raise make_exception(
                NotImplementedError,
                PonderError.RESAMPLE_CONVENTION_NOT_IMPLEMENTED,
                "resample() with convention != 'start' is not supported yet",
            )
        if kind is not None:
            raise make_exception(
                NotImplementedError,
                PonderError.RESAMPLE_KIND_NOT_IMPLEMENTED,
                "resample() with kind != None is not supported yet",
            )
        if on is not None:
            raise make_exception(
                NotImplementedError,
                PonderError.RESAMPLE_ON_NOT_IMPLEMENTED,
                "resample() with on != None is not supported yet",
            )
        if level is not None:
            raise make_exception(
                NotImplementedError,
                PonderError.RESAMPLE_LEVEL_NOT_IMPLEMENTED,
                "resample() with level != None is not supported yet",
            )
        if origin != "start_day":
            raise make_exception(
                NotImplementedError,
                PonderError.RESAMPLE_ORIGIN_NOT_IMPLEMENTED,
                "resample() with origin != 'start_day' is not supported yet",
            )
        if offset is not None:
            raise make_exception(
                NotImplementedError,
                PonderError.RESAMPLE_OFFSET_NOT_IMPLEMENTED,
                "resample() with offset != None is not supported yet",
            )
        if group_keys is not False:
            raise make_exception(
                NotImplementedError,
                PonderError.RESAMPLE_GROUP_KEYS_NOT_IMPLEMENTED,
                "resample() with `group_keys` param is not supported yet",
            )

        # Sort implicitly to mimic pandas behavior
        resample_obj = resample_obj.sort_index()
        return resample_obj.__constructor__(
            resample_obj._dataframe.resample(
                operator=operator,
                rule=rule,
                agg_args=agg_args,
                agg_kwargs=agg_kwargs,
            )
        )

    def resample_min(self, resample_kwargs, *min_args, **min_kwargs):
        return self._resample_pushdown_agg(
            GROUPBY_FUNCTIONS.MIN, resample_kwargs, min_args, min_kwargs
        )

    def resample_max(self, resample_kwargs, *max_args, **max_kwargs):
        return self._resample_pushdown_agg(
            GROUPBY_FUNCTIONS.MAX, resample_kwargs, max_args, max_kwargs
        )

    def resample_sum(self, resample_kwargs, *sum_args, **sum_kwargs):
        return self._resample_pushdown_agg(
            GROUPBY_FUNCTIONS.SUM, resample_kwargs, sum_args, sum_kwargs
        )

    def resample_mean(self, resample_kwargs, *mean_args, **mean_kwargs):
        return self._resample_pushdown_agg(
            GROUPBY_FUNCTIONS.MEAN, resample_kwargs, mean_args, mean_kwargs
        )

    def resample_median(self, resample_kwargs, *median_args, **median_kwargs):
        return self._resample_pushdown_agg(
            GROUPBY_FUNCTIONS.MEDIAN, resample_kwargs, median_args, median_kwargs
        )

    def resample_std(self, resample_kwargs, ddof=1, *std_args, **std_kwargs):
        std_kwargs["ddof"] = ddof
        return self._resample_pushdown_agg(
            GROUPBY_FUNCTIONS.STD, resample_kwargs, std_args, std_kwargs
        )

    def resample_var(self, resample_kwargs, ddof=1, *var_args, **var_kwargs):
        var_kwargs["ddof"] = ddof
        return self._resample_pushdown_agg(
            GROUPBY_FUNCTIONS.VAR, resample_kwargs, var_args, var_kwargs
        )

    def resample_count(self, resample_kwargs, *count_args, **count_kwargs):
        return self._resample_pushdown_agg(
            GROUPBY_FUNCTIONS.COUNT, resample_kwargs, count_args, count_kwargs
        )

    def resample_sem(self, resample_kwargs, ddof=1, *sem_args, **sem_kwargs):
        sem_kwargs["ddof"] = ddof
        return self._resample_pushdown_agg(
            GROUPBY_FUNCTIONS.SEM, resample_kwargs, sem_args, sem_kwargs
        )

    def resample_prod(self, resample_kwargs, *prod_args, **prod_kwargs):
        return self._resample_pushdown_agg(
            GROUPBY_FUNCTIONS.PROD, resample_kwargs, prod_args, prod_kwargs
        )

    def resample_quantile(
        self, resample_kwargs, q=0.5, *quantile_args, **quantile_kwargs
    ):
        quantile_kwargs["q"] = q
        return self._resample_pushdown_agg(
            GROUPBY_FUNCTIONS.QUANTILE,
            resample_kwargs,
            quantile_args,
            quantile_kwargs,
        )

    def resample_nunique(self, resample_kwargs, *nunique_args, **nunique_kwargs):
        # Resample nunique excludes nulls
        nunique_kwargs["dropna"] = True
        return self._resample_pushdown_agg(
            GROUPBY_FUNCTIONS.NUNIQUE,
            resample_kwargs,
            nunique_args,
            nunique_kwargs,
        )

    def resample_size(self, resample_kwargs, *size_args, **size_kwargs):
        return self._resample_pushdown_agg(
            GROUPBY_FUNCTIONS.SIZE,
            resample_kwargs,
            None,
            None,
        )

    def resample_first(self, resample_kwargs, *first_args, **first_kwargs):
        return self._resample_pushdown_agg(
            GROUPBY_FUNCTIONS.FIRST, resample_kwargs, first_args, first_kwargs
        )

    def resample_last(self, resample_kwargs, *last_args, **last_kwargs):
        return self._resample_pushdown_agg(
            GROUPBY_FUNCTIONS.LAST, resample_kwargs, last_args, last_kwargs
        )

    def resample_asfreq(self, resample_kwargs, *asfreq_args, **asfreq_kwargs):
        return self._resample_pushdown_agg(
            GROUPBY_FUNCTIONS.ASFREQ, resample_kwargs, asfreq_args, asfreq_kwargs
        )

    def resample_ohlc_ser(self, resample_kwargs, *ohlc_args, **ohlc_kwargs):
        # Ensure only numeric types per pandas behavior
        resample_obj = self.getitem_column_array(
            [
                self.columns[i]
                for i in range(len(self.dtypes))
                if is_numeric_dtype(self.dtypes.iloc[i])
            ]
        )
        if len(resample_obj.columns) == 0:
            raise make_exception(
                TypeError,
                PonderError.RESAMPLE_OLHC_SERIES_NO_NUMERIC_COLUMNS,
                "resample() cannot be performed against 'object' dtypes!",
            )
        # Calculate open, high, low, close
        res_open = resample_obj.resample_first(copy.deepcopy(resample_kwargs))
        res_high = resample_obj.resample_max(copy.deepcopy(resample_kwargs))
        res_low = resample_obj.resample_min(copy.deepcopy(resample_kwargs))
        res_close = resample_obj.resample_last(copy.deepcopy(resample_kwargs))
        # Change column names inplace
        res_open.columns = ["open"]
        res_high.columns = ["high"]
        res_low.columns = ["low"]
        res_close.columns = ["close"]
        # Aggregate columns into dataframe
        return res_open.concat(
            axis=1,
            other=[res_high, res_low, res_close],
        )

    def resample_ohlc_df(self, resample_kwargs, *ohlc_args, **ohlc_kwargs):
        # TODO: Implement after supporting multi-column indexing
        raise make_exception(
            NotImplementedError,
            PonderError.RESAMPLE_OLHC_DATAFRAME_NOT_IMPLEMENTED,
            "resample.ohlc() on DataFrames not yet supported",
        )

    def resample_fillna(
        self, resample_kwargs, method, limit, *fillna_args, **fillna_kwargs
    ):
        # For all downsampling operations, fillna simply calls "asfreq"
        return self.resample_asfreq(resample_kwargs)

    def resample_get_group(
        self, resample_kwargs, name, obj, *get_group_args, **get_group_kwargs
    ):
        if obj is not None:
            raise make_exception(
                NotImplementedError,
                PonderError.RESAMPLE_GET_GROUP_OBJ_NOT_IMPLEMENTED,
                "resample().get_group() with obj != None is not supported yet",
            )
        get_group_kwargs["name"] = name
        get_group_kwargs["obj"] = obj
        return self._resample_pushdown_agg(
            GROUPBY_FUNCTIONS.GET_GROUP,
            resample_kwargs,
            get_group_args,
            get_group_kwargs,
        )

    def asfreq(self, freq, method, how, normalize, fill_value):
        # Sort implicitly to mimic pandas behavior
        resample_obj = self.sort_index()
        return resample_obj.__constructor__(
            resample_obj._dataframe.resample(
                operator=GROUPBY_FUNCTIONS.ASFREQ,
                rule=freq,
                agg_args=None,
                agg_kwargs=None,
            )
        )

    def first(self, offset: pandas.DateOffset):
        if not isinstance(self.index, DBMSDateTimeIndex):
            raise make_exception(
                TypeError,
                PonderError.FIRST_ONLY_SUPPORTS_DATETIMEINDEX,
                "'first' only supports a DatetimeIndex index",
            )
        return self.__constructor__(
            self._dataframe.filter_rows(
                RowWiseFilterPredicates.DatesWithinOffsetOfMin(self.index.name, offset)
            )
        )

    def last(self, offset: pandas.DateOffset):
        if not isinstance(self.index, DBMSDateTimeIndex):
            raise make_exception(
                TypeError,
                PonderError.LAST_ONLY_SUPPORTS_DATETIMEINDEX,
                "'last' only supports a DatetimeIndex index",
            )
        return self.__constructor__(
            self._dataframe.filter_rows(
                RowWiseFilterPredicates.DatesWithinOffsetOfMax(self.index.name, offset)
            )
        )

    def memory_usage(self, index=True, deep=False):
        connection = self._dataframe._query_tree._conn
        column_names = self._dataframe.columns.array.tolist()
        all_column_names = (["Index"] if index else []) + column_names
        all_column_types = [np.int64] * len(all_column_names)
        sql_query = connection.generate_memory_usage(all_column_names)
        from ponder.core.io import DBMSIO

        new_qc = DBMSIO._from_raw_sql(
            connection,
            sql_query,
            all_column_names,
            all_column_types,
            "Index" if index else __PONDER_ORDER_COLUMN_NAME__,
        )
        new_dataframe = new_qc._dataframe.rename(
            new_row_labels=["__reduced__"],
            new_row_labels_names=[__UNNAMED_INDEX_COLUMN__],
        )
        new_qc._dataframe = new_dataframe
        return new_qc

    def reindex(
        self,
        axis: int,
        labels: Any,
        method: Optional[str] = None,
        level: Any = None,
        fill_value: Any = np.nan,
        limit: Optional[int] = None,
        tolerance: Optional[int] = None,
    ) -> "DBMSQueryCompiler":
        """Align QueryCompiler data with a new index along specified axis.

        Parameters
        ----------
        axis : {0, 1}
            Axis to align labels along. 0 is for index, 1 is for columns.
        labels : pandas.Series
            Index-labels to align with.
        method : {None, "backfill"/"bfill", "pad"/"ffill", "nearest"}
            Method to use for filling holes in reindexed frame.
        level : int or name
            Broadcast across a level, matching Index values on the passed MultiIndex
            level.
        fill_value : scalar
            Value to use for missing values in the resulted frame.
        limit : int
            Maximum number of consecutive elements to forward or backward fill.
        tolerance : int

        Returns
        -------
        DBMSQueryCompiler
            QueryCompiler with aligned axis.
        """
        if method is not None:
            raise make_exception(
                NotImplementedError,
                PonderError.REINDEX_METHOD_NOT_IMPLEMENTED,
                "reindex() with non-None method is not supported yet",
            )
        if level is not None:
            raise make_exception(
                NotImplementedError,
                PonderError.REINDEX_LEVEL_NOT_IMPLEMENTED,
                "reindex() with non-None level is not supported yet",
            )
        if not np.isnan(fill_value):
            raise make_exception(
                NotImplementedError,
                PonderError.REINDEX_FILL_VALUE_NOT_IMPLEMENTED,
                "reindex() with fill_value != np.nan is not supported yet",
            )
        if limit is not None:
            raise make_exception(
                NotImplementedError,
                PonderError.REINDEX_LIMIT_NOT_IMPLEMENTED,
                "reindex() with limit != None is not supported yet",
            )
        if tolerance is not None:
            raise make_exception(
                NotImplementedError,
                PonderError.REINDEX_TOLERANCE_NOT_IMPLEMENTED,
                "reindex() with tolerance != None is not supported yet",
            )
        if is_scalar(labels):
            raise make_exception(
                TypeError,
                PonderError.REINDEX_SCALAR_LABELS_INVALID,
                "Index(...) must be called with a collection of some kind, 'invalid' "
                + "was passed",
            )
        if axis == 0:
            if not isinstance(labels, (DBMSIndex, DBMSPositionMapping)):
                raise make_exception(
                    NotImplementedError,
                    PonderError.REINDEX_AXIS_0_ONLY_SUPPORTS_DBMS_INDEX,
                    "Cannot reindex on axis=0 with anything other than modin.pandas "
                    + "indexes",
                )
            return self.__constructor__(self._dataframe.reindex_rows(labels))
        return self.__constructor__(self._dataframe.reindex_columns(labels))

    def compare(
        self,
        other: "DBMSQueryCompiler",
        align_axis: int,
        keep_shape: bool,
        keep_equal: bool,
        result_names: tuple,
    ) -> "DBMSQueryCompiler":
        """Compare data of two QueryCompilers and highlight the difference.

        Parameters
        ----------
        other : DBMSQueryCompiler
            Query compiler to compare with. Has to be the same shape and the same
            labeling as `self`.
        align_axis : {0, 1}
        keep_shape : bool
        keep_equal : bool
        result_names: tuple
            Set the dataframes names in the comparison.

        Returns
        -------
        BaseQueryCompiler
            New QueryCompiler containing the differences between `self` and passed
            query compiler.
        """
        if not (self.columns.equals(other.columns) and self.index.equals(other.index)):
            # TODO(https://github.com/modin-project/modin/issues/5699): Remove this
            # workaround once the issue is fixed at API layer.
            raise make_exception(
                ValueError,
                PonderError.COMPARE_DIFFERENT_LABELS,
                "Can only compare identically-labeled objects",
            )
        if keep_shape:
            raise make_exception(
                NotImplementedError,
                PonderError.COMPARE_KEEP_SHAPE_NOT_IMPLEMENTED,
                "compare() with keep_shape=True is not supported yet",
            )
        if keep_equal:
            raise make_exception(
                NotImplementedError,
                PonderError.COMPARE_KEEP_EQUAL_NOT_IMPLEMENTED,
                "compare() with keep_equal=True is not supported yet",
            )
        if align_axis != 1:
            raise make_exception(
                NotImplementedError,
                PonderError.COMPARE_ALIGN_AXIS_NOT_IMPLEMENTED,
                "compare() with align_axis!=1 is not supported yet",
            )
        if result_names != ("self", "other"):
            raise make_exception(
                NotImplementedError,
                PonderError.COMPARE_RESULT_NAMES_NOT_IMPLEMENTED,
                "compare() with custom `result_names` is not supported yet",
            )
        # We assume that `other` has same row and column labels as self. API layer
        # should take care of that.
        # Have to use to_pandas() or similar to eagerly figure out which columns are in
        # the final result. There's no other way to build the result dataframe, since
        # we don't know the column names till we do the comparison.
        comparison_columns = [
            c
            # nulls are equal in compare(), but not in eq() or ==
            for c, all_equal in self._equal_null(other)
            .all()
            .to_pandas()
            .squeeze(axis=0)
            .items()
            if not all_equal
        ]
        return self.__constructor__(
            dataframe=self.getitem_column_array(comparison_columns)._dataframe.compare(
                other.getitem_column_array(comparison_columns)._dataframe
            )
        )

    def melt(
        self,
        id_vars,
        value_vars,
        var_name,
        value_name,
        col_level,
        ignore_index: bool,
    ) -> "DBMSQueryCompiler":
        """Unpivot a ``DataFrame`` from wide to long format, optionally leaving
        identifiers set.

        Parameters
        ----------
        id_vars : tuple, list, or ndarray
            Column(s) to use as identifier variables.
        value_vars : tuple, list, or ndarray
            Column(s) to unpivot.
        var_name : scalar
            Name to use for the 'variable' column.
        value_name : scalar
            Broadcast across a level, matching Index values on the passed MultiIndex
            level.
        col_level : int or str
            If columns are a MultiIndex then use this level to melt.
        ignore_index : bool
            Maximum number of consecutive elements to forward or backward fill.
        tolerance : int

        Returns
        -------
        DBMSQueryCompiler
            QueryCompiler with unpivoted DataFrame.
        """

        if col_level:
            raise make_exception(
                NotImplementedError,
                PonderError.MELT_COL_LEVEL_NOT_IMPLEMENTED,
                "melt() with col_level != None is not supported yet",
            )

        intermediate_qcs = []
        for value_var in value_vars:
            # Seems like pandas just skips over these cases
            if value_var in id_vars:
                continue
            # We are going to call it and create it for every value variable
            intermediate_qcs.append(
                self.__constructor__(
                    self._dataframe.melt(
                        id_vars=id_vars,
                        value_var=value_var,
                        var_name=var_name,
                        value_name=value_name,
                        col_level=col_level,
                        ignore_index=ignore_index,
                    )
                )
            )

        result = intermediate_qcs[0].concat(
            0, intermediate_qcs[1:], ignore_index=ignore_index
        )
        new_columns = [
            *id_vars,
            *(c for c in result.columns if c not in id_vars),
        ]
        return result.getitem_column_array(new_columns)

    def _replace_all(self, value) -> "DBMSQueryCompiler":
        return self.__constructor__(self._dataframe._replace_all(value))

    def shift(
        self,
        periods: int,
        freq: Optional[Frequency],
        axis,
        fill_value: Hashable,
    ) -> "DBMSQueryCompiler":
        """Shift QueryCompiler by desired number of periods with an optional
        time `freq`.

        Parameters
        ----------
        periods : int
            Number of periods to shift. Can be positive or negative.
        freq : DateOffset, tseries.offsets, timedelta, or str, optional
            Offset to use from the tseries module or time rule (e.g. 'EOM').
            If freq is specified then the index values are shifted but the data
            is not realigned. That is, use freq if you would like to extend the
            index when shifting and preserve the original data.
        axis : {0, 1}
            Shift direction.
        fill_value : Any
            The scalar value to use for newly introduced missing values.

        Returns
        -------
        BaseQueryCompiler
            New QueryCompiler containing shifted data.
        """
        if axis != 0:
            raise make_exception(
                NotImplementedError,
                PonderError.SHIFT_AXIS_1_NOT_IMPLEMENTED,
                "shift() with axis=1 is not supported yet",
            )
        if freq is not None:
            result = self.copy()
            # note that this requires an inefficient join with the new index
            result.index = self.index.shift(periods, freq)
            return result
        filled_df = (
            self.take_2d_positional(
                # work around bug where getting RangeIndex(number_bigger_than_df_length)
                # adds new rows.
                index=pandas.RangeIndex(min(abs(periods), len(self.index)))
            )._replace_all(fill_value)
            # astype() to work around bug: converting time column to null changes dtype
            # to None and we get None in pandas df instead of pd.NaT.
            .astype(dict(self.dtypes))
        )

        # getting an empty dataframe is buggy and too hard to fix, so skip the concat
        # in this case and just return filled_df.
        if abs(periods) >= len(self.index):
            return filled_df

        return (
            filled_df.concat(
                axis=0,
                other=self.take_2d_positional(
                    pandas.RangeIndex(start=0, stop=len(self.index) - periods)
                ),
                ignore_index=True,
            )
            if periods >= 0
            else self.take_2d_positional(
                index=pandas.RangeIndex(start=-periods, stop=len(self.index))
            ).concat(
                axis=0,
                other=filled_df,
                ignore_index=True,
            )
        )

    def apply(
        self,
        func,
        axis=0,
        raw=False,
        result_type=None,
        args=(),
        **kwargs,
    ):
        if result_type:
            raise make_exception(
                NotImplementedError,
                PonderError.APPLY_RESULT_TYPE_NOT_IMPLEMENTED,
                "apply() with result_type != None is not supported yet",
            )
        if raw:
            raise make_exception(
                NotImplementedError,
                PonderError.APPLY_RAW_NOT_IMPLEMENTED,
                "apply() with raw != None is not supported yet",
            )

        if sys.version_info.major == 3 and sys.version_info.minor != 8:
            version = ".".join(map(str, sys.version_info[:3]))
            warnings.warn(
                f"current Python version is {version}, but expected 3.8. User defined"
                + " functions may not work as expected due to compatibility issues."
            )

        warnings.warn(
            "apply() support only includes third-party packages pandas, numpy, and "
            + "modin. Using other third-party packages will result in ProgrammingError."
        )

        # Ignore the warning message here because we just use to_pandas to get the
        # output metadata
        output_pandas_df = self.to_pandas(ignore_warning=True).apply(
            func,
            axis,
            args=args,
            raw=raw,
            result_type=result_type,
            **kwargs,
        )

        # output_meta is the result of apply called on the first 10,000 rows of
        # the dataframe. We need this information so that we can determine the
        # output schema and we handle this in the client so that we don't execute
        # arbitrary functions in the pushdown service. It still might be possible
        # to run bad code in the snowflake UDTF.
        return self.__constructor__(
            self._dataframe.apply(
                func=cloudpickle.dumps(func, protocol=pickle.DEFAULT_PROTOCOL),
                axis=axis,
                raw=raw,
                result_type=result_type,
                output_meta=output_pandas_df,
                apply_type=APPLY_FUNCTION.ROW_WISE,
                na_action=None,
                func_args=args,
                func_kwargs=kwargs,
            )
        )

    def applymap(self, func, na_action=None, output_meta=None, **kwargs):
        if sys.version_info.major == 3 and sys.version_info.minor != 8:
            version = ".".join(map(str, sys.version_info[:3]))
            warnings.warn(
                f"current Python version is {version}, but expected 3.8. User defined"
                + " functions may not work as expected due to compatibility issues."
            )

        warnings.warn(
            "apply() support only includes third-party packages pandas, numpy, and "
            + "modin. Using other third-party packages will result in ProgrammingError."
        )

        # output_meta is the result of apply called on the first 10,000 rows of
        # the dataframe. We need this information so that we can determine the
        # output schema and we handle this in the client so that we don't execute
        # arbitrary functions in the pushdown service. It still might be possible
        # to run bad code in the snowflake UDTF.
        return self.__constructor__(
            self._dataframe.apply(
                func=cloudpickle.dumps(func, protocol=pickle.DEFAULT_PROTOCOL),
                axis=1,
                raw=False,
                result_type=None,
                output_meta=self.to_pandas().applymap(
                    func, na_action=na_action, **kwargs
                ),
                apply_type=APPLY_FUNCTION.ELEMENT_WISE,
                na_action=na_action,
                func_args=(),
                func_kwargs=kwargs,
            )
        )

    def cut(
        self,
        bins,
        right,
        labels,
        retbins,
        precision,
        include_lowest,
        duplicates,
        ordered,
    ):
        if not right:
            raise make_exception(
                NotImplementedError,
                PonderError.CUT_RIGHT_FALSE_NOT_IMPLEMENTED,
                "cut() with right=False is not supported yet",
            )
        if np.iterable(bins):
            bins = np.array(bins)
        else:
            # forked from pandas implementation of cut(). alternatively, to avoid
            # materializing min() and max() in separate queries, we could use
            # WIDTH_BUCKET in snowflake, but then we'd have to extract the interval
            # values in addition to the bucketing from snowflake.
            # TODO: pandas cut() works by
            # converting the pandas series to numpy and using some numpy methods.
            # Implement those methods in modin.numpy and use more of the pandas cut()
            # implementation.
            if is_scalar(bins) and bins < 1:
                raise make_exception(
                    ValueError,
                    PonderError.CUT_BINS_LESS_THAN_1,
                    "`bins` should be a positive integer.",
                )

            sz = len(self.index)

            if sz == 0:
                raise make_exception(
                    ValueError,
                    PonderError.CUT_EMPTY_ARRAY,
                    "Cannot cut empty array",
                )

            rng = (self.min().to_pandas().iloc[0, 0], self.max().to_pandas().iloc[0, 0])
            mn, mx = (mi + 0.0 for mi in rng)

            if np.isinf(mn) or np.isinf(mx):
                # GH 24314
                raise make_exception(
                    ValueError,
                    PonderError.CUT_INF,
                    "cannot specify integer `bins` when input data contains infinity",
                )
            elif mn == mx:  # adjust end points before binning
                mn -= 0.001 * abs(mn) if mn != 0 else 0.001
                mx += 0.001 * abs(mx) if mx != 0 else 0.001
                bins = np.linspace(mn, mx, bins + 1, endpoint=True)
            else:  # adjust end points after binning
                bins = np.linspace(mn, mx, bins + 1, endpoint=True)
                adj = (mx - mn) * 0.001  # 0.1% of the range
                if right:
                    bins[0] -= adj
                else:
                    bins[-1] += adj
        if labels is not None and len(labels) != len(bins) - 1:
            raise make_exception(
                ValueError,
                PonderError.CUT_LABELS_LENGTH_LABELS_LENGTH_MISMATCH,
                "Bin labels must be one fewer than the number of bin edges",
            )
        return self.__constructor__(
            self._dataframe.cut(bins, labels, precision, right, include_lowest)
        )

    def stack(self, level, dropna):
        if level != -1:
            raise make_exception(
                NotImplementedError,
                PonderError.STACK_LEVEL_NOT_MINUS_1_NOT_IMPLEMENTED,
                "stack() with level != -1 is not supported yet",
            )

        if isinstance(self.index, DBMSPositionMapping):
            # A little hacky, but this is what pandas defaults to
            names = ["index"]
        elif isinstance(self.index, DBMSIndex):
            names = self.index.names

        cols = self.columns

        # stack is equivalent to doing df.melt() - we just need to do some extra
        # metadata/index manipulation. This currently works well when the columns
        # don't have a multiindex, but may need to be changed when we do support
        # multiindex columns.
        melt_qc = (
            self.reset_index()
            .melt(
                id_vars=names,
                value_vars=cols,
                var_name="",
                value_name=__PONDER_REDUCED_COLUMN_NAME__,
                col_level=0,
                ignore_index=False,
            )
            .sort_rows_by_column_values(columns=names[0], ascending=True)
            .set_index_from_columns(names + [""])
        )

        if dropna:
            return melt_qc.dropna(how="any", thresh=None)
        else:
            return melt_qc

    def unstack(self, level, fill_value):
        level = level if is_list_like(level) else [level]
        cols = self.columns
        index_cols = list(self.index.names)

        # Check to see if we have a MultiIndex, if we do, make sure we remove
        # the appropriate level(s), and we pivot accordingly.
        if len(index_cols) > 1:
            pivot_cols = [index_cols[lev] for lev in level]
            index_cols = [
                index_cols[i] for i in range(len(index_cols)) if i not in level
            ]
            vals = [
                c for c in self.columns if c not in index_cols and c not in pivot_cols
            ]
            res_qc = self.reset_index().pivot(
                index=index_cols,
                columns=pivot_cols,
                values=vals,
                add_qualifier_to_new_column_names=False,
            )
        else:
            # N.B. normally non-MultiIndex cases would throw an error in pandas
            # for series objects. However, pandas seems to handle this for DFs
            # by doing a transposed stack! Strange behavior, but since we throw
            # an error in the modin API layer for Series without MultiIndex indices,
            # we can assume that this must be a DataFrame. This assumption might
            # change in the future, so this code should be changed along with it.
            if isinstance(self.index, DBMSPositionMapping):
                # A little hacky, but this is what pandas defaults to
                names = ["index"]
            elif isinstance(self.index, DBMSIndex):
                names = self.index.names

            cols = self.columns

            res_qc = (
                self.reset_index()
                .melt(
                    id_vars=names,
                    value_vars=cols,
                    var_name="",
                    value_name=__PONDER_REDUCED_COLUMN_NAME__,
                    col_level=0,
                    ignore_index=False,
                )
                .set_index_from_columns([""] + names)
            )

        # Do something for the fill_value
        if fill_value:
            res_qc = res_qc.fillna(
                squeeze_self=None, squeeze_value=None, value=fill_value
            )
        return res_qc

    def pct_change(self, periods, fill_method, limit, freq, **kwargs):
        if freq:
            raise make_exception(
                NotImplementedError,
                PonderError.PCT_CHANGE_FREQ_NOT_IMPLEMENTED,
                "pct_change with freq != None is not supported yet",
            )
        if kwargs:
            raise make_exception(
                NotImplementedError,
                PonderError.PCT_CHANGE_KWARGS_NOT_IMPLEMENTED,
                "Any extra kwargs for pct_change() are passed to DataFrame/Series.shift. Please see:"  # noqa: E501: line too long
                + " https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.pct_change.html"  # noqa: E501: line too long
                + " for more details. At this time, these kwargs are not yet supported",  # noqa: E501: line too long
            )

        # pandas internally calls its own shift method. We may need to do this as well
        # to support freq, but since this arg is optional, we will stick with the
        # naive implementation for now.
        if fill_method:
            filled_qc = self.fillna(None, None, method=fill_method, limit=limit)
        else:
            filled_qc = self

        return self.__constructor__(filled_qc._dataframe.pct_change(periods))

    def diff(self, periods, axis):
        if axis == 1:
            raise make_exception(
                NotImplementedError,
                PonderError.DIFF_AXIS_1_NOT_IMPLEMENTED,
                "diff() with axis=1 is not supported yet",
            )
        return self.__constructor__(self._dataframe.diff(periods, axis))

    def equals(self, other):
        if not isinstance(other, type(self)):
            raise make_exception(
                TypeError,
                PonderError.QUERY_COMPILER_EQUALS_NON_QUERY_COMPILER,
                "equal() should be called with two query compilers of same type, but "
                + f"got other of type {type(other).__name__}",
            )
        if not self.dtypes.equals(other.dtypes):
            # if dtypes are not equal, return false for every value in this dataframe.
            # _equal_null would raise a TypeError if a column has a string dtype in one
            # df and a numeric dtype in the other.
            return self._replace_all(False)
        return self._equal_null(other)

    @property
    def debug_vis(self):
        return self._dataframe.debug_vis
