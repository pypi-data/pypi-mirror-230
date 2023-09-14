from __future__ import annotations

from functools import reduce
from typing import Any, Optional

import numpy as np
import pandas
import pandas._libs.lib as lib
from pandas._libs.tslibs import to_offset
from pandas._typing import DtypeObj
from pandas.api.types import is_integer, is_list_like, is_scalar
from pandas.core.dtypes.common import needs_i8_conversion, pandas_dtype
from pandas.core.indexes.frozen import FrozenList

from ponder.core.error_codes import PonderError, make_exception

from .common import __PONDER_ORDER_COLUMN_NAME__, __PONDER_ROW_LABELS_COLUMN_NAME__


class DBMSIndex:
    # CAUTION: public methods of this class are exposed to users.
    _supports_partial_string_indexing = False

    def __init__(
        self,
        column_names: list[str],
        dtypes: list[DtypeObj],
        length,
        column_name_mappings=None,
    ):
        # np.int64 is a type, not a dtype 🤷‍♂️. need to accept both `type` and
        # `np.dtype`
        # for each dtype.

        # TODO: Remove these type checks once mypy enforces types.
        if not isinstance(column_names, list) or not all(
            isinstance(c, str) for c in column_names
        ):
            raise make_exception(
                ValueError,
                PonderError.INDEX_INIT_WITH_INVALID_COLUMN_NAMES,
                f"Initializing DBMSIndex with invalid column_names {column_names}",
            )

        if not isinstance(dtypes, list):
            raise make_exception(
                TypeError,
                PonderError.INDEX_INIT_WITH_INVALID_DTYPES,
                f"Initializing DBMSIndex with invalid dtypes {dtypes}",
            )

        if len(column_names) != len(dtypes):
            raise make_exception(
                ValueError,
                PonderError.INDEX_INIT_COLUMN_NAMES_DTYPES_LENGTH_MISMATCH,
                f"column_names {column_names} and dtypes {dtypes} must have same "
                + "length",
            )

        # TODO: column_names is exposed to users. Make it internal and use an accessor
        # to get column names.
        self.column_names = column_names

        self._column_name_mappings = column_name_mappings

        # Use pandas_dtype to convert strings, etc to valid pandas dtypes
        # This will also throw an error if the dtype is not valid.
        self._dtypes = [pandas_dtype(d) for d in dtypes]
        self.length = length

        # Properties which are queried lazily
        self._is_monotonic_increasing = False
        self._is_monotonic_decreasing = False
        self._monotonic_set = False
        self._hasnans = False
        self._hasnans_set = False

        if len(column_names) > 1:
            # Multiindex name is None by default.
            self._multiindex_name = None

    def get_database_column_name(self, dataframe_column_name):
        if self._column_name_mappings is None:
            return dataframe_column_name
        return self._column_name_mappings.get_db_name_from_df_name(
            dataframe_column_name
        )

    def get_dataframe_column_name(self, database_column_name):
        if self._column_name_mappings is None:
            return database_column_name
        return self._column_name_mappings.get_df_name_from_db_name(database_column_name)

    def get_db_to_df_map(self):
        return self._column_name_mappings

    def get_index_database_column_names(self):
        if self._column_name_mappings is None:
            return self.column_names
        return self._column_name_mappings.get_database_names_from_dataframe_names(
            self.column_names
        )

    def _ponder_set_pandas_index_names(self, names: Any):
        """Set the pandas names of this index.

        These are the names that we'll give the index when we convert to
        pandas. They are not necessarily the same as the names of the
        columns in the underlying dataframe. They are not necessarily
        strings.
        """
        self._ponder_pandas_index_names = names

    def _is_memory_usage_qualified(self):
        return True

    def __len__(self):
        return self.length

    def get_indexer_for(self, locs):
        raise make_exception(
            NotImplementedError,
            PonderError.INDEX_GET_INDEXER_FOR_NOT_IMPLEMENTED,
            "Ponder internal error: get_indexer_for not implemented for DBMSIndex",
        )

    # hasnan is lazily computed when the property
    # index.hasnan is accessed. If not already
    # calculated the _do_nan_check function will
    # be called to create a single-column dataframe
    # to execute .isna().any() on. The result of this
    # will be a single cell dataframe containing the
    # boolean result.
    def _do_nan_check(self):
        from .query_compiler import DBMSQueryCompiler

        # A suffix is added to the result column to
        # eliminate collisions between a new, default
        # index and the result column
        compiler_for_check = (
            DBMSQueryCompiler(self._dataframe)
            .reset_index()
            .getitem_column_array(key=self.column_names)
            .add_suffix("_RESULT")
        )
        self._hasnans = compiler_for_check.isna().any().to_numpy()[0][0]
        self._hasnans_set = True

    def _ponder_get_hasnans(self):
        if not self._hasnans_set:
            self._do_nan_check()
        return self._hasnans

    hasnans = property(_ponder_get_hasnans)

    # is_monotonic_increasing and decreasing is
    # calcuated when the property is accessed.
    # this function will create a a small dataframe
    # representing the index to call the
    # monotonic functions and retrieve the value from
    # the current cell. One improvement to this
    # might be to execute a single query to
    # check for increasing and decreasing monotonicity
    # at the same time
    def _do_monotonic_check(self):
        from .query_compiler import DBMSQueryCompiler

        compiler_for_check = (
            DBMSQueryCompiler(self._dataframe)
            .reset_index()
            .getitem_column_array(key=self.column_names)
        )
        self._is_monotonic_decreasing = False
        self._is_monotonic_increasing = (
            compiler_for_check._dataframe.is_monotonic_increasing()
            .to_pandas()
            .loc[1]["MONOTONIC_RESULT"]
        )
        if not self._is_monotonic_increasing:
            self._is_monotonic_decreasing = (
                compiler_for_check._dataframe.is_monotonic_decreasing()
                .to_pandas()
                .loc[1]["MONOTONIC_RESULT"]
            )

        # A check for monotonic can also set hasnans
        if self._is_monotonic_increasing or self._is_monotonic_decreasing:
            self._hasnans = False
            self._hasnans_set = True

        self._monotonic_set = True

    # Optimization for setting monotonic state when we sort by the index
    # column. This optimization is only applied if we know there are no
    # nans in the index, since determining that does have some cost.
    def _ponder_set_sort_state(self, sorted, ascending):
        if self._hasnans_set and not self.hasnans:
            self._is_monotonic_increasing = sorted and ascending
            self._is_monotonic_decreasing = sorted and not ascending
            self._monotonic_set = True

    def _ponder_get_monotonic_increasing(self):
        if not self._monotonic_set:
            self._do_monotonic_check()
        return self._is_monotonic_increasing

    def _ponder_get_monotonic_decreasing(self):
        if not self._monotonic_set:
            self._do_monotonic_check()
        return self._is_monotonic_decreasing

    is_monotonic_increasing = property(_ponder_get_monotonic_increasing)
    is_monotonic_decreasing = property(_ponder_get_monotonic_decreasing)

    def _ponder_dtypes_list(self) -> list[DtypeObj]:
        """End users use this index, so make clear this is an internal method.

        Return dtypes as a list, even if there is only one column in the
        index. We need this because MultiIndex has dtypes but single
        column indexes do not.
        """
        return self._dtypes

    @property
    def dtype(self):
        if len(self.column_names) > 1:
            # multiindex always has "object" dtype
            return np.dtype("O")
        return self._dtypes[0]

    @property
    def dtypes(self):
        if len(self.column_names) == 1:
            # not quite same as pandas error, which is like
            # "'Float64Index' object has no attribute 'dtypes'", but we don't have the
            # index type at hand.
            raise make_exception(
                AttributeError,
                PonderError.INDEX_WITH_ONE_COLUMN_HAS_NO_DTYPES,
                f"Index of type {self._dtypes[0]} has no attribute 'dtypes'",
            )
        return pandas.Series(self._dtypes, index=self.column_names, dtype="object")

    @property
    def nlevels(self):
        return len(self.column_names)

    def copy(self, name=None, deep=False, same_column_names_in_qt_df=False):
        if deep:
            raise make_exception(
                NotImplementedError,
                PonderError.INDEX_COPY_DEEP_NOT_IMPLEMENTED,
                "Index.copy with `deep=True` is not implemented.",
            )
        new_index = type(self)(
            self.column_names,
            self._dtypes,
            self.length,
            self.get_db_to_df_map() if same_column_names_in_qt_df is False else None,
        )
        if hasattr(self, "_ponder_pandas_index_names"):
            new_index._ponder_pandas_index_names = self._ponder_pandas_index_names
        if hasattr(self, "_dataframe"):
            new_index._dataframe = self._dataframe.copy()
        if name is not None:
            new_index.set_names(name, inplace=True)
        return new_index

    def _ponder_get_name(self):
        if len(self.column_names) == 1:
            return self.column_names[0]
        return self._multiindex_name

    def _ponder_set_names(self, names):
        if not is_list_like(names):
            raise make_exception(
                ValueError,
                PonderError.INDEX_INTERNAL_SET_NAMES_NON_LIST_LIKE,
                "Names must be a list-like",
            )
        if len(names) != len(self.column_names):
            raise make_exception(
                ValueError,
                PonderError.INDEX_INTERNAL_SET_NAMES_WRONG_LENGTH,
                f"Length of new names must be {len(self.column_names)}, "
                f"but got {len(names)}",
            )
        if all(isinstance(name, str) for name in names):
            new_column_names = names
        else:
            # TODO(https://ponderdata.atlassian.net/browse/POND-833): this is an
            # incomplete workaround for the fact that we can't have non-string column
            # names. we'll keep some incorrect placeholder names around, then replace
            # them with the correct names when we convert to pandas.
            self._ponder_pandas_index_names = names
            new_column_names = [
                f"{__PONDER_ROW_LABELS_COLUMN_NAME__}{i}" for i in range(len(names))
            ]
        # 1) reset the index
        # 2) rename the former index column
        # 3) set the index to the renamed index column
        with_new_index = (
            self._dataframe.from_labels(drop=False)
            .rename(
                new_col_labels=[*new_column_names, *list(self._dataframe.columns)],
            )
            .to_labels([*new_column_names])
        )
        # TODO(REFACTOR): Find a way to do the inplace update that's less brittle
        # than updating private fields of the dataframe.
        self._dataframe._query_tree = with_new_index._query_tree
        self._dataframe._row_positions_cache = with_new_index._row_positions_cache
        self._dataframe._column_labels_cache = with_new_index._column_labels_cache
        self._dataframe._column_types_cache = with_new_index._column_types_cache
        self._dataframe._db_df_column_name_mappings = (
            with_new_index._db_df_column_name_mappings
        )
        self._column_name_mappings = with_new_index.index._column_name_mappings
        self._dataframe._row_labels_cache = self
        self.column_names = new_column_names

    def _ponder_set_name(self, name):
        if len(self.column_names) > 1:
            self._multiindex_name = name
        else:
            self.names = [name]

    name = property(_ponder_get_name, _ponder_set_name)

    def _ponder_get_names(self) -> FrozenList[str]:
        return FrozenList(self.column_names)

    names = property(_ponder_get_names, _ponder_set_names)

    def set_names(self, names, level=None, inplace=False):
        if not inplace:
            new_index = self.copy()
            new_index.set_names(names, level=level, inplace=True)
            return new_index
        if level is None:
            names = [names] if isinstance(names, str) else names
            self.names = names
        else:
            if isinstance(level, int):
                list_names = self._ponder_get_names()
                list_names[level] = names
                self.names = list_names
            elif is_list_like(level) and all([isinstance(lev, int) for lev in level]):
                list_names = self._ponder_get_names()
                for lev, name in zip(level, names):
                    list_names[lev] = name
                self.names = list_names
            else:
                wrong_type = type(level[0]) if is_list_like(level) else type(level)
                raise make_exception(
                    TypeError,
                    PonderError.INDEX_SET_NAMES_LEVEL_PARAM_WRONG_TYPE,
                    f"objects of type {wrong_type} not supported for level argument.",
                )

    def __getitem__(self, item):
        # this is supposed to be able to take slices.
        # TODO: consider how to replicate iloc-like range-based indexing for slices
        # without duplicating too much code. can take slices and negative numbers.
        if is_scalar(item):
            if not (is_integer(item) and item >= 0):
                raise make_exception(
                    NotImplementedError,
                    PonderError.DBMS_INDEX_GETITEM_NOT_A_POSITIVE_INTEGER,
                    "Ponder Internal Error: can only support positive integer key "
                    + f"for __getitem__ on DMBSIndex. Got {item} of type "
                    + f"{type(item).__name__}",
                )
            if item not in range(len(self)):
                raise make_exception(
                    IndexError,
                    PonderError.DBMS_INDEX_GETITEM_OUT_OF_BOUNDS,
                    f"index {item} is out of bounds for axis 0 with size {len(self)}",
                )
            # we converted scalar to a list. pandas returns a scalar from calls
            # like index[0], but a list of length 1 from index[[0]]. Match that
            # behavior.
            result = self._get_pandas_index_at_row_positions([item])
            return result[0]
        if isinstance(item, list) and all(is_integer(i) and i >= 0 for i in item):
            # be careful to return another DBMSIndex, not a pandas index!
            return self._dataframe.mask(row_positions=item, col_positions=[0]).index
        raise make_exception(
            NotImplementedError,
            PonderError.DBMS_INDEX_GETITEM_UNSUPPORTED_TYPE,
            "Ponder Internal Error: can only support nonnegative integer or list "
            + "of nonnegative integers key for __getitem__ on DMBSIndex. "
            + f"Got {item} of type {type(item).__name__}",
        )

    def __ge__(self, other):
        from .query_compiler import DBMSQueryCompiler

        return (
            DBMSQueryCompiler(self._dataframe)
            .reset_index()
            .getitem_column_array(key=self.column_names[0])
            .ge(other)
            .to_pandas()[self.column_names[0]]
            .array
        )

    def __le__(self, other):
        from .query_compiler import DBMSQueryCompiler

        return (
            DBMSQueryCompiler(self._dataframe)
            .reset_index()
            .getitem_column_array(key=self.column_names[0])
            .le(other)
            .to_pandas()[self.column_names[0]]
            .array
        )

    def _to_datetime(self, **kwargs):
        from .query_compiler import DBMSQueryCompiler

        index_qc = (
            DBMSQueryCompiler(self._dataframe)
            .reset_index()
            .getitem_column_array(key=self.column_names)
        )
        if not all(d == str for d in self._dtypes):
            index_qc = index_qc.astype({col: "str" for col in self.column_names})
        new_index = (
            index_qc.to_datetime(**kwargs)
            .set_index_from_columns(self.column_names)
            .index
        )
        return new_index

    def _to_pandas(self) -> pandas.Index:
        return self._get_pandas_index_at_row_positions(row_positions=None)

    # signature copied from Pandas.Index
    def to_frame(self, index=True, name=lib.no_default):
        return self._get_pandas_index_at_row_positions(row_positions=None).to_frame(
            index, name
        )

    def _get_pandas_index_at_row_positions(self, row_positions: Optional[list[int]]):
        # TODO: add a method to the dataframe that masks just the index columns. No
        # need to even select data column 0.
        return (
            self._dataframe.mask(row_positions=row_positions, col_positions=[])
            .to_pandas()
            .index
        )

    def __repr__(self):
        # Throughout this method, we only care about the index, so we select 0 data
        # columns along with the (implicitly always selected) index columns from the
        # frame, convert to pandas, and get the index of the result.
        col_positions = []
        # We will only print the first and last 10 index values
        if len(self) <= 20:
            return repr(
                self._dataframe.mask(col_positions=col_positions).to_pandas().index
            )
        first = repr(
            self._dataframe.mask(
                row_positions=list(range(10)), col_positions=col_positions
            )
            .to_pandas()
            .index
        )
        second = repr(
            self._dataframe.mask(
                row_positions=list(range(self.length - 10, self.length)),
                col_positions=col_positions,
            )
            .to_pandas()
            .index
        )
        # This will tell us how many spaces we need to move over for the values
        # in the index
        spaces = "".join([" " for _ in second.split("[")[0]])
        # We need to add the dots and the length here since we don't get those
        # for free
        return (
            f"{first.split('],')[0]},\n {spaces}...\n {spaces}"
            + "".join(second.split("[")[1:])[:-1]
            + f", length={len(self)})"
        )

    def _summary(self, name=None) -> str:
        """Return a summarized representation.

        Parameters
        ----------
        name : str
            name to use in the summary representation

        Returns
        -------
        String with a summarized representation of the index
        """
        # this code is adapted from pandas.core.indexes.base._summary
        if len(self) > 0:
            if len(self) == 1:
                # BUG: probably would be a bug with iloc[[5, 5]], too-- slecting the
                # same position only gives one row because we translate to "WHERE
                # ROW_NUMBER IN (5, 5)". work around tha by selectin just one row and
                # duplicating it.
                pandas_index = self._get_pandas_index_at_row_positions([0])
                head, tail = pandas_index[0], pandas_index[0]
            else:
                pandas_index = self._get_pandas_index_at_row_positions(
                    [0, len(self) - 1]
                )
                head, tail = pandas_index[0], pandas_index[1]
            if hasattr(head, "format") and not isinstance(head, str):
                head = head.format()
            elif needs_i8_conversion(self.dtype):
                # e.g. Timedelta, display as values, not quoted
                head = pandas_index._formatter_func(head).replace("'", "")
            if hasattr(tail, "format") and not isinstance(tail, str):
                tail = tail.format()
            elif needs_i8_conversion(self.dtype):
                # e.g. Timedelta, display as values, not quoted
                tail = pandas_index._formatter_func(tail).replace("'", "")

            index_summary = f", {head} to {tail}"
        else:
            index_summary = ""

        if name is None:
            if isinstance(self, DBMSDateTimeIndex):
                name = "DatetimeIndex"
            elif len(self.column_names) > 1:
                name = "MultiIndex"
            # There are more exotic index types. Give "index" for now. "Index" is what
            # we get for an index on strings.
            else:
                name = "Index"
        return f"{name}: {len(self)} entries{index_summary}"

    def equals(self, other):
        from .query_compiler import DBMSQueryCompiler

        if isinstance(other, DBMSPositionMapping):
            raise make_exception(
                NotImplementedError,
                PonderError.DBMS_INDEX_EQUALS_DBMS_POSITION_MAPPING_NOT_IMPLEMENTED,
                "Ponder Internal Error: cannot use equals() to compare "
                + "DBMSIndex to DBMSPositionMapping.",
            )
        if not isinstance(other, DBMSIndex):
            return False
        if self.column_names != other.column_names:
            return False
        # Use the query compiler's ability to do equals() on two dataframes. It will
        # compare data columns but not row labels columns, so first reset index on each
        # dataframe, then select the former row labels columns and compare them.
        compiler_for_self = (
            DBMSQueryCompiler(self._dataframe)
            .reset_index()
            .getitem_column_array(key=self.column_names)
        )
        compiler_for_other = (
            DBMSQueryCompiler(other._dataframe)
            .reset_index()
            .getitem_column_array(key=other.column_names)
        )
        # give the row labels columns new names for comparison. This works around what's
        # probably an internal bug in a case where the index column name is
        # _PONDER_ROW_LABELS_ -- EquiJoinNode always adds _PONDER_ROW_LABELS_ as row
        # labels column name, but if _PONDER_ROW_LABELS_ is also the column name we're
        # comparing, we get an ambiguous column name error.
        compiler_for_self.columns = compiler_for_other.columns = [
            f"index_equals_{i}" for i in range(len(self.column_names))
        ]
        equals_pandas_df: pandas.DataFrame = (
            compiler_for_self.eq(compiler_for_other).all(axis=0).all(axis=1).to_pandas()
        )
        assert equals_pandas_df.shape == (1, 1)
        return equals_pandas_df.iloc[0, 0]

    @property
    def is_unique(self) -> bool:
        raise make_exception(
            NotImplementedError,
            PonderError.DBMS_INDEX_IS_UNIQUE_NOT_IMPLEMENTED,
            "is_unique not implemented for DBMSIndex",
        )

    def __contains__(self, key):
        if len(self.column_names) == 1 and is_list_like(key):
            # this isn't quite right because you can have a mutliindex with a single
            # level, in which case a key like (2,) should be valid, but I don't want
            # to go through the trouble of creating a reproducer.
            return False

        # easier to work with a query compiler than to work with self._dataframe
        from .query_compiler import DBMSQueryCompiler

        compiler_with_index_reset = DBMSQueryCompiler(self._dataframe).reset_index()
        keys = key if is_list_like(key) else [key]

        # if the types are not compatible, e.g. checking if a string is in an int
        # index, we should return false. the most convenient way to do that is to
        # try the comparison and catch any resulting TypeError. Ideally we'd have
        # a utility to check dtype compatibility for comparison, but the code for that
        # is part of BinaryPredicate and not very easily reusable. This approach is also
        # not too different from what pandas does, e.g. here is some code for MultiIndex
        # __contains__:
        # https://github.com/pandas-dev/pandas/blob/29f949980170ada984ebf02770356f1d28b980ff/pandas/core/indexes/multi.py#L1241-L1247
        try:
            return (
                len(
                    compiler_with_index_reset.getitem_array(
                        reduce(
                            DBMSQueryCompiler.__and__,
                            [
                                compiler_with_index_reset.getitem_column_array(
                                    key=[column]
                                )._equal_null(value)
                                for column, value in zip(
                                    self.column_names[: len(keys)], keys
                                )
                            ],
                        )
                    ).index
                )
                > 0
            )
        except TypeError:
            return False

    def to_series(self, index=None, name=None):
        if index is not None:
            raise make_exception(
                NotImplementedError,
                PonderError.DBMS_INDEX_TO_SERIES_INDEX_NOT_IMPLEMENTED,
                "Ponder Internal Error: to_series with index not implemented",
            )
        if name is not None:
            raise make_exception(
                NotImplementedError,
                PonderError.DBMS_INDEX_TO_SERIES_NAME_NOT_IMPLEMENTED,
                "Ponder Internal Error: to_series with name not implemented",
            )
        if len(self.column_names) > 1:
            # to_series on multi-level index returns a tuple for each row. That's a lot
            # of extra work to implement.
            raise make_exception(
                NotImplementedError,
                PonderError.DBMS_INDEX_TO_SERIES_MULTIPLE_LEVELS_NOT_IMPLEMENTED,
                "Ponder Internal Error: to_series with multiple levels not "
                + "implemented",
            )
        # TODO: maybe we should move DBMSIndex to the API layer so we don't have to do
        # this cyclic import multiple times?
        import modin.pandas as pd

        from ponder.core.query_compiler import DBMSQueryCompiler

        # TODO: We are basically doing df.set_index(drop=False), which we haven't
        # implemented yet. The efficient way to do that would be to select
        # self.column_names[0] twice and make one of the columns an index column.
        # However, we start hitting a few bugs if we do that because the query tree
        # assumes in many places that all the column names in the databse are unique.
        # For now, use a join to set the index of the new frame to a copy of this index.
        frame = pd.DataFrame(
            query_compiler=DBMSQueryCompiler(self._dataframe)
        ).reset_index()[self.column_names[0]]
        frame.name = "__PONDER_INDEX_TO_SERIES"
        frame.index = self.copy()
        frame.name = self.column_names[0]
        return frame

    def get_level_values(self, level):
        if isinstance(level, str) and level not in self.column_names:
            raise make_exception(
                KeyError,
                PonderError.DBMS_INDEX_GET_LEVEL_VALUES_LEVEL_NOT_FOUND,
                f"Level {level} not found",
            )
        column_names = [self.column_names[level]] if isinstance(level, int) else [level]
        return self._dataframe.from_labels(drop=False).to_labels(column_names).index


