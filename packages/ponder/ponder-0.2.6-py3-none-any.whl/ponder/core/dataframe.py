from __future__ import annotations

import itertools
import logging
from typing import Dict, Hashable, Iterable, List, Optional, Union

import numpy as np
import pandas
from modin.core.dataframe.base.dataframe.utils import Axis
from modin.pandas.utils import check_both_not_none
from pandas._libs.tslibs import to_offset
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_datetime64tz_dtype,
    is_dict_like,
    is_list_like,
)
from pandas.core.dtypes.cast import find_common_type
from pandas.core.dtypes.common import is_categorical_dtype, is_scalar

from ponder.core.dataframequerytreehelper import (
    DBDFColumnNameMapping,
    copy_index_with_qt_df_having_same_column_names,
    generate_add_compare_post_join_columns,
    generate_dataframe_names_from_database_names,
    generate_join_schema,
    generate_merge_asof_schema,
    generate_new_db_column_name,
    get_column_names_and_types_from_query_tree,
    get_dataframe_column_names_for_pivot,
    get_renamed_query_tree_with_df_column_names,
    replace_dtype_column_names,
    replace_map_with_database_columns,
    replace_multi_index_column_names,
)
from ponder.core.error_codes import PonderError, make_exception

from .common import (
    __ISIN_DATAFRAME_LEFT_PREFIX__,
    __ISIN_DATAFRAME_RIGHT_PREFIX__,
    __ISIN_SERIES_VALUES_COLUMN_NAME__,
    __PONDER_AGG_OTHER_COL_ID__,
    __PONDER_AGG_OTHER_COL_NAME__,
    __PONDER_ORDER_COLUMN_NAME__,
    __PONDER_REDUCED_COLUMN_NAME__,
    __PONDER_ROW_LABELS_COLUMN_NAME__,
    __PONDER_STORED_PROC_ROW_LABEL_COLUMN_NAME__,
    __UNNAMED_INDEX_COLUMN__,
    GROUPBY_FUNCTIONS,
    MAP_FUNCTION,
    REDUCE_FUNCTION,
    ByParams,
    MapFunction,
    groupby_view_funcs,
)
from .index import DBMSDateTimeIndex, DBMSIndex, DBMSPositionMapping
from .query_tree import (
    BinaryComparisonNode,
    NewRowLabelsColumnsNode,
    RowWiseFilterPredicates,
)
from .sql_dialect import _pandas_offset_object_to_seconds

logger = logging.getLogger(__name__)


def _get_categories_from_snowflake_object(
    cat_object, col_type: pandas.CategoricalDtype
):
    if not isinstance(cat_object, dict):
        return None
    # For categorical data, we store a category json object in snowflake like
    # {"_ponder_category": 3}, where the category value is the index of the category in
    # the list of categories. If the index is -1, then the value doesn't match one of
    # the categories, and we return NaN as pandas does.
    category_index = cat_object["_ponder_category"]
    if category_index == -1:
        return float("nan")
    return col_type.categories[cat_object["_ponder_category"]]