class DBMSDateTimeIndex(DBMSIndex):
    _supports_partial_string_indexing = True

    def __init__(
        self,
        column_names: list[str],
        dtypes: list[DtypeObj],
        length,
        freq,
        column_name_mappings=None,
    ):
        super().__init__(column_names, dtypes, length, column_name_mappings)
        self.freq = freq

    def shift(self, periods=1, freq=None) -> "DBMSDateTimeIndex":
        if freq is None:
            if self.freq is None:
                raise make_exception(
                    ValueError,
                    PonderError.DBMS_INDEX_SHIFT_NO_FREQ,
                    "Cannot shift with no freq",
                )
            freq = self.freq
        elif isinstance(freq, str):
            freq = to_offset(freq)
        # this is a circular import. usually we should not use circular imports, but
        # it's easier to work with a query compiler than to use self._dataframe
        from .query_compiler import DBMSQueryCompiler

        return (
            DBMSQueryCompiler(self._dataframe)
            .reset_index()
            .getitem_column_array([self.name])
            .add(freq * periods)
            .set_index_from_columns(keys=[self.name], drop=True)
            .index
        )

    def copy(self, name=None, deep=False, same_column_names_in_qt_df=False):
        if deep:
            raise make_exception(
                NotImplementedError,
                PonderError.DBMS_DATETIME_INDEX_COPY_DEEP_NOT_IMPLEMENTED,
                "DBMSDateTimeIndex.copy not implemented for `deep=True`.",
            )
        new_index = type(self)(
            self.column_names,
            self._dtypes,
            self.length,
            self.freq,
            self._column_name_mappings if same_column_names_in_qt_df is False else None,
        )
        if hasattr(self, "_dataframe"):
            new_index._dataframe = self._dataframe.copy()
        if name is not None:
            new_index.set_names(name, inplace=True)
        return new_index