class DBMSDataframe(object):
    # Need some global connection object

    def __init__(
        self,
        query_tree,
        new_column_labels=None,
        new_row_labels=None,
        new_dtypes=None,
        new_row_positions=None,
    ):
        # maybe prefetch some metadata
        logger.debug(f"""DBMSDataframe init new_column_labels {new_column_labels}""")
        if new_column_labels is not None:
            self._column_labels_cache = pandas.Index(new_column_labels)
        else:
            self._column_labels_cache = new_column_labels
        self._database_column_labels_cache = None
        self._column_types_cache = new_dtypes
        self._db_df_column_name_mappings = DBDFColumnNameMapping(
            new_column_labels,
            query_tree.get_column_names(),
            query_tree._conn.case_insensitive_identifiers(),
            query_tree._conn.case_fold_identifiers(),
        )

        if isinstance(new_row_labels, DBMSIndex) and new_row_positions is None:
            assert new_column_labels is not None, "Columns must be set to proceed"
            # TODO: If multiindex this will need to be handled slightly
            # differently
            if new_row_labels.column_names == [__PONDER_ORDER_COLUMN_NAME__]:
                # This code path gets hit whenever we did a data-dependent
                # filter and still have the default row labels. Since we
                # want to keep them around, we implicitly create a new row
                # number column and keep the old column under the name
                # __PONDER_ROW_LABELS_COLUMN_NAME__.
                keep_old_row_numbers = True
                if new_row_labels.length is None:
                    length = query_tree.get_num_rows()
                    new_row_labels.length = length
                else:
                    length = len(new_row_labels)
                self._row_labels_cache = DBMSIndex(
                    [__PONDER_ROW_LABELS_COLUMN_NAME__],
                    [np.int64],
                    length,
                    self._db_df_column_name_mappings,
                )
            else:
                keep_old_row_numbers = False
                if new_row_labels.length is None:
                    length = query_tree._conn.get_num_rows(query_tree)
                    new_row_labels.length = length
                self._row_labels_cache = new_row_labels
            self._query_tree = query_tree.generate_row_numbers(
                keep_old_row_numbers=keep_old_row_numbers,
            )
            self._row_positions_cache = DBMSPositionMapping(
                pandas.RangeIndex(len(new_row_labels))
            )
        else:
            self._query_tree = query_tree
            self._row_labels_cache = new_row_labels
            self._row_positions_cache = new_row_positions

    # Metadata

    _column_labels_cache = None  # mutable!
    _column_types_cache = None  # mutable!
    _row_labels_cache = None  # mutable!
    _row_positions_cache = None  # mutable!
    _database_column_labels = None  # mutable!
    _database_types_cache = None  # mutable!

    def get_db_column_name(self, col_name):
        db_col_name = self._db_df_column_name_mappings.get_db_name_from_df_name(
            col_name
        )
        if db_col_name == col_name:
            if isinstance(self.index, DBMSIndex):
                return self.index.get_database_column_name(col_name)
        return db_col_name

    def get_df_column_name(self, col_name):
        return self._db_df_column_name_mappings.get_df_name_from_db_name(col_name)

    def get_db_to_df_map(self):
        return self._db_df_column_name_mappings

    def get_query_tree(self):
        return self._query_tree

    def _get_column_labels(self):
        """Set column labels cache if unset, then return labels."""
        if self._column_labels_cache is None:
            # compute columns
            column_label_list = self._query_tree.get_column_names()
            column_type_list = self._query_tree.get_column_types()
            self._column_labels_cache = pandas.Index(column_label_list)
            self._column_types_cache = pandas.Series(
                column_type_list, index=self._column_labels_cache, dtype=object
            )
        return self._column_labels_cache

    def _get_column_types(self):
        """Set column types cache if unset, then return types."""
        if self._column_types_cache is None:
            # compute columns
            column_label_list = self._query_tree.get_column_names()
            column_type_list = self._query_tree.get_column_types()
            self._column_labels_cache = pandas.Index(column_label_list)
            self._column_types_cache = pandas.Series(
                column_type_list, index=self._column_labels_cache, dtype=object
            )
        if not isinstance(self._column_types_cache, pandas.Series):
            assert isinstance(
                self._column_types_cache, list
            ), "Invalid column types object"
            self._column_types_cache = pandas.Series(
                self._column_types_cache, index=self._column_labels_cache, dtype=object
            )
        return self._column_types_cache

    def _get_database_column_labels(self):
        """Set database column labels cache if unset, then return labels."""
        if self._database_column_labels_cache is None:
            self._database_column_labels_cache = pandas.Index(
                [self.get_db_column_name(col_name) for col_name in self.columns]
            )
        return self._database_column_labels_cache

    def _get_database_column_types(self):
        if self._database_types_cache is None:
            self._database_types_cache = replace_dtype_column_names(
                self.dtypes, self.database_columns
            )
        if not isinstance(self._database_types_cache, pandas.Series):
            assert isinstance(
                self._database_types_cache, list
            ), "Invalid column types object"
            self._database_types_cache = pandas.Series(
                self._database_types_cache,
                index=self._database_column_labels_cache,
                dtype=object,
            )
        return self._database_types_cache

    def _get_row_labels(self):
        """Set row labels cache if unset, then return labels."""
        if self._row_labels_cache is None:
            # compute row names
            length = self._query_tree.get_num_rows()
            self._row_labels_cache = DBMSPositionMapping(pandas.RangeIndex(0, length))
        self._row_labels_cache._dataframe = self
        return self._row_labels_cache

    columns = property(_get_column_labels)  # immutable!
    index = property(_get_row_labels)  # immutable!
    dtypes = property(_get_column_types)  # immutable!
    database_columns = property(_get_database_column_labels)
    database_dtypes = property(_get_database_column_types)

    @property
    def __constructor__(self):
        return type(self)

    def copy(self):
        return self.__constructor__(
            self._query_tree,
            self._column_labels_cache,
            self._row_labels_cache,
            self._column_types_cache,
            self._row_positions_cache,
        )

    # to/from pandas
    def to_pandas(self):
        pandas_df = self._query_tree.to_pandas()
        # convert categorical columns in both the index and the data from category
        # JSON objects to the actual category values.
        for col, col_type in itertools.chain(
            self.dtypes.items(),
            (
                zip(self.index.column_names, self.index._ponder_dtypes_list())
                if isinstance(self.index, DBMSIndex)
                else iter([])
            ),
        ):
            if is_categorical_dtype(col_type):
                db_col_name = self.get_db_column_name(col)
                pandas_df[db_col_name] = pandas_df[db_col_name].astype(col_type)

        if isinstance(self.index, DBMSPositionMapping):
            # the positions mappings won't match if we retrieve less than the full
            # complement of rows.
            if len(pandas_df) < self._query_tree.get_row_transfer_limit():
                if self.index.is_reset:
                    pandas_df.index = self.index.true_labels
                else:
                    pandas_df.index = self.index.position_map
        else:
            index_database_column_names = self.index.get_index_database_column_names()
            if all(item in pandas_df.columns for item in index_database_column_names):
                mapper = {}
                for i in range(len(pandas_df.columns)):
                    for j in range(len(index_database_column_names)):
                        if (
                            pandas_df.columns.values[i]
                            == index_database_column_names[j]
                        ):
                            mapper[
                                pandas_df.columns.values[i]
                            ] = self.index.column_names[j]
                            break
                if len(mapper) > 0:
                    pandas_df.rename(columns=mapper, inplace=True)
                pandas_df.set_index(self.index.column_names, inplace=True)
            # This doesn't happen very often, but there can be cases where the
            # dtype of the df read from Snowflake doesn't match our index dtype.
            # e.g. df.groupby(dropna=True) will drop null keys within our generated
            # query. When we read in the resulting dataframe, the index will have
            # an int64 dtype instead of the original float64 dtype.
            if isinstance(pandas_df.index, pandas.MultiIndex):
                pandas_df.index = replace_multi_index_column_names(
                    pandas_df.index,
                    self.index.get_db_to_df_map(),
                )
                new_level_types = []
                for level, t in zip(pandas_df.index.levels, self.index.dtypes):
                    # datetime64[ns] apparently cannot be "astyped" to datetime64.
                    if t == "datetime64" and str(level.dtype) == "datetime64[ns]":
                        new_level_types.append(level.astype("datetime64[ns]"))
                    else:
                        new_level_types.append(level.astype(t))
                pandas_df.index = pandas_df.index.set_levels(new_level_types)
            else:
                # datetime64[ns] apparently cannot be "astyped" to datetime64.
                if (
                    str(self.index.dtype) == "datetime64"
                    and str(pandas_df.index.dtype) == "datetime64[ns]"
                ):
                    pandas_df.index = pandas_df.index.astype("datetime64[ns]")
                elif is_datetime64tz_dtype(pandas_df.index.dtype) and (
                    is_datetime64_any_dtype(self.index.dtype)
                    and not is_datetime64tz_dtype(self.index.dtype)
                ):
                    # for upsampling we generate a tz-aware datetime64[ns] index with
                    # GENERATE_TIMESTAMP_ARRAY. We assume most of the time that bigquery
                    # timestamps are tz-naive, and our original index is tz-naive (at
                    # least in test cases). If we try to use astype() to convert the
                    # tz-aware new index to the tz-naive type of the original index,
                    # pandas 2.0+ raises raises TypeError and tells us to explicitly
                    # strip the timezone, e.g. with tz_localize(None).
                    # TODO: we should find a way to strip the timezone from
                    # GENERATE_TIMESTAMP_ARRAY. The timezones of the generated
                    # timestamps might not be consistent with those of the original
                    # data.
                    pandas_df.index = pandas_df.index.tz_localize(None)
                else:
                    pandas_df.index = pandas_df.index.astype(self.index.dtype)

            # Do not show internal names for index columns.
            pandas_df.index = pandas_df.index.set_names(
                [
                    None
                    if name == __PONDER_ROW_LABELS_COLUMN_NAME__
                    and not hasattr(self.index, "_ponder_pandas_index_names")
                    or name
                    in [
                        # TODO: Implement df.rename_axis() to avoid relying on the
                        # "index" label, which pandas uses as a label whenever a
                        # label-less index column is converted to a data column.
                        "index",
                        __PONDER_AGG_OTHER_COL_ID__,
                        __PONDER_AGG_OTHER_COL_NAME__,
                    ]
                    else name
                    for name in self.index.names
                ]
            )

            if isinstance(self.index, DBMSDateTimeIndex):
                try:
                    pandas_df.index.freq = self.index.freq
                except Exception:
                    pass

            if hasattr(self.index, "_ponder_pandas_index_names"):
                pandas_df.index.names = self.index._ponder_pandas_index_names
            elif (
                pandas_df.index.name is not None
                and __PONDER_ROW_LABELS_COLUMN_NAME__ in pandas_df.index.name
            ):
                # This is internal, no need to show it to the user
                pandas_df.index.name = None

        if __PONDER_ROW_LABELS_COLUMN_NAME__ in pandas_df.columns.array:
            if __PONDER_ROW_LABELS_COLUMN_NAME__ not in self.columns.array:
                if len(pandas_df.columns.array) > len(self.columns.array):
                    pandas_df = pandas_df.drop(
                        columns=__PONDER_ROW_LABELS_COLUMN_NAME__
                    )

        if __PONDER_ORDER_COLUMN_NAME__ in pandas_df.columns.array:
            if __PONDER_ORDER_COLUMN_NAME__ not in self.columns.array:
                if len(pandas_df.columns.array) > len(self.columns.array):
                    pandas_df = pandas_df.drop(columns=__PONDER_ORDER_COLUMN_NAME__)

        pandas_df = pandas_df[
            [self.get_db_column_name(col_name) for col_name in self.columns]
        ]
        pandas_df.columns = self.columns

        ret_val = pandas_df
        ret_val.columns.name = self.columns.name
        return ret_val

    def to_csv(self, **kwargs):
        new_query_tree = get_renamed_query_tree_with_df_column_names(self)
        new_query_tree.to_csv(
            path=kwargs["path_or_buf"],
            sep=kwargs["sep"],
            header=kwargs["header"],
            date_format=kwargs["date_format"],
            na_rep=kwargs["na_rep"],
        )

    def to_sql(
        self,
        name,
        con=None,
        schema=None,
        if_exists="fail",
        index=True,
        index_label=None,
        chunksize=None,
        dtype=None,
        method=None,
    ):
        new_query_tree = get_renamed_query_tree_with_df_column_names(self)
        new_query_tree.to_sql(
            table_name=name,
            row_labels_column_types=self.index._ponder_dtypes_list(),
            if_exists=if_exists,
            index=index,
            index_label=index_label,
        )

    # Querying and manipulating metadata

    def mask(
        self,
        row_labels: Optional[List[Hashable]] = None,
        row_positions: Optional[List[int]] = None,
        col_labels: Optional[List[Hashable]] = None,
        col_positions: Optional[List[int]] = None,
    ):
        if check_both_not_none(row_labels, row_positions):
            raise make_exception(
                Exception,
                PonderError.DATAFRAME_MASK_WITH_ROW_LABELS_AND_ROW_POSITIONS,
                "Internal error: both row_labels and row_positions were provided -"
                " please provide only one of row_labels and row_positions.",
            )
        if check_both_not_none(col_labels, col_positions):
            raise make_exception(
                Exception,
                PonderError.DATAFRAME_MASK_WITH_COL_LABELS_AND_COL_POSITIONS,
                "Internal error: both col_labels and col_positions were provided -"
                " please provide only one of col_labels and col_positions.",
            )

        # This is the column that will be used for the label-based filter
        # We are passed row_labels or row_positions, which will be applied
        # to the column name in this variable.
        column_names_for_filter = (
            [__PONDER_ORDER_COLUMN_NAME__]
            if isinstance(self.index, DBMSPositionMapping)
            else self.index.column_names
        )
        if all(
            lab is None
            for lab in [row_labels, row_positions, col_labels, col_positions]
        ):
            return self.copy()
        # Ensure that the mapping between a row mapping that has been reset is
        # still correct
        if (
            row_labels is not None
            and isinstance(self.index, DBMSPositionMapping)
            and (self.index.is_reset or self.index.is_true_labels())
        ):
            # swap these when labels and positions are interchangeable
            # this way, we can maintain our position mapping
            row_positions, row_labels = row_labels, row_positions
        # Ensure that the mapping between a row mapping that has been reset is
        # still correct
        if row_labels is not None and isinstance(self.index, DBMSDateTimeIndex):
            # if we have a time index, and the row labels are not timestamps,
            # convert them now.
            row_labels = list(
                map(
                    lambda label: label
                    if isinstance(label, pandas.Timestamp)
                    else pandas.to_datetime(label),
                    row_labels,
                )
            )

        if row_positions is not None:
            column_names_for_filter = [__PONDER_ORDER_COLUMN_NAME__]
            if isinstance(self.index, DBMSPositionMapping):
                # The index here is still a mapping between position and label,
                # so we keep it.
                new_row_labels = self.index[row_positions]
                final_position_cache = None  # this was None before
                # we will re-use the old row positions to avoid
                # re-materializing positions
                row_labels = new_row_labels.position_map
            else:
                # We have to create a new index and update the row position
                # cache
                if isinstance(self.index, DBMSDateTimeIndex):
                    new_row_labels = DBMSDateTimeIndex(
                        self.index.column_names,
                        self.index._ponder_dtypes_list(),
                        len(row_positions),
                        self.index.freq,
                        self.index.get_db_to_df_map(),
                    )
                else:
                    new_row_labels = DBMSIndex(
                        self.index.column_names,
                        self.index._ponder_dtypes_list(),
                        len(row_positions),
                        self.index.get_db_to_df_map(),
                    )
                if self._row_positions_cache is not None:
                    final_position_cache = self._row_positions_cache[row_positions]
                else:
                    final_position_cache = DBMSPositionMapping(
                        pandas.Index(row_positions)
                    )
                row_labels = final_position_cache.position_map
        elif row_labels is not None:
            # TODO: implement the selection here when we have positions that do
            if isinstance(self.index, DBMSPositionMapping):
                new_row_labels = DBMSIndex(
                    [__PONDER_ORDER_COLUMN_NAME__],
                    {__PONDER_ORDER_COLUMN_NAME__: __PONDER_ORDER_COLUMN_NAME__}[
                        np.int64
                    ],
                    len(row_labels),
                    self.get_db_to_df_map(),
                )
                final_position_cache = None
            else:
                # The new positions will be determined later, based on the resulting
                # order.
                # TODO: Can we avoid re-materializing these?
                final_position_cache = None

                if isinstance(self.index, DBMSDateTimeIndex):
                    new_row_labels = DBMSDateTimeIndex(
                        self.index.column_names,
                        self.index._ponder_dtypes_list(),
                        len(row_labels),
                        self.index.freq,
                        self.index.get_db_to_df_map(),
                    )
                else:
                    new_row_labels = DBMSIndex(
                        self.index.column_names,
                        self.index._ponder_dtypes_list(),
                        len(row_labels),
                        self.index.get_db_to_df_map(),
                    )
        else:
            # not filtering by rows at all, so positions are the same
            final_position_cache = self._row_positions_cache
            new_row_labels = self.index

        if col_labels is None and col_positions is None:
            col_labels_for_mask = None
        elif col_labels is not None:
            col_labels_for_mask = col_labels
        else:
            # TODO: We could use column positions to select columns in the SQL
            # query. That way we could defer materializing column metadata.
            col_labels_for_mask = self.columns[col_positions]
        database_column_names_for_filter = [
            self.get_db_column_name(column) for column in column_names_for_filter
        ]
        database_col_positions_for_mask = (
            [self.get_db_column_name(column) for column in col_labels_for_mask]
            if col_labels_for_mask is not None
            else None
        )
        result_tree = self._query_tree.add_mask(
            column_names_for_filter=database_column_names_for_filter,
            row_positions=row_labels,
            col_positions=database_col_positions_for_mask,
            order_column_name=__PONDER_ORDER_COLUMN_NAME__,
        )

        if col_labels_for_mask is None:
            new_column_labels = self._column_labels_cache
        else:
            new_column_labels = col_labels_for_mask

        # TODO: It might not be worth it to materialize column metadata to get
        # dtypes.
        if col_positions is not None:
            new_dtypes = self.dtypes.iloc[col_positions]
        elif col_labels is not None:
            new_dtypes = self.dtypes[col_labels]
        else:
            new_dtypes = self._column_types_cache
        return self.__constructor__(
            result_tree,
            new_row_labels=new_row_labels,
            new_column_labels=new_column_labels,
            new_dtypes=new_dtypes,
            new_row_positions=final_position_cache,
        )

    def setitem_scalar_broadcast(self, key, value):
        if not is_scalar(value):
            raise make_exception(
                RuntimeError,
                PonderError.DATAFRAME_SETITEM_SCALAR_BROADCAST_WITH_NON_SCALAR,
                "Internal error- query compiler setitem/insert should handle "
                + "non-scalar setitem broadcast",
            )
        result_tree = self._query_tree.add_literal_columns([key], [str], [value])
        df_column_names = [
            self.get_df_column_name(col_name)
            for col_name in result_tree.get_root().get_column_names()
        ]
        df_column_types = replace_dtype_column_names(
            result_tree.get_column_types(), df_column_names
        )
        return self.__constructor__(
            result_tree,
            new_column_labels=df_column_names,
            new_row_labels=self.index,
            new_dtypes=df_column_types,
            new_row_positions=self._row_positions_cache,
        )

    def binary_op_with_scalar(self, sql_infix, other, self_on_right):
        import decimal

        if isinstance(other, decimal.Decimal):
            other = float(other)
        result_tree = self._query_tree.add_binary_comparison(
            sql_infix, other, self.database_columns, self.database_dtypes, self_on_right
        )
        return self.__constructor__(
            result_tree,
            new_column_labels=self.columns,
            new_row_labels=self.index,
            new_dtypes=replace_dtype_column_names(
                result_tree.get_root().get_column_types(), self.columns
            ),
            new_row_positions=self._row_positions_cache,
        )

    def get_from_binary_comparison(self, other: BinaryComparisonNode):
        result_tree = self._query_tree.add_get_from_binary_comparison(other)
        if isinstance(self.index, DBMSPositionMapping):
            new_row_labels = DBMSIndex(
                [__PONDER_ORDER_COLUMN_NAME__],
                [np.int64],
                None,
                self.get_db_to_df_map(),
            )
        else:
            new_row_labels = DBMSIndex(
                self.index.column_names,
                self.index._ponder_dtypes_list(),
                None,
                self.index.get_db_to_df_map(),
            )
        return self.__constructor__(
            result_tree,
            new_column_labels=self._column_labels_cache,
            new_row_labels=new_row_labels,
            new_dtypes=self._column_types_cache,
            new_row_positions=None,
        )

    def from_labels(self, drop: bool):
        assert self._row_positions_cache is not None or isinstance(
            self.index, DBMSPositionMapping
        ), "Not yet supported for unmaterialized positions"
        if self._row_positions_cache is not None:
            assert isinstance(self.index, DBMSIndex), (
                "We currently only set row position cache when the labels are a column"
                " in the database"
            )

            index_column_names = self.index.column_names
            new_index = self._row_positions_cache.reset()

            # If we have a MultiIndex, we just need to make sure that they are in
            # the new_column_names and the new_dtypes.
            if drop:
                new_column_names = self.columns
                new_dtypes = self.dtypes
            else:
                new_column_names = pandas.Index(index_column_names).append(self.columns)
                new_dtypes = pandas.concat(
                    [
                        pandas.Series(
                            {
                                column_name: dtype
                                for column_name, dtype in zip(
                                    index_column_names, self.index._ponder_dtypes_list()
                                )
                            }
                        ),
                        self.dtypes,
                    ]
                )
            return self.__constructor__(
                self._query_tree.reset_row_labels_columns(
                    self.index._ponder_dtypes_list(), drop=drop, index_pos_map=False
                ),
                new_column_names,
                new_index,
                new_dtypes,
                new_row_positions=None,
            )

        # This is the case where we have DBMSPositionMapping
        new_index = self.index.reset()
        if drop:
            new_column_names = self.columns
            new_dtypes = self.dtypes
        else:
            # pandas just calls the new index as "index" and any other cols
            # as "level_0", "level_1". We are yet to handle that case
            # TODO: handle the naming of the position mapping intelligently
            new_column_names = pandas.Index(["index"]).append(self.columns)
            new_dtypes = pandas.concat(
                [pandas.Series({"index": self.index.dtype}), self.dtypes]
            )

        return self.__constructor__(
            self._query_tree.reset_row_labels_columns(
                self.index._ponder_dtypes_list(), drop=drop, index_pos_map=True
            ),
            new_column_names,
            new_index,
            new_dtypes,
            new_row_positions=None,
        )

    def index_to_labels(self, new_index):
        if new_index[0].column_names != self.index.column_names:
            raise make_exception(
                NotImplementedError,
                PonderError.DATAFRAME_INDEX_TO_LABELS_WITH_DIFFERENT_COLUMNS,
                "Setting a new index with different columns than the original is "
                + "not supported",
            )

        return self.__constructor__(
            self._query_tree,
            pandas.Index(self._column_labels_cache),
            new_index[0],
            self.dtypes,
            self._row_positions_cache,
        )

    def to_labels(self, column_list: List[Hashable]):
        new_row_positions_cache = (
            self._row_positions_cache
            if self._row_positions_cache is not None
            else self.index
        )
        # API layer should guarantee column_list is subset of columns.
        if len(column_list) == 1 and is_datetime64_any_dtype(
            self.dtypes[column_list[0]]
        ):
            new_row_labels = DBMSDateTimeIndex(
                column_list,
                list(self.dtypes[column_list]),
                len(self.index),
                None,
                self.get_db_to_df_map(),
            )
        else:
            new_row_labels = DBMSIndex(
                column_list,
                list(self.dtypes[column_list]),
                len(self.index),
                self.get_db_to_df_map(),
            )
        new_cols = [c for c in self._column_labels_cache if c not in column_list]
        new_dtypes = self.dtypes[new_cols]

        database_column_list = [
            self.get_db_column_name(col_name) for col_name in column_list
        ]

        return self.__constructor__(
            self._query_tree.add_row_labels_columns(None, database_column_list),
            pandas.Index(new_cols),
            new_row_labels,
            new_dtypes,
            new_row_positions_cache,
        )

    def filter_by_types(self, types: Union[type, str, List[type], List[str]]):
        if isinstance(types, str):
            types = getattr(np, types.lower())
        if not isinstance(types, list):
            types = [types]
        return self.mask(
            col_labels=self.dtypes[
                [
                    c
                    for c in self.columns
                    if any(issubclass(self.dtypes[c], t) for t in types)
                ]
            ].index
        )

    def rename(
        self,
        new_row_labels: Optional[Union[Dict[Hashable, Hashable], List]] = None,
        new_row_labels_names: Optional[list[str]] = None,
        new_col_labels: Optional[Union[Dict[Hashable, Hashable], List]] = None,
        new_col_labels_name: Optional[str] = None,
    ):
        if new_col_labels is not None:
            if new_row_labels_names is not None:
                raise make_exception(
                    NotImplementedError,
                    PonderError.DATAFRAME_RENAME_WITH_BOTH_NEW_ROW_LABELS_NAMES_AND_NEW_COL_LABELS,  # noqa: E501
                    "Internal error: dataframe rename with both new_row_labels_names "
                    + "and new_col_labels_names",
                )
            if is_list_like(new_col_labels) and not is_dict_like(new_col_labels):
                new_col_labels = list(new_col_labels)
            if isinstance(new_col_labels, list):
                assert len(new_col_labels) == len(
                    self.columns
                ), "Mismatched column lengths!"
                new_column_names = pandas.Index(new_col_labels)
                new_col_labels_dict = {
                    old: new for old, new in zip(self.columns, new_col_labels)
                }
            else:
                new_col_labels_dict = new_col_labels
                new_column_names = pandas.Index(new_col_labels_dict.values())
            if new_col_labels_name is not None:
                new_column_names.name = new_col_labels_name
            new_dtypes = self.dtypes.copy()
            new_dtypes.index = new_column_names
            if (
                isinstance(self.index, DBMSIndex)
                and len(self.index.column_names) == 1
                and self.index.name in new_col_labels_dict.values()
            ):
                # This is a hack for when we are renaming a column to the same name as
                # an index column. This scenario comes up in series groupby reductions,
                # e.g. groupby.size(), which is how value_counts() is implemented. In
                # this scenario, change the index name in the DB to
                # __PONDER_ROW_LABELS_COLUMN_NAME__, but keep the index aware of its
                # "true" name for the user. The new frame will behave incorrectly if we
                # try to drop the index with from_labels(), since we'll call the new
                # column __PONDER_ROW_LABELS_COLUMN_NAME__.
                # TODO(https://ponderdata.atlassian.net/browse/POND-753): Use a more
                # robust solution for duplicate column names.
                self.index._ponder_set_pandas_index_names([self.index.name])
                # When we update the index name, the index will change this dataframe's
                # index column name to __PONDER_ROW_LABELS_COLUMN_NAME__.

                self.index.name = __PONDER_ROW_LABELS_COLUMN_NAME__

            # if the columns are being renamed - update the query tree as well.
            # Otherwise you might end up with duplicates in the query tree layer and
            # that breaks in subtle ways.  It took Bala 12 hours of debugging to
            # figure out why
            # testindex.py's test_int_index_equals_int_index_in_different_order
            # was failing.
            new_database_column_names = [
                self._query_tree._conn.generate_sanitized_name(col_name)
                for col_name in new_column_names
            ]
            column_renames = {
                self._query_tree.get_column_names()[i]: new_database_column_names[i]
                for i in range(len(new_database_column_names))
            }
            new_query_tree = self._query_tree.add_column_rename(column_renames)
            return self.__constructor__(
                new_query_tree,
                new_column_names,
                self.index,
                new_dtypes,
                self._row_positions_cache,
            )
        if new_row_labels is not None:
            if is_list_like(new_row_labels):
                new_row_labels = list(new_row_labels)
            if isinstance(new_row_labels, list):
                new_row_labels = {i: label for i, label in enumerate(new_row_labels)}
            dtype = np.array([v for k, v in new_row_labels.items()]).dtype
            # TODO: Need to use the mapping object to get the correct join keys
            if new_row_labels_names is None:
                new_row_labels_names = [__UNNAMED_INDEX_COLUMN__]
            elif len(new_row_labels_names) != 1:
                raise make_exception(
                    NotImplementedError,
                    PonderError.DATAFRAME_RENAME_WITH_MULTIPLE_NEW_ROW_LABELS_NAMES,
                    "Can only rename with a single row label name, but got label "
                    + f"names {new_row_labels_names}",
                )
            return self.__constructor__(
                self._query_tree.add_row_labels_columns(
                    new_row_labels, new_row_labels_names
                ),
                new_column_labels=self.columns,
                new_row_labels=DBMSIndex(
                    new_row_labels_names,
                    [dtype],
                    len(new_row_labels),
                    self.get_db_to_df_map(),
                ),
                new_dtypes=self.dtypes,
                new_row_positions=self.index
                if isinstance(self.index, DBMSPositionMapping)
                else self._row_positions_cache,
            )
        raise make_exception(
            RuntimeError,
            PonderError.DATAFRAME_RENAME_WITH_BOTH_NEW_ROW_LABELS_AND_NEW_COL_LABELS,
            "Internal error: dataframe rename with new row labels and new column "
            + "labels both None",
        )

    # Dataframe data queries

    def rolling(
        self,
        axis: int,
        operator: str,
        window: int,
        non_numeric_cols,
        agg_args,
        agg_kwargs,
        win_type=None,
    ):
        # TODO: Only considering axis, operator, window, min_periods
        from .query_compiler import __WINDOW_AGGREGATE_MAP__

        if operator not in [
            "SUM",
            "AVG",
            "MIN",
            "MAX",
            "VARIANCE",
            "STDDEV",
            "COUNT",
            "SEM",
            "MEDIAN",
            "KURTOSIS",
            "SKEW",
            "CORR",
            "COV",
            "QUANTILE",
            "RANK",
            __WINDOW_AGGREGATE_MAP__,
        ]:
            raise make_exception(
                NotImplementedError,
                PonderError.DATAFRAME_ROLLING_OPERATOR_NOT_IMPLEMENTED,
                f"rolling() with operator {operator} is not supported yet",
            )

        if operator == __WINDOW_AGGREGATE_MAP__ and "func_map" not in agg_kwargs.keys():
            raise make_exception(
                TypeError,
                PonderError.DATAFRAME_ROLLING_FUNC_MAP_NOT_SET,
                f"""If operator {__WINDOW_AGGREGATE_MAP__},
                    func_map must be set in agg_kwargs""",
            )

        if operator in ["CORR", "COV"]:
            # The following loop generates an n^2 matrix where n is #columns. Each row
            # is generated using a separate query by taking one column at a time
            # (other_col_id), and computing its pairwise corr/cov with all the columns
            # (including itself). The final matrix is the concatenation of all rows.
            # Both the id and name of the "other" column are also included in each row -
            # to be later converted into an index. The id is kept only to sort rows such
            # that both rows and columns follow the same order. After sorting is done,
            # the id is dropped and only the name remains.
            df = None
            new_query_tree = get_renamed_query_tree_with_df_column_names(self)
            for other_col_id in range(len(self.columns)):
                intermediate_tree = new_query_tree.add_cumulative_function(
                    function=(
                        operator
                        if operator != __WINDOW_AGGREGATE_MAP__
                        else agg_kwargs["func_map"]
                    ),
                    columns=self.columns,
                    skipna=False,
                    window=window,
                    non_numeric_cols=non_numeric_cols,
                    other_col_id=other_col_id,
                )
                new_column_labels = intermediate_tree.get_column_names()

                new_dtypes = intermediate_tree.get_root().dtypes
                index_length = (
                    self.index.size
                    if isinstance(self.index, DBMSPositionMapping)
                    else self.index.length
                )
                new_row_labels = DBMSPositionMapping(
                    pandas.Index([i for i in range(index_length)])
                )
                intermediate_df = self.__constructor__(
                    intermediate_tree,
                    new_column_labels=new_column_labels,
                    new_row_labels=new_row_labels,
                    new_dtypes=new_dtypes,
                    new_row_positions=self._row_positions_cache,
                ).from_labels(drop=False)
                if df is None:
                    df = intermediate_df
                else:
                    df = df.concat(
                        axis=0, others=[intermediate_df], how="outer", sort=False
                    ).from_labels(drop=True)
            df = (
                df.to_labels(
                    [
                        "index",
                        __PONDER_AGG_OTHER_COL_ID__,
                        __PONDER_AGG_OTHER_COL_NAME__,
                    ]
                )
                .sort_by(
                    axis=0,
                    columns=[
                        "index",
                        __PONDER_AGG_OTHER_COL_ID__,
                    ],
                    ascending=[True, True],
                )
                .from_labels(drop=False)
            )
            # Breaking the chain here to be able to use `df.columns` below.
            df = df.mask(
                col_labels=[
                    col
                    for col in df.columns
                    if col not in [__PONDER_AGG_OTHER_COL_ID__]
                ]
            ).to_labels(["index", __PONDER_AGG_OTHER_COL_NAME__])
            return df

        if win_type is not None or operator in [
            "MEDIAN",
            "KURTOSIS",
            "SKEW",
            "QUANTILE",
            "RANK",
        ]:
            agg_kwargs.update(
                {
                    "purpose": "rolling",
                    "window": window,
                    "win_type": win_type,
                    "win_func": operator,
                    "view_names": ["T1", "T2"],
                }
            )
            if operator == "QUANTILE":
                agg_kwargs.update(
                    {
                        "quantile": agg_args[0],
                        "interpolation": agg_args[1],
                    }
                )
            elif operator == "RANK":
                agg_kwargs.update(
                    {
                        "method": agg_args[0],
                        "ascending": agg_args[1],
                        "pct": agg_args[2],
                        "numeric_only": agg_args[3],
                    }
                )
            database_column_names = [
                self.get_db_column_name(col_name) for col_name in self.columns
            ]
            new_query_tree = self._query_tree.add_with_self_cross_join(
                columns=database_column_names,
                kwargs=agg_kwargs,
            )
        else:
            database_column_names = [
                self.get_db_column_name(col_name) for col_name in self.columns
            ]
            db_agg_kwargs = {}
            if operator == __WINDOW_AGGREGATE_MAP__:
                for key, value in agg_kwargs["func_map"].items():
                    db_agg_kwargs[self.get_db_column_name(key)] = value
            new_query_tree = self._query_tree.add_cumulative_function(
                function=(
                    operator if operator != __WINDOW_AGGREGATE_MAP__ else db_agg_kwargs
                ),
                columns=database_column_names,
                skipna=False,
                window=window,
                non_numeric_cols=non_numeric_cols,
            )
        dataframe_column_names = [
            self.get_df_column_name(col_name)
            for col_name in new_query_tree.get_column_names()
        ]
        return self.__constructor__(
            new_query_tree,
            new_column_labels=dataframe_column_names,
            new_row_labels=self._row_labels_cache,
            new_dtypes=replace_dtype_column_names(
                new_query_tree.get_column_types(), dataframe_column_names
            ),
            new_row_positions=self._row_positions_cache,
        )

    def expanding(
        self,
        axis: int,
        operator: str,
        min_window: int,
        non_numeric_cols,
        agg_args,
        agg_kwargs,
    ):
        from .query_compiler import __WINDOW_AGGREGATE_MAP__

        if operator not in [
            "SUM",
            "AVG",
            "MIN",
            "MAX",
            "VARIANCE",
            "STDDEV",
            "COUNT",
            "SEM",
            "MEDIAN",
            "KURTOSIS",
            "SKEW",
            "CORR",
            "COV",
            "QUANTILE",
            "RANK",
            __WINDOW_AGGREGATE_MAP__,
        ]:
            raise make_exception(
                NotImplementedError,
                PonderError.DATAFRAME_EXPANDING_OPERATOR_NOT_SUPPORTED,
                f"expanding() with operator {operator} is not supported yet",
            )

        if operator in ["CORR", "COV"]:
            # See the explanation of the loop below in `rolling()`'s code.
            new_query_tree = get_renamed_query_tree_with_df_column_names(self)
            df = None
            for other_col_id in range(len(self.columns)):
                intermediate_tree = new_query_tree.add_cumulative_function(
                    function=(
                        operator
                        if operator != __WINDOW_AGGREGATE_MAP__
                        else agg_kwargs["func_map"]
                    ),
                    columns=self.columns,
                    skipna=False,
                    window=min_window,
                    non_numeric_cols=non_numeric_cols,
                    expanding=True,
                    other_col_id=other_col_id,
                )
                index_length = (
                    self.index.size
                    if isinstance(self.index, DBMSPositionMapping)
                    else self.index.length
                )
                new_row_labels = DBMSPositionMapping(
                    pandas.Index([i for i in range(index_length)])
                )
                intermediate_df = self.__constructor__(
                    intermediate_tree,
                    new_column_labels=intermediate_tree.get_column_names(),
                    new_row_labels=new_row_labels,
                    new_dtypes=intermediate_tree.get_column_types(),
                    new_row_positions=self._row_positions_cache,
                ).from_labels(drop=False)
                if df is None:
                    df = intermediate_df
                else:
                    df = df.concat(
                        axis=0, others=[intermediate_df], how="outer", sort=False
                    ).from_labels(drop=True)
            df = (
                df.to_labels(
                    [
                        "index",
                        __PONDER_AGG_OTHER_COL_ID__,
                        __PONDER_AGG_OTHER_COL_NAME__,
                    ]
                )
                .sort_by(
                    axis=0,
                    columns=[
                        "index",
                        __PONDER_AGG_OTHER_COL_ID__,
                    ],
                    ascending=[True, True],
                )
                .from_labels(drop=False)
            )
            # Breaking the chain here to be able to use `df.columns` below.
            df = df.mask(
                col_labels=[
                    col
                    for col in df.columns
                    if col not in [__PONDER_AGG_OTHER_COL_ID__]
                ]
            ).to_labels(["index", __PONDER_AGG_OTHER_COL_NAME__])
            return df
        elif operator in ["MEDIAN", "KURTOSIS", "SKEW", "QUANTILE", "RANK"]:
            agg_kwargs.update(
                {
                    "purpose": "expanding",
                    "window": min_window,
                    "win_func": operator,
                    "view_names": ["T1", "T2"],
                }
            )
            if operator == "QUANTILE":
                agg_kwargs.update(
                    {
                        "quantile": agg_args[0],
                        "interpolation": agg_args[1],
                    }
                )
            elif operator == "RANK":
                agg_kwargs.update(
                    {
                        "method": agg_args[0],
                        "ascending": agg_args[1],
                        "pct": agg_args[2],
                        "numeric_only": agg_args[3],
                    }
                )
            database_column_names = [
                self.get_db_column_name(col_name) for col_name in self.columns
            ]
            new_query_tree = self._query_tree.add_with_self_cross_join(
                columns=database_column_names,
                kwargs=agg_kwargs,
            )
        else:
            database_columns = [
                self.get_db_column_name(col_name) for col_name in self.columns
            ]
            function = (
                operator
                if operator != __WINDOW_AGGREGATE_MAP__
                else agg_kwargs["func_map"]
            )
            function = replace_map_with_database_columns(
                function, self.get_db_to_df_map()
            )
            new_query_tree = self._query_tree.add_cumulative_function(
                function=function,
                columns=database_columns,
                skipna=False,
                window=min_window,
                non_numeric_cols=non_numeric_cols,
                expanding=True,
            )
        dataframe_columns = [
            self.get_df_column_name(col_name)
            for col_name in new_query_tree.get_column_names()
        ]
        return self.__constructor__(
            new_query_tree,
            new_column_labels=dataframe_columns,
            new_row_labels=self._row_labels_cache,
            new_dtypes=replace_dtype_column_names(
                new_query_tree.get_column_types(), dataframe_columns
            ),
            new_row_positions=self._row_positions_cache,
        )

    def resample(self, operator: str, rule: str, agg_args, agg_kwargs):
        if operator not in [
            GROUPBY_FUNCTIONS.MIN,
            GROUPBY_FUNCTIONS.MAX,
            GROUPBY_FUNCTIONS.SUM,
            GROUPBY_FUNCTIONS.MEAN,
            GROUPBY_FUNCTIONS.MEDIAN,
            GROUPBY_FUNCTIONS.STD,
            GROUPBY_FUNCTIONS.VAR,
            GROUPBY_FUNCTIONS.COUNT,
            GROUPBY_FUNCTIONS.SEM,
            GROUPBY_FUNCTIONS.PROD,
            GROUPBY_FUNCTIONS.QUANTILE,
            GROUPBY_FUNCTIONS.NUNIQUE,
            GROUPBY_FUNCTIONS.SIZE,
            GROUPBY_FUNCTIONS.FIRST,
            GROUPBY_FUNCTIONS.LAST,
            GROUPBY_FUNCTIONS.ASFREQ,
            GROUPBY_FUNCTIONS.GET_GROUP,
        ]:
            raise make_exception(
                NotImplementedError,
                PonderError.DATAFRAME_RESAMPLE_OPERATOR_NOT_IMPLEMENTED,
                f"resample() with operator {operator} is not supported yet",
            )

        # Assume the timestamps are uniform across the dataframe
        # (1) Calculate the delta in seconds between first and last entries
        index_length = self.index.length
        index_start, index_end = self.index._get_pandas_index_at_row_positions(
            [0, index_length - 1]
        )
        sum_index_interval = (index_end - index_start).total_seconds()
        # (2) Detect whether operation is upsampling or downsampling
        offset = to_offset(rule)
        offset_sec = _pandas_offset_object_to_seconds(offset)
        index_interval = sum_index_interval / (index_length - 1)

        new_query_tree = self._query_tree.add_resample_function(
            index_dtype=self.index.dtype,
            function=operator,
            columns=self.database_columns,
            offset=offset,
            start_val=index_start,
            end_val=index_end,
            sum_interval=sum_index_interval,
            interval=index_interval,
            is_downsampling=(offset_sec >= index_interval),
            agg_args=agg_args,
            agg_kwargs=agg_kwargs,
        )
        freq = None
        if operator != GROUPBY_FUNCTIONS.GET_GROUP:
            # resample.get_group() sets freq = None
            freq = rule
        # Have to make new DBMSIndex because length and freq may have changed.
        new_row_labels = DBMSDateTimeIndex(
            self.index.column_names,
            [self.index.dtype],
            None,
            freq=freq,
            column_name_mappings=self.index.get_db_to_df_map(),
        )
        return self.__constructor__(
            new_query_tree,
            new_column_labels=pandas.Index(
                [
                    self.get_df_column_name(col_name)
                    for col_name in new_query_tree.get_column_names()
                ]
            ),
            new_row_labels=new_row_labels,
            new_dtypes=new_query_tree.dtypes,
            new_row_positions=None,
        )

    def sort_by(
        self,
        axis: Union[int, Axis],
        columns: Union[str, List[str]],
        ascending: Union[bool, List[bool]] = True,
        handle_duplicates: str = None,
    ):
        if axis == 1 or axis == Axis.COL_WISE:
            raise make_exception(
                NotImplementedError,
                PonderError.DATAFRAME_SORT_AXIS_1,
                "Sorting columns by row values is not implemented yet",
            )
        keep_old_row_numbers = isinstance(self.index, DBMSPositionMapping)
        database_columns = [self.get_db_column_name(col_name) for col_name in columns]
        new_query_tree = self._query_tree.add_sort(
            database_columns, ascending, keep_old_row_numbers, handle_duplicates
        )
        if isinstance(self.index, DBMSPositionMapping):
            new_row_labels = DBMSIndex(
                [__PONDER_ROW_LABELS_COLUMN_NAME__],
                [np.int64],
                len(self.index),
                self.get_db_to_df_map(),
            )
        else:
            new_row_labels = self.index.copy()

        if isinstance(self.index, DBMSIndex):
            if self.index._ponder_get_names() == columns:
                new_row_labels._ponder_set_sort_state(True, ascending)
            else:
                new_row_labels._ponder_set_sort_state(False, False)

        ret_df = self.__constructor__(
            new_query_tree,
            new_column_labels=self.columns,
            new_row_labels=new_row_labels,
            new_dtypes=self.dtypes,
            new_row_positions=None,
        )
        return ret_df

    def map_pandas_grouper_to_database(self, pandas_grouper):
        database_key = self.get_db_column_name(pandas_grouper.key)
        database_grouper = pandas.Grouper(
            key=database_key,
            level=pandas_grouper.level,
            freq=pandas_grouper.freq,
            axis=pandas_grouper.axis,
            sort=pandas_grouper.sort,
            closed=pandas_grouper.closed,
            label=pandas_grouper.label,
            convention=pandas_grouper.convention,
            origin=pandas_grouper.origin,
            offset=pandas_grouper.offset,
            dropna=pandas_grouper.dropna,
        )
        return database_grouper

    def _generate_database_by_params(self, by, use_dataframe_column_names=False):
        database_by = {}
        for obj, param in by.get_map().items():
            if param.get("graft_predicates"):
                if isinstance(obj, DBMSDataframe):
                    new_query_tree = obj.get_query_tree()
                    new_query_tree = (
                        get_renamed_query_tree_with_df_column_names(obj)
                        if use_dataframe_column_names
                        else new_query_tree
                    )
                    database_by[new_query_tree] = param
                elif isinstance(obj, pandas.Grouper):
                    database_obj = self.map_pandas_grouper_to_database(obj)
                    database_by[database_obj] = param
                else:
                    database_by[obj] = param
            else:
                new_query_tree = obj.get_query_tree()
                new_query_tree = (
                    get_renamed_query_tree_with_df_column_names(obj)
                    if use_dataframe_column_names
                    else new_query_tree
                )
                database_by[new_query_tree] = param
        return ByParams(database_by)

    def _map_groupby_operator_to_database(self, operator):
        if is_dict_like(operator):
            ret_operator = {}
            for key, val in operator.items():
                ret_operator[self.get_db_column_name(key)] = val
            return ret_operator

        return operator

    def groupby(
        self,
        operator: Union[list, GROUPBY_FUNCTIONS],
        sort_by_group_keys: bool = True,
        columns_to_aggregate: Optional[Iterable] = None,
        axis: Union[int, Axis] = None,
        by=None,
        as_index=True,
        result_schema: Optional[Dict[Hashable, type]] = None,
        agg_args: Optional[tuple] = None,
        agg_kwargs: Optional[Dict] = None,
        dropna: bool = True,
    ):
        """Groupby operation on a dataframe.

        Parameters
        ----------
        operator : Union[list, str]
            The operator to apply to each group.
        sort_by_group_keys : bool, default: True
            Whether to use group keys as the primary key, with original
            position as secondary key. Set this to False, to only sort
            by original position.
        columns_to_aggregate : Iterable, default: None
            Columns to aggregate. If None, aggregates all this dataframe's
            columns except the ones in `by`.
        axis : Union[int, axis], default: None
            Not sure of this argument works.
        by : ByParams, default: None
            What to group by.
        as_index : bool, default: True
            Whether to make the group keys the index.
        result_schema : Optional[Dict[Hashable, type]], default: None
            This doesn't do anything.
        agg_args : Optional[tuple], default: None
            Positional args for the given aggregation function.
        agg_kwargs : Optional[Dict], default: None
            Key-word args for the given aggregation function.
        dropna : bool, default: True
            Whether to drop null group keys.

        Returns
        -------
        DBMSDataframe
             A new DBMSDataframe with the groupby result.
        """
        by_columns = by.columns

        # In the future, it might be worth rewriting this code so we don't have
        # to shoe horn logic specific to corr or cov in the general groupby function
        # wrapper.
        corr_or_cov = operator in [
            GROUPBY_FUNCTIONS.CORR,
            GROUPBY_FUNCTIONS.COV,
        ]
        df = None
        other_col_ids = [None]
        use_dataframe_column_names = False
        if corr_or_cov:
            new_tree = get_renamed_query_tree_with_df_column_names(self)
            use_dataframe_column_names = True
            database_by = self._generate_database_by_params(
                by, use_dataframe_column_names=use_dataframe_column_names
            )
            other_cols = [
                n for n in new_tree.get_column_names() if n not in database_by.columns
            ]
            other_col_ids = [id for id in range(len(other_cols))]
            database_operator = operator
        else:
            new_tree = self._query_tree
            database_by = self._generate_database_by_params(
                by, use_dataframe_column_names=use_dataframe_column_names
            )
            database_operator = None
            if operator is not None:
                database_operator = self._map_groupby_operator_to_database(operator)

        # See the explanation of the loop below in `rolling()`'s code.
        database_columns_to_aggregate = None
        if columns_to_aggregate is not None:
            database_columns_to_aggregate = (
                columns_to_aggregate
                if use_dataframe_column_names
                else (
                    [
                        self.get_db_column_name(col_name)
                        for col_name in columns_to_aggregate
                    ]
                )
            )

        for other_col_id in other_col_ids:
            intermediate_tree = new_tree.add_groupby(
                by if use_dataframe_column_names else database_by,
                as_index,
                operator if use_dataframe_column_names else database_operator,
                sort_by_group_keys,
                columns_to_aggregate
                if use_dataframe_column_names
                else database_columns_to_aggregate,
                agg_args,
                agg_kwargs,
                dropna,
                other_col_id,
                self.index._ponder_dtypes_list(),  # Needed for idxmax/idxmin
            )

            # Since we use NewRowLabelsColumnsNode for setting the correct metadata,
            # we can rely on the column labels and dtypes from there. Remove this
            # comment once we handle the metadata correctly in GroupByNode.
            assert isinstance(
                intermediate_tree._root, NewRowLabelsColumnsNode
            ), "groupby node should have a NewRowLabelsColumnsNode as root for now"

            new_column_labels = generate_dataframe_names_from_database_names(
                self.columns.values,
                operator,
                intermediate_tree.get_column_names(),
                self._query_tree.get_column_names(),
                self._db_df_column_name_mappings,
            )

            new_dtypes = intermediate_tree.get_column_types()
            new_row_label_column_names = [
                self.get_df_column_name(col_name)
                for col_name in intermediate_tree.get_row_labels_column_names()
            ]

            # If as_index is True, we set the index to be the groupby column.
            # If as_index is False, we set the new index to be none, which will
            # recompute to be a DBMSPositionMapping based on the number of
            # rows available in the resulting DataFrame. Position should be maintained
            # and handled by the GroupBy SQL generation.
            if as_index:
                new_index_columns = list(by_columns)
                # This only works because the root is NewRowLabelsColumnsNode
                # It's also possible that the dtype of the row labels changes, so we
                # can't rely on using self.dtypes.
                new_row_label_column_types = (
                    intermediate_tree.get_root().get_row_labels_column_types()
                )
                new_row_labels = DBMSIndex(
                    new_index_columns,
                    new_row_label_column_types,
                    None,
                    None if use_dataframe_column_names else self.get_db_to_df_map(),
                )
            # This should be generalized to handle any case where as_index is false
            # but we don't handle metadata properly in multiple cases so we
            # can't do that yet. For now, let's just special case for head and tail.
            elif operator in groupby_view_funcs:
                index_dtypes = []
                for c in new_row_label_column_names:
                    if c in self.dtypes:
                        index_dtypes.append(self.dtypes[c])
                    elif c == __PONDER_ROW_LABELS_COLUMN_NAME__:
                        index_dtypes.append(np.int64)
                    else:
                        raise make_exception(
                            ValueError,
                            PonderError.GROUPBY_INDEX_DTYPE_NOT_FOUND,
                            f"Unknown column name {c}",
                        )
                new_row_labels = DBMSIndex(
                    new_row_label_column_names,
                    index_dtypes,
                    None,
                    None
                    if use_dataframe_column_names
                    else self._db_df_column_name_mappings,
                )
            else:
                new_row_labels = None
            intermediate_df = self.__constructor__(
                intermediate_tree,
                new_column_labels,
                new_row_labels=new_row_labels,
                new_dtypes=new_dtypes,
                new_row_positions=None,
            )
            index_length = 0
            if corr_or_cov:
                index_length = intermediate_df.index.length
            if df is None:
                df = intermediate_df
                if not corr_or_cov:
                    # no need for looping
                    return df
                else:
                    df = df.from_labels(drop=False)
                    df._row_labels_cache = DBMSPositionMapping(
                        pandas.RangeIndex(
                            start=other_col_id * index_length,
                            stop=(other_col_id + 1) * index_length,
                        )
                    )
            else:
                intermediate_df = intermediate_df.from_labels(drop=False)
                intermediate_df._row_labels_cache = DBMSPositionMapping(
                    pandas.RangeIndex(
                        start=other_col_id * index_length,
                        stop=(other_col_id + 1) * index_length,
                    )
                )
                df = df.concat(
                    axis=0, others=[intermediate_df], how="outer", sort=False
                ).from_labels(drop=True)
        df = (
            df.to_labels(
                [
                    *new_row_label_column_names,
                    __PONDER_AGG_OTHER_COL_ID__,
                    __PONDER_AGG_OTHER_COL_NAME__,
                ]
            )
            .sort_by(
                axis=0,
                columns=[*new_row_label_column_names, __PONDER_AGG_OTHER_COL_ID__],
                ascending=[True] * len(new_row_label_column_names) + [True],
            )
            .from_labels(drop=False)
        )
        # Breaking the chain here to be able to use `df.columns` below.
        df = df.mask(
            col_labels=[
                col for col in df.columns if col not in [__PONDER_AGG_OTHER_COL_ID__]
            ]
        ).to_labels([*new_row_label_column_names, __PONDER_AGG_OTHER_COL_NAME__])
        return df

    def concat(
        self,
        axis: Union[int, Axis],
        others: Union["DBMSDataframe", List["DBMSDataframe"]],
        how,
        sort,
    ):
        if axis in [0, Axis.COL_WISE]:
            if not all(isinstance(o.index, type(self.index)) for o in others):
                index_types = list(map(lambda x: type(x.index).__name__, others))
                index_types.append(type(self.index).__name__)
                raise make_exception(
                    NotImplementedError,
                    PonderError.CONCAT_AXIS_0_DIFFERENT_INDEX_TYPES,
                    "Cannot concat DataFrames with different index types "
                    + f"({index_types}) on axis=0, "
                    + "because doing so would require materializing and then "
                    + "joining against a new index column, resulting in "
                    + "performance issues.",
                )
            if isinstance(self.index, DBMSIndex):
                # TODO add support for appending row labels
                raise make_exception(
                    NotImplementedError,
                    PonderError.CONCAT_AXIS_0_DBMS_INDEX,
                    "Cannot concat DataFrames with DBMSIndex on axis=0",
                )
            else:
                new_length = len(self.index) + sum(len(o.index) for o in others)
                new_row_labels = DBMSIndex(
                    [__PONDER_ROW_LABELS_COLUMN_NAME__],
                    [np.int64],
                    new_length,
                    self.get_db_to_df_map(),
                )
                new_row_positions = DBMSPositionMapping(
                    pandas.RangeIndex(new_length),
                )
            # first need to align columns
            new_columns = self.columns
            new_database_columns = pandas.Index(
                [self.get_db_column_name(col_name) for col_name in self.columns]
            )
            for o in others:
                right_index = o.columns
                right_database_index = pandas.Index(
                    [o.get_db_column_name(col_name) for col_name in o.columns]
                )

                if how == "outer" and not sort:
                    new_columns = new_columns.union(right_index, sort=False)
                    new_database_columns = new_database_columns.union(
                        right_database_index, sort=False
                    )
                else:
                    new_columns = new_columns.join(right_index, how=how, sort=sort)
                    new_database_columns = new_database_columns.join(
                        right_database_index, how=how, sort=sort
                    )
            new_dtypes = pandas.Series(index=new_columns, dtype=object)
            for col in new_columns:
                new_dtypes[col] = find_common_type(
                    [
                        frame.dtypes[col]
                        for frame in (self, *others)
                        if col in frame.dtypes
                    ]
                )
            new_database_dtypes = replace_dtype_column_names(
                new_dtypes, new_database_columns
            )
            # TODO revisit efficiency
            if not self.columns.equals(new_columns):
                temp_dtypes = [
                    self.dtypes[c] if c in self.columns else new_dtypes[c]
                    for c in new_columns
                ]
                new_database_dtypes = replace_dtype_column_names(
                    temp_dtypes, new_database_columns
                )
                left_query_tree = self._query_tree.add_null_columns(
                    self.database_columns,
                    new_database_columns,
                    new_dtypes=new_database_dtypes.tolist(),
                )
            else:
                left_query_tree = self._query_tree
            other_query_trees = []
            for o in others:
                if not o.columns.equals(new_columns):
                    temp_dtypes = [
                        o.dtypes[c] if c in o.columns else new_dtypes[c]
                        for c in new_columns
                    ]
                    new_database_dtypes = replace_dtype_column_names(
                        temp_dtypes, new_database_columns
                    )
                    other_query_trees.append(
                        o._query_tree.add_null_columns(
                            o.database_columns,
                            new_database_columns,
                            new_dtypes=new_database_dtypes.tolist(),
                        )
                    )
                else:
                    other_query_trees.append(o._query_tree)
            new_query_tree = left_query_tree.add_union_all(
                other_query_trees, new_database_dtypes
            )

            return DBMSDataframe(
                new_query_tree,
                new_columns,
                new_row_labels,
                new_dtypes,
                new_row_positions,
            )
        else:
            if isinstance(self.index, DBMSIndex):
                if not all(isinstance(o.index, type(self.index)) for o in others):
                    raise make_exception(
                        NotImplementedError,
                        PonderError.CONCAT_AXIS_1_DIFFERENT_INDEX_TYPES,
                        "Cannot concat DataFrames with different index types on axis=1",
                    )
                if len(self.index.column_names) > 1:
                    raise make_exception(
                        NotImplementedError,
                        PonderError.CONCAT_AXIS_1_MULTIPLE_INDEX_LEVELS,
                        "Cannot concat DataFrames with multiple index levels on axis=1",
                    )
                new_row_labels = self.index
                use_db_index = True
            elif not all(
                isinstance(o.index, DBMSPositionMapping) for o in others
            ) or not isinstance(self.index, DBMSPositionMapping):
                raise make_exception(
                    NotImplementedError,
                    PonderError.CONCAT_AXIS_1_NON_RANGE_INDEX,
                    "Cannot concat frames with non-range indexes on axis=1",
                )
            else:
                new_row_labels = None
                use_db_index = False
            intermediate_tree = self._query_tree
            df_schema = self.columns.values
            suffixes = ("_x", "_y")
            for other in others:
                left_on = [self.index.name if use_db_index else "LEFT_ORDER"]
                right_on = [other.index.name if use_db_index else "RIGHT_ORDER"]
                df_schema = generate_join_schema(
                    df_schema,
                    other.columns.values,
                    how=how,
                    left_on=left_on,
                    right_on=right_on,
                    suffixes=suffixes,
                    indicator=False,
                )
                intermediate_tree = intermediate_tree.add_join(
                    right=other._query_tree,
                    how=how,
                    left_on=[self.get_db_column_name(col_name) for col_name in left_on],
                    right_on=[
                        other.get_db_column_name(col_name) for col_name in right_on
                    ],
                    suffixes=suffixes,
                    use_db_index=use_db_index,
                )
            return self.__constructor__(
                intermediate_tree,
                new_column_labels=df_schema,
                new_row_labels=new_row_labels,
                new_dtypes=pandas.concat([self.dtypes] + [o.dtypes for o in others]),
            )

    def insert_pandas_df(self, pandas_df, add_col_last=False):
        new_tree = self._query_tree.make_tree_from_pdf_using_connection(pandas_df)
        df = DBMSDataframe(
            new_tree,
            new_column_labels=new_tree.get_dataframe_column_names(),
            new_dtypes=replace_dtype_column_names(
                new_tree.get_column_types(), new_tree.get_dataframe_column_names()
            ),
        )
        if add_col_last:
            return self.concat(axis=1, others=[df], how="inner", sort=False)
        else:
            return df.concat(axis=1, others=[self], how="inner", sort=False)

    def binary_op(
        self, op, right_frame, join_type="outer", axis=None, sort_columns=True
    ):
        # TODO: there is probably a bug here-- we just ignore the axis param. At the
        # same time, we have a special case for adding a series that's like df.iloc[0]:
        # treat it as a row rather than a column. e.g.
        # df = pd.DataFrame([[1, 2], [3, 4]])
        # df + df.iloc[0]
        if (
            isinstance(right_frame, TransposedDBMSDataframe)
            and len(right_frame.columns) == 1
        ):
            right_frame_transpose = right_frame.transpose()
            new_columns = self.columns.union(right_frame_transpose.columns)
            # tree doesn't know order of columns
            final_tree = self._query_tree.add_broadcast_binary_op(
                right_frame_transpose._query_tree,
                op,
                [
                    self.get_db_column_name(col_name)
                    if col_name in self.columns
                    else right_frame_transpose.get_db_column_name(col_name)
                    for col_name in new_columns
                ],
            )
            new_dtypes = replace_dtype_column_names(
                final_tree.get_column_types(), new_columns
            )
        else:
            # if we have set the index we need to preserve that
            # column in the equijoin
            #
            # TODO https://ponderdata.atlassian.net/browse/POND-1458

            if isinstance(self.index, DBMSIndex):
                use_db_index = True
            else:
                use_db_index = False
            suffixes = ["_ponder_left", "_ponder_right"]
            intermediate_tree = self._query_tree.add_join(
                right_frame._query_tree,
                join_type,
                ["LEFT_ORDER"],
                ["RIGHT_ORDER"],
                suffixes,
                use_db_index=use_db_index,
            )
            final_tree = intermediate_tree.add_binary_post_join(
                self.database_columns,
                self.dtypes[self.columns],
                right_frame.database_columns,
                right_frame.dtypes[right_frame.columns],
                suffixes,
                op,
            )
            if sort_columns:
                left_columns = self.columns
                right_columns = right_frame.columns
                new_columns = left_columns.union(right_columns)
                new_database_columns = [
                    self.get_db_column_name(col_name)
                    if col_name in self.columns
                    else right_frame.get_db_column_name(col_name)
                    for col_name in new_columns
                ]
                final_tree_column_names = final_tree.get_column_names()
                new_database_columns = [
                    col_name
                    for col_name in new_database_columns
                    if col_name in final_tree_column_names
                ]
                final_tree = final_tree.add_reorder_columns(new_database_columns)
                new_columns = []
                for col in new_database_columns:
                    df_col_name = self.get_df_column_name(col)
                    if col == df_col_name:
                        df_col_name = right_frame.get_df_column_name(col)
                    new_columns.append(df_col_name)
            else:
                new_columns = [
                    self.get_df_column_name(col_name)
                    if col_name in self.database_columns
                    else right_frame.get_df_column_name(col_name)
                    for col_name in final_tree.get_column_names()
                ]

            new_dtypes = replace_dtype_column_names(
                final_tree.get_column_types(), new_columns
            )

        return self.__constructor__(
            final_tree,
            new_columns,
            self.index,
            new_dtypes,
            self._row_positions_cache,
        )

    def derived_column(self, column: "DBMSDataframe", new_column_name):
        new_db_column_name = generate_new_db_column_name(
            self._query_tree.get_column_names(), new_column_name, self._query_tree._conn
        )
        new_query_tree = self._query_tree.add_derived_column(
            column._query_tree,
            new_db_column_name,
        )
        new_column_names = [col_name for col_name in self.columns]
        new_column_names.append(new_column_name)

        new_dtypes = replace_dtype_column_names(
            new_query_tree.get_root().get_column_types(), new_column_names
        )
        return self.__constructor__(
            new_query_tree,
            new_column_labels=pandas.Index(new_column_names),
            new_row_labels=self.index,
            new_dtypes=new_dtypes,
            new_row_positions=self._row_positions_cache,
        )

    def filter_rows(self, condition: RowWiseFilterPredicates.RowWiseFilterPredicate):
        if isinstance(self.index, DBMSPositionMapping):
            new_row_labels = DBMSIndex(
                [__PONDER_ORDER_COLUMN_NAME__],
                [np.int64],
                None,
                self.get_db_to_df_map(),
            )
        else:
            new_row_labels = DBMSIndex(
                self.index.column_names,
                self.index._ponder_dtypes_list(),
                None,
                self.index.get_db_to_df_map(),
            )

        new_condition = condition.update_column_names(
            self.get_db_to_df_map(),
            self.index.get_db_to_df_map()
            if isinstance(self.index, DBMSIndex)
            else None,
        )
        return self.__constructor__(
            self._query_tree.add_filter(new_condition),
            new_column_labels=self.columns,
            new_row_labels=new_row_labels,
            new_dtypes=self._column_types_cache,
            new_row_positions=None,
        )

    def project(
        self,
        axis: Union[Axis, int],
        columns_selection,
        project_column_names,
        project_column_types,
    ):
        assert axis == 1, "Projection can only happen when axis=1"
        new_query_tree = self._query_tree.add_project(
            columns_selection, project_column_names, project_column_types
        )
        return self.__constructor__(
            new_query_tree,
            new_column_labels=(
                new_query_tree.get_root().get_column_names()
                if project_column_names is None
                else self._column_labels_cache
            ),
            new_row_labels=self._row_labels_cache,
            new_dtypes=new_query_tree.get_root().get_column_types(),
            new_row_positions=self._row_positions_cache,
        )

    def map(
        self, func: MapFunction, labels_to_apply_over: Optional[list[str]] = None
    ) -> "DBMSDataframe":
        """Map a set of columns to the same type.

        Parameters
        ----------
        func : MapFunction
            The function to apply to each column.
        labels_to_apply_over : list of str, default: None
            The labels to apply the function over. If None, apply over all columns.
            These columns can be row label columns, an order column, or data columns.

        Returns
        -------
        DBMSDataframe
            A new dataframe with the function applied to each column. This function will
            not modify columns that are not in labels_to_apply_over.
        """
        if not isinstance(func, MapFunction):
            raise make_exception(
                RuntimeError,
                PonderError.MAP_FUNCTION_NOT_EXPECTED_ENUM,
                f"Map only supports {MapFunction} as func, not {func} "
                + f"of type {type(func)}",
            )
        database_labels_to_apply_over = None
        if labels_to_apply_over is not None:
            if is_list_like(labels_to_apply_over):
                database_labels_to_apply_over = [
                    self.get_db_column_name(col_name)
                    for col_name in labels_to_apply_over
                ]
            else:
                database_labels_to_apply_over = self.get_db_column_name(
                    labels_to_apply_over
                )
        database_columns = [
            self.get_db_column_name(col_name) for col_name in self.columns
        ]
        new_query_tree = self._query_tree.add_map(
            func,
            database_columns
            if database_labels_to_apply_over is None
            else database_labels_to_apply_over,
        )
        if (
            func._id in (MAP_FUNCTION.str_split, MAP_FUNCTION.str_rsplit)
            and func._params_list[3] is True
        ):
            new_column_labels = pandas.RangeIndex(
                start=0, stop=func._params_list[2] + 1, step=1
            )
        else:
            new_column_labels = [
                self.get_df_column_name(col_name)
                for col_name in new_query_tree.get_root().get_column_names()
            ]

        old_index = self._row_labels_cache
        new_row_labels = (
            DBMSDateTimeIndex(
                column_names=old_index.column_names,
                dtypes=[
                    func._return_type
                    if labels_to_apply_over is not None and n in labels_to_apply_over
                    else t
                    for n, t in zip(
                        old_index.column_names, old_index._ponder_dtypes_list()
                    )
                ],
                length=old_index.length,
                freq=getattr(old_index, "freq", None),
                column_name_mappings=old_index.get_db_to_df_map(),
            )
            if isinstance(old_index, DBMSIndex)
            else old_index
        )
        return self.__constructor__(
            new_query_tree,
            new_column_labels,
            new_row_labels=new_row_labels,
            new_dtypes=replace_dtype_column_names(
                new_query_tree.dtypes, new_column_labels
            ),
            new_row_positions=self._row_positions_cache,
        )

    def reduce(
        self,
        func: REDUCE_FUNCTION,
        axis: Axis,
        dtypes: Optional[object] = None,
        percentile: Optional[float] = None,
        params_list: Optional[object] = None,
    ):
        """Reduce the given axis to length 1 by applying the given function.

        Parameters
        ----------
        func : REDUCE_FUNCTION
            The reduce function.
        axis : Axis
            The axis to reduce.
        dtypes: object, optional
            The dtypes of the result.
        percentile: float, optional
            percentile for percentile reduction. This param is not valid for
            row-wise reduce.
        params_list: object, optional
            parameter list for func. This param is not valid for
            row-wise reduce.

        Returns
        -------
        DBMSDataframe
            A new dataframe resulting from the reduction.
        """
        if not isinstance(func, REDUCE_FUNCTION):
            raise make_exception(
                RuntimeError,
                PonderError.REDUCE_FUNCTION_NOT_EXPECTED_ENUM,
                f"Reduce only supports {REDUCE_FUNCTION} as function, not "
                + f"{func} of type {type(func)}",
            )
        assert dtypes is not None, "Easy case first"
        # TODO: Axis enum is supposed to reduce confusion about the
        # interpretation of axis for operators, but here we are treating
        # Axis(1) and axis of int(0) the same, which means that Axis(axis)
        # has the opposite meaning of axis itself when axis=0. Fix this
        # inconsistency here and elsewhere.
        if axis == Axis.COL_WISE or axis == 0:
            new_row_labels = DBMSPositionMapping(pandas.RangeIndex(1))
            corr_or_cov = func in [REDUCE_FUNCTION.CORR, REDUCE_FUNCTION.COV]
            df = None
            other_col_ids = [None]
            if corr_or_cov:
                other_col_ids = [id for id in range(len(self.columns))]
            # See the explanation of the loop below in `rolling()`'s code.
            for other_col_id in other_col_ids:
                # need to put back the dataframe column name since they come back as
                # values in the dataframe.
                use_dataframe_column_names = False
                if other_col_id is not None:
                    intermediate_tree = get_renamed_query_tree_with_df_column_names(
                        self
                    )
                    use_dataframe_column_names = True
                else:
                    intermediate_tree = self._query_tree
                intermediate_tree = intermediate_tree.add_column_wise_reduce(
                    func,
                    dtypes,
                    self.columns
                    if use_dataframe_column_names
                    else self.database_columns,
                    percentile=percentile,
                    params_list=params_list,
                    other_col_id=other_col_id,
                )

                new_columns = self.columns
                new_dtypes = dtypes
                if corr_or_cov:
                    new_columns = pandas.Index(
                        [__PONDER_AGG_OTHER_COL_ID__, __PONDER_AGG_OTHER_COL_NAME__]
                    ).append(new_columns)
                    new_dtypes = pandas.concat(
                        [
                            pandas.Series(
                                {
                                    __PONDER_AGG_OTHER_COL_ID__: "int",
                                    __PONDER_AGG_OTHER_COL_NAME__: "object",
                                }
                            ),
                            new_dtypes,
                        ]
                    )
                    new_row_labels = DBMSPositionMapping(
                        pandas.RangeIndex(start=other_col_id, stop=other_col_id + 1)
                    )
                intermediate_df = self.__constructor__(
                    query_tree=intermediate_tree,
                    new_column_labels=new_columns,
                    new_row_labels=new_row_labels,
                    new_dtypes=new_dtypes,
                )
                if df is None:
                    df = intermediate_df
                    if not corr_or_cov:
                        # no need for looping
                        return df
                else:
                    df = df.concat(
                        axis=0, others=[intermediate_df], how="outer", sort=False
                    ).from_labels(drop=True)
            df = (
                df.to_labels(
                    [__PONDER_AGG_OTHER_COL_ID__, __PONDER_AGG_OTHER_COL_NAME__]
                )
                .sort_by(
                    axis=0, columns=[__PONDER_AGG_OTHER_COL_ID__], ascending=[True]
                )
                .from_labels(drop=False)
            )
            # Breaking the chain here to be able to use `df.columns` below.
            df = df.mask(
                col_labels=[
                    col
                    for col in df.columns
                    if col not in [__PONDER_AGG_OTHER_COL_ID__]
                ]
            ).to_labels([__PONDER_AGG_OTHER_COL_NAME__])
            return df
        else:
            if percentile is not None:
                raise make_exception(
                    RuntimeError,
                    PonderError.PERCENTILE_NOT_VALID_FOR_ROW_WISE_REDUCE,
                    "percentile does not make sense for row-wise reduce.",
                )
            if params_list is not None:
                raise make_exception(
                    RuntimeError,
                    PonderError.PARAMS_LIST_NOT_VALID_FOR_ROW_WISE_REDUCE,
                )
            new_column_name = __PONDER_REDUCED_COLUMN_NAME__
            new_columns = pandas.Index([new_column_name])
            new_row_labels = self.index
            new_dtypes = dtypes
            assert (
                len(dtypes) == 1
            ), "Internal error: row-wise reduce dtypes should be length 1"
            return self.__constructor__(
                self._query_tree.add_row_wise_reduce(func, new_column_name, dtypes[0]),
                new_column_labels=new_columns,
                new_row_labels=new_row_labels,
                new_dtypes=new_dtypes,
            )

    def join(self, other, how, left_on, right_on, suffixes, indicator):
        if left_on is None:
            database_left_on = []
        else:
            left_on = left_on if is_list_like(left_on) else [left_on]
            database_left_on = [self.get_db_column_name(column) for column in left_on]
        if right_on is None:
            database_right_on = []
        else:
            right_on = right_on if is_list_like(right_on) else [right_on]
            database_right_on = [
                other.get_db_column_name(column) for column in right_on
            ]

        new_query_tree = self._query_tree.add_join(
            other._query_tree,
            how,
            database_left_on,
            database_right_on,
            suffixes,
            indicator=indicator,
        )

        new_columns = generate_join_schema(
            self.columns.values,
            other.columns,
            how=how,
            left_on=left_on,
            right_on=right_on,
            suffixes=suffixes,
            indicator=indicator,
        )

        new_dtypes = new_query_tree.get_column_types()
        return self.__constructor__(
            new_query_tree, new_column_labels=new_columns, new_dtypes=new_dtypes
        )

    def update(
        self, other, join="left", overwrite=True, filter_func=None, errors="raise"
    ):
        # matches pandas 1.5.3
        if errors not in ["raise", "ignore"]:
            raise make_exception(
                ValueError,
                PonderError.UPDATE_ERRORS_PARAMETER_NOT_VALID,
                "The parameter errors must be either 'ignore' or 'raise'",
            )
        if join != "left":
            raise make_exception(
                NotImplementedError,
                PonderError.UPDATE_JOIN_PARAMETER_UNSUPPORTED,
                "update() with join != 'left' is not supported yet",
            )

        # ponder specific errors
        if not overwrite:
            raise make_exception(
                NotImplementedError,
                PonderError.UPDATE_OVERWRITE_FALSEY_PARAMETER_UNSUPPORTED,
                "update() requires truthy overwrite",
            )
        if filter_func is not None:
            raise make_exception(
                NotImplementedError,
                PonderError.UPDATE_FILTER_FUNC_PARAMETER_UNSUPPORTED,
                "update() with filter_func != None is not supported yet",
            )
        if errors != "raise":
            raise make_exception(
                NotImplementedError,
                PonderError.UPDATE_ERRORS_PARAMETER_UNSUPPORTED,
                "update() requires errors to be 'raise' (default)",
            )

        # collect the common columns
        common_columns = [value for value in self.columns if value in other.columns]

        if len(common_columns) <= 0:
            return self

        database_common_columns = [
            self.get_db_column_name(col_name) for col_name in common_columns
        ]

        # Create a join node
        new_join = self._query_tree.add_join(
            right=other._query_tree,
            how=join,
            left_on=[self.index.name],
            right_on=[other.index.name],
            suffixes=("_UpdateA", "_UpdateB"),
        )
        # Create a dict consisting of { <col to create> : [ < cols to coalesce > ]}
        database_coalesce_definition = {
            c: [c + "_UpdateA", c + "_UpdateB"] for c in database_common_columns
        }
        new_coalesce = new_join.add_coalesce(
            database_coalesce_definition, self.database_columns
        )
        # update always returns the exact same columns and dtypes
        return self.__constructor__(
            new_coalesce,
            new_column_labels=self._get_column_labels(),
            new_dtypes=self.dtypes,
        )

    def merge_asof(
        self,
        other,
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
        # not throwing any errors at this time for parameters that can clash.
        # For instance either on has to be set or both of left_on and right_on.
        if left_index is not None and left_index is not False:
            left_on = [self.index.name]
        if right_index is not None and right_index is not False:
            right_on = [self.index.name]

        if left_on:
            left_on = [left_on] if isinstance(left_on, str) else left_on
            database_left_on = [self.get_db_column_name(column) for column in left_on]
        else:
            database_left_on = []

        if right_on:
            right_on = [right_on] if isinstance(right_on, str) else right_on
            database_right_on = [
                other.get_db_column_name(column) for column in right_on
            ]
        else:
            database_right_on = []

        if left_by:
            left_by = [left_by] if isinstance(left_by, str) else left_by
            database_left_by = [self.get_db_column_name(column) for column in left_by]
        else:
            database_left_by = []

        if right_by:
            right_by = [right_by] if isinstance(right_by, str) else right_by
            database_right_by = [
                other.get_db_column_name(column) for column in right_by
            ]
        else:
            database_right_by = []

        new_columns = generate_merge_asof_schema(
            self.columns.values,
            other.columns.values,
            left_on=left_on,
            right_on=right_on,
            left_index=left_index,
            right_index=right_index,
            left_by=left_by,
            right_by=right_by,
            suffixes=suffixes,
            tolerance=tolerance,
            allow_exact_matches=allow_exact_matches,
            direction=direction,
        )

        new_query_tree = self._query_tree.add_merge_asof(
            other._query_tree,
            database_left_on,
            database_right_on,
            left_index,
            right_index,
            database_left_by,
            database_right_by,
            suffixes,
            tolerance,
            allow_exact_matches,
            direction,
        )
        new_dtypes = new_query_tree.get_column_types()

        return self.__constructor__(
            new_query_tree, new_column_labels=new_columns, new_dtypes=new_dtypes
        )

    def transpose(self):
        return TransposedDBMSDataframe(self)

    def is_monotonic_increasing(self):
        new_row_labels = DBMSIndex(
            [__PONDER_ORDER_COLUMN_NAME__],
            [np.int64],
            None,
            self.get_db_to_df_map(),
        )
        return self.__constructor__(
            self._query_tree.is_monotonic_increasing(),
            new_column_labels=["MONOTONIC_RESULT"],
            new_row_labels=new_row_labels,
            new_dtypes=[np.dtype(bool)],
            new_row_positions=None,
        )

    def is_monotonic_decreasing(self):
        new_row_labels = DBMSIndex(
            [__PONDER_ORDER_COLUMN_NAME__],
            [np.int64],
            None,
            self.get_db_to_df_map(),
        )
        return self.__constructor__(
            self._query_tree.is_monotonic_decreasing(),
            new_column_labels=["MONOTONIC_RESULT"],
            new_row_labels=new_row_labels,
            new_dtypes=[np.dtype(bool)],
            new_row_positions=None,
        )

    def pivot(
        self,
        index,
        columns,
        values_column_name,
        aggfunc,
        add_qualifier_to_new_column_names=True,
    ):
        # TODO(https://community.snowflake.com/s/ideas): If snowflake ever supports the
        # idea "Pivot without specifying values", use that instead of executing a
        # separate query to get all the unique values.
        if len(index) > 1:
            raise make_exception(
                NotImplementedError,
                PonderError.PIVOT_MULTIPLE_INDEX_COLUMNS_UNSUPPORTED,
                "pivot() with multiple index columns is not supported yet",
            )
        database_columns = [self.get_db_column_name(col_name) for col_name in columns]
        database_values_column_name = self.get_db_column_name(values_column_name)
        database_index_name = (
            self.get_db_column_name(index[0])
            if index is not None and index[0] is not None
            else None
        )
        unique_values = self._query_tree.get_unique_values(database_columns[0])
        unique_values = sorted([v for v in unique_values if v is not None])
        sanitized_values_dict = self._query_tree.generate_sanitized_values(
            unique_values
        )

        if sanitized_values_dict is not None and len(sanitized_values_dict) > 0:
            new_tree = self._query_tree.add_replace_value(
                database_columns[0], sanitized_values_dict
            )
        else:
            new_tree = self._query_tree

        if sanitized_values_dict is None:
            unique_values_for_query = unique_values
        else:
            unique_values_for_query = [
                sanitized_values_dict.get(value, value) for value in unique_values
            ]

        new_tree = new_tree.add_pivot(
            database_index_name,
            database_columns[0],
            database_values_column_name,
            unique_values_for_query,
            aggfunc,
            add_qualifier_to_new_column_names,
        )

        if index is not None and index[0] is not None:
            new_row_labels = DBMSIndex(
                index, [self.dtypes[index[0]]], None, self.get_db_to_df_map()
            )
        else:
            new_row_labels = None
        if sanitized_values_dict is not None:
            reverse_values_dict = {
                value: key for key, value in sanitized_values_dict.items()
            }
        else:
            reverse_values_dict = None
        df_columns = get_dataframe_column_names_for_pivot(
            df_values_column_name=values_column_name,
            db_values_column_name=database_values_column_name,
            db_column_names=new_tree.get_column_names(),
            column_name_mappings=self.get_db_to_df_map(),
            values_dict=reverse_values_dict,
            prefix_sep="_",
            db_prefix_sep="_",
        )
        df = self.__constructor__(
            new_tree,
            new_column_labels=df_columns,
            new_row_labels=new_row_labels,
            new_dtypes=replace_dtype_column_names(new_tree.dtypes, df_columns),
            new_row_positions=None,
        )
        return df

    def get_dummies(self, column, dummy_na, prefix: str, prefix_sep: str):
        if column is None or (is_list_like(column) and len(column) > 1):
            raise make_exception(
                NotImplementedError,
                PonderError.GET_DUMMIES_MULTIPLE_COLUMNS_UNSUPPORTED,
                "get_dummies() with multiple columns is not supported yet",
            )
        # pandas sorts these, so we will also
        database_column = self.get_db_column_name(column)
        unique_values = self._query_tree.get_unique_values(database_column)
        if dummy_na is False:
            unique_values = list(filter(lambda x: x is not None, unique_values))
        unique_values.sort(key=lambda e: (e is None, e))

        sanitized_values_dict = self._query_tree.generate_sanitized_values(
            unique_values
        )
        if sanitized_values_dict is not None:
            new_tree = self._query_tree.add_replace_value(
                database_column, sanitized_values_dict
            )
        else:
            new_tree = self._query_tree

        if prefix is not None:
            database_prefix = self._query_tree._conn.generate_sanitized_name(prefix)
        else:
            database_prefix = None

        if prefix_sep is not None:
            database_prefix_sep = self._query_tree._conn.generate_sanitized_name(
                prefix_sep
            )
        else:
            database_prefix_sep = None

        if sanitized_values_dict is None:
            unique_values_for_query = unique_values
        else:
            unique_values_for_query = [
                sanitized_values_dict.get(value, value) for value in unique_values
            ]

        new_query_tree = new_tree.add_get_dummies(
            database_column,
            unique_values_for_query,
            database_prefix,
            database_prefix_sep,
        )

        if sanitized_values_dict is not None:
            reverse_values_dict = {
                value: key for key, value in sanitized_values_dict.items()
            }
        else:
            reverse_values_dict = None
        new_columns = get_dataframe_column_names_for_pivot(
            df_values_column_name=prefix if prefix is not None else column,
            db_values_column_name=database_prefix
            if database_prefix is not None
            else database_column,
            db_column_names=new_query_tree.get_column_names(),
            column_name_mappings=self.get_db_to_df_map(),
            values_dict=reverse_values_dict,
            prefix_sep=prefix_sep,
            db_prefix_sep=database_prefix_sep if prefix_sep is not None else None,
        )
        new_columns = pandas.Index(new_columns)
        new_dtypes = new_query_tree.get_column_types()
        return self.__constructor__(
            new_query_tree,
            new_column_labels=new_columns,
            new_row_labels=self._row_labels_cache,
            new_dtypes=new_dtypes,
            new_row_positions=self._row_positions_cache,
        )

    def idx_minmax(self, min):
        # Note, this code makes a lot of assumptions as we only support
        # axis=0 for now.

        index_column_name = __PONDER_ROW_LABELS_COLUMN_NAME__
        index_column_type = np.dtype(int)  # default for position mapping

        # If we have a SnowflakeIndex, we need to get the column name and the
        # type and propagate the index information to the query tree.
        if isinstance(self.index, DBMSIndex):
            if len(self.index.column_names) != 1:
                raise make_exception(
                    NotImplementedError,
                    PonderError.IDX_MINMAX_MULTIPLE_INDEX_COLUMNS_UNSUPPORTED,
                    "idxmin()/idxmax() are only supported for single column indexes",
                )
            index_column_name = self.index.column_names[0]
            index_column_type = self.index._ponder_dtypes_list()[0]

        renamed_query_tree = get_renamed_query_tree_with_df_column_names(self)
        new_query_tree = renamed_query_tree.add_idx_minmax(
            index_column_name, index_column_type, min
        )

        assert isinstance(
            new_query_tree._root, NewRowLabelsColumnsNode
        ), "we should have a new row labels node that sets the index"

        new_row_labels = DBMSIndex(
            ["COLUMN_NAME"],
            [np.dtype("O")],
            None,
            self.get_db_to_df_map(),
        )
        df = self.__constructor__(
            new_query_tree,
            new_column_labels=new_query_tree.get_column_names(),
            new_row_labels=new_row_labels,
            new_dtypes=new_query_tree.get_column_types(),
            new_row_positions=None,
        )
        return df

    def dot(self, other_frame, transposed=False, transposed_other=False):
        new_query_tree = self._query_tree.add_dot_product(
            self, other_frame, transposed, transposed_other
        )
        if not transposed:
            return self.__constructor__(
                new_query_tree,
                new_column_labels=new_query_tree.get_column_names(),
                new_dtypes=new_query_tree.get_column_types(),
                new_row_labels=self._row_labels_cache,
                new_row_positions=self._row_positions_cache,
            )
        else:
            new_row_labels = DBMSPositionMapping(
                pandas.RangeIndex(0, len(self.columns))
            )
            return self.__constructor__(
                new_query_tree,
                new_column_labels=new_query_tree.get_column_names(),
                new_dtypes=new_query_tree.get_column_types(),
                new_row_labels=new_row_labels,
                new_row_positions=new_row_labels,
            )

    def dropna(self, axis, how: str, thresh: Optional[int], subset, index_name: str):
        database_subset = None
        if subset is not None:
            database_subset = [self.get_db_column_name(col_name) for col_name in subset]
        database_index_name = self.get_db_column_name(index_name)
        new_query_tree = self._query_tree.add_dropna(
            axis, how, thresh, database_subset, database_index_name
        )
        if axis == 0:
            if isinstance(self.index, DBMSPositionMapping):
                new_row_labels = DBMSIndex(
                    [__PONDER_ORDER_COLUMN_NAME__],
                    [np.int64],
                    None,
                    self.get_db_to_df_map(),
                )
            else:
                new_row_labels = DBMSIndex(
                    self.index.column_names,
                    self.index._ponder_dtypes_list(),
                    None,
                    self.get_db_to_df_map(),
                )
            new_row_positions = None
            if self._column_labels_cache is None:
                new_column_labels = new_query_tree.get_column_names()
                new_column_types = new_query_tree.get_column_types()
                new_column_types = replace_dtype_column_names(
                    new_column_types, new_column_labels
                )
            else:
                new_column_labels = self._column_labels_cache
                new_column_types = self._column_types_cache
        else:
            new_row_labels = self._row_labels_cache
            new_column_labels = [
                self.get_df_column_name(col_name)
                for col_name in new_query_tree.get_column_names()
            ]
            new_column_types = new_query_tree.get_column_types()
            new_column_types = replace_dtype_column_names(
                new_column_types, new_column_labels
            )
            new_row_positions = self._row_positions_cache
        return self.__constructor__(
            new_query_tree,
            new_column_labels=new_column_labels,
            new_dtypes=new_column_types,
            new_row_labels=new_row_labels,
            new_row_positions=new_row_positions,
        )

    def pandas_mask(self, mask_predicate, value_dict, columns_to_upcast_to_object):
        database_columns = [
            self.get_db_column_name(col_name) for col_name in self.columns
        ]

        database_columns_to_upcast_to_object = []
        if columns_to_upcast_to_object is not None:
            database_columns_to_upcast_to_object = [
                self.get_db_column_name(col_name)
                for col_name in columns_to_upcast_to_object
            ]

        col_to_value = None
        if value_dict is not None:
            col_to_value = {}
            for key, entry in value_dict.items():
                col_to_value[self.get_db_column_name(key)] = entry

        new_query_tree = self._query_tree.add_pandas_mask(
            binary_pred=mask_predicate,
            columns=database_columns,
            value_dict=col_to_value,
            columns_to_upcast_to_object=database_columns_to_upcast_to_object,
        )

        return self.__constructor__(
            new_query_tree,
            self.columns,
            new_row_labels=self._row_labels_cache,
            new_dtypes=new_query_tree.get_root().get_column_types(),
            new_row_positions=self._row_positions_cache,
        )

    def fillna(
        self,
        value,
        method,
        limit,
        group_cols: Optional[list[str]],
        columns_to_upcast_to_object,
    ):
        database_columns = [
            self.get_db_column_name(col_name) for col_name in self.columns
        ]
        if group_cols is not None and len(group_cols) != 0:
            database_group_cols = [
                self.get_db_column_name(col_name) for col_name in group_cols
            ]
        else:
            database_group_cols = None
        if columns_to_upcast_to_object is not None:
            database_columns_to_upcast_to_object = [
                self.get_db_column_name(col_name)
                for col_name in columns_to_upcast_to_object
            ]
        else:
            database_columns_to_upcast_to_object = None

        database_value = None
        if value is not None:
            database_value = {}
            for key, entry in value.items():
                database_value[self.get_db_column_name(key)] = entry

        new_query_tree = self._query_tree.add_fillna(
            database_value,
            method,
            limit,
            database_columns,
            self.dtypes.tolist(),
            database_group_cols,
            database_columns_to_upcast_to_object,
        )

        return self.__constructor__(
            new_query_tree,
            self.columns,
            new_row_labels=self._row_labels_cache,
            new_dtypes=new_query_tree.get_root().get_column_types(),
            new_row_positions=self._row_positions_cache,
        )

    def str_func(self, function, params_list, return_type="object"):
        from .query_tree import STRING_FUNCTIONS

        new_query_tree = self._query_tree.add_string_function(
            function, params_list, return_type
        )
        if (
            function in (STRING_FUNCTIONS.str_split, STRING_FUNCTIONS.str_rsplit)
            and params_list[3]
        ):
            new_column_labels = pandas.RangeIndex(
                start=0, stop=params_list[2] + 1, step=1
            )
        else:
            new_column_labels = new_query_tree.get_root().get_column_names()
        return self.__constructor__(
            new_query_tree,
            new_column_labels,
            new_row_labels=self._row_labels_cache,
            new_dtypes=new_query_tree.get_root().get_column_types(),
            new_row_positions=self._row_positions_cache,
        )

    def cast_func(
        self,
        cast_from_map,
        cast_to_map,
        column_names,
        return_types,
        new_col_names=None,
        reset_order=False,
        **kwargs,
    ):
        database_column_names = [
            self.get_db_column_name(col_name) for col_name in column_names
        ]
        database_cast_from_map = replace_map_with_database_columns(
            cast_from_map, self._db_df_column_name_mappings
        )
        database_cast_to_map = replace_map_with_database_columns(
            cast_to_map, self._db_df_column_name_mappings
        )
        new_query_tree = self._query_tree.add_cast_function(
            cast_from_map=database_cast_from_map,
            cast_to_map=database_cast_to_map,
            columns=database_column_names,
            return_types=return_types,
            new_col_names=new_col_names,
            reset_order=reset_order,
            **kwargs,
        )
        dataframe_column_names = [
            self.get_df_column_name(col_name)
            for col_name in new_query_tree.get_column_names()
        ]
        return self.__constructor__(
            new_query_tree,
            new_column_labels=(dataframe_column_names),
            new_row_labels=self._row_labels_cache,
            new_dtypes=replace_dtype_column_names(
                new_query_tree.get_root().get_column_types(), dataframe_column_names
            ),
            new_row_positions=self._row_positions_cache,
        )

    def cumulative_func(self, function, skipna, window=None):
        new_query_tree = self._query_tree.add_cumulative_function(
            function, self.database_columns, skipna, window
        )
        new_column_labels, new_dtypes = get_column_names_and_types_from_query_tree(
            new_query_tree, self.get_db_to_df_map()
        )
        return self.__constructor__(
            new_query_tree,
            new_column_labels=new_column_labels,
            new_row_labels=self._row_labels_cache,
            new_dtypes=new_dtypes,
            new_row_positions=self._row_positions_cache,
        )

    def abs(self):
        new_query_tree = self._query_tree.add_abs(self.database_columns)
        new_column_labels, new_dtypes = get_column_names_and_types_from_query_tree(
            new_query_tree, self.get_db_to_df_map()
        )
        return self.__constructor__(
            new_query_tree,
            new_column_labels=new_column_labels,
            new_row_labels=self._row_labels_cache,
            new_dtypes=new_dtypes,
            new_row_positions=self._row_positions_cache,
        )

    def round(self, decimals):
        new_query_tree = self._query_tree.add_round(self.database_columns, decimals)
        new_column_labels, new_dtypes = get_column_names_and_types_from_query_tree(
            new_query_tree, self.get_db_to_df_map()
        )
        return self.__constructor__(
            new_query_tree,
            new_column_labels=new_column_labels,
            new_row_labels=self._row_labels_cache,
            new_dtypes=new_dtypes,
            new_row_positions=self._row_positions_cache,
        )

    def str_extract(self, pat, flags, expand):
        import re

        n = re.compile(pat).groups
        new_query_tree = self._query_tree.add_str_extract(
            self.database_columns, pat, flags, expand
        )
        if expand or n > 1:
            new_column_labels = [i for i in range(n)]
        else:
            new_column_labels = [
                self.get_df_column_name(col_name)
                for col_name in new_query_tree.get_column_names()
            ]

        return self.__constructor__(
            new_query_tree,
            new_column_labels,
            new_row_labels=self._row_labels_cache,
            new_dtypes=new_query_tree.get_root().get_column_types(),
            new_row_positions=self._row_positions_cache,
        )

    def str_partition(self, sep, expand):
        new_query_tree = self._query_tree.add_str_partition(
            self.database_columns, sep, expand
        )
        if expand:
            new_column_labels = pandas.RangeIndex(start=0, stop=3, step=1)
        else:
            new_column_labels = [
                self.get_df_column_name(col_name)
                for col_name in new_query_tree.get_column_names()
            ]
        return self.__constructor__(
            new_query_tree,
            new_column_labels,
            new_row_labels=self._row_labels_cache,
            new_dtypes=new_query_tree.get_column_types(),
            new_row_positions=self._row_positions_cache,
        )

    def str_rpartition(self, sep, expand):
        new_query_tree = self._query_tree.add_str_rpartition(
            self.database_columns, sep, expand
        )
        if expand:
            new_column_labels = pandas.RangeIndex(start=0, stop=3, step=1)
        else:
            new_column_labels = new_query_tree.get_root().get_column_names()
        return self.__constructor__(
            new_query_tree,
            new_column_labels,
            new_row_labels=self._row_labels_cache,
            new_dtypes=new_query_tree.get_column_types(),
            new_row_positions=self._row_positions_cache,
        )

    def isin(
        self,
        values: Union["DBMSDataframe", Dict],
        ignore_indices: bool,
        self_is_series: bool,
    ):
        # we need to check the columns in the query tree implementation anyway, so we
        # don't have to worry about accessing uncached self.columns.
        if isinstance(values, dict):
            db_values = replace_map_with_database_columns(
                values, self.get_db_to_df_map()
            )
            new_query_tree = self._query_tree.add_isin_dict(db_values)
        else:
            # TODO: The following may be a lie, but we would have to write tests
            # to be sure
            # We do isin with series and dataframe by merging with the values. We want
            # to merge on the index of each frame (i.e. left_index=True,
            # right_index=True) but we don't have general support for that yet, so for
            # now only support merging two identical positional indexes.
            # TODO: once merge() supports joining on index, join on index, but beware
            # that in that case, we have to distinguish between nulls produced by the
            # join and nulls that were orginally in `values`.
            assert isinstance(values, DBMSDataframe)
            if not isinstance(values.index, DBMSPositionMapping) or not isinstance(
                self.index, DBMSPositionMapping
            ):
                raise make_exception(
                    NotImplementedError,
                    PonderError.ISIN_WITH_NON_RANGE_INDEX,
                    message="Cannot do isin with indexes that are not simple "
                    + "positional indexes yet",
                )
            if not self.index.position_map.equals(values.index.position_map):
                raise make_exception(
                    NotImplementedError,
                    PonderError.ISIN_WITH_DIFFERENT_POSITION_MAPS,
                    message="Cannot do isin with indexes that have  different "
                    + "position maps yet",
                )
            original_column_names = self._query_tree.get_column_names()
            original_column_types = self._query_tree.get_column_types()
            if ignore_indices:
                # When values is a series, its name doesn't matter. Rename the series
                # to a name that we can recognize after the join (this could be
                # accomplished more precisely with suffixes, but this hack should
                # work unless the internal name conflicts with data column names)
                values = values.rename(
                    new_col_labels=[__ISIN_SERIES_VALUES_COLUMN_NAME__]
                )
                values = values.pushdown_df_names_to_query_tree()
                intermediate_tree = self._query_tree.add_join(
                    values._query_tree,
                    how="left",
                    left_on=["LEFT_ORDER"],
                    right_on=["RIGHT_ORDER"],
                    suffixes=["", ""],
                )
                new_query_tree = intermediate_tree.add_dataframe_isin_series(
                    original_column_names,
                    original_column_types,
                    values.dtypes[0],
                )
            else:
                intermediate_tree = self._query_tree.add_join(
                    values._query_tree,
                    how="left",
                    left_on=["LEFT_ORDER"],
                    right_on=["RIGHT_ORDER"],
                    suffixes=[
                        __ISIN_DATAFRAME_LEFT_PREFIX__,
                        __ISIN_DATAFRAME_RIGHT_PREFIX__,
                    ],
                )
                new_query_tree = intermediate_tree.add_dataframe_isin_dataframe(
                    original_column_names,
                    values._query_tree.get_column_names(),
                )
        return self.__constructor__(
            new_query_tree,
            new_column_labels=self.columns,
            new_row_labels=self._row_labels_cache,
            new_dtypes=[np.bool_] * len(self.columns),
            new_row_positions=self._row_positions_cache,
        )

    def reindex_columns(self, column_names: pandas.Index):
        new_dtypes = [
            self.dtypes[c] if c in self.columns else np.float64 for c in column_names
        ]
        database_column_list = [
            self.get_db_column_name(col_name) for col_name in column_names
        ]
        new_query_tree = self._query_tree.add_null_columns(
            self.database_columns, database_column_list, new_dtypes
        )
        return self.__constructor__(
            query_tree=new_query_tree,
            new_column_labels=column_names,
            new_row_labels=self._row_labels_cache,
            new_dtypes=new_dtypes,
            new_row_positions=self._row_positions_cache,
        )

    def reindex_rows(self, row_labels: Union[DBMSIndex, DBMSPositionMapping]):
        return row_labels._dataframe.mask(col_positions=[]).concat(
            axis=1, others=[self], how="left", sort=False
        )

    def compare(self, other: "DBMSDataframe") -> "DBMSDataframe":
        """Compare two dataframes.

        This method assumes the two dataframes have the same row and column labels, and
        that every column in the dataframes has at least one diff.

        Parameters
        ----------
        other : DBMSDataframe
            The dataframe to compare to.

        Returns
        -------
        DBMSDataframe
            A dataframe with the compare() result. If the original frame has columns
            A, B, and C, the result frame will have columns A_self, A_other, B_self,
            B_other, C_self, C_other. Where columns A and B have no diff, the values
            will be None or NaN. Where columns A and B have a diff, the values will be
            the original values from the corresponding column in the original frames.
            Only rows with at least one diff will be present in the result frame.
        """
        # if self.index is a DBMSIndex, it can have duplicate values, and that makes
        # joining on the index complicated. API layer should have guaranteed that the
        # indexes of the two frames are equal, so always join on order, which is unique.
        merged_tree = self._query_tree.add_join(
            other._query_tree,
            how="left",
            left_on=["LEFT_ORDER"],
            right_on=["RIGHT_ORDER"],
            suffixes=[
                "_x",
                "_y",
            ],
            use_db_index=True,
        )
        new_query_tree = merged_tree.add_compare_post_join(
            self.database_columns, self._query_tree.get_column_types()
        )
        new_df_columns = generate_add_compare_post_join_columns(
            self.columns, suffixes=["self", "other"]
        )
        return self.__constructor__(
            new_query_tree,
            new_column_labels=new_df_columns,
            new_row_labels=self._row_labels_cache,
            new_dtypes=new_query_tree.dtypes,
            new_row_positions=self._row_positions_cache,
        ).filter_rows(
            # Drop rows that have no diff. A row has no diff if and only if all entries
            # are None or NaN. None and NaN compare equal, so any row with only None
            # and NaN for each column has all entries equal.
            RowWiseFilterPredicates.DropNaRows(
                how="all", columns=new_df_columns, thresh=None
            )
        )

    def melt(
        self,
        id_vars,
        value_var,
        var_name,
        value_name,
        col_level,
        ignore_index,
    ):
        renamed_query_tree = get_renamed_query_tree_with_df_column_names(self)
        new_query_tree = renamed_query_tree.add_melt(
            id_vars=id_vars,
            value_var=value_var,
            var_name=var_name,
            value_name=value_name,
            col_level=col_level,
            ignore_index=ignore_index,
        )
        return self.__constructor__(
            new_query_tree,
            new_column_labels=new_query_tree.get_column_names(),
            new_row_labels=None,
            new_dtypes=new_query_tree.get_column_types(),
            new_row_positions=None,
        )

    def apply(
        self,
        func,
        axis,
        raw,
        result_type,
        output_meta,
        apply_type,
        na_action,  # This only applies to applymap and Series.map
        func_args,
        func_kwargs,
    ):
        # Need to be able to handle DataFrame and Series
        if isinstance(output_meta, pandas.DataFrame):
            output_columns = output_meta.columns.tolist()
            output_columns_dtypes = output_meta.dtypes.tolist()
            db_output_column_types = output_columns_dtypes
            # detect list return types for object dtypes so
            # we can tell the database what the real type is
            for i, dt in enumerate(output_columns_dtypes):
                # the real types of an object can be mixed
                # here we make the assumption that everything
                # is the same and there are no NaNs
                if dt == np.dtype("O"):
                    if is_list_like(output_meta[output_columns[i]][0]):
                        db_output_column_types[i] = [type(list())]
        elif isinstance(output_meta, pandas.Series):
            output_columns = [__PONDER_REDUCED_COLUMN_NAME__]
            output_columns_dtypes = [output_meta.dtypes]
            # detect a list within the series using the first value
            # the dtype for this is normally "object" but we
            # want to return an ARRAY from the database not a
            # TEXT
            if is_list_like(output_meta[0]):
                db_output_column_types = [type(list())]
            else:
                db_output_column_types = output_columns_dtypes

        if axis == 1:
            if isinstance(self.index, DBMSIndex):
                if len(self.index.names) > 1:
                    row_labels_dtypes = self.index.dtypes
                else:
                    row_labels_dtypes = [self.index.dtype]
            else:
                row_labels_dtypes = [self.index.type]
        else:
            row_labels_dtypes = [output_meta.index.dtype]

        # we can't know if the function does something with column names
        # so we put back the original column names..
        new_query_tree = get_renamed_query_tree_with_df_column_names(self)
        # We ASSUME that the order and position column dtypes don't change
        new_query_tree = new_query_tree.add_apply(
            func,
            output_columns,
            output_columns_dtypes,
            db_output_column_types,
            axis,
            result_type,
            row_labels_dtypes,
            apply_type,
            na_action,
            func_args,
            func_kwargs,
        )
        if axis == 1:
            return self.__constructor__(
                new_query_tree,
                new_column_labels=(new_query_tree.get_column_names()),
                new_row_labels=copy_index_with_qt_df_having_same_column_names(self),
                new_dtypes=new_query_tree.get_column_types(),
                new_row_positions=self._row_positions_cache,
            )
        else:
            new_index_columns = [__PONDER_STORED_PROC_ROW_LABEL_COLUMN_NAME__]
            new_row_label_column_types = (
                new_query_tree.get_root().get_row_labels_column_types()
            )
            new_row_labels = DBMSIndex(
                new_index_columns, new_row_label_column_types, None
            )
            ret_df = self.__constructor__(
                new_query_tree,
                new_column_labels=(new_query_tree.get_column_names()),
                new_row_labels=new_row_labels,
                new_dtypes=new_query_tree.get_column_types(),
                new_row_positions=None,
            )
            ret_df.index.name = __UNNAMED_INDEX_COLUMN__
            return ret_df

    def _replace_all(self, value):
        new_query_tree = self._query_tree.add_replace_all(value)
        return self.__constructor__(
            new_query_tree,
            new_column_labels=self.columns,
            new_row_labels=self._row_labels_cache,
            new_dtypes=pandas.Series(
                new_query_tree.get_column_types(), index=self.columns
            ),
            new_row_positions=self._row_positions_cache,
        )

    def clip(self, lower, upper, axis):
        new_tree = self._query_tree.add_clip(
            columns=self._query_tree.get_column_names(),
            lower_list=lower,
            upper_list=upper,
        )
        return self.__constructor__(
            new_tree,
            new_column_labels=self.columns,
            new_row_labels=self._row_labels_cache,
            new_dtypes=new_tree.dtypes,
            new_row_positions=self._row_positions_cache,
        )

    def cut(self, bins, labels, precision, right, include_lowest):
        """Cut columns into bins."""
        new_tree = self._query_tree.add_cut(
            bins, labels, precision, right, include_lowest
        )
        return self.__constructor__(
            new_tree,
            new_column_labels=self.columns,
            new_row_labels=self._row_labels_cache,
            new_dtypes=new_tree.dtypes,
            new_row_positions=self._row_positions_cache,
        )

    def pct_change(self, periods):
        """Return percent change between pairs of values."""
        new_tree = self._query_tree.add_pct_change(periods)
        return self.__constructor__(
            new_tree,
            new_column_labels=self.columns,
            new_row_labels=self._row_labels_cache,
            new_dtypes=new_tree.dtypes,
            new_row_positions=self._row_positions_cache,
        )

    def diff(self, periods, axis):
        """Return discrete difference between pairs of elements."""
        new_tree = self._query_tree.add_diff(periods)
        return self.__constructor__(
            new_tree,
            new_column_labels=self.columns,
            new_row_labels=self._row_labels_cache,
            new_dtypes=new_tree.dtypes,
            new_row_positions=self._row_positions_cache,
        )

    def pushdown_df_names_to_query_tree(self):
        new_tree = get_renamed_query_tree_with_df_column_names(self)
        return self.__constructor__(
            new_tree,
            new_column_labels=self.columns,
            new_row_labels=copy_index_with_qt_df_having_same_column_names(self),
            new_dtypes=self.dtypes,
            new_row_positions=self._row_positions_cache,
        )

    @property
    def debug_vis(self):
        return self._query_tree.debug_vis

    def invert(self):
        return self.__constructor__(
            self._query_tree.add_invert(),
            new_column_labels=self._column_labels_cache,
            new_row_labels=self._row_labels_cache,
            new_dtypes=self._column_types_cache,
            new_row_positions=self._row_positions_cache,
        )


class TransposedDBMSDataframe:
    def __init__(self, original_frame: DBMSDataframe):
        self._untransposed_frame = original_frame

    @property
    def columns(self):
        return self._untransposed_frame.index

    @property
    def index(self):
        return self._untransposed_frame.columns

    @property
    def dtypes(self):
        if len(self.columns) == 0:
            return pandas.Series(dtype=np.dtype("O"), index=self.columns)
        # A given column of the transposed frame has one element coming from each column
        # of the original dataframe, so the dtype of each column of the transposed frame
        # is the common type of the dtypes of the original frame.
        return pandas.Series(
            [find_common_type(list(self._untransposed_frame.dtypes))]
            * len(self.columns),
            index=self.columns._to_pandas(),
            dtype=object,
        )

    def __getattr__(self, name):
        # __getattr__ only called when normal attribute lookup fails
        if hasattr(self._untransposed_frame, name):
            attr = getattr(self._untransposed_frame, name)
            if callable(attr):
                raise make_exception(
                    NotImplementedError,
                    PonderError.TRANSPOSED_METHOD_NOT_IMPLEMENTED,
                    f"Method {name} not implemented for transposed dataframes",
                )
        raise make_exception(
            AttributeError,
            PonderError.TRANSPOSED_DATAFRAME_ATTRIBUTE_NOT_FOUND,
            f"Transposed dataframe has no attribute {name}.",
        )

    def rename(
        self,
        new_row_labels: Optional[Union[Dict[Hashable, Hashable], List]] = None,
        new_row_labels_names: Optional[list[str]] = None,
        new_col_labels: Optional[Union[Dict[Hashable, Hashable], List]] = None,
        new_col_labels_name: Optional[str] = None,
    ):
        if new_row_labels_names is None:
            new_col_labels_name_for_transpose = new_row_labels_names
        elif len(new_row_labels_names) != 1:
            raise make_exception(
                NotImplementedError,
                PonderError.TRANSPOSED_RENAME_MULTIPLE_ROW_LABELS_NAMES_NOT_IMPLEMENTED,
                f"Cannot rename transposed frame row labels to {new_row_labels_names}",
            )
        else:
            new_col_labels_name_for_transpose = new_row_labels_names[0]
        return self._untransposed_frame.rename(
            new_row_labels=new_col_labels,
            new_row_labels_names=(
                new_col_labels_name
                if new_col_labels_name is None
                else [new_col_labels_name]
            ),
            new_col_labels=new_row_labels,
            new_col_labels_name=new_col_labels_name_for_transpose,
        ).transpose()

    def to_pandas(self):
        return self._untransposed_frame.to_pandas().transpose()

    def mask(
        self,
        row_labels: Optional[List[Hashable]] = None,
        row_positions: Optional[List[int]] = None,
        col_labels: Optional[List[Hashable]] = None,
        col_positions: Optional[List[int]] = None,
    ):
        return self._untransposed_frame.mask(
            row_labels=col_labels,
            row_positions=col_positions,
            col_labels=row_labels,
            col_positions=row_positions,
        ).transpose()

    def transpose(self):
        return self._untransposed_frame

    def binary_op_with_scalar(self, *args, **kwargs):
        return self._untransposed_frame.binary_op_with_scalar(
            *args, **kwargs
        ).transpose()

    def binary_op(
        self, op, right_frame, join_type="outer", axis=None, sort_columns=True
    ):
        if not sort_columns:
            # sort_column=False means we have to skip sorting the rows of the
            # untransposed frame, which I suppose means we remove the "order by" in
            # the join. We can think about that later.
            raise make_exception(
                NotImplementedError,
                PonderError.TRANSPOSED_BINARY_OP_SORT_COLUMNS_FALSE_NOT_IMPLEMENTED,
                "Cannot perform binary operation on transposed frame with "
                + "sort_columns=False",
            )
        return self._untransposed_frame.binary_op(
            op,
            right_frame.transpose(),
            join_type,
            axis,
            sort_columns=True,
        ).transpose()

    def from_labels(self, drop: bool):
        if not drop:
            raise make_exception(
                NotImplementedError,
                PonderError.TRANSPOSED_FROM_LABELS_DROP_FALSE_NOT_IMPLEMENTED,
                "Cannot reset index on transposed frame with drop=False",
            )
        return self._untransposed_frame.rename(
            new_col_labels=[
                str(i) for i in range(len(self._untransposed_frame.columns))
            ]
        ).transpose()

    def reduce(
        self,
        func: REDUCE_FUNCTION,
        axis: Axis,
        dtypes: Optional[object] = None,
        percentile: Optional[float] = None,
        params_list: Optional[object] = None,
    ):
        """Reduce the given axis to length 1 by applying the given function.

        Parameters
        ----------
        func : REDUCE_FUNCTION
            The reduce function.
        axis : Axis
            The axis to reduce.
        dtypes: object, optional
            The dtypes of the result.
        percentile: float, optional
            percentile for percentile reduction. This param is not valid for
            row-wise reduce.
        params_list: object, optional
            parameter list for func. This param is not valid for
            row-wise reduce.

        Returns
        -------
        DBMSDataframe
            A new dataframe resulting from the reduction.
        """
        if axis is Axis.ROW_WISE:
            assert len(dtypes) == 1, "dtypes must be a single dtype for row-wise reduce"
            untransposed_frame_dtypes = pandas.Series(
                dtypes[0] * len(self.index),
                index=(
                    self.index._to_pandas()
                    if hasattr(self.index, "_to_pandas")
                    else self.index
                ),
                dtype=object,
            )
        else:
            if len(self.index) == 0:
                untransposed_frame_dtypes = pandas.Series(dtype=np.dtype("O"))
            else:
                untransposed_frame_dtypes = pandas.Series(
                    [find_common_type(list(dtypes))],
                    index=[__PONDER_REDUCED_COLUMN_NAME__],
                    dtype=object,
                )
        return self._untransposed_frame.reduce(
            func,
            axis=(Axis.COL_WISE if axis is Axis.ROW_WISE else Axis.ROW_WISE),
            dtypes=untransposed_frame_dtypes,
            percentile=percentile,
            params_list=params_list,
        ).transpose()

    def pushdown_df_names_to_query_tree(self):
        return self._untransposed_frame.pushdown_df_names_to_query_tree().transpose()