# A 1D numpy compatible array implementation
# representing a range of True values in
# a sea of False.
# TODO: If we can return this as a subclass
# of ndarray it will be much more efficient,
# but this would require a fully compatible
# implementation using the sparse representation.
# https://numpy.org/doc/stable/user/basics.dispatch.html
class bool_range_array:
    def __init__(self, size, start, stop):
        self._size = size
        self._start = start
        self._stop = stop

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(N={self._size},"
            f"start={self._start}, start={self._stop})"
        )

    # Called when numpy operations are performed on this object
    def __array__(self, dtype=None):
        return np.concatenate(
            (
                np.repeat([False], self._start),
                np.repeat([True], self._stop - self._start),
                np.repeat([False], self._size - self._stop),
            )
        )

    def __contains__(self, key):
        if isinstance(key, str):
            try:
                key_for_superclass = pandas.Timestamp(key)
            except Exception:
                return False
        else:
            key_for_superclass = key
        return super().__contains__(key_for_superclass)


# TODO: Split DBMSPositionMapping into a DMBSRangeIndex and DBMSPositionMapping
# to allow for optimizations in .loc
class DBMSPositionMapping:
    # CAUTION: public methods of this class are exposed to users.
    name = __PONDER_ORDER_COLUMN_NAME__

    def __init__(self, positions, is_reset=False, true_labels=None):
        assert isinstance(positions, pandas.Index), "Incorrect positions mapping type"
        assert true_labels is None or isinstance(
            true_labels, pandas.Index
        ), "Incorrect true labels type"
        self.position_map = positions
        self.is_reset = is_reset
        # This value is set when the index is reset, we want to maintain the mapping
        # but also need to maintain the new labels.
        self.true_labels = true_labels

    def copy(self, name=None, deep=False):
        if deep:
            raise make_exception(
                ValueError,
                PonderError.DBMS_POSITION_MAPPING_COPY_DEEP_NOT_IMPLEMENTED,
                "DBMSPositionMapping.copy not implemented for `deep=True`.",
            )
        new_index = type(self)(self.position_map, self.is_reset, self.true_labels)
        if hasattr(self, "_dataframe"):
            new_index._dataframe = self._dataframe.copy()
        if name is not None:
            new_index.set_names(name, inplace=True)
        return new_index

    def __getitem__(self, item):
        if is_scalar(item):
            return self.position_map[item]
        if isinstance(item, slice) and isinstance(self.position_map, pandas.RangeIndex):
            start_pos = (
                self.position_map.start
                if item.start is None
                else self.position_map.start + item.start
            )
            stop_pos = (
                self.position_map.stop
                if item.stop is None
                else self.position_map.start + item.stop + 1
            )
            new_pos_map = pandas.RangeIndex(start_pos, stop_pos)
        else:
            item = np.array(item)
            if len(item) == 1 and isinstance(self.position_map, pandas.RangeIndex):
                try:
                    new_pos_map = self.position_map[item]
                except IndexError:
                    raise make_exception(
                        KeyError,
                        PonderError.DBMS_POSITION_MAPPING_GETITEM_KEY_ERROR,
                        str(item),
                    )
            is_range = all(prev - cur == 1 for cur, prev in zip(item[:-1], item[1:]))
            if is_range and isinstance(self.position_map, pandas.RangeIndex):
                if len(item) > 0:
                    new_pos_map = pandas.RangeIndex(
                        self.position_map.start + item[0],
                        self.position_map.start + item[-1] + 1,
                    )
                else:
                    new_pos_map = pandas.Index([])
            elif isinstance(self.position_map, pandas.RangeIndex):
                new_pos_map = pandas.Index([self.position_map.start + i for i in item])
            else:
                new_pos_map = self.position_map[item]
        if self.is_reset:
            new_true_mapping = self.true_labels[item]
        else:
            new_true_mapping = None
        return DBMSPositionMapping(
            new_pos_map,
            is_reset=self.is_reset,
            true_labels=new_true_mapping,
        )

    def __ge__(self, other):
        if not is_integer(other):
            raise make_exception(
                TypeError,
                PonderError.DBMS_POSITION_MAPPING_GE_INVALID_COMPARISON,
                str(other),
            )
        range = self[other:]
        # We return a standard ndarray here for compatibility. Ideally we would return
        # a subclass which is sparse; but that will require more work.
        return bool_range_array(
            len(self.position_map), range.start, range.stop
        ).__array__()

    def __le__(self, other):
        if not is_integer(other):
            raise make_exception(
                TypeError,
                PonderError.DBMS_POSITION_MAPPING_LE_INVALID_COMPARISON,
                str(other),
            )
        range = self[:other]
        # We return a standard ndarray here for compatibility. Ideally we would return
        # a subclass which is sparse; but that will require more work.
        return bool_range_array(
            len(self.position_map), range.start, range.stop
        ).__array__()

    def _to_pandas(self) -> pandas.Index:
        return self.true_labels if self.is_reset else self.position_map

    def reset(self):
        return DBMSPositionMapping(
            self.position_map,
            is_reset=True,
            true_labels=pandas.RangeIndex(len(self.position_map)),
        )

    def is_true_labels(self):
        return (
            self.position_map[0] == 0
            and isinstance(self.position_map, pandas.RangeIndex)
            and self.position_map.step == 1
        )

    @property
    def type(self):
        return np.dtype("int64")

    def __getattr__(self, item):
        # TODO: we need to make sure that this works, but that we don't have unintended
        # consequences when returning non-DBMSPositionMapping objects.
        if item == "get_type":
            return np.dtype("int64")
        return self.position_map.__getattribute__(item)

    def __repr__(self):
        return repr(self.position_map)

    def __len__(self):
        return len(self.position_map)

    def _ponder_dtypes_list(self):
        return [np.dtype(self.position_map.dtype)]

    def equals(self, other: Any) -> bool:
        if isinstance(other, DBMSIndex):
            raise make_exception(
                NotImplementedError,
                PonderError.DBMS_POSITION_MAPPING_EQUALS_DBMS_INDEX_NOT_IMPLEMENTED,
                "Ponder Internal Error: cannot use equals() to compare "
                + "DBMSPositionMapping to DBMSIndex.",
            )
        if not isinstance(other, DBMSPositionMapping):
            return False
        return self._to_pandas().equals(other._to_pandas())

    def get_indexer_for(self, locs) -> np.ndarray[np.intp]:
        return self.position_map.get_indexer_for(locs)
