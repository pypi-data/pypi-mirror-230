from __future__ import annotations

import copy
import functools
import inspect
import itertools
import logging
import os
import random
import string
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Union

import numpy as np
import pandas
import pandas._libs.lib as lib
from pandas._typing import DtypeObj
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_dtype,
    is_dict_like,
    is_float_dtype,
    is_integer_dtype,
    is_list_like,
    is_string_dtype,
    is_timedelta64_dtype,
)
from pandas.core.dtypes.common import is_numeric_dtype, pandas_dtype
from pandas.core.reshape.tile import _format_labels

from ponder.core.common import get_execution_configuration
from ponder.core.dataframequerytreehelper import (
    generate_db_column_names,
    replace_dtype_column_names,
)
from ponder.core.error_codes import PonderError, make_exception
from ponder.core.sql_dialect import _pandas_offset_object_to_n_and_sql_unit

from .common import (
    __PONDER_AGG_OTHER_COL_ID__,
    __PONDER_AGG_OTHER_COL_NAME__,
    __PONDER_ORDER_COLUMN_NAME__,
    __PONDER_REDUCED_COLUMN_NAME__,
    __PONDER_ROW_LABELS_COLUMN_NAME__,
    __PONDER_STORED_PROC_ROW_LABEL_COLUMN_NAME__,
    __SQL_QUERY_LEN_LIMIT__,
    GROUPBY_FUNCTIONS,
    MAP_FUNCTION,
    REDUCE_FUNCTION,
    MapFunction,
    UnionAllDataForDialect,
    generate_column_name_from_value,
    groupby_function_to_reduce_enum,
    groupby_view_funcs,
    groupby_window_funcs,
)

logger = logging.getLogger(__name__)

# python versions older than 3.9 do not support the cache function,
# which per the docs is the same thing as lru_cache(maxsize=None).
if sys.version_info < (3, 9):
    cache = functools.lru_cache(maxsize=None)
else:
    cache = functools.cache


def _rangify(i):
    for a, b in itertools.groupby(enumerate(i), lambda pair: pair[1] - pair[0]):
        b = list(b)
        yield b[0][1], b[-1][1]


def _rewrite_literal_for_binary_op(
    literal: Any, literal_type: Union[type, pandas_dtype], connection
) -> Any:
    if isinstance(literal, str):
        return f"'{literal}'"
    if literal_type == pandas.Timestamp:
        return connection.scalar_timestamp_for_subtraction(literal)
    if literal_type == pandas.Timedelta:
        return connection.timedelta_to_datetime_addend(literal)
    if literal_type == pandas.tseries.offsets.DateOffset:
        raise make_exception(
            NotImplementedError,
            PonderError.BINARY_OP_WITH_DATEOFFSET_SCALAR_NOT_SUPPORTED,
            "Binary operations with DateOffset are not supported",
        )
    if issubclass(literal_type, pandas.tseries.offsets.BaseOffset):
        # for date offsets like pandas._libs.tslibs.offsets.Hour
        try:
            timedelta = pandas.to_timedelta(literal)
        except ValueError:
            # sometimes the number of nanoseconds in an offset is not well defined, e.g.
            # pd.to_timedelta(pd.DateOffset(month=1)).
            # TODO(https://ponderdata.atlassian.net/browse/POND-873): support this
            raise make_exception(
                NotImplementedError,
                PonderError.BINARY_OP_WITH_OFFSET_SCALAR_NOT_CONVERTABLE_TO_NANOSECONDS,
                (
                    "Ponder Internal Error: Cannot add or subtract time offsets that "
                    + "can't be converted to nanoseconds"
                ),
            )
        return connection.timedelta_to_datetime_addend(timedelta)
    if literal is None or np.isnan(literal):
        return "NULL"
    return literal


class RowWiseFilterPredicates:
    class RowWiseFilterPredicate(ABC):
        @abstractmethod
        def generate_predicate(self, conn) -> str:
            pass

        def update_column_names(self, column_name_mapper, index_column_name_mapper):
            pass

        def get_new_column_name(
            self, column_name, column_name_mapper, index_column_name_mapper
        ):
            new_column_name = column_name_mapper.get_db_name_from_df_name(column_name)
            if new_column_name == column_name:
                if index_column_name_mapper is None:
                    return new_column_name
                return index_column_name_mapper.get_db_name_from_df_name(column_name)
            return new_column_name

    class RowValueEqualsGroupByLookupKey(RowWiseFilterPredicate):
        def __init__(self, by_columns: Iterable, lookup_key: Iterable):
            self._by_columns = by_columns
            self.lookup_key = lookup_key

        @cache
        def generate_predicate(self, conn) -> str:
            return conn.generate_row_value_equals_group_by_key_predicate(
                self._by_columns, self.lookup_key
            )

        def update_column_names(self, column_name_mapper, index_column_name_mapper):
            new_by_columns = [
                self.get_new_column_name(
                    col_name, column_name_mapper, index_column_name_mapper
                )
                for col_name in self._by_columns
            ]
            return RowWiseFilterPredicates.RowValueEqualsGroupByLookupKey(
                new_by_columns, self.lookup_key
            )

    class RowValueNotEquals(RowWiseFilterPredicate):
        def __init__(self, column_name: str, index_values: Iterable):
            self._column_name = column_name
            self._index_values = index_values

        @cache
        def generate_predicate(self, conn) -> str:
            return conn.generate_row_value_not_equals_predicate(
                self._column_name, self._index_values
            )

        def update_column_names(self, column_name_mapper, index_column_name_mapper):
            new_column_name = self.get_new_column_name(
                self._column_name, column_name_mapper, index_column_name_mapper
            )
            return RowWiseFilterPredicates.RowValueNotEquals(
                new_column_name, self._index_values
            )

    class RowValueGE(RowWiseFilterPredicate):
        def __init__(self, column_name: str, value):
            self._column_name = column_name
            self._value = value

        @cache
        def generate_predicate(self, conn) -> str:
            return conn.generate_row_ge_value_predicate(self._column_name, self._value)

        def update_column_names(self, column_name_mapper, index_column_name_mapper):
            new_column_name = self.get_new_column_name(
                self._column_name, column_name_mapper, index_column_name_mapper
            )
            return RowWiseFilterPredicates.RowValueGE(new_column_name, self._value)

    class RowValueLE(RowWiseFilterPredicate):
        def __init__(self, column_name: str, value):
            self._column_name = column_name
            self._value = value

        @cache
        def generate_predicate(self, conn) -> str:
            return conn.generate_row_le_value_predicate(self._column_name, self._value)

        def update_column_names(self, column_name_mapper, index_column_name_mapper):
            new_column_name = self.get_new_column_name(
                self._column_name, column_name_mapper, index_column_name_mapper
            )
            return RowWiseFilterPredicates.RowValueLE(new_column_name, self._value)

    class RowValueBetweenInclusive(RowWiseFilterPredicate):
        def __init__(self, column_name: str, value_start, value_stop):
            self._column_name = column_name
            self._value_start = value_start
            self._value_stop = value_stop

        @cache
        def generate_predicate(self, conn) -> str:
            return conn.generate_row_between_inclusive_predicate(
                self._column_name, self._value_start, self._value_stop
            )

        def update_column_names(self, column_name_mapper, index_column_name_mapper):
            new_column_name = self.get_new_column_name(
                self._column_name, column_name_mapper, index_column_name_mapper
            )
            return RowWiseFilterPredicates.RowValueBetweenInclusive(
                new_column_name, self._value_start, self._value_stop
            )

    class TimesInRange(RowWiseFilterPredicate):
        def __init__(
            self,
            column_name: str,
            start_time_micros: int,
            end_time_micros: int,
            include_start: bool,
            include_end: bool,
            compare_start_to_utc_time: bool,
            compare_end_to_utc_time: bool,
        ):
            self._column_name = column_name
            self._start_time_micros = start_time_micros
            self._end_time_micros = end_time_micros
            self._include_start = include_start
            self._include_end = include_end
            self._compare_start_to_utc_time = compare_start_to_utc_time
            self._compare_end_to_utc_time = compare_end_to_utc_time

        def generate_predicate(self, conn) -> str:
            return conn.generate_between_time_filter_expression(
                self._column_name,
                self._start_time_micros,
                self._end_time_micros,
                self._include_start,
                self._include_end,
                self._compare_start_to_utc_time,
                self._compare_end_to_utc_time,
            )

        def update_column_names(self, column_name_mapper, index_column_name_mapper):
            new_column_name = self.get_new_column_name(
                self._column_name, column_name_mapper, index_column_name_mapper
            )
            return RowWiseFilterPredicates.TimesInRange(
                new_column_name,
                self._start_time_micros,
                self._end_time_micros,
                self._include_start,
                self._include_end,
                self._compare_start_to_utc_time,
                self._compare_end_to_utc_time,
            )

    class ColumnIsMax(RowWiseFilterPredicate):
        def __init__(self, column_name: str, by_columns: Optional[List] = None):
            self._column_name = column_name
            # _by_columns are for specific cases like groupby.idxmax
            self._by_columns = by_columns

        def generate_predicate(self, conn) -> str:
            return conn.generate_column_is_max_predicate(
                self._column_name, self._by_columns
            )

        def update_column_names(self, column_name_mapper, index_column_name_mapper):
            new_column_name = self.get_new_column_name(
                self._column_name, column_name_mapper, index_column_name_mapper
            )
            new_by_columns = None
            if self._by_columns:
                new_by_columns = [
                    column_name_mapper.get_db_name_from_df_name(col_name)
                    for col_name in self._by_columns
                ]
            return RowWiseFilterPredicates.ColumnIsMax(new_column_name, new_by_columns)

    class ColumnIsMin(RowWiseFilterPredicate):
        def __init__(self, column_name: str, by_columns: Optional[List] = None):
            self._column_name = column_name
            # _by_columns are for specific cases like groupby.idxmin
            self._by_columns = by_columns

        def generate_predicate(self, conn) -> str:
            return conn.generate_column_is_min_predicate(
                self._column_name, self._by_columns
            )

        def update_column_names(self, column_name_mapper, index_column_name_mapper):
            new_column_name = self.get_new_column_name(
                self._column_name, column_name_mapper, index_column_name_mapper
            )
            new_by_columns = None
            if self._by_columns:
                new_by_columns = [
                    column_name_mapper.get_db_name_from_df_name(col_name)
                    for col_name in self._by_columns
                ]
            return RowWiseFilterPredicates.ColumnIsMin(new_column_name, new_by_columns)

    class DropNaRows(RowWiseFilterPredicate):
        def __init__(self, how: str, thresh: Optional[int], columns: list[str]):
            self._how = how
            self._thresh = thresh
            self._columns = columns

        def generate_predicate(self, conn) -> str:
            return conn.generate_drop_na_rows_predicate(
                self._how, self._thresh, self._columns
            )

        def update_column_names(self, column_name_mapper, index_column_name_mapper):
            new_columns = None
            if self._columns:
                new_columns = [
                    self.get_new_column_name(
                        col_name, column_name_mapper, index_column_name_mapper
                    )
                    for col_name in self._columns
                ]
            return RowWiseFilterPredicates.DropNaRows(
                self._how, self._thresh, new_columns
            )

    class DatesWithinOffsetOfMin(RowWiseFilterPredicate):
        def __init__(self, column_name: str, offset: pandas.DateOffset):
            self._column_name = column_name
            self._offset = offset

        def generate_predicate(self, conn) -> str:
            return conn.generate_dates_within_offset_of_min_predicate(
                self._column_name, self._offset
            )

        def update_column_names(self, column_name_mapper, index_column_name_mapper):
            new_column = self.get_new_column_name(
                self._column_name, column_name_mapper, index_column_name_mapper
            )
            return RowWiseFilterPredicates.DatesWithinOffsetOfMin(
                new_column, self._offset
            )

    class DatesWithinOffsetOfMax(RowWiseFilterPredicate):
        def __init__(self, column_name: str, offset: pandas.DateOffset):
            self._column_name = column_name
            self._offset = offset

        def generate_predicate(self, conn) -> str:
            return conn.generate_dates_within_offset_of_max_predicate(
                self._column_name, self._offset
            )

        def update_column_names(self, column_name_mapper, index_column_name_mapper):
            new_column = self.get_new_column_name(
                self._column_name, column_name_mapper, index_column_name_mapper
            )
            return RowWiseFilterPredicates.DatesWithinOffsetOfMax(
                new_column, self._offset
            )


def throw_exception_on_cross_database_operations():
    raise make_exception(
        NotImplementedError,
        PonderError.CROSS_DATABASE_QUERIES_NOT_SUPPORTED,
        ("Ponder does not support cross-database operations yet."),
    )


class QueryTree(object):
    """A QueryTree is a tree of nodes that represents a query.

    The query tree's interface is IMMUTABLE. After you construct a query
    tree, none of its exposed attributes should change.
    """

    def __init__(self, conn, root):
        self._conn = conn
        self._root = root

    @staticmethod
    def make_tree_from_table(conn, sql, order_column_name=""):
        return QueryTree(conn=conn, root=LeafNode(sql, conn, order_column_name))

    @staticmethod
    def make_tree_from_raw_sql(
        conn, sql_query, column_names, column_types, order_column_name=""
    ):
        return QueryTree(
            conn=conn,
            root=RawSQLLeafNode(
                conn, sql_query, column_names, column_types, order_column_name
            ),
        )

    @staticmethod
    def make_tree_from_csv(
        conn,
        file_path,
        sep,
        header,
        skipfooter,
        parse_dates,
        date_format,
        na_values,
        names=lib.no_default,
        dtype=None,
        on_bad_lines="error",
        order_column_name=__PONDER_ORDER_COLUMN_NAME__,
    ):
        logger = logging.getLogger()
        logger.debug("Determining schema for file")
        csv_file_df = pandas.read_csv(
            file_path,
            sep=sep,
            header=header,
            parse_dates=parse_dates,
            date_format=date_format,
            na_values=na_values,
            names=names,
            dtype=dtype,
            on_bad_lines=on_bad_lines,
            # It's possible to have a dtype mismatch since we read only part of
            # the data.
            nrows=1000,
        )
        logger.debug("Finished determining schema for file")
        table_name = f"""PONDER_{"".join(
            random.choices(string.ascii_uppercase, k=10)
        )}"""

        # don't need to pass the names and dtypes since that'll be taken from the
        # dataframe we created above.
        return QueryTree(
            conn=conn,
            root=CsvNode(
                conn,
                table_name,
                csv_file_df,
                file_path,
                sep,
                header,
                skipfooter,
                parse_dates,
                date_format,
                na_values,
                on_bad_lines,
                order_column_name,
            ),
        )

    @staticmethod
    def make_tree_from_parquet(
        conn, file_path, engine, columns, storage_options, use_nullable_dtypes
    ):
        from fsspec.core import url_to_fs

        logger = logging.getLogger()
        logger.debug("Determining schema for file")

        # We are trying to get the engine specific information about the dataset
        # We want the paths to the parquet files in the dataset
        # We then want to stage each one of these files to the staging area

        from pyarrow._dataset import HivePartitioning
        from pyarrow.parquet import ParquetDataset

        storage_options = storage_options if storage_options else {}
        fs, fs_path = url_to_fs(file_path, **storage_options)

        dataset = ParquetDataset(fs_path, filesystem=fs, use_legacy_dataset=False)

        # Some DBs don't like it when we have file:// prepended to local files
        if "file" in fs.protocol:
            fs_files = dataset.files
        else:
            fs_files = [fs.unstrip_protocol(fpath) for fpath in dataset.files]

        table_name = f"""PONDER_{"".join(
            random.choices(string.ascii_uppercase, k=10)
        )}"""

        pandas_types = {}
        df_columns = []
        # Sometimes the pandas_metadata may not be defined, so we need to
        # comb through and get the dtypes ourselves.
        if dataset.schema.pandas_metadata:
            for col in dataset.schema.pandas_metadata["columns"]:
                pandas_types[col["name"]] = col["pandas_type"]
                df_columns.append(col["name"])
        else:
            for field in dataset.schema:
                df_columns.append(field.name)
                pandas_types[field.name] = np.dtype(field.type.to_pandas_dtype())

        df_dtypes = pandas.Series(pandas_types)

        hive_partitioning = (
            True if isinstance(dataset.partitioning, HivePartitioning) else False
        )
        logger.debug("Finished determining schema for file")

        return QueryTree(
            conn=conn,
            root=ParquetNode(
                conn,
                table_name=table_name,
                column_names=df_columns,
                column_types=df_dtypes,
                files=fs_files,
                columns=columns,
                storage_options=storage_options,
                fs=fs,
                hive_partitioning=hive_partitioning,
            ),
        )

    @staticmethod
    def make_tree_from_pdf(conn, pdf):
        return QueryTree(conn=conn, root=PdfNode(conn, pdf))

    def make_tree_from_pdf_using_connection(self, pdf):
        return QueryTree.make_tree_from_pdf(self._conn, pdf)

    def get_row_transfer_limit(self):
        return self._conn.get_row_transfer_limit()

    @classmethod
    def build(cls, sql, conn):
        return cls(LeafNode(sql, conn))

    def get_column_names(self):
        return self._root.get_column_names()

    def get_dataframe_column_names(self):
        return self._root.get_dataframe_column_names()

    def get_column_types(self):
        return self._root.get_column_types()

    def get_row_labels_column_names(self):
        return self._root.get_row_labels_column_names()

    @property
    def dtypes(self) -> pandas.Series:
        # TODO(REFACTOR): use this property in many places where we zip column names
        # and types together.
        return self._root.dtypes

    @property
    def columns(self) -> pandas.Index:
        return self._root.columns

    def get_conn(self):
        return self._conn

    def get_num_rows(self):
        return self._conn.get_num_rows(self)

    def get_unique_values(self, column):
        return self._conn.get_unique_values(self._root, column)

    def generate_sanitized_values(self, value_list):
        return self._conn.generate_sanitized_values(value_list)

    def data_hash(self):
        """Get a hash of all leaf nodes within this tree."""
        return self._root.data_hash()

    def add_merge_asof(
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
        merge_asof_node = MergeAsOfNode(
            self._conn,
            self.get_root(),
            other.get_root(),
            left_on,
            right_on,
            left_by,
            right_by,
            suffixes,
            tolerance,
            allow_exact_matches,
            direction,
        )
        real_node = merge_asof_node.get_real_node()
        new_tree = QueryTree(self._conn, real_node)
        return new_tree

    def handle_join_on_columns(self, join_node):
        if len(join_node._matched_fields) == 0:
            return join_node

        if join_node._suffixes is None:
            return join_node

        left_on = join_node._left_on

        join_node_columns = join_node.get_column_names()
        join_node_column_types = join_node.get_column_types()
        suffixes = join_node._suffixes

        final_column_names = []
        final_column_expressions = []
        final_dtypes = []

        for column_name, column_type in zip(join_node_columns, join_node_column_types):
            # join_node._matched_fields has the names of the columns on the
            # right side of the on clause that originally had the same names
            # as the columns on the left side of the on clause. Pandas behavior is
            # to coalesce same named columns from the on clause.
            if column_name in join_node._matched_fields:
                continue

            # We can unconditionally add the type of the column.
            final_dtypes.append(column_type)

            # If the column doesn't appear in the "on" clause, we leave it alone.
            if column_name not in left_on:
                final_column_names.append(column_name)
                final_column_expressions.append(column_name)
                continue

            # Now we're in business.
            original_column_name = column_name
            if original_column_name.endswith(suffixes[0]):
                original_column_name = column_name[: -len(suffixes[0])]
            if original_column_name + suffixes[1] in join_node._matched_fields:
                final_column_names.append(original_column_name)
                final_column_expressions.append(
                    self._conn.generate_coalesce(
                        [
                            original_column_name + suffixes[0],
                            original_column_name + suffixes[1],
                        ]
                    )
                )
            else:
                final_column_names.append(column_name)
                final_column_expressions.append(column_name)
        final_node = ChangeColumns(
            self._conn,
            join_node,
            final_column_names,
            final_column_expressions,
            final_dtypes,
            join_node.get_order_column_name(),
            False,
        )
        return final_node

    def add_join(
        self,
        right,
        how,
        left_on,
        right_on,
        suffixes,
        order_column_name="",
        use_db_index: bool = False,
        indicator: bool = False,
    ):
        logger.debug(f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}""")
        # traceback.print_stack()

        join_node = EquiJoinNode(
            self._conn,
            self._root,
            right._root,
            how,
            left_on,
            right_on,
            suffixes,
            order_column_name,
            use_db_index,
            indicator=indicator,
        )

        join_node = self.handle_join_on_columns(join_node)
        new_tree = QueryTree(self._conn, join_node)
        return new_tree

    def add_filter(
        self,
        condition: RowWiseFilterPredicates.RowWiseFilterPredicate,
        order_column_name="",
    ):
        new_node = FilterNode(self._conn, self._root, condition, order_column_name)
        new_tree = QueryTree(self._conn, new_node)
        return new_tree

    def add_project(
        self,
        columns_selection,
        project_column_names=None,
        project_column_types=None,
        order_column_name="",
    ):
        new_node = ProjectNode(
            self._conn,
            self._root,
            columns_selection,
            project_column_names,
            project_column_types,
            order_column_name,
        )
        new_tree = QueryTree(self._conn, new_node)
        return new_tree

    def add_map(self, fn: MapFunction, labels_to_apply_over=None):
        # TODO: Separate the implementation details for str_split and str_rsplit from
        # the implementation of add_map.
        if (
            fn._id in (MAP_FUNCTION.str_split, MAP_FUNCTION.str_rsplit)
            and fn._params_list[3] is True
        ):
            assert len(labels_to_apply_over) == 1
            fn._params_list[2] = self._conn.get_max_str_splits(
                self, labels_to_apply_over[0], fn._params_list[1], fn._params_list[2]
            )

        map_node = MapNode(
            self._conn,
            self._root,
            fn,
            labels_to_apply_over,
            self._root.get_order_column_name(),
        )
        if (
            fn._id in (MAP_FUNCTION.str_split, MAP_FUNCTION.str_rsplit)
            and fn._params_list[3] is True
        ):
            intermediate_tree = QueryTree(self._conn, map_node)
            n = fn._params_list[2] + 1
            final_column_names = [f"Part_{i}" for i in range(n)]
            final_column_expressions = self._conn.generate_map_column_expressions(
                labels_to_apply_over,
                n,
            )
            final_dtypes = [np.dtype("O")] * n
            final_node = ChangeColumns(
                self._conn,
                intermediate_tree._root,
                final_column_names,
                final_column_expressions,
                final_dtypes,
                intermediate_tree._root.get_order_column_name(),
                False,
            )
            final_tree = QueryTree(self._conn, final_node)
            return final_tree
        new_query_tree = QueryTree(self._conn, map_node)
        return new_query_tree

    def add_column_wise_reduce(
        self,
        fn: REDUCE_FUNCTION,
        new_dtypes: pandas.Series,
        labels_to_apply_over=None,
        percentile: float = None,
        params_list: object = None,
        other_col_id=None,
    ):
        new_node = ColumnWiseReduceNode(
            self._conn,
            self._root,
            fn,
            labels_to_apply_over,
            new_dtypes,
            percentile,
            params_list,
            other_col_id,
        )
        new_tree = QueryTree(self._conn, new_node)
        return new_tree

    def add_row_wise_reduce(
        self,
        fn: REDUCE_FUNCTION,
        new_column_name,
        new_dtype: pandas_dtype,
        order_column_name="",
    ):
        new_node = RowWiseReduceNode(
            self._conn, self._root, fn, new_column_name, new_dtype, order_column_name
        )
        return QueryTree(self._conn, new_node)

    def add_mask(
        self,
        column_names_for_filter,
        row_positions,
        col_positions,
        order_column_name,
    ):
        new_node = SelectFromWhereNode(
            self._conn,
            self._root,
            column_names_for_filter,
            row_positions,
            col_positions,
            order_column_name,
        )
        return QueryTree(self._conn, new_node)

    def add_literal_columns(self, new_columns, new_dtypes: Iterable, values: Iterable):
        new_node = LiteralColumnNode(
            self._conn, self._root, new_columns, new_dtypes, values
        )
        new_tree = QueryTree(self._conn, new_node)
        return new_tree

    def add_null_columns(self, current_columns, new_columns, new_dtypes: Iterable):
        new_node = NullColumnNode(
            self._conn, self._root, current_columns, new_columns, new_dtypes
        )
        new_tree = QueryTree(self._conn, new_node)
        return new_tree

    def add_union_all(self, right_trees, new_dtypes: pandas.Series):
        new_node = UnionAllNode(
            self._conn, self._root, [r._root for r in right_trees], new_dtypes
        )
        reorder_node = ReassignOrderPostUnionAllNode(self._conn, new_node)
        new_tree = QueryTree(self._conn, reorder_node)
        return new_tree

    def generate_row_numbers(self, keep_old_row_numbers=False, order_column_name=""):
        new_node = RowNumberNode(self._conn, self._root, keep_old_row_numbers)
        new_tree = QueryTree(self._conn, new_node)
        return new_tree

    def add_binary_comparison(
        self, op, other, columns: pandas.Series, column_types, self_on_right
    ):
        new_node = BinaryComparisonNode(
            self._conn, self._root, op, other, columns, column_types, self_on_right
        )
        new_tree = QueryTree(self._conn, new_node)
        return new_tree

    def add_get_from_binary_comparison(self, other):
        new_node = GetFromBinaryComparisonNode(self._conn, self._root, other)
        new_tree = QueryTree(self._conn, new_node)
        return new_tree

    # Walk over the columns in the "by" query tree and graft them onto
    # the current query tree.
    def merge_replace(self, target_query_node, source_query_node):
        clauses = source_query_node.get_predicates()
        source_columns = source_query_node.get_column_names()

        # SelectFromWhereNodes has get_predicates but sometimes they don't do anything.
        # We can short circuit this case by checking if the lhs is a column and that
        # there is no op.
        if all(clause._op == "" and clause._lhs_is_column for clause in clauses):
            return target_query_node

        column_names_list = []
        column_expressions_list = []
        column_types_list = []
        for col, expression in zip(source_columns, clauses):
            column_names_list.append(col)
            column_expressions_list.append(str(expression))
            column_types_list.append(expression.return_type())

        for col, col_type in zip(
            target_query_node.get_column_names(),
            target_query_node.get_column_types(),
        ):
            if col not in source_columns:
                column_names_list.append(col)
            else:
                # for now renaming to something predictable.  I (batur) believe
                # we will need to revisit this feature since it doesn't correspond
                # to what Pandas will do here. Once we have feedback on what
                # makes sense - we can reimplement.
                column_names_list.append(f"{col}_RENAMED")
            column_expressions_list.append(self._conn.format_name(col))
            column_types_list.append(col_type)
        change_columns = ChangeColumns(
            target_query_node._conn,
            target_query_node,
            column_names_list,
            column_expressions_list,
            column_types_list,
            target_query_node.get_order_column_name(),
            False,
        )
        return change_columns

    def merge_grouper(self, source_query_node, grouper, resample_args):
        # TODO: we will need to handle upsampling too at some point, which
        # might require some more resample code refactoring which we can try
        # to do later.
        index_col_expression = self._conn.generate_downsample_function(
            col=grouper.key,
            offset=resample_args["offset"],
            start_val=resample_args["index_start"],
            end_val=resample_args["index_end"],
            sum_interval=resample_args["sum_index_interval"],
        )

        column_names_list = []
        column_expressions_list = []
        column_types_list = []

        for col, col_type in zip(
            source_query_node.get_column_names(),
            source_query_node.get_column_types(),
        ):
            column_names_list.append(col)
            column_types_list.append(col_type)
            if col == grouper.key:
                column_expressions_list.append(index_col_expression)
            else:
                column_expressions_list.append(self._conn.format_name(col))

        return ChangeColumns(
            source_query_node._conn,
            source_query_node,
            column_names_list,
            column_expressions_list,
            column_types_list,
            source_query_node.get_order_column_name(),
            False,
        )

    def add_groupby(
        self,
        by,
        as_index,
        operator,
        sort_by_group_keys,
        columns_to_aggregate: Optional[Iterable],
        agg_args: Optional[tuple] = None,
        agg_kwargs: Optional[Dict] = None,
        dropna: bool = True,
        other_col_id=None,
        row_labels_dtypes=None,
    ):
        node = self._root

        # We can have multiple objs in by, so we want to iterate over each
        # one and see which ones require grafting.
        for obj, param in by.get_map().items():
            if param.get("graft_predicates"):
                if isinstance(obj, QueryTree):
                    obj_node = obj.get_root()
                else:
                    obj_node = obj
                # obj_node may not be an actual QueryNode
                predicates = (
                    obj_node.get_predicates()
                    if hasattr(obj_node, "get_predicates")
                    else []
                )
                if len(predicates) > 0:
                    node = self.merge_replace(node, obj_node)
                elif isinstance(obj_node, pandas.Grouper):
                    node = self.merge_grouper(
                        node, obj_node, param.get("resample_args")
                    )

        # Very particular case, but if we are doing a groupby with nth and
        # as_index is not true, then we want to return the original order
        # and basically ignore sorting by the group keys.
        if operator == GROUPBY_FUNCTIONS.NTH and not as_index:
            sort_by_group_keys = False

        # Note that by is a ByParams object
        by_columns = by.columns

        # Fast track this case, we can probably do the same for the other
        # view functions.
        # Should we move this check to the dataframe layer and then just call
        # add_filter and bypass the groupby node altogether?
        if operator == GROUPBY_FUNCTIONS.GET_GROUP:
            lookup_key = agg_kwargs.get("name", None)
            if len(by_columns) > 1:
                if not isinstance(lookup_key, tuple):
                    raise make_exception(
                        ValueError,
                        PonderError.GROUPBY_GET_GROUP_KEY_NOT_TUPLE,
                        "must supply a tuple to get_group with multiple grouping keys",
                    )
                elif len(by_columns) != len(lookup_key):
                    raise make_exception(
                        ValueError,
                        PonderError.GROUPBY_GET_GROUP_KEY_NOT_SAME_LENGTH_AS_BY,
                        "must supply a same-length tuple to get_group"
                        + " with multiple grouping keys",
                    )
                # For the sake of consistency, let's convert lookup_key to a list
                lookup_key = list(lookup_key)
            else:
                lookup_key = [lookup_key]

            predicate = RowWiseFilterPredicates.RowValueEqualsGroupByLookupKey(
                by_columns, lookup_key
            )
            new_node = FilterNode(
                self._conn,
                node,
                predicate,
                order_column_name=node.get_order_column_name(),
            )
        elif operator in (GROUPBY_FUNCTIONS.IDXMAX, GROUPBY_FUNCTIONS.IDXMIN):
            # Need to determine what columns we are going to aggregate
            new_node = self._get_groupby_idx_minmax(
                node,
                by_columns=by_columns,
                operator=operator,
                columns_to_aggregate=columns_to_aggregate,
                sort_by_group_keys=sort_by_group_keys,
                row_labels_dtypes=row_labels_dtypes,
            )
        else:
            new_node = GroupByNode(
                self._conn,
                node,
                by_columns,
                operator,
                sort_by_group_keys,
                columns_to_aggregate,
                agg_args=agg_args,
                agg_kwargs=agg_kwargs,
                dropna=dropna,
                other_col_id=other_col_id,
            )

        # Assigning a meaningful label to groupby results didn't make sense
        # so we usually decide to get rid of them. There are some points where
        # we need to keep them though, namely for the groupby_window_funcs.
        if as_index:
            new_row_label_column_names = by_columns
        else:
            # TODO: get rid of these special case checks once we handle metadata
            # correctly in GroupByNode.
            # We can't assume that we will get row labels from our input node
            if operator in groupby_window_funcs or operator in groupby_view_funcs:
                new_row_label_column_names = node.get_row_labels_column_names()
            else:
                new_row_label_column_names = []

        if operator == GROUPBY_FUNCTIONS.FIRST or operator == GROUPBY_FUNCTIONS.LAST:
            # First and last window functions force us to reduce after
            groupby_reduce_node = GroupByNode(
                self._conn,
                new_node,
                by_columns,
                GROUPBY_FUNCTIONS.MIN,
                sort_by_group_keys,
                columns_to_aggregate,
                agg_args=agg_args,
                agg_kwargs=agg_kwargs,
                dropna=dropna,
                other_col_id=other_col_id,
            )
            if as_index:
                new_row_label_column_names = by_columns
            else:
                new_row_label_column_names = []
            groupby_reduce_correct_labels = NewRowLabelsColumnsNode(
                self._conn, groupby_reduce_node, None, new_row_label_column_names
            )
            return QueryTree(self._conn, groupby_reduce_correct_labels)

        # TODO: should fix data column names, row label column names, and data column
        # types coming out of GroupByNode instead of adding this node with
        # new_row_labels=None. @mvashishtha thinks the GroupByNode by itself is invalid
        # because those outputs are incorrect.
        new_node = NewRowLabelsColumnsNode(
            self._conn,
            new_node,
            new_row_labels=None,
            new_row_label_column_names=new_row_label_column_names,
        )
        return QueryTree(self._conn, new_node)

    def _get_groupby_idx_minmax(
        self,
        node,
        by_columns,
        operator,
        columns_to_aggregate,
        sort_by_group_keys,
        row_labels_dtypes,
    ):
        if columns_to_aggregate is None:
            columns_to_aggregate = [
                n for n in node.get_column_names() if n not in by_columns
            ]

        if len(columns_to_aggregate) > 1:
            raise make_exception(
                ValueError,
                PonderError.GROUPBY_IDX_MINMAX_MULTIPLE_COLUMNS,
                """we should only process one column at a time for
                    groupby.idxmax/idxmin""",
            )

        col_name = columns_to_aggregate[0]

        # First we filter out with qualify the positions, then we sort if
        # needed and then we pick the columns that we need
        col_node = FilterNode(
            self._conn,
            self._root,
            RowWiseFilterPredicates.ColumnIsMin(col_name, by_columns)
            if operator == GROUPBY_FUNCTIONS.IDXMIN
            else RowWiseFilterPredicates.ColumnIsMax(col_name, by_columns),
            self._root.get_order_column_name(),
        )
        if sort_by_group_keys:
            sort_cols = by_columns
        else:
            sort_cols = [__PONDER_ORDER_COLUMN_NAME__]

        col_node = OrderByNode(
            self._conn,
            col_node,
            columns=sort_cols,
            ascending=True,
            keep_old_row_numbers=False,
            handle_duplicates=None,
        )

        # TODO: currently don't handle cases where we have MultiIndex columns
        # and we are trying to get idxmax/idxmin.
        if len(col_node.get_row_labels_column_names()) > 1:
            raise make_exception(
                NotImplementedError,
                PonderError.GROUPBY_IDX_MINMAX_MULTIINDEX,
                """idxmax()/idxmin() with multiindex is not supported yet""",
            )

        # Need to get the column names that we care about for our result
        new_column_names = []
        new_column_types = []
        new_column_expressions = []
        for col, dtype in zip(col_node.get_column_names(), col_node.get_column_types()):
            # If the column is in by, then we add those in as is
            # If the column is the column we are looking at, then the expression should
            # capture the row labels
            if col in by_columns:
                new_column_names.append(col)
                new_column_types.append(dtype)
                new_column_expressions.append(self._conn.format_name(col))
            elif col == col_name:
                # Since we don't support MultiIndex, we can assume that the
                # length of the row labels and its dtypes is just 1.
                new_column_names.append(col)
                new_column_types.append(row_labels_dtypes[0])
                new_column_expressions.extend(
                    self._conn.format_names_list(col_node.get_row_labels_column_names())
                )

        return ChangeColumns(
            self._conn,
            node=col_node,
            column_names=new_column_names,
            column_expressions=new_column_expressions,
            column_types=new_column_types,
            order_column_name=self._root.get_order_column_name(),
            has_aggregation=False,
        )

    def add_sort(self, columns, ascending, keep_old_row_numbers, handle_duplicates):
        new_node = OrderByNode(
            self._conn,
            self._root,
            columns,
            ascending,
            keep_old_row_numbers,
            handle_duplicates,
        )
        return QueryTree(self._conn, new_node)

    def add_binary_post_join(
        self, left_columns, left_types, right_columns, right_types, suffixes, op
    ):
        new_node = BinaryPostJoinNode(
            self._conn,
            self._root,
            left_columns,
            left_types,
            right_columns,
            right_types,
            suffixes,
            op,
        )
        return QueryTree(self._conn, new_node)

    def add_column_rename(self, column_renames: dict):
        new_node = RenameColumnsNode(self._conn, self._root, column_renames)
        return QueryTree(self._conn, new_node)

    def add_derived_column(self, column_tree: "QueryTree", new_column_name):
        new_node = DerivedColumnNode(
            self._conn, self._root, column_tree._root, new_column_name
        )
        return QueryTree(self._conn, new_node)

    def add_replace_value(self, column_name, replace_values_dict):
        new_node = ReplaceValueNode(
            self._conn, self._root, column_name, replace_values_dict
        )
        return QueryTree(self._conn, new_node)

    def add_pivot(
        self,
        grouping_column_name,
        pivot_column_name,
        values_column_name,
        unique_values,
        aggfunc,
        add_qualifier_to_new_column_names=True,
    ):
        from .pivot import PivotNode

        new_node = PivotNode(
            self._conn,
            self._root,
            grouping_column_name,
            pivot_column_name,
            values_column_name,
            unique_values,
            aggfunc,
            add_qualifier_to_new_column_names,
        )
        if grouping_column_name is not None:
            new_node = NewRowLabelsColumnsNode(
                self._conn, new_node, None, [grouping_column_name]
            )
        return QueryTree(self._conn, new_node)

    def add_get_dummies(self, column, unique_values, prefix: str, prefix_sep: str):
        new_node = GetDummiesNode(
            self._conn, self._root, column, unique_values, prefix, prefix_sep
        )
        return QueryTree(self._conn, new_node)

    def add_idx_minmax(self, index_column_name, index_column_type, min: bool):
        column_nodes = []

        # new_dtypes needs to be a Series for UnionAllNode
        # It's possible that COLUMN_NAME is not an object type, so we will
        # need to handle that at some point.
        new_dtypes = pandas.Series(
            {
                "COLUMN_NAME": np.dtype("O"),
                __PONDER_REDUCED_COLUMN_NAME__: index_column_type,
            },
            dtype=object,
        )

        for col_name in self._root.get_column_names():
            col_node = FilterNode(
                self._conn,
                self._root,
                RowWiseFilterPredicates.ColumnIsMin(col_name)
                if min
                else RowWiseFilterPredicates.ColumnIsMax(col_name),
                self._root.get_order_column_name(),
            )
            # Putting the column names in single quotes will set the value of
            # COLUMN_NAME to actually have the column name.
            column_name_expression = f"'{col_name}'"
            column_value_expression = (
                f"MIN({self._conn.format_name(index_column_name)})"
            )
            col_node = ChangeColumns(
                self._conn,
                node=col_node,
                column_names=[
                    "COLUMN_NAME",
                    __PONDER_REDUCED_COLUMN_NAME__,
                ],
                column_expressions=[
                    column_name_expression,
                    column_value_expression,
                ],
                column_types=new_dtypes.tolist(),
                order_column_name=self._root.get_order_column_name(),
                has_aggregation=True,
            )
            column_nodes.append(col_node)
        idx_node = UnionAllNode(
            self._conn, column_nodes[0], column_nodes[1:], new_dtypes
        )
        # UnionAllNode postjoin to maintain the order
        reorder_node = ReassignOrderPostUnionAllNode(self._conn, idx_node)

        # We set the new row labels to be COLUMN_NAME
        row_labels_node = NewRowLabelsColumnsNode(
            self._conn, reorder_node, None, ["COLUMN_NAME"]
        )
        return QueryTree(self._conn, row_labels_node)

    def add_row_labels_columns(
        self, new_row_labels: Optional[dict], new_row_labels_names: list[str]
    ):
        new_node = NewRowLabelsColumnsNode(
            self._conn,
            self._root,
            new_row_labels,
            new_row_labels_names,
        )
        return QueryTree(self._conn, new_node)

    def reset_row_labels_columns(
        self, row_labels_types: list[DtypeObj], drop: bool, index_pos_map: bool
    ):
        """Convert row labels columns to data columns.

        Parameters:
            row_labels_types: list[DtypeObj]
                The types of the row labels columns.
            drop: bool
                Whether or not to drop the row labels from the columns.
            index_pos_map: bool
                Whether or not the Index is a position map.
        Returns:
            A new QueryTree with the row labels columns converted to data columns.
        """
        new_column_names = []
        column_expressions = []
        if not drop:
            if index_pos_map:
                new_column_names.append("index")
                column_expressions.append(
                    self._conn.format_name(__PONDER_ORDER_COLUMN_NAME__)
                )
            else:
                row_labels_column_names = self._root.get_row_labels_column_names()
                new_column_names.extend(row_labels_column_names)
                column_expressions.extend(
                    [self._conn.format_name(n) for n in row_labels_column_names]
                )
        new_column_names.extend([*self._root.get_column_names()])
        column_expressions.extend(
            [self._conn.format_name(n) for n in self._root.get_column_names()]
        )
        new_root = ChangeColumns(
            conn=self._conn,
            node=self._root,
            column_names=new_column_names,
            column_expressions=column_expressions,
            column_types=(
                *([] if drop else row_labels_types),
                *self._root.get_column_types(),
            ),
            order_column_name=self._root.get_order_column_name(),
            has_aggregation=False,
            new_row_labels_column_names=[],
        )
        return QueryTree(self._conn, root=new_root)

    def add_broadcast_binary_op(self, broadcast_tree, op, new_columns):
        new_node = BroadcastBinaryOpNode(
            self._conn, self._root, broadcast_tree._root, op, new_columns
        )
        new_tree = QueryTree(self._conn, new_node)
        return new_tree

    def execute(self):
        return self._conn.execute(self._root)

    def to_pandas(self):
        return self._conn.to_pandas(self._root)

    def to_csv(self, path, sep=",", header=True, date_format=None, na_rep=""):
        return self._conn.to_csv(
            path=path,
            node=self._root,
            sep=sep,
            header=header,
            date_format=date_format,
            na_rep=na_rep,
        )

    def get_root(self):
        return self._root

    def _is_monotonic(self, increasing):
        if len(self._root.get_column_names()) != 1:
            raise make_exception(
                ValueError,
                PonderError.IS_MONOTONIC_WITH_MULTIPLE_COLUMNS,
                "DataFrame can have only one column for invoking"
                " is_monotonic variants",
            )

        # start by creating a project node that computes the LAG value.
        column_name = self._root.get_column_names()[0]
        lag_val_column_name = f"LAG_{column_name}"
        lag_val_column_expression = self._conn.generate_lag_val_expr(
            column_name, self._root.get_order_column_name()
        )
        inner_node = ChangeColumns(
            self._conn,
            self._root,
            [column_name, lag_val_column_name],
            [column_name, lag_val_column_expression],
            [
                self._root.get_column_types()[0],
                self._root.get_column_types()[0],
            ],
            self._root.get_order_column_name(),
        )

        inner_tree = QueryTree(self._conn, inner_node)

        # now create the intermediate that adds the IFF condition.
        intermediate_column_name = f"FLAG_{column_name}"
        intermediate_column_expression = (
            self._conn._dialect.generate_monotonic_intermediate(
                increasing, lag_val_column_name, column_name
            )
        )
        intermediate_node = ChangeColumns(
            self._conn,
            inner_tree._root,
            [intermediate_column_name],
            [intermediate_column_expression],
            [np.dtype(bool)],
            inner_tree._root.get_order_column_name(),
        )
        intermediate_tree = QueryTree(self._conn, intermediate_node)

        # finally the result that does the BOOLAND_AGG
        final_column_name = "MONOTONIC_RESULT"
        final_column_expression = (
            self._conn._dialect.generate_reduction_column_transformation(
                REDUCE_FUNCTION.LOGICAL_AND,
                self._conn.format_name(intermediate_column_name),
            )
        )

        final_node = ChangeColumns(
            self._conn,
            intermediate_tree._root,
            [final_column_name, inner_tree._root.get_order_column_name()],
            [final_column_expression, "1"],
            [np.dtype(bool), np.dtype(int)],
            intermediate_tree._root.get_order_column_name(),
            True,
        )
        final_tree = QueryTree(self._conn, final_node)
        return final_tree

    def is_monotonic_increasing(self):
        return self._is_monotonic(True)

    def is_monotonic_decreasing(self):
        return self._is_monotonic(False)

    def to_sql(
        self,
        table_name,
        row_labels_column_types: list[np.dtype],
        if_exists="fail",
        index=True,
        index_label=None,
    ):
        self._conn.materialize_rows_to_table(
            table_name,
            self._root.get_column_names(),
            self._root.get_column_types(),
            if_exists,
            index,
            index_label,
            self._root.get_row_labels_column_names(),
            row_labels_column_types,
            self._root.generate_sql(),
        )

    def add_dot_product(
        self, left_frame, right_frame, transposed=False, transposed_other=False
    ):
        dot_prod_node = DotProductNode(
            conn=self._conn,
            left_input_node=self._root,
            left_index=left_frame.index,
            right_input_node=right_frame._query_tree._root,
            right_index=right_frame.index,
            transposed=transposed,
            transposed_other=transposed_other,
        )
        return QueryTree(self._conn, dot_prod_node)

    def add_dropna(
        self,
        axis: int,
        how,
        thresh,
        subset,
        index_name,
    ):
        return (
            self.add_filter(
                RowWiseFilterPredicates.DropNaRows(
                    how, thresh, self.get_column_names() if subset is None else subset
                )
            )
            if axis == 0
            else self.add_project(
                self._conn.generate_drop_na_columns_query(
                    how, thresh, subset, index_name, self.get_column_names()
                ),
                project_column_names=None,
                project_column_types=None,
            )
        )

    def add_pandas_mask(
        self,
        binary_pred,
        columns,
        value_dict,
        columns_to_upcast_to_object,
    ):
        column_expressions = [
            self._conn.generate_pandas_mask(
                f"{binary_pred}",
                column_name,
                value_dict,
                column_name in columns_to_upcast_to_object,
            )
            for column_name in columns
        ]
        change_columns_node = ChangeColumns(
            self._conn,
            self._root,
            columns,
            column_expressions,
            self._root.get_column_types(),
            self._root.get_order_column_name(),
        )
        return QueryTree(self._conn, change_columns_node)

    def add_fillna(
        self,
        value,
        method,
        limit,
        columns,
        dtypes,
        group_cols,
        columns_to_upcast_to_object,
    ):
        if method is not None:
            columns_selection = self._conn.generate_method_fill_na(
                method, limit, columns, group_cols
            )
            new_query_tree = self.add_project(
                columns_selection=columns_selection,
                project_column_names=columns,
                project_column_types=dtypes,
            )
            return new_query_tree

        column_names = columns
        column_expressions = [
            self._conn.generate_value_dict_fill_na(
                column_name,
                value,
                limit,
                group_cols,
                column_name in columns_to_upcast_to_object,
            )
            for column_name in columns
        ]
        change_columns_node = ChangeColumns(
            self._conn,
            self._root,
            column_names,
            column_expressions,
            dtypes,
            self._root.get_order_column_name(),
        )
        new_query_tree = QueryTree(self._conn, change_columns_node)
        return new_query_tree

    def add_cast_function(
        self,
        cast_from_map,
        cast_to_map,
        columns,
        return_types,
        new_col_names=None,
        reset_order=False,
        **kwargs,
    ):
        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name} columns -->\n
        {columns}
        self._root.get_column_names() -->\n
        {self._root.get_column_names()}\n
        new_col_names -->\n
        {new_col_names}
        """
        )

        casted_columns_expressions = self._conn.generate_casted_columns(
            columns, cast_from_map, cast_to_map, **kwargs
        )
        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            New ChangeColumns QueryTree node\n
            column_names -->\n
            {(
                self._root.get_column_names()
                if new_col_names is None
                else new_col_names
            )}\n
            column_expressions -->\n
            {casted_columns_expressions}\n
            column_types -->\n
            {return_types}\n
            order_column_name -->\n
            {self._root.get_order_column_name()}
            reset_order -->\n
            {reset_order}
            """
        )
        change_columns_node = ChangeColumns(
            conn=self._conn,
            node=self._root,
            column_names=(
                self._root.get_column_names()
                if new_col_names is None
                else new_col_names
            ),
            column_expressions=casted_columns_expressions,
            column_types=return_types,
            order_column_name=self._root.get_order_column_name(),
            has_aggregation=False,
            reset_order=reset_order,
        )
        new_query_tree = QueryTree(self._conn, change_columns_node)
        return new_query_tree

    def add_with_self_cross_join(
        self,
        columns,
        kwargs,
    ):
        """This is a generic function with a template to create the following
        type of SQL query Feel free to hack it as per your needs as currently
        it is only spcific to
        rolling(window=<window>,win_type='gaussian').sum(std=<std>) WITH <view-
        name>(<c1, c2, c3...>) AS (SELECT columns FROM <input node>) SELECT.

        <fixed-statements>, <IFF based clauses or other aggregations>
        FROM <view-name> as T1, <view-name> as T2 WHERE <selection
        predicates> AND <join-predicates> GROUP BY <group-by clause>
        ORDER BY <order-by clause>
        """

        cross_joins_kwargs = copy.deepcopy(kwargs)
        win_func = cross_joins_kwargs.get("win_func", None)
        win_type = cross_joins_kwargs.get("win_type", None)

        new_columns = [col for col in columns]
        new_dtypes = [type for type in self._root.get_column_types()]
        if win_func in ["STDDEV", "VARIANCE"] and win_type.lower() in ["gaussian"]:
            cross_joins_kwargs["win_func"] = "AVG"
            view_names = cross_joins_kwargs.get("view_names", None)

            new_columns += [f"{col+'_MU'}" for col in columns]
            column_expressions = [
                f"{view_names[0]}.{self._conn.format_name(col)}" for col in columns
            ]
            column_expressions += [
                self._conn.generate_with_cross_join_col_expr(
                    col, kwargs=copy.deepcopy(cross_joins_kwargs)
                )
                for col in columns
            ]
            new_dtypes += self._root.get_column_types()
        else:
            column_expressions = [
                self._conn.generate_with_cross_join_col_expr(
                    col, kwargs=copy.deepcopy(cross_joins_kwargs)
                )
                for col in columns
            ]

        cross_joins_kwargs = copy.deepcopy(kwargs)
        win_func = cross_joins_kwargs.get("win_func", None)
        win_type = cross_joins_kwargs.get("win_type", None)

        new_columns = [col for col in columns]
        new_dtypes = [type for type in self._root.get_column_types()]
        if win_func in ["STDDEV", "VARIANCE"] and win_type.lower() in ["gaussian"]:
            # In the case of gaussian-weighted standard deviation and variance, we need
            # to first compute the gaussian-weighted average, and then in a second step
            # plug that average (or mu) into the formula for stdev or variance.
            cross_joins_kwargs["win_func"] = "AVG"
            view_names = cross_joins_kwargs.get("view_names", None)

            # For each column, we'll add an additional column to store its average (mu).
            new_columns += [f"{col+'_MU'}" for col in columns]
            column_expressions = [
                f"{view_names[0]}.{self._conn.format_name(col)}" for col in columns
            ]
            column_expressions += [
                self._conn.generate_with_cross_join_col_expr(
                    col, kwargs=copy.deepcopy(cross_joins_kwargs)
                )
                for col in columns
            ]
            new_dtypes += self._root.get_column_types()
        else:
            column_expressions = [
                self._conn.generate_with_cross_join_col_expr(
                    col, kwargs=copy.deepcopy(cross_joins_kwargs)
                )
                for col in columns
            ]

        first_cross_join_node = WithClauseCrossJoin(
            self._conn,
            self._root,
            new_columns,
            column_expressions,
            new_dtypes,
            self._root.get_order_column_name(),
            kwargs=kwargs,
        )

        if win_func in ["STDDEV", "VARIANCE"] and win_type.lower() in ["gaussian"]:
            change_columns_kwargs = copy.deepcopy(kwargs)
            change_columns_kwargs["win_func"] = win_func
            column_expressions = [
                self._conn.generate_with_cross_join_col_expr(
                    col, kwargs=copy.deepcopy(change_columns_kwargs)
                )
                for col in columns
            ]

            second_cross_join_node = WithClauseCrossJoin(
                self._conn,
                first_cross_join_node,
                columns,
                column_expressions,
                self._root.get_column_types(),
                self._root.get_order_column_name(),
                kwargs=kwargs,
            )
            return QueryTree(self._conn, second_cross_join_node)

        return QueryTree(self._conn, first_cross_join_node)

    def add_cumulative_function(
        self,
        function,
        columns,
        skipna,
        window=None,
        non_numeric_cols=[],
        expanding=False,
        other_col_id=None,
    ):
        other_col = None if other_col_id is None else columns[other_col_id]
        col_funcs = (
            function.items()
            if isinstance(function, dict)
            else itertools.product(columns, [function])
        )
        column_expressions = [
            self._conn.generate_cumulative_function(
                col_func,
                col,
                skipna,
                window,
                non_numeric_col=(col in non_numeric_cols),
                expanding=expanding,
                other_col=other_col,
            )
            for col, col_func in col_funcs
        ]
        column_types = self._root.get_column_types()
        if other_col_id is not None:
            other_col = columns[other_col_id]
            columns = [
                __PONDER_AGG_OTHER_COL_ID__,
                __PONDER_AGG_OTHER_COL_NAME__,
            ] + list(columns)
            column_expressions = [
                f"{other_col_id}",
                f"'{other_col}'",
            ] + column_expressions
            column_types = (
                ["int", "object"] + column_types
                if isinstance(self._root, RenameColumnsNode)
                else column_types
            )

        change_columns_node = ChangeColumns(
            self._conn,
            self._root,
            columns,
            column_expressions,
            column_types,
            self._root.get_order_column_name(),
            has_aggregation=False,
        )
        new_query_tree = QueryTree(self._conn, change_columns_node)
        return new_query_tree

    def add_resample_function(
        self,
        index_dtype,
        function,
        columns,
        offset,
        start_val,
        end_val,
        sum_interval,
        interval,
        is_downsampling,
        agg_args,
        agg_kwargs,
    ):
        # Earlier layers should have assured there is only one row label column
        index_col_name = self._root.get_row_labels_column_names()[0]
        column_names = [index_col_name]
        if is_downsampling:
            index_col_expression = self._conn.generate_downsample_function(
                col=index_col_name,
                offset=offset,
                start_val=start_val,
                end_val=end_val,
                sum_interval=sum_interval,
            )
            column_expressions = [index_col_expression]
            for column_name in columns:
                column_names.append(column_name)
                column_expressions.append(self._conn.format_name(column_name))
            change_columns_node = ChangeColumns(
                conn=self._conn,
                node=self._root,
                column_names=column_names,
                column_expressions=column_expressions,
                column_types=[index_dtype, *self._root.get_column_types()],
                order_column_name=self._root.get_order_column_name(),
                has_aggregation=False,
            )
        else:
            # For the upsampling case, we want to reindex the dataframe with the new
            # upsampled index. `LeafNode` is used to compute the new upsampled index.
            # We then use `EquiJoinNode` as follows:

            # Left Table: self_with_index_reset._root
            # index, value
            # 12, A
            # 1, B
            # 2, C

            # Right Table: leaf_node
            # index, generate_series
            # 12, 12:00
            # 12, 12:30
            # 1, 1:00
            # 1, 1:30
            # 2, 2:00
            # 2, 2:30

            # Right join left table with right table
            # index_x, value, index_y, generate_series
            # 12, A, 12, 12:00
            # 12, A, 12, 12:30
            # 1, B, 1, 1:00
            # 1, B, 1, 1:30
            # 2, C, 2, 2:00
            # 2, C, 2, 2:30

            # Reset Index
            self_with_index_reset = self.reset_row_labels_columns(
                row_labels_types=[index_dtype],
                drop=False,
                index_pos_map=False,
            )
            # Generate Cast Expression
            n, unit = _pandas_offset_object_to_n_and_sql_unit(offset)
            if unit in ("second", "minute", "hour", "day"):
                # Cast to TIMESTAMP to match generated index type
                casted_index_col_expression = self._conn.generate_cast_to_type(
                    col=index_col_name,
                    cast_type="datetime",
                )
            else:
                # Cast to DATETIME to match generated index type
                casted_index_col_expression = self._conn.generate_cast_to_type(
                    col=index_col_name,
                    cast_type="date",
                )
            column_names = [index_col_name]
            column_expressions = [casted_index_col_expression]
            for column_name in columns:
                column_names.append(column_name)
                column_expressions.append(self._conn.format_name(column_name))
            change_columns_node = ChangeColumns(
                conn=self._conn,
                node=self_with_index_reset._root,
                column_names=column_names,
                column_expressions=column_expressions,
                column_types=self_with_index_reset._root.get_column_types(),
                order_column_name=self_with_index_reset._root.get_order_column_name(),
                has_aggregation=False,
            )
            # Use LeafNode for the right side of the join
            index_col_expression = self._conn.generate_upsample_function(
                col=index_col_name,
                offset=offset,
                start_val=start_val,
                end_val=end_val,
                sum_interval=sum_interval,
                interval=interval,
            )
            leaf_node = LeafNode(
                table_name=index_col_expression,
                conn=self._conn,
                retain_table_column_names=True,
            )
            # Perform Right Join
            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}"""
            )
            join_node = EquiJoinNode(
                conn=self._conn,
                left=change_columns_node,
                right=leaf_node,
                how="right",
                left_on=[index_col_name],
                right_on=[index_col_name],
                suffixes=("_x", "_y"),
                order_column_name=self._root.get_order_column_name(),
            )
            # Use ChangeColumns to drop unnecessary columns post-join
            # and populate with NaN values
            final_column_names = [index_col_name]
            final_column_expressions = [self._conn.format_name("generate_series")]
            for column_name in columns:
                final_column_names.append(column_name)
                final_column_expressions.append(
                    self._conn.generate_get_first_element_by_row_label_rank(
                        col=column_name,
                        # Note: Output of `EquiJoinNode` cannot be a multi-index
                        row_labels_column_name=join_node.get_row_labels_column_names()[
                            0
                        ],
                    )
                )
            change_columns_node = ChangeColumns(
                conn=self._conn,
                node=join_node,
                column_names=final_column_names,
                column_expressions=final_column_expressions,
                column_types=[index_dtype, *self._root.get_column_types()],
                order_column_name=self._root.get_order_column_name(),
                has_aggregation=False,
            )

        # Perform GroupBy Aggregation
        if function == GROUPBY_FUNCTIONS.GET_GROUP:
            # Special Case GROUPBY_FUNCTIONS.GET_GROUP direct to FilterNode
            predicate = RowWiseFilterPredicates.RowValueEqualsGroupByLookupKey(
                by_columns=[index_col_name], lookup_key=[agg_kwargs.get("name", None)]
            )
            groupby_node_with_wrong_labels = FilterNode(
                conn=self._conn,
                node=change_columns_node,
                predicate=predicate,
                order_column_name=change_columns_node.get_order_column_name(),
            )
        else:
            groupby_node_with_wrong_labels = GroupByNode(
                conn=self._conn,
                node=change_columns_node,
                by=[index_col_name],
                aggregation=function,
                sort_by_group_keys=True,
                columns_to_aggregate=None,
                order_column_name="",
                agg_args=agg_args,
                agg_kwargs=agg_kwargs,
            )

        # Correct GroupBy Labels
        if function in (
            GROUPBY_FUNCTIONS.FIRST,
            GROUPBY_FUNCTIONS.LAST,
            GROUPBY_FUNCTIONS.ASFREQ,
        ):
            # Case where we have a window function, so have to reduce after
            groupby_node_reduce = GroupByNode(
                conn=self._conn,
                node=groupby_node_with_wrong_labels,
                by=[index_col_name],
                aggregation=GROUPBY_FUNCTIONS.MIN,
                sort_by_group_keys=True,
                columns_to_aggregate=None,
            )
            groupby_node_with_correct_labels = NewRowLabelsColumnsNode(
                self._conn, groupby_node_reduce, None, [index_col_name]
            )
        else:
            groupby_node_with_correct_labels = NewRowLabelsColumnsNode(
                self._conn, groupby_node_with_wrong_labels, None, [index_col_name]
            )

        # Special case GroupBy Size since only one column is returned
        if function == GROUPBY_FUNCTIONS.SIZE:
            # COUNT(*) returns column `__reduced__`
            final_column_names = [columns[0]]
            final_column_expressions = [
                self._conn.format_name(__PONDER_REDUCED_COLUMN_NAME__)
            ]
            groupby_node_with_correct_labels = ChangeColumns(
                conn=self._conn,
                node=groupby_node_with_correct_labels,
                column_names=final_column_names,
                column_expressions=final_column_expressions,
                column_types=[np.dtype(">i1")],
                order_column_name=self._root.get_order_column_name(),
                has_aggregation=False,
            )

        # Ensure we include buckets with no values in downsampling case
        if is_downsampling and function != GROUPBY_FUNCTIONS.GET_GROUP:
            # Ensure we include buckets with no values
            # by essentially performing a reindex on the corrected
            # index
            index_col_expression = self._conn.generate_downsample_index_function(
                col=index_col_name,
                offset=offset,
                start_val=start_val,
                end_val=end_val,
            )
            # Use LeafNode to generate correct downsampling
            # index including buckets with no values
            leaf_node = LeafNode(
                table_name=index_col_expression,
                conn=self._conn,
                retain_table_column_names=True,
            )
            # Perform Left Join (essentially reindex)
            join_node = EquiJoinNode(
                conn=self._conn,
                left=leaf_node,
                right=groupby_node_with_correct_labels,
                how="left",
                left_on=["generate_series"],
                right_on=[index_col_name],
                suffixes=("_x", "_y"),
                order_column_name=self._root.get_order_column_name(),
            )

            if function == GROUPBY_FUNCTIONS.SIZE:
                # Special case for size since guaranteed to be one row
                # and NULL values should be replace with 0
                final_column_names = [index_col_name, columns[0]]
                final_column_expressions = [
                    self._conn.format_name("generate_series"),
                    self._conn.generate_replace_nan_with_0(columns[0]),
                ]
                change_columns_node = ChangeColumns(
                    conn=self._conn,
                    node=join_node,
                    column_names=final_column_names,
                    column_expressions=final_column_expressions,
                    column_types=[index_dtype, np.dtype(">i1")],
                    order_column_name=self._root.get_order_column_name(),
                    has_aggregation=False,
                )
            else:
                # Use ChangeColumns to drop unnecessary columns post-join
                # and populate with NaN values
                final_column_names = [index_col_name]
                final_column_expressions = [self._conn.format_name("generate_series")]
                for column_name in columns:
                    final_column_names.append(column_name)
                    final_column_expressions.append(self._conn.format_name(column_name))
                change_columns_node = ChangeColumns(
                    conn=self._conn,
                    node=join_node,
                    column_names=final_column_names,
                    column_expressions=final_column_expressions,
                    column_types=[index_dtype, *self._root.get_column_types()],
                    order_column_name=self._root.get_order_column_name(),
                    has_aggregation=False,
                )
            # Use NewRowLabelsColumnsNode to remove _PONDER_ROW_LABELS_
            groupby_node_with_correct_labels = NewRowLabelsColumnsNode(
                self._conn, change_columns_node, None, [index_col_name]
            )
        return QueryTree(self._conn, groupby_node_with_correct_labels)

    def add_abs(self, columns):
        column_expressions = [
            self._conn.generate_abs(column_name) for column_name in columns
        ]
        change_columns_node = ChangeColumns(
            self._conn,
            self._root,
            columns,
            column_expressions,
            self._root.get_column_types(),
            self._root.get_order_column_name(),
            has_aggregation=False,
        )
        new_query_tree = QueryTree(self._conn, change_columns_node)
        return new_query_tree

    def add_invert(self):
        return QueryTree(
            conn=self._conn,
            root=ChangeColumns(
                conn=self._conn,
                node=self._root,
                column_names=self._root.get_column_names(),
                column_expressions=[
                    self._conn.generate_boolean_negation(c)
                    if is_bool_dtype(t)
                    else self._conn.generate_bitwise_negation(c)
                    for c, t in self.dtypes.items()
                ],
                column_types=self._root.get_column_types(),
                order_column_name=self._root.get_order_column_name(),
                has_aggregation=False,
            ),
        )

    def add_round(self, columns, decimals):
        column_expressions = [
            self._conn.generate_round(column_name, decimals) for column_name in columns
        ]
        change_columns_node = ChangeColumns(
            self._conn,
            self._root,
            columns,
            column_expressions,
            self._root.get_column_types(),
            self._root.get_order_column_name(),
            has_aggregation=False,
        )
        new_query_tree = QueryTree(self._conn, change_columns_node)
        return new_query_tree

    def add_str_extract(self, columns, pat, flags, expand):
        import re

        n = re.compile(pat).groups
        column_expressions = self._conn.generate_str_extract(columns[0], pat, flags)
        if expand or n > 1:
            columns = [f"Part{str(i)}" for i in range(n)]
            column_types = self._root.get_column_types() * n
        else:
            column_types = self._root.get_column_types()
        change_columns_node = ChangeColumns(
            self._conn,
            self._root,
            columns,
            column_expressions,
            column_types,
            self._root.get_order_column_name(),
            has_aggregation=False,
        )
        new_query_tree = QueryTree(self._conn, change_columns_node)
        return new_query_tree

    def add_str_partition(self, columns, sep, expand):
        column_expressions = self._conn.generate_str_partition(columns[0], sep, expand)
        if expand:
            columns = ["Part0", "Part1", "Part2"]
            column_types = self._root.get_column_types() * 3
        else:
            column_types = self._root.get_column_types()
        change_columns_node = ChangeColumns(
            self._conn,
            self._root,
            columns,
            column_expressions,
            column_types,
            self._root.get_order_column_name(),
            has_aggregation=False,
        )
        new_query_tree = QueryTree(self._conn, change_columns_node)
        return new_query_tree

    def add_str_rpartition(self, columns, sep, expand):
        column_expressions = self._conn.generate_str_rpartition(columns[0], sep, expand)
        if expand:
            columns = ["Part0", "Part1", "Part2"]
            column_types = self._root.get_column_types() * 3
        else:
            column_types = self._root.get_column_types()
        change_columns_node = ChangeColumns(
            self._conn,
            self._root,
            columns,
            column_expressions,
            column_types,
            self._root.get_order_column_name(),
            has_aggregation=False,
        )
        new_query_tree = QueryTree(self._conn, change_columns_node)
        return new_query_tree

    def add_isin_dict(self, values):
        column_names = self._root.get_column_names()
        column_expressions = [
            self._conn.generate_isin_collection_expression(
                column_name, column_type, values[column_name]
            )
            for column_name, column_type in zip(
                column_names, self._root.get_column_types()
            )
        ]
        change_columns_node = ChangeColumns(
            self._conn,
            self._root,
            column_names,
            column_expressions,
            [np.bool_] * len(column_names),
            self._root.get_order_column_name(),
            has_aggregation=False,
        )
        return QueryTree(self._conn, change_columns_node)

    def add_dataframe_isin_series(
        self,
        original_column_names: list[str],
        original_column_types: list[np.dtype],
        series_type: np.dtype,
    ):
        column_expressions = [
            self._conn.generate_dataframe_isin_series(name)
            for name, type in zip(original_column_names, original_column_types)
        ]
        change_columns_node = ChangeColumns(
            self._conn,
            self._root,
            original_column_names,
            column_expressions,
            [np.bool_] * len(original_column_names),
            self._root.get_order_column_name(),
            has_aggregation=False,
        )
        return QueryTree(self._conn, change_columns_node)

    def add_dataframe_isin_dataframe(
        self, original_column_names: list[str], values_column_names: list[str]
    ):
        column_expressions = []
        for column_name in original_column_names:
            if column_name in values_column_names:
                column_expressions.append(
                    self._conn.generate_dataframe_isin_dataframe(column_name)
                )
            else:
                column_expressions.append(self._conn.generate_false_constant())
        change_columns_node = ChangeColumns(
            self._conn,
            self._root,
            original_column_names,
            column_expressions,
            [np.bool_] * len(original_column_names),
            self._root.get_order_column_name(),
            has_aggregation=False,
        )
        return QueryTree(self._conn, change_columns_node)

    def add_clip(
        self,
        columns: list[str],
        lower_list: Optional[float],
        upper_list: Optional[float],
    ):
        # TODO(REFACTOR): This error checking should go to a higher layer, maybe even
        # the API layer.
        if lower_list is not None and len(columns) != len(lower_list):
            raise make_exception(
                RuntimeError,
                PonderError.CLIP_LOWER_BOUND_WRONG_LENGTH,
                "clip requires lower bounds array of the same size",
            )
        if upper_list is not None and len(columns) != len(upper_list):
            raise make_exception(
                RuntimeError,
                PonderError.CLIP_UPPER_BOUND_WRONG_LENGTH,
                "clip requires upper bounds array of the same size",
            )
        if lower_list is None and upper_list is None:
            raise make_exception(
                RuntimeError, PonderError.CLIP_NO_BOUNDS, "Nothing to clip with"
            )
        if upper_list is not None and lower_list is None:
            # TODO: We probably want to move this down into the dialects, which
            # would keep the SQL a little more succinct on some databases, but
            # this is generic enough SQL to keep the NULL handling for LEAST
            # and GREATEST consistent.
            expressions = (
                f"""
                CASE WHEN {self._conn.format_name(col)} IS NULL
                THEN NULL ELSE
                LEAST({self._conn.format_name(col)}, {upper_list[idx]})
                END
                """
                for idx, col in enumerate(columns)
            )

        elif lower_list is not None and upper_list is None:
            expressions = (
                f"""
                CASE WHEN {self._conn.format_name(col)} IS NULL
                THEN NULL ELSE
                GREATEST({self._conn.format_name(col)}, {lower_list[idx]})
                END
                """
                for idx, col in enumerate(columns)
            )
        else:
            # np.minimum(a_max, np.maximum(a, a_min))
            expressions = (
                f"""
                    CASE WHEN {self._conn.format_name(col)} IS NULL
                    THEN NULL ELSE
                    LEAST(GREATEST({self._conn.format_name(col)},
                    {lower_list[idx]}), {upper_list[idx]})
                    END
                    """
                for idx, col in enumerate(columns)
            )
        change_columns_node = ChangeColumns(
            conn=self._conn,
            node=self._root,
            column_names=columns,
            column_expressions=expressions,
            column_types=self._root.get_column_types(),
            order_column_name=self._root.get_order_column_name(),
            has_aggregation=False,
        )
        return QueryTree(self._conn, change_columns_node)

    def add_coalesce(self, columns_to_coalesce, original_column_names):
        column_expressions = [
            f"COALESCE("
            f"{', '.join(map(self._conn.format_name, columns_to_coalesce[c]))})"
            if c in columns_to_coalesce.keys()
            else c
            for c in original_column_names
        ]
        change_columns_node = ChangeColumns(
            conn=self._conn,
            node=self._root,
            column_names=original_column_names,
            column_expressions=column_expressions,
            column_types=[np.bool_] * len(original_column_names),
            order_column_name=self._root.get_order_column_name(),
            has_aggregation=False,
        )
        return QueryTree(self._conn, change_columns_node)

    def add_compare_post_join(
        self,
        original_columns: Iterable[str],
        original_column_types: Iterable[pandas_dtype],
    ):
        """Add a node to the query tree that implements compare() after a join.

        This method assumes the input has already joined the two tables for compare()
        and that the join suffixes for common columns were _x and _y for this frame
        and the other frame, respectively.

        Parameters
        ----------
        original_columns : Iterable[str]
            The columns of the original query tree.
        original_column_types : Iterable[pandas_dtype]
            The types of the columns of the original query tree

        Returns
        -------
        QueryTree
            A new query tree with the compare post join node added.
        """
        (
            column_names,
            column_expressions,
            column_types,
        ) = self._conn.generate_compare_post_join_results(
            original_columns, original_column_types
        )
        change_columns_node = ChangeColumns(
            conn=self._conn,
            node=self._root,
            column_names=column_names,
            column_expressions=column_expressions,
            column_types=column_types,
        )
        return QueryTree(self._conn, change_columns_node)

    def add_melt(
        self,
        id_vars,
        value_var,
        var_name,
        value_name,
        col_level,
        ignore_index,
    ):
        new_column_names = []
        new_column_types = []
        new_column_expressions = []

        # value_var is the column we want to make into variable
        # var_name is the name of the variable column
        # value_name is the name of the value column
        for col_name, col_type in zip(
            self._root.get_column_names(), self._root.get_column_types()
        ):
            if col_name in id_vars:
                new_column_names.append(col_name)
                new_column_types.append(col_type)
                new_column_expressions.append(self._conn.format_name(col_name))
            elif col_name == value_var:
                # Let us also rename the original
                new_column_names.append(var_name)
                new_column_types.append(np.dtype(object))
                new_column_expressions.append(f"'{col_name}'")

                # Right now the assumption is that col_names are strings
                # Let us rename the col_name -> value_name
                new_column_names.append(value_name)
                new_column_types.append(col_type)
                new_column_expressions.append(self._conn.format_name(col_name))

        change_columns_node = ChangeColumns(
            conn=self._conn,
            node=self._root,
            column_names=new_column_names,
            column_expressions=new_column_expressions,
            column_types=new_column_types,
        )

        return QueryTree(self._conn, change_columns_node)

    def add_replace_all(self, value):
        change_columns_node = ChangeColumns(
            conn=self._conn,
            node=self._root,
            column_names=self.get_column_names(),
            column_expressions=[self._conn.format_value(value)] * len(self.columns),
            column_types=[pandas.Series(value).dtype] * len(self.dtypes),
        )
        return QueryTree(self._conn, change_columns_node)

    def add_apply(
        self,
        func,
        output_column_list,
        output_column_types,
        db_output_column_types,
        axis,
        result_type,
        row_labels_dtypes,
        apply_type,
        na_action,
        func_args,
        func_kwargs,
    ):
        from .apply import ApplyStoredProcedureNode, ApplyUDFNode

        if axis == 1:
            apply_node = ApplyUDFNode(
                self._conn,
                self._root,
                func,
                output_column_list,
                output_column_types,
                db_output_column_types,
                axis,
                result_type,
                row_labels_dtypes,
                apply_type,
                na_action,
                func_args,
                func_kwargs,
            )
        else:
            stored_proc_node = ApplyStoredProcedureNode(
                self._conn,
                self._root,
                output_column_list,
                output_column_types,
                __PONDER_STORED_PROC_ROW_LABEL_COLUMN_NAME__,
                row_labels_dtypes,
                func,
            )
            apply_node = NewRowLabelsColumnsNode(
                self._conn,
                stored_proc_node,
                None,
                [__PONDER_STORED_PROC_ROW_LABEL_COLUMN_NAME__],
            )

        return QueryTree(self._conn, apply_node)

    def add_cut(self, bins, labels, precision, right, include_lowest):
        new_dtype = (
            pandas.CategoricalDtype(
                categories=_format_labels(
                    bins, precision, right, include_lowest, dtype=None
                ),
                ordered=True,
            )
            if labels is None
            else pandas.CategoricalDtype(labels, ordered=True)
        )
        change_columns_node = ChangeColumns(
            conn=self._conn,
            node=self._root,
            column_names=self.get_column_names(),
            column_expressions=[
                self._conn.generate_cut_expression(
                    self.get_column_names()[0], new_dtype.categories, bins
                )
            ],
            column_types=[new_dtype],
            order_column_name=self._root.get_order_column_name(),
        )
        return QueryTree(self._conn, change_columns_node)

    def add_pct_change(self, periods):
        # All we really need to do here is generate the SQL for the new column
        # names pretty much. Then we use ChangeColumns to do the rewrite and TA-DA!
        column_expressions = [
            self._conn.generate_pct_change(col, periods)
            for col in self.get_column_names()
        ]

        # dtypes should all be float
        new_dtypes = [np.dtype(float)] * len(self.dtypes)

        change_columns_node = ChangeColumns(
            conn=self._conn,
            node=self._root,
            column_names=self.get_column_names(),
            column_expressions=column_expressions,
            column_types=new_dtypes,
            order_column_name=self._root.get_order_column_name(),
        )
        return QueryTree(self._conn, change_columns_node)

    def add_diff(self, periods):
        # Similar to pct_change, for axis=0, just need to generate SQL and use
        # ChangeColumns node
        column_expressions = [
            self._conn.generate_diff(col, periods) for col in self.get_column_names()
        ]

        # even if the original dtypes are just ints, pandas still returns floats
        new_dtypes = [np.dtype(float)] * len(self.dtypes)

        change_columns_node = ChangeColumns(
            conn=self._conn,
            node=self._root,
            column_names=self.get_column_names(),
            column_expressions=column_expressions,
            column_types=new_dtypes,
            order_column_name=self._root.get_order_column_name(),
        )
        return QueryTree(self._conn, change_columns_node)

    def add_reorder_columns(self, reordered_columns_list):
        reordered_columns_node = ReorderColumnsNode(
            conn=self._conn, node=self._root, column_names=reordered_columns_list
        )

        return QueryTree(self._conn, reordered_columns_node)

    def debug_vis(self, output: str = "", browser: bool = True):
        """
        Chops down the forest so I could see clearly.

        Saves a visualization of the query tree to a file.
        Saves the SQL generated by each node to a separate file.

        Parameters
        ----------

        output: str
            The output directory.
            If not specified, use `.ponder/query-tree-vis/{current-time}`

        browser: bool
            Whether to open the browser.
        """

        from . import debug_vis

        if output:
            output = Path(output)
        else:
            now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            output = Path(".ponder/query-tree-vis") / now

        debug_vis.debug_vis(root=self._root, output_folder=output, browser=browser)


def _cache_cacheable_node_methods(cls) -> None:
    """Cache all query tree nodes that should be cached.

    Query tree nodes have a stateless interface, so every public method should always
    return the same result given the same inputs. This rewrites some node methods that
    take no arguments to cached versions.

    We could have tried to apply a decorator to each node class to cache the properties,
    but that requires more code and it's harder to maintain. We also can't implement all
    these methods only in the superclass, because each node implements things
    differently.

    Args:
        cls: The class to rewrite.
    """

    def cache_method(method_name):
        uncached_method = getattr(cls, method_name)
        # if class doesn't implement an abstract method, don't reset the method to a
        # concrete method that caches the result.
        if getattr(uncached_method, "__isabstractmethod__", False):
            raise make_exception(
                RuntimeError,
                PonderError.QUERY_TREE_CLASS_METHOD_NOT_IMPLEMENTED,
                f"Internal error: {cls} does not implement {method_name}",
            )
        cached_value_name = f"_{method_name}_cache"
        # all instances of the cache will start with the cached property set to None.
        setattr(cls, cached_value_name, None)

        def cached_method(self):
            # Use the uncached method to set the cache if it's not already set.
            cached_result = getattr(self, cached_value_name)
            if cached_result is None:
                # doing magic to get property value:
                # https://stackoverflow.com/a/13369120/17554722
                result = (
                    uncached_method.__get__(self)
                    if isinstance(uncached_method, property)
                    else uncached_method(self)
                )
                setattr(self, cached_value_name, result)
                return result
            # some methods like get_column_names() return mutable lists. We can't return
            # the reference to the same such object multiple times, so make a copy.
            return copy.deepcopy(cached_result)

        # Replace the uncached method with the cached method. The method may be a
        # property (e.g.`dtypes`), in which case we have to convert the cached method
        # to a property.
        setattr(
            cls,
            method_name,
            property(cached_method)
            if isinstance(uncached_method, property)
            else cached_method,
        )

    for attribute in [
        "get_order_column_name",
        "generate_sql",
        "get_column_names",
        "get_column_types",
        "get_row_labels_column_names",
        "columns",
        "dtypes",
    ]:
        cache_method(attribute)


def embed_node_info(query_generator):
    @functools.wraps(query_generator)
    def func_wrapper(self, *args, **kwargs):
        query = query_generator(self, *args, **kwargs)
        if os.environ.get("DEBUG_EMBED_QUERY_NODE_INFO", "").lower() == "true":
            # type(self).__name__ can be in an encoding that the snowflake
            # query UI can't recognize, so convert to string with the default utf-8
            # encoding.
            class_name = str(type(self).__name__)
            return (
                f"\n /* {class_name} begin */ \n {query} \n /* {class_name} end */" ""
            )
        else:
            return query

    return func_wrapper


@dataclass(frozen=True, init=False)
class QueryTreeNodeDependency:
    parents: Sequence[QueryTreeNode]
    """
    Parent node that the query node is dependent on.
    """

    extras: Mapping[str, Any]
    """
    Extra information that the node depends on e.g. parameters.
    """

    def __init__(
        self,
        *,
        parents: Sequence[QueryTreeNode] = (),
        extras: Mapping[str, Any] | None = None,
    ):
        # Using None as default value because there's no `frozendict`.
        if extras is None:
            extras = {}

        object.__setattr__(self, "parents", parents)
        object.__setattr__(self, "extras", {k: str(v) for k, v in extras.items()})

    def __post_init__(self):
        for parent in self.parents:
            assert isinstance(parent, QueryTreeNode), parent

        for key in self.extras:
            assert isinstance(key, str), key


class QueryTreeNode(ABC):
    def __init__(self, conn, order_column_name=""):
        self._order_column_name = __PONDER_ORDER_COLUMN_NAME__
        if len(order_column_name) != 0:
            self._order_column_name = order_column_name
        self._conn = conn

    def __str__(self):
        # This might require additional packages to be installed.
        from . import debug_vis

        return debug_vis.PONDER_SHOW_FORMATTED_SQL(self)

    @abstractmethod
    def generate_sql(self) -> str:
        raise make_exception(
            NotImplementedError,
            PonderError.QUERY_TREE_GENERATE_SQL_NOT_IMPLEMENTED,
            f"Internal error: {type(self)} does not implement generate_sql",
        )

    def __init_subclass__(cls, *args, **kwargs) -> None:
        # We need to rewrite some methods of every subclass of this class, rather than
        # the methods of this class itself. Modifying __init_subclass__ lets us do that.
        super().__init_subclass__(*args, **kwargs)
        cls.generate_sql = embed_node_info(cls.generate_sql)
        _cache_cacheable_node_methods(cls)

    def get_order_column_name(self):
        return self._order_column_name

    def get_row_labels_column_names(self) -> list[str]:
        return [__PONDER_ROW_LABELS_COLUMN_NAME__]

    def get_order_and_labels_column_strings(self):
        return self._conn.get_order_and_labels_column_strings(self)

    @abstractmethod
    def get_column_names(self):
        pass

    @abstractmethod
    def get_column_types(self):
        pass

    # Override to allow for parent nodes to merge expressions
    # when applicable ( such as in DerivedColumn )
    def get_expressions(self):
        # if the input node has predicates, the string form of the predicates is
        # equivalent to their expressions.
        # TODO: combine expressions and "predicates" (which are not just boolean
        # predicates and really are binary expression trees) so we don't have to keep
        # thinking about both.
        predicates = self.get_predicates()
        return [str(p) for p in predicates] if len(predicates) > 0 else []

    # Override to allow for parent nodes to merge predicates
    # when applicable
    def get_predicates(self):
        return []

    @property
    def dtypes(self) -> pandas.Series:
        # TODO(REFACTOR): use this property in many places where we zip column names
        # and types together.
        assert not isinstance(
            self.get_column_types(), pandas.Series
        ), f"Column types are a pandas.Series object for node {type(self)}"
        return pandas.Series(
            self.get_column_types(), index=self.get_column_names(), dtype="object"
        )

    @property
    def columns(self) -> pandas.Index:
        return pandas.Index(self.get_column_names())

    @abstractmethod
    def data_hash(self):
        raise make_exception(
            NotImplementedError,
            PonderError.QUERY_TREE_DATA_HASH_NOT_IMPLEMENTED,
            f"Internal error: {type(self)} does not implement data_hash",
        )

    @abstractmethod
    def depends_on(self) -> QueryTreeNodeDependency:
        ...


class RawSQLLeafNode(QueryTreeNode):
    def __init__(
        self, conn, sql_query, column_names, column_types, order_column_name=""
    ):
        super().__init__(conn, order_column_name)
        self._sql_query = sql_query
        self._conn = conn
        self._order_column_name = order_column_name
        self._column_names = column_names
        self._column_types = column_types

    def generate_sql(self):
        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {self._sql_query}"""
        )
        return self._sql_query

    def get_dataframe_column_names(self):
        return self._column_names

    def get_column_names(self):
        return self._column_names

    def get_column_types(self):
        return self._column_types

    def data_hash(self):
        return hash(self._sql_query)

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(extras={"sql_query": self._sql_query})


class LeafNode(QueryTreeNode):
    def __init__(
        self, table_name, conn, order_column_name="", retain_table_column_names=False
    ):
        super().__init__(conn, order_column_name)
        self._table_name = table_name
        # Initially the sql query will be the same as the table name. Once
        # the table is materialized -we change it to a query on the
        # materialized table.
        self._sql_query = table_name
        # TODO: Make sure these generated names are unique.  Note that temp tables
        # can have the same names as regular tables.  The only name clash we need to
        # avoid is with other temp tables we've created in the same session.  This
        # scheme also has the advantage that we don't need to escape the table
        # names.
        self._materialized_table_name = conn.create_temp_table_name()

        # The table might have been materialized already. If so, the connection
        # layer will return the name with which it was materialized earlier.
        self._materialized_table_name = self._conn.materialize_table(
            table_name, self._materialized_table_name
        )
        metadata = conn.get_temp_table_metadata(self._materialized_table_name)
        # Unzip the metadata pairs:
        # [(col_0, type_0), (col_1, type_1)] => [[col_0, col_1], [type_0, type_1]]
        self._dataframe_column_names, self._column_types = metadata

        if retain_table_column_names:
            self._column_names = self._dataframe_column_names
        else:
            self._column_names = generate_db_column_names(
                self._dataframe_column_names, self._conn
            )

        # Cache the query so we don't have to generate it every time.
        self._sql_query = self._conn.generate_select_with_renamed_columns(
            self._materialized_table_name,
            self._dataframe_column_names,
            self._column_names,
            [__PONDER_ORDER_COLUMN_NAME__, __PONDER_ROW_LABELS_COLUMN_NAME__],
        )

    def generate_sql(self):
        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {self._sql_query}"""
        )
        return self._sql_query

    def get_dataframe_column_names(self):
        return self._dataframe_column_names

    def get_column_names(self):
        return self._column_names

    def get_column_types(self):
        return self._column_types

    def data_hash(self):
        return hash(self._materialized_table_name)

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(extras={"table_name": self._table_name})


class CsvNode(QueryTreeNode):
    def __init__(
        self,
        conn,
        table_name,
        df,
        file_path,
        sep,
        header,
        skipfooter,
        parse_dates,
        date_format,
        na_values,
        on_bad_lines="error",
        order_column_name="",
    ):
        super().__init__(conn, order_column_name)
        self._table_name = table_name
        # Initially the sql query will be the same as the table name. Once
        # the table is materialized -we change it to a query on the
        # materialized table.
        self._sql_query = table_name
        self._column_names = generate_db_column_names(df.columns, conn)
        self._table_name = self._conn.materialize_csv_file_as_table(
            table_name,
            self._column_names,
            df.dtypes,
            file_path,
            sep,
            header,
            skipfooter,
            parse_dates,
            date_format,
            na_values,
            on_bad_lines,
            order_column_name,
        )
        self._dataframe_column_names = list(df.columns)
        self._column_types = list(df.dtypes)
        # Cache the query so we don't have to generate it every time.
        self._sql_query = self._conn.generate_select(
            self._table_name, self.get_column_names(), skipfooter
        )

    def generate_sql(self):
        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {self._sql_query}"""
        )
        return self._sql_query

    def get_column_names(self):
        return self._column_names

    def get_column_types(self):
        return self._column_types

    def get_dataframe_column_names(self):
        return self._dataframe_column_names

    def data_hash(self):
        return hash(self._table_name)

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(extras={"table_name": self._table_name})


class ParquetNode(QueryTreeNode):
    def __init__(
        self,
        conn,
        table_name,
        column_names,
        column_types,
        files,
        columns,
        storage_options,
        # TODO: seems redundant to have file system argument in addition to storage
        # options and the list of files. However, duckdb needs the file system to read
        # from adlfs, and snowflake needs the list of files to add them to staging.
        # duckdb uses the list of files but could probably use the original path
        # instead. We might be able to clean this up.
        fs,
        hive_partitioning=False,
    ):
        super().__init__(conn)

        # If columns are defined, then we should filter out the column names
        # and column types that we care about
        if columns:
            column_names = columns
            column_types = column_types[columns]

        column_types = column_types.tolist()
        self._table_name = self._conn.materialize_parquet_files_as_table(
            table_name,
            column_names,
            column_types,
            files,
            storage_options,
            fs,
            hive_partitioning,
        )
        self._column_names = column_names
        self._column_types = column_types

        # Cache the query so we don't have to generate it every time.
        self._sql_query = self._conn.generate_select(
            self._table_name, self.get_column_names()
        )

        # Used for DuckDB for now, will be needed for others
        self._hive_partitioning = hive_partitioning

    def generate_sql(self):
        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {self._sql_query}"""
        )
        return self._sql_query

    def get_column_names(self):
        return self._column_names

    def get_dataframe_column_names(self):
        return self.get_column_names()

    def get_column_types(self):
        return self._column_types

    def data_hash(self):
        return hash(self._table_name)

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(extras={"table_name": self._table_name})


class PdfNode(QueryTreeNode):
    def __init__(self, conn, pandas_df):
        super().__init__(conn)
        self._materialized_table_name = self._conn.create_temp_table_name()
        self._dataframe_column_names = pandas_df.columns.values.tolist()
        self._column_names = generate_db_column_names(
            self._dataframe_column_names, conn
        )
        pandas_df = pandas_df.copy(deep=True)
        pandas_df.columns = [str(col_name) for col_name in pandas_df.columns]
        for i in range(len(pandas_df.columns.values)):
            pandas_df.columns.values[i] = self._column_names[i]
        self._materialized_table_name = conn.materialize_pandas_dataframe_as_table(
            self._materialized_table_name,
            pandas_df,
            order_column_name=__PONDER_ORDER_COLUMN_NAME__,
        )

        metadata = conn.get_temp_table_metadata(self._materialized_table_name)
        # Unzip the metadata pairs:
        # [(col_0, type_0), (col_1, type_1)] => [[col_0, col_1], [type_0, type_1]]
        self._column_names, self._column_types = metadata
        # Cache the query so we don't have to generate it every time.
        # Cache the query so we don't have to generate it every time.
        self._sql_query = self._sql_query = self._conn.generate_select(
            self._materialized_table_name, self.get_column_names()
        )

    def generate_sql(self):
        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {self._sql_query}"""
        )
        return self._sql_query

    def get_column_names(self):
        return self._column_names

    def get_dataframe_column_names(self):
        return self._dataframe_column_names

    def get_column_types(self):
        return self._column_types

    def data_hash(self):
        return hash(self._materialized_table_name)

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            extras={"table_name": self._materialized_table_name}
        )


def rename_input_columns(join_node):
    left_column_list = join_node._left.get_column_names()
    right_column_list = join_node._right.get_column_names()
    left_column_rename_map = {}
    right_column_rename_map = {}

    for left_column_name in left_column_list:
        for right_column_name in right_column_list:
            if left_column_name == right_column_name:
                if join_node._suffixes[0] is not None:
                    new_left_col_name = left_column_name + join_node._suffixes[0]
                    while new_left_col_name in (left_column_list + right_column_list):
                        new_left_col_name = new_left_col_name + join_node._suffixes[0]
                    left_column_rename_map[left_column_name] = new_left_col_name

                if join_node._suffixes[1] is not None:
                    new_right_col_name = right_column_name + join_node._suffixes[1]
                    while new_right_col_name in (left_column_list + right_column_list):
                        new_right_col_name = new_right_col_name + join_node._suffixes[1]
                    right_column_rename_map[right_column_name] = new_right_col_name

    original_left_order_column_name = join_node._left.get_order_column_name()
    original_right_order_column_name = join_node._right.get_order_column_name()

    if len(left_column_rename_map) != 0:
        join_node._left = RenameColumnsNode(
            join_node._conn, join_node._left, left_column_rename_map, "LEFT_ORDER"
        )
        left_on_rename = [
            left_column_rename_map[left_on_column_name]
            if left_on_column_name in left_column_rename_map
            else left_on_column_name
            for left_on_column_name in join_node._left_on
        ]
        join_node._left_on = left_on_rename
        if hasattr(join_node, "_left_by"):
            left_by_rename = [
                left_column_rename_map[left_by_column_name]
                if left_by_column_name in left_column_rename_map
                else left_by_column_name
                for left_by_column_name in join_node._left_by
            ]
            join_node._left_by = left_by_rename
    elif original_left_order_column_name == original_right_order_column_name:
        join_node._left = RenameColumnsNode(
            join_node._conn, join_node._left, left_column_rename_map, "LEFT_ORDER"
        )

    if len(right_column_rename_map) != 0:
        join_node._right = RenameColumnsNode(
            join_node._conn, join_node._right, right_column_rename_map, "RIGHT_ORDER"
        )
        right_on_rename = [
            right_column_rename_map[right_on_column_name]
            if right_on_column_name in right_column_rename_map
            else right_on_column_name
            for right_on_column_name in join_node._right_on
        ]
        join_node._right_on = right_on_rename
        matched_on_rename = [
            right_column_rename_map[right_on_column_name]
            if right_on_column_name in right_column_rename_map
            else right_on_column_name
            for right_on_column_name in join_node._matched_fields
        ]
        join_node._matched_fields = matched_on_rename
        if hasattr(join_node, "_right_by"):
            right_by_rename = [
                right_column_rename_map[right_by_column_name]
                if right_by_column_name in right_column_rename_map
                else right_by_column_name
                for right_by_column_name in join_node._right_by
            ]
            join_node._right_by = right_by_rename

    elif original_left_order_column_name == original_right_order_column_name:
        join_node._right = RenameColumnsNode(
            join_node._conn, join_node._right, right_column_rename_map, "RIGHT_ORDER"
        )
    return left_column_rename_map


class EquiJoinNode(QueryTreeNode):
    def __init__(
        self,
        conn,
        left,
        right,
        how,
        left_on,
        right_on,
        suffixes,
        order_column_name="",
        use_db_index: bool = False,
        indicator: bool = False,
    ):
        if left._conn != right._conn:
            throw_exception_on_cross_database_operations()
        super().__init__(conn, order_column_name)
        self._left = left
        self._right = right
        left_on = [left_on] if isinstance(left_on, str) else left_on
        right_on = [right_on] if isinstance(right_on, str) else right_on
        self._left_on = left_on[:] if left_on is not None else []
        self._right_on = right_on[:] if right_on is not None else []
        self._use_db_index = use_db_index

        self._indicator = indicator
        self._matched_fields = [
            right_field
            for right_field in self._right_on
            if right_field in self._left_on
        ]

        self._suffixes = suffixes
        self._how = how

        rename_input_columns(self)
        self._column_names = self._left.get_column_names()[:]
        self._column_types = [type for type in self._left.get_column_types()]

        if len(self._matched_fields) == 0:
            self._column_names.extend(self._right.get_column_names())
            self._column_types.extend(self._right.get_column_types())
        else:
            self._column_names.extend(self._right.get_column_names())
            self._column_types.extend(self._right.get_column_types())
        if indicator:
            self._column_names.extend(["_merge"])
            self._column_types.extend([str])

    def generate_sql(self):
        sql_query = self._conn.generate_join(
            self._left,
            self._right,
            self._column_names,
            self._how,
            self._left_on,
            self._right_on,
            self._left.get_order_column_name(),
            self._right.get_order_column_name(),
            self._order_column_name,
            self.get_row_labels_column_names() if self._use_db_index else None,
            indicator=self._indicator,
        )

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def get_column_names(self):
        return self._column_names

    def get_column_types(self):
        return self._column_types

    def return_metadata(self):
        pass

    def get_row_labels_column_names(self):
        if self._use_db_index:
            return self._left.get_row_labels_column_names()
        return [__PONDER_ROW_LABELS_COLUMN_NAME__]

    def data_hash(self):
        return hash(
            tuple(dict.fromkeys((self._left.data_hash(), self._right.data_hash())))
        )

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            parents=[self._left, self._right],
            extras={"left_on": self._left_on, "right_on": self._right_on},
        )


class MergeAsOfNode(QueryTreeNode):
    def __init__(
        self,
        conn,
        left,
        right,
        left_on,
        right_on,
        left_by,
        right_by,
        suffixes,
        tolerance,
        allow_exact_matches,
        direction,
    ):
        if left._conn != right._conn:
            throw_exception_on_cross_database_operations()

        super().__init__(conn)
        self._left = left
        self._right = right
        self._left_on = [left_on] if isinstance(left_on, str) else left_on
        self._right_on = [right_on] if isinstance(right_on, str) else right_on
        self._left_by = [left_by] if isinstance(left_by, str) else left_by[:]
        self._right_by = [right_by] if isinstance(right_on, str) else right_by[:]
        self._suffixes = suffixes[:] if suffixes is not None else ("_x", "_y")
        self._tolerance = tolerance
        self._allow_exact_matches = allow_exact_matches
        self._direction = direction
        self._matched_fields = []
        left_column_rename_map = rename_input_columns(self)
        self._change_columns_node = None

        # We need to put back the names of columns from the left if the columns they
        # clash with on the right are part of the on or by clauses
        if len(left_column_rename_map) > 0:
            restored_column_names = []
            restored_column_expressions = []

            current_column_names = self.get_column_names()
            for current_column_name in current_column_names:
                found_item = False
                for item in left_column_rename_map.items():
                    if item[1] == current_column_name:
                        renamed_column_name = item[0]
                        renamed_column_expression = self._conn.format_name(item[1])
                        found_item = True
                        break
                if found_item is False:
                    renamed_column_name = current_column_name
                    renamed_column_expression = self._conn.format_name(
                        current_column_name
                    )
                restored_column_names.append(renamed_column_name)
                restored_column_expressions.append(renamed_column_expression)
            self._change_columns_node = ChangeColumns(
                self._conn,
                self,
                restored_column_names,
                restored_column_expressions,
                self.get_column_types(),
            )

    def generate_sql(self):
        sql_query = self._conn.generate_join_asof(
            self._left,
            self._right,
            self._left_on,
            self._right_on,
            self._left_by,
            self._right_by,
            self._tolerance,
            self._allow_exact_matches,
            self._direction,
            self._left.get_order_column_name(),
            self._right.get_order_column_name(),
            self._order_column_name,
        )

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def get_column_names(self):
        return list(self._left.get_column_names()) + [
            right_column_name
            for right_column_name in list(self._right.get_column_names())
            if right_column_name not in self._right_on
            and right_column_name not in self._right_by
        ]

    def get_column_types(self):
        return list(self._left.get_column_types()) + [
            self._right.get_column_types()[i]
            for i in range(len(self._right.get_column_types()))
            if self._right.get_column_names()[i] not in self._right_on
            and self._right.get_column_names()[i] not in self._right_by
        ]

    def return_metadata(self):
        pass

    def get_row_labels_column_names(self):
        return [__PONDER_ROW_LABELS_COLUMN_NAME__]

    def get_real_node(self):
        if self._change_columns_node is None:
            return self
        return self._change_columns_node

    def data_hash(self):
        return hash()

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            parents=[self._left, self._right],
            extras={
                "left_on": self._left_on,
                "right_on": self._right_on,
                "left_by": self._left_by,
                "right_by": self._right_by,
            },
        )


class SelectFromWhereNode(QueryTreeNode):
    def __init__(
        self,
        conn,
        node,
        column_names_for_filter,
        row_labels,
        col_labels,
        order_column_name,
    ):
        super().__init__(conn, order_column_name)
        self._input_node = node
        self._row_labels = row_labels
        self._col_labels = col_labels
        self._column_names_for_filter = column_names_for_filter

    def return_metadata(self):
        pass

    def get_column_names(self):
        if self._col_labels is None:
            return self._input_node.get_column_names()
        return list(self._col_labels)

    def generate_sql(self):
        sql_query = self._conn.generate_select_from_in(self)

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def get_input_node(self):
        return self._input_node

    def get_column_types(self):
        if self._col_labels is None:
            return self._input_node.get_column_types()
        column_types = []
        for mask_column_name in self._col_labels:
            for i in range(len(self._input_node.get_column_names())):
                if mask_column_name == self._input_node.get_column_names()[i]:
                    column_types.append(self._input_node.get_column_types()[i])
                    break
        return column_types

    def get_predicates(self):
        if self._row_labels is not None:
            raise make_exception(
                RuntimeError,
                PonderError.SELECT_CLAUSE_MISSING_ROW_LABELS,
                "Ponder Internal Error: Select clause missing row labels",
            )
        return [
            BinaryPredicate(
                self._conn,
                lhs=self._conn.format_name(col),
                lhs_type=type,
                lhs_is_literal=False,
                lhs_is_column=True,
                op=None,
                rhs=None,
                rhs_type=None,
                rhs_is_literal=None,
                rhs_is_column=None,
            )
            for col, type in zip(self.get_column_names(), self.get_column_types())
        ]

    def get_row_labels_column_names(self):
        return self._input_node.get_row_labels_column_names()

    def data_hash(self):
        return self._input_node.data_hash()

    def get_expressions(self):
        if self._col_labels is None:
            return self._input_node.get_expressions()
        return [
            expression
            for name, expression in zip(
                self._input_node.get_column_names(), self._input_node.get_expressions()
            )
            if name in self._col_labels
        ]

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            parents=[self._input_node], extras={"filter": self._column_names_for_filter}
        )


def _convert_to_truthy_values(conn, input_node, exclude=[]):
    new_column_names = []
    new_column_expressions = []
    new_column_types = []
    for column_name, column_type in zip(
        input_node.get_column_names(), input_node.get_column_types()
    ):
        # We convert everything to booleans based on whether something
        # is truthy or falsy
        new_column_name = f"{column_name}"
        formatted_col = conn.format_name(column_name)
        new_column_names.append(new_column_name)
        if column_name in exclude:
            new_column_expressions.append(formatted_col)
            new_column_types.append(column_type)
        else:
            new_column_expressions.append(
                conn.generate_truthy_bool_expression(formatted_col, column_type)
            )
            new_column_types.append(np.dtype(bool))

    return ChangeColumns(
        conn,
        input_node,
        new_column_names,
        new_column_expressions,
        new_column_types,
        input_node.get_order_column_name(),
    )


class GroupByNode(QueryTreeNode):
    def __init__(
        self,
        conn,
        node,
        by: list[str],
        aggregation,
        sort_by_group_keys,
        columns_to_aggregate: Optional[Iterable],
        order_column_name="",
        agg_args=None,
        agg_kwargs=None,
        dropna=True,
        other_col_id=None,
    ):
        super().__init__(conn, order_column_name)
        self._conn = conn
        self._input_node = node
        self._by = by
        self._aggregation = aggregation
        self._sort_by_group_keys = sort_by_group_keys
        self._columns_to_aggregate = columns_to_aggregate
        # Just set default value for agg args and kwargs so we don't have to deal
        # with any type errors down the stack.
        self._agg_args = agg_args or []
        self._agg_kwargs = agg_kwargs or {}
        self._dropna = dropna
        self._other_col_id = other_col_id

        # Existing infra to cast to boolean type does not handle null values. As
        # a result, we need to implement our own method which manually assigns
        # truthy/falsy values based on the specific dtype.
        if aggregation in (GROUPBY_FUNCTIONS.ALL, GROUPBY_FUNCTIONS.ANY):
            self._input_node = _convert_to_truthy_values(
                self._conn, self._input_node, by
            )

        if aggregation in (
            GROUPBY_FUNCTIONS.SIZE,
            GROUPBY_FUNCTIONS.CUMCOUNT,
            GROUPBY_FUNCTIONS.NGROUP,
        ):
            # groupby.size() returns a Series with group sizes, so the shape of our
            # result is going to be different from how we handle other aggregations.
            # We want to keep group key columns and replace all the other columns with
            # a single dummy column that we will use to keep track of the group sizes.
            new_column_names = []
            new_column_expressions = []
            new_column_types = []
            for column_name, column_type in zip(
                self._input_node.get_column_names(), self._input_node.get_column_types()
            ):
                if column_name in by:
                    new_column_name = f"{column_name}"
                    new_column_expression = self._conn.format_name(column_name)
                    new_column_names.append(new_column_name)
                    new_column_expressions.append(new_column_expression)
                    new_column_types.append(column_type)

            # We need to add a dummy column for our new column
            dummy_col = self._input_node.get_column_names()[0]
            new_column_names.append(__PONDER_REDUCED_COLUMN_NAME__)
            new_column_expressions.append(self._conn.format_name(dummy_col))
            new_column_types.append(np.dtype(int))

            self._input_node = ChangeColumns(
                self._conn,
                self._input_node,
                new_column_names,
                new_column_expressions,
                new_column_types,
                self._input_node.get_order_column_name(),
            )

        # This handles a very specific case where the aggregate function
        # has multiple functions. For example: df.groupby('A').agg(['all', 'sum'])
        # SQL doesn't handle this properly on its own so we have to deal with it.
        if (
            not is_dict_like(aggregation)
            and is_list_like(aggregation)
            and len(aggregation) > 1
        ):
            new_column_names = []
            new_column_expressions = []
            new_column_types = []
            aggregation_map = {}
            for column_name, column_type in zip(
                self._input_node.get_column_names(), self._input_node.get_column_types()
            ):
                if column_name in by:
                    new_column_name = f"{column_name}"
                    new_column_expression = self._conn.format_name(column_name)
                    new_column_names.append(new_column_name)
                    new_column_expressions.append(new_column_expression)
                    new_column_types.append(column_type)
                else:
                    # We should be mindful that we may need to only extract numeric
                    # columns for certain functions.
                    for agg_func in aggregation:
                        agg_name = agg_func.__name__ if callable(agg_func) else agg_func
                        new_column_name = f"{column_name}_{agg_name}"
                        aggregation_map[new_column_name] = agg_func
                        formatted_col = self._conn.format_name(column_name)
                        if agg_func in ("any", "all"):
                            new_column_expression = (
                                self._conn.generate_truthy_bool_expression(
                                    formatted_col, column_type
                                )
                            )
                            new_column_types.append(np.dtype(bool))
                        else:
                            new_column_expression = formatted_col
                            new_column_types.append(column_type)
                        new_column_names.append(new_column_name)
                        new_column_expressions.append(new_column_expression)

            change_columns_node = ChangeColumns(
                self._conn,
                self._input_node,
                new_column_names,
                new_column_expressions,
                new_column_types,
                self._input_node.get_order_column_name(),
            )
            self._input_node = change_columns_node
            self._aggregation = aggregation_map
        if columns_to_aggregate is None:
            self._columns_to_aggregate = [
                n for n in self._input_node.get_column_names() if n not in self._by
            ]
        else:
            self._columns_to_aggregate = columns_to_aggregate

    def get_column_names(self):
        column_names = self._input_node.get_column_names()
        if self._other_col_id is not None:
            column_names = [
                __PONDER_AGG_OTHER_COL_ID__,
                __PONDER_AGG_OTHER_COL_NAME__,
            ] + column_names
        return column_names

    def get_column_types(self):
        column_types = self._input_node.get_column_types()
        if self._other_col_id is not None:
            column_types = (
                ["int", "object"] + column_types
                if isinstance(self._input_node, RenameColumnsNode)
                else column_types
            )
        return column_types

    def generate_sql(self):
        aggregation_function_map = {}
        qualify_clause = ""
        if isinstance(self._aggregation, dict):
            for key, value in self._aggregation.items():
                # ideally we would convert the method to an aggregation enum at the
                # query compiler layer, as we do for pivot, but there are at least 2
                # cases where two objects map to the same enum even but we need to give
                # each a different column name: np.max gets a column called "amax" and
                # np.min gets a column called "amin", while both np.max and "max" map
                # to the MAX reduction and likewhise for min. Since this node is also
                # responsible for generating the output column names, it needs to know
                # whether it's getting e.g. "max" or np.max.
                aggregation_function_map[key] = groupby_function_to_reduce_enum(value)
        else:
            # TODO: we can probably write these using the FilterNode instead
            # We can follow the example with get_group().
            if self._aggregation == GROUPBY_FUNCTIONS.HEAD:
                qualify_clause = self._conn.generate_groupby_head_predicate(
                    self._by,
                    self._input_node.get_order_column_name(),
                    self._agg_kwargs.get("n", 5),
                )
            elif self._aggregation == GROUPBY_FUNCTIONS.TAIL:
                qualify_clause = self._conn.generate_groupby_tail_predicate(
                    self._by,
                    self._input_node.get_order_column_name(),
                    self._agg_kwargs.get("n", 5),
                )
            elif self._aggregation == GROUPBY_FUNCTIONS.NTH:
                # TODO: need to handle the dropna case
                n = self._agg_kwargs.get("n", 0)
                dropna = self._agg_kwargs.get("dropna", None)
                if dropna:
                    raise make_exception(
                        NotImplementedError,
                        PonderError.GROUPBY_NTH_DROPNA_NOT_IMPLEMENTED,
                        "groupby.nth() with dropna=True is not supported yet",
                    )

                if isinstance(n, slice):
                    step = n.step if n.step else 1
                    n = list(range(n.start, n.stop, step))
                elif not is_list_like(n):
                    n = [n]

                qualify_clause = self._conn.generate_groupby_nth_predicate(
                    self._by,
                    self._input_node.get_order_column_name(),
                    n,
                )
            aggregation_function_map = {
                x: self._aggregation for x in self._columns_to_aggregate
            }
        groupby_sql = self._conn.generate_groupby(
            self._sort_by_group_keys,
            self,
            aggregation_function_map,
            self._input_node.get_row_labels_column_names(),
            self._input_node.get_order_column_name(),
            self.get_order_column_name(),
            self._by,
            self._agg_args,
            self._agg_kwargs,
            self._dropna,
            self._other_col_id,
        )
        sql_query = f"{groupby_sql} {qualify_clause}"

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )

        return sql_query

    def get_input(self):
        return self._input_node

    def data_hash(self):
        return self._input_node.data_hash()

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            parents=[self._input_node],
            extras={
                "by": self._by,
                "agg": self._aggregation,
                "sort": self._sort_by_group_keys,
            },
        )


class FilterNode(QueryTreeNode):
    def __init__(
        self,
        conn,
        node,
        predicate: RowWiseFilterPredicates.RowWiseFilterPredicate,
        order_column_name,
    ):
        super().__init__(conn, order_column_name)
        self._input_node = node
        self._predicate = predicate

    def get_column_names(self):
        return self._input_node.get_column_names()

    def return_metadata(self):
        pass

    def generate_sql(self):
        input_node_sql = self._input_node.generate_sql()
        if (
            get_execution_configuration().mask_with_temp_table
            and len(input_node_sql) >= __SQL_QUERY_LEN_LIMIT__
        ):
            temp_table_name = self._conn.create_temp_table_name()

            (
                temp_table_create_sql,
                temp_table_project_sql,
            ) = self._conn._dialect.generate_temp_table_for_subquery(
                temp_table_name, input_node_sql
            )

            logger.debug(f"{self.__class__.__name__} {temp_table_name} being created")
            self._conn.run_query_and_return_results(temp_table_create_sql)
            logger.debug(f"{self.__class__.__name__} {temp_table_name} DONE")
            input_node_sql = temp_table_project_sql
        sql_query = f"""
            SELECT *
            FROM
                {self._conn._dialect.generate_subselect_expression(input_node_sql)}
            {self._predicate.generate_predicate(self._conn)}"""

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def get_column_types(self):
        return self._input_node.get_column_types()

    def get_row_labels_column_names(self):
        return self._input_node.get_row_labels_column_names()

    def data_hash(self):
        return self._input_node.data_hash()

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            parents=[self._input_node], extras={"predicate": self._predicate}
        )


class ProjectNode(QueryTreeNode):
    def __init__(
        self,
        conn,
        node,
        columns_selection,
        project_column_names,
        project_column_types,
        order_column_name,
    ):
        super().__init__(conn, order_column_name)
        self._input_node = node
        self._columns_selection = columns_selection
        self._precompute_columns = project_column_names is None
        if self._precompute_columns:
            self._column_names = conn.get_project_columns(node, columns_selection)
        else:
            self._column_names = project_column_names
        self._column_types = project_column_types

    def get_column_names(self):
        return self._column_names

    def get_expressions(self):
        if is_list_like(self._columns_selection):
            return self._columns_selection
        return [self._columns_selection]

    def return_metadata(self):
        pass

    def generate_sql(self):
        sql_query = self._conn.generate_project_node_query(self)

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def get_column_types(self):
        if self._column_types is not None:
            return self._column_types
        out_column_types = []
        for i in range(len(self._input_node.get_column_names())):
            in_col_name = self._input_node.get_column_names()[i]
            in_col_type = self._input_node.get_column_types()[i]
            for out_col_name in self.get_column_names():
                if in_col_name != out_col_name:
                    continue
                out_column_types.append(in_col_type)
        return out_column_types

    def get_row_labels_column_names(self):
        return self._input_node.get_row_labels_column_names()

    def data_hash(self):
        hash(tuple(dict.fromkeys(self.get_expressions(), self._input_node.data_hash())))

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            parents=[self._input_node],
            extras={"columns_selection": self._columns_selection},
        )


class MapNode(QueryTreeNode):
    """Functions that are built in to a given database."""

    def __init__(
        self,
        conn,
        node,
        fn: MapFunction,
        labels_to_apply_over,
        order_column_name,
    ):
        super().__init__(conn, order_column_name)
        self._input_node = node
        self._function = fn
        if labels_to_apply_over is None:
            raise make_exception(
                NotImplementedError,
                PonderError.MAP_NODE_CANNOT_MAP_OVER_ALL_COLUMNS,
                "Ponder Internal Error: Cannot map across all columns",
            )
        # TODO change to getting column names from self._input_node
        self._labels_to_apply_over = labels_to_apply_over

    def get_column_names(self):
        return self._input_node.get_column_names()

    def return_metadata(self):
        pass

    def generate_sql(self):
        sql_query = self._conn.generate_map_node_query(self)

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def get_column_types(self):
        column_types = []
        for c, t in self._input_node.dtypes.items():
            if c in self._labels_to_apply_over:
                if self._function._return_type == "object":
                    # Special case when string functions return
                    # Python object dtype instead of numpy type
                    column_types.append(np.dtype("O"))
                else:
                    column_types.append(self._function._return_type)
            else:
                column_types.append(t)
        return column_types

    def get_predicates(self):
        input_expressions = self._input_node.get_expressions()
        input_predicates = self._input_node.get_predicates()
        if len(input_predicates) > 0:
            predicates = [
                f"{self._function.generate_sql(self._conn).format(p)}"
                for p in input_predicates
            ]
            left_is_column = False
        elif len(input_expressions) > 0:
            predicates = [
                f"{self._function.generate_sql(self._conn).format(p)}"
                for p in input_expressions
            ]
            left_is_column = False
        else:
            predicates = [
                self._function.generate_sql(self._conn).format(
                    self._conn.format_name(label)
                )
                for label in self._labels_to_apply_over
            ]
            left_is_column = True
        return [
            BinaryPredicate(
                self._conn,
                lhs=pred,
                lhs_type=self._function._return_type,
                lhs_is_literal=False,
                lhs_is_column=left_is_column,
                op=None,
                rhs=None,
                rhs_type=None,
                rhs_is_literal=None,
                rhs_is_column=None,
            )
            for pred in predicates
        ]

    def get_row_labels_column_names(self):
        return self._input_node.get_row_labels_column_names()

    def data_hash(self):
        return self._input_node.data_hash()

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            parents=[self._input_node], extras={"function": self._function}
        )


class ColumnWiseReduceNode(QueryTreeNode):
    def __init__(
        self,
        conn,
        node,
        fn: REDUCE_FUNCTION,
        labels_to_apply_over,
        new_dtypes: pandas.Series,
        percentile: float = None,
        params_list: object = None,
        other_col_id=None,
    ):
        super().__init__(conn)
        self._input_node = node
        self._function = fn
        self._column_types = list(new_dtypes)

        if fn in (REDUCE_FUNCTION.LOGICAL_AND, REDUCE_FUNCTION.LOGICAL_OR):
            self._input_node = _convert_to_truthy_values(
                conn,
                self._input_node,
            )

        if labels_to_apply_over is None:
            raise make_exception(
                NotImplementedError,
                PonderError.REDUCE_NODE_CANNOT_REDUCE_OVER_ALL_COLUMNS,
                "Ponder Internal Error: Cannot apply reduction across all columns",
            )
        self._labels_to_apply_over = labels_to_apply_over
        self._percentile = percentile
        self._params_list = params_list
        self._other_col_id = other_col_id

    def percentile(self) -> Optional[float]:
        return self._percentile

    def params_list(self) -> Optional[object]:
        return self._params_list

    def return_metadata(self):
        pass

    def generate_sql(self):
        sql_query = self._conn.generate_column_wise_reduce_node_query(self)

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def get_column_names(self):
        column_names = list(self._labels_to_apply_over)
        if self._other_col_id is not None:
            column_names = [
                __PONDER_AGG_OTHER_COL_ID__,
                __PONDER_AGG_OTHER_COL_NAME__,
            ] + column_names
        return column_names

    def get_column_types(self):
        column_types = self._column_types
        if self._other_col_id is not None:
            column_types = ["int", "object"] + column_types
        return column_types

    def get_row_labels_column_names(self):
        return [__PONDER_ROW_LABELS_COLUMN_NAME__]

    def data_hash(self):
        return self._input_node.data_hash()

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            parents=[self._input_node], extras={"function": self._function}
        )


class RowWiseReduceNode(QueryTreeNode):
    """This applies a reduction to each row."""

    def __init__(
        self,
        conn,
        node,
        function: REDUCE_FUNCTION,
        result_column_name,
        result_dtype: pandas_dtype,
        order_column_name=__PONDER_ORDER_COLUMN_NAME__,
    ):
        super().__init__(conn, order_column_name=order_column_name)
        self._input_node = node
        self._function = function
        self._result_column_name = result_column_name
        self._result_dtype = result_dtype

    def generate_sql(self):
        sql_query = self._conn.generate_row_wise_reduce_node_query(self)

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def get_column_names(self):
        return [self._result_column_name]

    def get_row_labels_column_names(self):
        return self._input_node.get_row_labels_column_names()

    def get_column_types(self):
        return [self._result_dtype]

    def data_hash(self):
        return self._input_node.data_hash()

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            parents=[self._input_node], extras={"function": self._function}
        )


class RowNumberNode(QueryTreeNode):
    def __init__(self, conn, node, keep_old_row_numbers):
        super().__init__(conn)
        self._input_node = node
        self._keep_old_row_numbers = keep_old_row_numbers

    def generate_sql(self):
        sql_query = self._conn.generate_row_numbers_query(self)

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def get_column_names(self):
        return list(self._input_node.get_column_names())

    def get_row_labels_column_names(self):
        if self._keep_old_row_numbers:
            # TODO: update this to be passed in
            return [__PONDER_ROW_LABELS_COLUMN_NAME__]
        return self._input_node.get_row_labels_column_names()

    def get_column_types(self):
        return self._input_node.get_column_types()

    def data_hash(self):
        return self._input_node.data_hash()

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(parents=[self._input_node])


class RenameColumnsNode(QueryTreeNode):
    def __init__(
        self,
        conn,
        node,
        column_name_renames: dict[str, str],
        order_column_name=__PONDER_ORDER_COLUMN_NAME__,
    ):
        super().__init__(conn, order_column_name)
        self._input_node = node
        self._column_name_renames = column_name_renames
        self._column_names = list(
            column_name
            if column_name not in self._column_name_renames
            else self._column_name_renames[column_name]
            for column_name in self._input_node.get_column_names()
        )
        self._column_types = replace_dtype_column_names(
            self._input_node.get_column_types(), self._column_names
        ).tolist()
        self._conn = conn
        self._row_labels_column_names = [
            self._column_name_renames.get(n, n)
            for n in self._input_node.get_row_labels_column_names()
        ]

    def get_column_names(self):
        return self._column_names

    def get_column_types(self):
        return self._column_types

    def generate_sql(self):
        sql_query = self._conn.generate_rename_columns(
            self._input_node,
            self._column_name_renames,
            self._input_node.get_order_column_name(),
            self._order_column_name,
            self._input_node.get_row_labels_column_names(),
        )

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def get_row_labels_column_names(self):
        return self._row_labels_column_names

    def data_hash(self):
        return self._input_node.data_hash()

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            parents=[self._input_node],
            extras={"column_name_renames": self._column_name_renames},
        )


class LiteralColumnNode(QueryTreeNode):
    def __init__(
        self, conn, node, new_columns, new_dtypes: Iterable, new_values: Iterable = None
    ):
        super().__init__(conn)
        self._conn = conn
        self._input_node = node
        assert len(new_columns) == len(new_dtypes)
        assert new_values is None or len(new_columns) == len(new_values)
        self._new_columns = new_columns
        self._new_dtypes = new_dtypes
        self._new_values = (
            new_values if new_values is not None else [None] * len(new_columns)
        )
        self._current_columns = node.get_column_names()
        self._all_columns = node.get_column_names()
        self._all_columns += new_columns
        self._all_dtypes = node.get_column_types()
        if isinstance(self._all_dtypes, pandas.Series):
            self._all_dtypes = pandas.Series(self._all_dtypes.to_list() + new_dtypes)
        else:
            self._all_dtypes += new_dtypes

    def generate_sql(self):
        column_strings = [f"{self._conn.format_name(c)}" for c in self._current_columns]
        new_column_strings = [
            f"{self._conn.format_name(c)}"
            if c in self._current_columns
            else f"{self._conn.format_value_by_type(self._new_values[i])} "
            f"AS {self._conn.format_name(c)}"
            for i, c in enumerate(self._new_columns)
        ]

        column_strings += new_column_strings
        sql_query = f"""
        SELECT
            {self.get_order_and_labels_column_strings()},
            {", ".join(column_strings)}
        FROM {self._conn.generate_subselect_expression(self._input_node.generate_sql())}
        """
        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def get_column_names(self):
        return self._all_columns

    def get_row_labels_column_names(self):
        return self._input_node.get_row_labels_column_names()

    def get_column_types(self):
        return self._all_dtypes

    def data_hash(self):
        return self._input_node.data_hash()

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            parents=[self._input_node],
            extras={
                "new_columns": self._new_columns,
                "new_dtypes": self._new_dtypes,
                "new_values": self._new_values,
            },
        )


class NullColumnNode(QueryTreeNode):
    def __init__(self, conn, node, current_columns, new_columns, new_dtypes: Iterable):
        super().__init__(conn)
        self._conn = conn
        self._input_node = node
        self._current_columns = current_columns
        self._new_columns = new_columns
        self._new_dtypes = new_dtypes

    def generate_sql(self):
        column_strings = [
            f"{self._conn.format_name(c)}"
            if c in self._current_columns
            else f"NULL AS {self._conn.format_name(c)}"
            for c in self._new_columns
        ]
        sql_query = f"""
        SELECT
            {self.get_order_and_labels_column_strings()},
            {", ".join(column_strings)}
        FROM
            {self._conn.generate_subselect_expression(self._input_node.generate_sql())}
        """

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def get_column_names(self):
        return list(self._new_columns)

    def get_row_labels_column_names(self):
        return self._input_node.get_row_labels_column_names()

    def get_column_types(self):
        return self._new_dtypes

    def data_hash(self):
        return self._input_node.data_hash()

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            parents=[self._input_node],
            extras={
                "current_columns": self._current_columns,
                "new_columns": self._new_columns,
                "new_dtypes": self._new_dtypes,
            },
        )


class UnionAllNode(QueryTreeNode):
    """Union the rows of all input nodes together.

    This node assumes the input nodes all have the same order, label,
    and data column names.
    """

    def __init__(self, conn, left_node, right_nodes, new_dtypes: pandas.Series):
        for node in right_nodes:
            if node._conn != left_node._conn:
                throw_exception_on_cross_database_operations()

        super().__init__(conn)
        # It's not obvious that new_dtypes needs to be a pandas.Series here,
        # so let's make an informative error
        if not isinstance(new_dtypes, pandas.Series):
            raise make_exception(
                TypeError,
                PonderError.UNION_ALL_DTYPES_NOT_SERIES,
                f"new_dtypes must be a pandas.Series, not {type(new_dtypes)}",
            )
        self._input_node = left_node
        self._right_nodes = right_nodes
        self._new_dtypes = new_dtypes

    def generate_sql(self):
        data = []
        for node in (self._input_node, *self._right_nodes):
            input_node_sql = node.generate_sql()
            if (
                get_execution_configuration().mask_with_temp_table
                and len(input_node_sql) >= __SQL_QUERY_LEN_LIMIT__
            ):
                temp_table_name = self._conn.create_temp_table_name()
                (
                    temp_table_create_sql,
                    temp_table_project_sql,
                ) = self._conn._dialect.generate_temp_table_for_subquery(
                    temp_table_name, input_node_sql
                )

                logger.debug(
                    f"{self.__class__.__name__} {temp_table_name} being created"
                )
                self._conn.run_query_and_return_results(temp_table_create_sql)
                logger.debug(f"{self.__class__.__name__} {temp_table_name} DONE")
                input_node_sql = temp_table_project_sql
            data.append(UnionAllDataForDialect(sql=input_node_sql, dtypes=node.dtypes))

        sql_query = self._conn.generate_union_all_query(
            # data=[
            #     UnionAllDataForDialect(sql=node.generate_sql(), dtypes=node.dtypes)
            #     for node in (self._input_node, *self._right_nodes)
            # ],
            data=data,
            column_names=self._input_node.get_column_names(),
            row_labels_column_names=self._input_node.get_row_labels_column_names(),
            order_column_name=self._input_node.get_order_column_name(),
            new_dtypes=self._new_dtypes,
        )

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def get_column_types(self):
        return list(self._input_node.get_column_types())

    def get_column_names(self):
        return self._input_node.get_column_names()

    def get_row_labels_column_names(self):
        return self._input_node.get_row_labels_column_names()

    def data_hash(self):
        leafset = (node.data_hash() for node in (self._input_node, *self._right_nodes))
        return hash(tuple(dict.fromkeys("UnionAllNode", leafset)))

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            parents=[self._input_node, *self._right_nodes],
            extras={"new_dtypes": self._new_dtypes},
        )


class ReassignOrderPostUnionAllNode(QueryTreeNode):
    def __init__(self, conn, node):
        super().__init__(conn)
        self._input_node = node

    def generate_sql(self):
        input_node_sql = self._input_node.generate_sql()
        if (
            get_execution_configuration().mask_with_temp_table
            and len(input_node_sql) >= __SQL_QUERY_LEN_LIMIT__
        ):
            temp_table_name = self._conn.create_temp_table_name()
            (
                temp_table_create_sql,
                temp_table_project_sql,
            ) = self._conn._dialect.generate_temp_table_for_subquery(
                temp_table_name, input_node_sql
            )

            logger.debug(f"{self.__class__.__name__} {temp_table_name} being created")
            self._conn.run_query_and_return_results(temp_table_create_sql)
            logger.debug(f"{self.__class__.__name__} {temp_table_name} DONE")
            input_node_sql = temp_table_project_sql

        sql_query = self._conn.generate_reassign_order_post_union_command(
            self._input_node.get_column_names(),
            input_node_sql,
        )

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def get_column_names(self):
        return self._input_node.get_column_names()

    def get_column_types(self):
        return self._input_node.get_column_types()

    def get_row_labels_column_names(self) -> list[str]:
        return [__PONDER_ROW_LABELS_COLUMN_NAME__]

    def get_order_column_name(self):
        # This should be updated to be passed in
        return __PONDER_ORDER_COLUMN_NAME__

    def data_hash(self):
        return self._input_node.data_hash()

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(parents=[self._input_node])


class NewRowLabelsColumnsNode(QueryTreeNode):
    """
    Adds new row labels columns to the input node, and/or converts one or more data
    columns in the input node to row labels columns. If doing only the latter, note
    that this node will generate the same SQL that the input node generates, but some
    columns that were formerly data columns will now be row labels columns. For example,
    if the input node has columns "a", "b", and "c" and row labels column name
    "__PONDER_ROW_LABELS_COLUMN__", and we pass new_row_labels = None
    but new_row_label_column_names = "a", the SQL of this node is the same as the SQL
    of the input node but we have the following changes:

    TODO: @mvashishtha thinks we should get rid of the functionality where
    new row_labels is None and new_row_label_column_names is a list. In that case,
    input nodes should be responsible for telling other nodes what their row label
    columns and data columns are.

    get_column_names():
        before: ["a", "b", "c"]
        after: ["b", "c"]
    get_row_labels_column_names():
        before: ["__PONDER_ROW_LABELS_COLUMN__"]
        after: ["a"]

    Attributes
    ----------
    conn : SnowflakeConnection
        The connection to the database
    node : QueryTreeNode
        The input node
    new_row_labels : Optional[Dict[str]]
        A dictionary mapping the new row labels column names to existing column names.
    new_row_label_column_names : list[str]
        A list of the new row labels column names.
    """

    def __init__(
        self, conn, node, new_row_labels, new_row_label_column_names: list[str]
    ):
        # TODO: once we enforce mypy, remove this type check
        if not (
            isinstance(new_row_label_column_names, list)
            and all(isinstance(x, str) for x in new_row_label_column_names)
        ):
            raise make_exception(
                RuntimeError,
                PonderError.NEW_ROW_LABELS_COLUMNS_NOT_LIST_OF_STRINGS,
                "new_row_label_column_names must be a list of strings, but "
                + f"instead is: {new_row_label_column_names}",
            )
        super().__init__(conn)
        self._input_node = node
        self._new_row_labels = new_row_labels
        self._new_row_label_column_names = new_row_label_column_names

    def generate_sql(self):
        if self._new_row_labels is not None:
            sql_query = self._conn.generate_new_row_labels_columns_command(
                self._new_row_label_column_names,
                self._input_node.get_column_names(),
                self._input_node.generate_sql(),
                self._new_row_labels,
            )

            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name} if cond
                {sql_query}"""
            )
            return sql_query
        else:
            sql_query = self._input_node.generate_sql()

            logger.debug(
                f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name} else cond
                {sql_query}"""
            )
            return sql_query

    def get_column_names(self):
        return [
            col
            for col in self._input_node.get_column_names()
            if col not in self._new_row_label_column_names
        ]

    def get_column_types(self):
        input_col_names = self._input_node.get_column_names()
        input_col_types = self._input_node.get_column_types()
        return [
            input_col_types[i]
            for i in range(len(input_col_names))
            if input_col_names[i] not in self._new_row_label_column_names
        ]

    def get_row_labels_column_names(self):
        return self._new_row_label_column_names

    def data_hash(self):
        return self._input_node.data_hash()

    # Keep this exclusive to NewRowLabelsColumnsNode for now
    def get_row_labels_column_types(self) -> list[str]:
        return self._input_node.dtypes[self._new_row_label_column_names].tolist()

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            parents=[self._input_node],
            extras={
                "new_row_labels": self._new_row_labels,
                "new_row_label_column_names": self._new_row_label_column_names,
            },
        )


class BinaryPredicate:
    def __init__(
        self,
        conn,
        lhs,
        lhs_type,
        lhs_is_literal,
        # lhs_is_column is supposed [0] to tell whether to "see whether it's [the op is]
        # a transformation/expression or an atomic literal/column, where a parenthesis
        # won't be needed" but it's also used here [1] to decide whether to graft
        # a predicate for some groupby cases, and we can’t use op == "" alone because
        # we sometimes change the op [2] from e.g. “//” to “” even though we are
        # actually doing something in the op. It would be nice to delete lhs_is_column,
        # but we would need a different way to do [1].
        # [0] https://ponder-org.slack.com/archives/C0265H7ES0M/p1692644033821479?thread_ts=1692642850.134779&cid=C0265H7ES0M # noqa: E501
        # [1] https://github.com/ponder-org/soda/blob/bcde8d52e2e5e2afb8890c4fddc116b0fcae66e7/ponder/core/query_tree.py#L917 # noqa: E501
        # [2] https://github.com/ponder-org/soda/blob/bcde8d52e2e5e2afb8890c4fddc116b0fcae66e7/ponder/core/query_tree.py#L5032 # noqa: E501
        lhs_is_column,
        op: str,
        rhs,
        rhs_type,
        rhs_is_literal,
        rhs_is_column,
    ):
        self._conn = conn
        self._lhs = lhs
        self._lhs_type = lhs_type
        self._lhs_is_literal = lhs_is_literal
        self._lhs_is_column = lhs_is_column
        self._op = op
        self._rhs = rhs
        self._rhs_type = rhs_type
        self._rhs_is_literal = rhs_is_literal
        self._rhs_is_column = rhs_is_column
        self._check_types()
        self._coerce_and_rewrite()

    def __str__(self):
        if self._op == "equal_null":
            return self._conn.generate_equal_null_predicate(self._lhs, self._rhs)
        elif self._op in ["=", "<", "<=", ">", ">="]:
            # bigquery won't let us put COLUMN_NAME>=NULL anywhere because
            # "Operands of >= cannot be literal NULL", but we know we're returning
            # FALSE in that case, so we can just return the literal FALSE.
            return (
                "FALSE"
                if self._lhs == "NULL" or self._rhs == "NULL"
                else f"IFNULL({self._lhs}{self._op}{self._rhs}, FALSE)"
            )
        elif self._op == "-" and (
            (
                is_datetime64_dtype(self._lhs_type)
                and is_datetime64_dtype(self._rhs_type)
            )
            or (
                is_datetime64_dtype(self._lhs_type)
                and self._rhs_type == pandas.Timestamp
            )
            or (
                self._lhs_type == pandas.Timestamp
                and is_datetime64_dtype(self._rhs_type)
            )
        ):
            return self._conn.generate_datetime_minus_datetime(self._lhs, self._rhs)
        elif (
            self._op == "-"
            and is_datetime64_dtype(self._lhs_type)
            and (
                self._rhs_type == pandas.Timedelta
                or issubclass(self._rhs_type, pandas.tseries.offsets.BaseOffset)
            )
        ):
            return self._conn.generate_datetime_minus_timedelta(self._lhs, self._rhs)
        elif (
            self._op == "+"
            and is_datetime64_dtype(self._lhs_type)
            and (
                self._rhs_type == pandas.Timedelta
                or issubclass(self._rhs_type, pandas.tseries.offsets.BaseOffset)
            )
        ):
            return self._conn.generate_datetime_plus_timedelta(
                datetime_sql=self._lhs, timedelta_sql=self._rhs
            )
        elif (
            self._op == "+"
            and is_datetime64_dtype(self._rhs_type)
            and (
                self._lhs_type == pandas.Timedelta
                or issubclass(self._lhs_type, pandas.tseries.offsets.BaseOffset)
            )
        ):
            return self._conn.generate_datetime_plus_timedelta(
                datetime_sql=self._rhs, timedelta_sql=self._lhs
            )
        else:
            return f"{self._lhs} {self._op} {self._rhs}"

    def __format__(self, format_spec) -> str:
        """Need this method for f-strings."""
        return str(self)

    def _check_types(self):
        type_error = False
        if self._op in ["==", "<", "<=", ">", ">=", "!=", "equal_null"]:
            if not (
                self._lhs_type == self._rhs_type
                or (
                    is_numeric_dtype(self._lhs_type)
                    and is_numeric_dtype(self._rhs_type)
                )
                or (is_string_dtype(self._lhs_type) and is_string_dtype(self._rhs_type))
                or (
                    is_string_dtype(self._lhs_type)
                    and is_datetime64_dtype(self._rhs_type)
                )
                or (
                    is_datetime64_dtype(self._lhs_type)
                    and is_string_dtype(self._rhs_type)
                )
                or (
                    is_datetime64_dtype(self._lhs_type)
                    and is_datetime64_dtype(self._rhs_type)
                )
                or (
                    is_timedelta64_dtype(self._lhs_type)
                    and self._rhs_type == pandas.Timedelta
                )
                or (
                    self._lhs_type == pandas.Timedelta
                    and is_timedelta64_dtype(self._rhs_type)
                )
                or isinstance(self._lhs, type(None))
                or isinstance(self._rhs, type(None))
                or isinstance(self._lhs, type(np.NaN))
                or isinstance(self._rhs, type(np.NaN))
            ):
                type_error = True
        elif self._op in ["&", "|", "^"]:
            if not (
                (is_integer_dtype(self._lhs_type) or is_bool_dtype(self._lhs_type))
                and (is_integer_dtype(self._rhs_type) or is_bool_dtype(self._rhs_type))
            ):
                type_error = True
        elif self._op in ["/", "//", "%"]:
            if not (
                (is_numeric_dtype(self._lhs_type) and is_numeric_dtype(self._rhs_type))
                or (
                    is_timedelta64_dtype(self._lhs_type)
                    and is_timedelta64_dtype(self._rhs_type)
                )
                or (
                    is_timedelta64_dtype(self._lhs_type)
                    and self._rhs_type == pandas.Timedelta
                )
                or (
                    self._lhs_type == pandas.Timedelta
                    and is_timedelta64_dtype(self._rhs_type)
                )
            ):
                type_error = True
        elif self._op in ["**"]:
            if not (
                (is_numeric_dtype(self._lhs_type) and is_numeric_dtype(self._rhs_type))
            ):
                type_error = True
        elif self._op == "-":
            if not (
                (is_numeric_dtype(self._lhs_type) and is_numeric_dtype(self._rhs_type))
                or (
                    is_datetime64_dtype(self._lhs_type)
                    and is_datetime64_dtype(self._rhs_type)
                )
                or (
                    is_datetime64_dtype(self._lhs_type)
                    and (
                        (
                            self._rhs_type != "object"
                            and self._rhs_type in (pandas.Timestamp, pandas.Timedelta)
                        )
                        or (
                            inspect.isclass(self._rhs_type)
                            and issubclass(
                                self._rhs_type, pandas.tseries.offsets.BaseOffset
                            )
                        )
                    )
                )
                or (
                    self._lhs_type == pandas.Timestamp
                    and is_datetime64_dtype(self._rhs_type)
                )
                or (
                    is_timedelta64_dtype(self._lhs_type)
                    and is_timedelta64_dtype(self._rhs_type)
                )
                or (
                    is_timedelta64_dtype(self._lhs_type)
                    and self._rhs_type == pandas.Timedelta
                )
                or (
                    self._lhs_type == pandas.Timedelta
                    and is_timedelta64_dtype(self._rhs_type)
                )
            ):
                type_error = True
        elif self._op == "+":
            if not (
                (is_numeric_dtype(self._lhs_type) and is_numeric_dtype(self._rhs_type))
                or (is_string_dtype(self._lhs_type) and is_string_dtype(self._rhs_type))
                or (
                    is_timedelta64_dtype(self._lhs_type)
                    and is_timedelta64_dtype(self._rhs_type)
                )
                or (
                    is_timedelta64_dtype(self._lhs_type)
                    and self._rhs_type == pandas.Timedelta
                )
                or (
                    self._lhs_type == pandas.Timedelta
                    and is_timedelta64_dtype(self._rhs_type)
                )
                or (
                    is_datetime64_dtype(self._lhs_type)
                    and (
                        (
                            self._rhs_type != "object"
                            and self._rhs_type in (pandas.Timestamp, pandas.Timedelta)
                        )
                        or (
                            inspect.isclass(self._rhs_type)
                            and issubclass(
                                self._rhs_type, pandas.tseries.offsets.BaseOffset
                            )
                        )
                    )
                )
                or (
                    (
                        (
                            self._lhs_type != "object"
                            and self._lhs_type in (pandas.Timestamp, pandas.Timedelta)
                        )
                        or (
                            inspect.isclass(self._lhs_type)
                            and issubclass(
                                self._lhs_type, pandas.tseries.offsets.BaseOffset
                            )
                        )
                    )
                    and is_datetime64_dtype(self._rhs_type)
                )
            ):
                type_error = True
        elif self._op == "*":
            if not (
                (is_numeric_dtype(self._lhs_type) and is_numeric_dtype(self._rhs_type))
                or (is_string_dtype(self._lhs_type) and is_bool_dtype(self._rhs_type))
                or (
                    is_string_dtype(self._lhs_type) and is_integer_dtype(self._rhs_type)
                )
                or (is_bool_dtype(self._lhs_type) and is_string_dtype(self._rhs_type))
                or (
                    is_integer_dtype(self._lhs_type) and is_string_dtype(self._rhs_type)
                )
            ):
                type_error = True
        if type_error:
            raise make_exception(
                TypeError,
                PonderError.BINARY_OP_INVALID_TYPES,
                (
                    f"unsupported operand type(s) for {self._op}: "
                    + f"{self._lhs_type} and {self._rhs_type}"
                ),
            )

    def _coerce_and_rewrite(self):
        if self._op is not None and self._op != "!=" and self._lhs_is_literal:
            self._lhs = _rewrite_literal_for_binary_op(
                self._lhs, self._lhs_type, self._conn
            )
        elif self._op is not None and self._op != "!=" and self._rhs_is_literal:
            self._rhs = _rewrite_literal_for_binary_op(
                self._rhs, self._rhs_type, self._conn
            )
        # coerce

        cast_lhs_to_int = False
        cast_rhs_to_int = False
        # DuckDB may cast to integer when performing
        # math with negative integers so we try to
        # keep literals as doubles.
        cast_rhs_to_double = False
        cast_lhs_to_double = False

        if (
            self._op in ["==", "<", "<=", ">", ">="]
            and is_bool_dtype(self._lhs_type)
            and not is_bool_dtype(self._rhs_type)
        ):
            cast_lhs_to_int = True
        if (
            self._op in ["==", "<", "<=", ">", ">="]
            and is_bool_dtype(self._rhs_type)
            and not is_bool_dtype(self._lhs_type)
        ):
            cast_rhs_to_int = True
        if self._op in ["+", "-", "*", "**", "/", "//", "%"] and is_bool_dtype(
            self._lhs_type
        ):
            cast_lhs_to_int = True
        if self._op in ["+", "-", "*", "**", "/", "//", "%"] and is_bool_dtype(
            self._rhs_type
        ):
            cast_rhs_to_int = True
        if self._op in ["/", "//", "%"] and is_integer_dtype(self._rhs_type):
            cast_rhs_to_double = True
        if self._op in ["/", "//", "%"] and is_integer_dtype(self._lhs_type):
            cast_lhs_to_double = True
        if (
            self._op in ["&", "|", "^"]
            and is_bool_dtype(self._lhs_type)
            and not is_bool_dtype(self._rhs_type)
        ):
            cast_lhs_to_int = True
        if (
            self._op in ["&", "|", "^"]
            and is_bool_dtype(self._rhs_type)
            and not is_bool_dtype(self._lhs_type)
        ):
            cast_rhs_to_int = True

        if cast_lhs_to_int:
            if self._lhs_is_literal or self._lhs_is_column:
                self._lhs = f"CAST({str(self._lhs)} AS INT)"
            else:
                self._lhs = f"CAST({str(self._lhs)} AS INT)"
        if cast_rhs_to_int:
            if self._rhs_is_literal or self._rhs_is_column:
                self._rhs = f"CAST({str(self._rhs)} AS INT)"
            else:
                self._rhs = f"CAST({str(self._rhs)} AS INT)"

        # "casting" a literal integer to double
        # This obviously is not casting, but it allows us to
        # resolve differences in datatypes between the dbs
        # for literal values. GBQ does not have a double type
        # for instance.
        if cast_rhs_to_double and self._rhs_is_literal:
            self._rhs = f"{str(self._rhs)}.0"
        if cast_lhs_to_double and self._lhs_is_literal:
            self._lhs = f"{str(self._lhs)}.0"

        # rewrite

        if self._op is None:
            self._op = self._rhs = ""
        elif self._op == "==":
            self._op = "="
        elif self._op == "!=":
            comparison = BinaryPredicate(
                self._conn,
                self._lhs,
                self._lhs_type,
                self._lhs_is_literal,
                self._lhs_is_column,
                "==",
                self._rhs,
                self._rhs_type,
                self._rhs_is_literal,
                self._rhs_is_column,
            )
            self._lhs = f"NOT ({comparison})"
            self._lhs_type = np.dtype(bool)
            self._lhs_is_column = False
            self._op = self._rhs = ""
        elif (
            self._op == "+"
            and is_string_dtype(self._lhs_type)
            and is_string_dtype(self._rhs_type)
        ):
            self._lhs = f"CONCAT({str(self._lhs)},{str(self._rhs)})"
            self._lhs_type = np.dtype(str)
            self._lhs_is_column = False
            self._op = self._rhs = ""
        elif (
            self._op == "*"
            and is_string_dtype(self._lhs_type)
            and (is_bool_dtype(self._rhs_type) or is_integer_dtype(self._rhs_type))
        ):
            self._lhs = f"REPEAT({str(self._lhs)},{str(self._rhs)})"
            self._lhs_is_column = False
            self._op = self._rhs = ""
        elif (
            self._op == "*"
            and (is_bool_dtype(self._lhs_type) or is_integer_dtype(self._lhs_type))
            and is_string_dtype(self._rhs_type)
        ):
            self._lhs = f"REPEAT({str(self._rhs)},{str(self._lhs)})"
            self._lhs_type = np.dtype(str)
            self._lhs_is_column = False
            self._op = self._rhs = ""
        elif self._op == "**":
            self._lhs = f"POW({str(self._lhs)},{str(self._rhs)})"
            if is_float_dtype(self._lhs_type) or is_float_dtype(self._rhs_type):
                self._lhs_type = np.dtype(float)
            else:
                self._lhs_type = np.dtype(int)
            self._lhs_is_column = False
            self._op = self._rhs = ""
        elif self._op == "//":
            if not self._lhs_is_literal and not self._lhs_is_column:
                self._lhs = f"({str(self._lhs)})"
            if not self._rhs_is_literal and not self._rhs_is_column:
                self._rhs = f"({str(self._rhs)})"
            self._lhs = f"FLOOR({self._lhs}/{self._rhs})"
            if is_float_dtype(self._lhs_type) or is_float_dtype(self._rhs_type):
                self._lhs_type = np.dtype(float)
            else:
                self._lhs_type = np.dtype(int)
            self._lhs_is_column = False
            self._op = self._rhs = ""
        elif (
            self._op == "&"
            and is_bool_dtype(self._lhs_type)
            and is_bool_dtype(self._rhs_type)
        ):
            self._op = " AND "
        elif self._op == "&":
            self._lhs = self._conn.generate_bitwise_and(self._lhs, self._rhs)
            self._lhs_type = np.dtype(int)
            self._lhs_is_column = False
            self._op = self._rhs = ""
        elif (
            self._op == "|"
            and is_bool_dtype(self._lhs_type)
            and is_bool_dtype(self._rhs_type)
        ):
            self._op = " OR "
        elif self._op == "|":
            self._lhs = self._conn.generate_bitwise_or(self._lhs, self._rhs)
            self._lhs_type = np.dtype(int)
            self._lhs_is_column = False
            self._op = self._rhs = ""
        elif self._op == "^":
            self._lhs = self._conn.generate_bitwise_xor(self._lhs, self._rhs)
            self._lhs_type = np.dtype(int)
            self._lhs_is_column = False
            self._op = self._rhs = ""
        elif self._op == "%":
            # Implements the floored version of modulo used by python
            self._lhs = (
                f"({str(self._lhs)} - {str(self._rhs)} * "
                f"FLOOR({str(self._lhs)} / {str(self._rhs)}))"
            )
            # floored modulo has a result type of the divisor
            if is_float_dtype(self._rhs_type):
                self._lhs_type = np.dtype(float)
            elif (
                is_timedelta64_dtype(self._rhs_type)
                or self._rhs_type == pandas.Timedelta
            ):
                self._lhs_type = np.dtype("m")
                self._rhs_type = np.dtype("m")
            else:
                self._lhs_type = np.dtype(int)
            self._lhs_is_column = False
            self._op = self._rhs = ""
        # parenthesize

        if not self._lhs_is_literal and not self._lhs_is_column and self._op != "":
            self._lhs = f"({str(self._lhs)})"
        if not self._rhs_is_literal and not self._rhs_is_column and self._op != "":
            self._rhs = f"({str(self._rhs)})"

    def return_type(self):
        if self._op in ["=", "<", "<=", ">", ">=", "!=", "AND", "OR", "equal_null"]:
            return np.dtype(bool)
        elif self._op == "-" and (
            (
                is_datetime64_dtype(self._lhs_type)
                and is_datetime64_dtype(self._rhs_type)
            )
            or (
                is_datetime64_dtype(self._lhs_type)
                and self._rhs_type == pandas.Timestamp
            )
            or (
                self._lhs_type == pandas.Timestamp
                and is_datetime64_dtype(self._rhs_type)
            )
        ):
            return np.dtype("m")
        elif self._op in ["-", "+", "%", "//"] and (
            (
                is_timedelta64_dtype(self._lhs_type)
                and is_timedelta64_dtype(self._rhs_type)
            )
            or (
                is_timedelta64_dtype(self._lhs_type)
                and self._rhs_type == pandas.Timedelta
            )
            or (
                self._lhs_type == pandas.Timedelta
                and is_timedelta64_dtype(self._rhs_type)
            )
        ):
            if self._op == "//":
                return np.dtype(int)
            return np.dtype("m")
        elif (
            self._op in ["+", "-", "*", "**", "//", "%"]
            and is_numeric_dtype(self._lhs_type)
            and is_numeric_dtype(self._rhs_type)
        ):
            if is_float_dtype(self._lhs_type) or is_float_dtype(self._rhs_type):
                return np.dtype(float)
            else:
                return np.dtype(int)
        elif self._op == "/":
            return np.dtype(float)
        # is_string_dtype is true for DateOffset subclasses, which we don't want to
        # treat as strings, (and indeed for most objects).
        elif (
            is_string_dtype(self._lhs_type)
            and not (
                isinstance(self._lhs_type, type)
                and issubclass(self._lhs_type, pandas.DateOffset)
            )
            and self._lhs_type != pandas.Timedelta
        ) or (
            is_string_dtype(self._rhs_type)
            and not (
                isinstance(self._rhs_type, type)
                and issubclass(self._rhs_type, pandas.DateOffset)
            )
            and self._rhs_type != pandas.Timedelta
        ):
            return np.dtype(object)
        else:
            return self._lhs_type


class BinaryComparisonNode(QueryTreeNode):
    def __init__(
        self,
        conn,
        input_node,
        op: str,
        other: Any,
        columns: pandas.Series,
        column_types,
        self_on_right,
    ):
        super().__init__(conn)
        self._input_node = input_node
        self._op = op
        self._other = other
        self._columns = columns
        self._column_types = column_types
        self._self_on_right = self_on_right

    def generate_sql(self):
        input_node_sql = self._input_node.generate_sql()
        if (
            get_execution_configuration().mask_with_temp_table
            and len(input_node_sql) >= __SQL_QUERY_LEN_LIMIT__
        ):
            temp_table_name = self._conn.create_temp_table_name()
            (
                temp_table_create_sql,
                temp_table_project_sql,
            ) = self._conn._dialect.generate_temp_table_for_subquery(
                temp_table_name, input_node_sql
            )

            logger.debug(f"{self.__class__.__name__} {temp_table_name} being created")
            self._conn.run_query_and_return_results(temp_table_create_sql)
            logger.debug(f"{self.__class__.__name__} {temp_table_name} DONE")
            input_node_sql = temp_table_project_sql

        expressions = []
        for col, col_type in zip(
            self._conn.format_names_list(list(self._columns)),
            self._column_types,
        ):
            if self._self_on_right:
                predicate = BinaryPredicate(
                    self._conn,
                    lhs=self._other,
                    lhs_type=type(self._other),
                    lhs_is_literal=True,
                    lhs_is_column=False,
                    op=self._op,
                    rhs=col,
                    rhs_type=col_type,
                    rhs_is_literal=False,
                    rhs_is_column=True,
                )
            else:
                predicate = BinaryPredicate(
                    self._conn,
                    lhs=col,
                    lhs_type=col_type,
                    lhs_is_literal=False,
                    lhs_is_column=True,
                    op=self._op,
                    rhs=self._other,
                    rhs_type=type(self._other),
                    rhs_is_literal=True,
                    rhs_is_column=False,
                )
            expressions.append(f"{predicate} AS {col}")
        select = ", ".join(expressions)
        sql_query = (
            f"SELECT {self.get_order_and_labels_column_strings()}, {select} FROM"
            f" {self._conn.generate_subselect_expression(input_node_sql)}"
        )
        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def get_column_names(self):
        return list(self._columns)

    def get_column_types(self):
        return [pred.return_type() for pred in self.get_predicates()]

    def get_predicates(self):
        input_predicates = self._input_node.get_predicates()
        if len(input_predicates) > 0:
            predicates = input_predicates
            pred_types = [pred.return_type() for pred in predicates]
            pred_is_column = False
        else:
            predicates = self._conn.format_names_list(list(self._columns))
            pred_types = self._column_types
            pred_is_column = True

        return [
            BinaryPredicate(
                self._conn,
                lhs=pred,
                lhs_type=pred_type,
                lhs_is_literal=False,
                lhs_is_column=pred_is_column,
                op=self._op,
                rhs=self._other,
                rhs_type=type(self._other),
                rhs_is_literal=True,
                rhs_is_column=False,
            )
            if not self._self_on_right
            else BinaryPredicate(
                self._conn,
                lhs=self._other,
                lhs_type=type(self._other),
                lhs_is_literal=True,
                lhs_is_column=False,
                op=self._op,
                rhs=pred,
                rhs_type=pred_type,
                rhs_is_literal=False,
                rhs_is_column=pred_is_column,
            )
            for pred, pred_type in zip(predicates, pred_types)
        ]

    def get_row_labels_column_names(self):
        return self._input_node.get_row_labels_column_names()

    def data_hash(self):
        leaves = [self._input_node.data_hash()]
        if isinstance(self._other, QueryTreeNode):
            leaves = [self._other.data_hash(), leaves]
        return hash(tuple(dict.fromkeys(leaves)))

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            parents=[self._input_node],
            extras={
                "other": self._other,
                "op": self._op,
                "columns": self._columns,
                "column_types": self._column_types,
            },
        )


class GetFromBinaryComparisonNode(QueryTreeNode):
    def __init__(self, conn, input_node, indexer_node):
        super().__init__(conn)
        self._input_node = input_node
        self._indexer_node = indexer_node

    def generate_sql(self):
        sql_query = self._conn.generate_get_from_binary_comparison_node_query(
            self._input_node, self._indexer_node
        )

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def get_column_names(self):
        return self._input_node.get_column_names()

    def get_column_types(self):
        return self._input_node.get_column_types()

    def get_row_labels_column_names(self):
        return self._input_node.get_row_labels_column_names()

    def data_hash(self):
        return self._input_node.data_hash()

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(parents=[self._input_node, self._indexer_node])


class OrderByNode(QueryTreeNode):
    def __init__(
        self,
        conn,
        input_node,
        columns,
        ascending,
        keep_old_row_numbers,
        handle_duplicates,
    ):
        super().__init__(conn)
        self._input_node = input_node
        self._sort_columns = columns
        self._ascending = ascending
        self._keep_old_row_numbers = keep_old_row_numbers
        self._handle_duplicates = handle_duplicates

    def generate_sql(self):
        sql_query = self._conn.generate_sort_values_query(
            self._input_node,
            self._sort_columns,
            self._ascending,
            self._input_node.get_order_column_name(),
            self._keep_old_row_numbers,
            self.get_row_labels_column_names(),
            self._handle_duplicates,
        )

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def get_column_names(self):
        return list(self._input_node.get_column_names())

    def get_column_types(self):
        return self._input_node.get_column_types()

    def get_row_labels_column_names(self):
        if self._keep_old_row_numbers:
            return [__PONDER_ROW_LABELS_COLUMN_NAME__]
        else:
            return self._input_node.get_row_labels_column_names()

    def data_hash(self):
        return self._input_node.data_hash()

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            parents=[self._input_node],
            extras={
                "sort": self._sort_columns,
                "ascending": self._ascending,
                "handle_duplicates": self._handle_duplicates,
            },
        )


class BinaryPostJoinNode(QueryTreeNode):
    def __init__(
        self,
        conn,
        input_node,
        left_columns,
        left_types,
        right_columns,
        right_types,
        suffixes,
        op,
    ):
        super().__init__(conn)
        self._input_node = input_node
        self._left_columns = left_columns
        self._left_types = left_types
        self._right_columns = right_columns
        self._right_types = right_types
        self._left_suffix = suffixes[0]
        self._right_suffix = suffixes[1]
        self._op = op
        query_and_metadata = self._conn.get_binary_post_join_query_and_metadata(
            self._left_columns,
            self._left_types,
            self._right_columns,
            self._right_types,
            self._op,
            self._left_suffix,
            self._right_suffix,
            self._input_node,
        )
        self._query = query_and_metadata[0]
        self._output_columns = list(entry[0] for entry in query_and_metadata[1])
        self._output_types = list(entry[1] for entry in query_and_metadata[1])

    def generate_sql(self):
        sql_query = self._query

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def get_column_names(self):
        return self._output_columns

    def get_column_types(self):
        return self._output_types

    def get_predicates(self):
        left_predicates = []
        left_types = []
        if not isinstance(self._input_node, EquiJoinNode):
            left_node = self._input_node._input_node._left
        else:
            left_node = self._input_node._left
        left_input_predicates = left_node._input_node.get_predicates()
        if len(left_input_predicates) > 0:
            left_predicates = left_input_predicates
            left_types = [pred.return_type() for pred in left_predicates]
            left_is_column = False
        elif isinstance(left_node._input_node, (RenameColumnsNode)):
            # Two levels deep on the left side
            left_input_input_predicates = (
                left_node._input_node._input_node.get_predicates()
            )
            if len(left_input_input_predicates) > 0:
                left_predicates = left_input_input_predicates
                left_types = [pred.return_type() for pred in left_predicates]
                left_is_column = False
            else:
                left_predicates = left_input_input_predicates
                left_types = left_node._input_node._input_node.get_column_types()
                left_is_column = True
        else:
            left_predicates = self._left_columns
            left_types = self._left_types
            left_is_column = True
        right_predicates = []
        right_types = []
        if not isinstance(self._input_node, EquiJoinNode):
            right_node = self._input_node._input_node._right
        else:
            right_node = self._input_node._right
        right_input_predicates = right_node._input_node.get_predicates()
        if len(right_input_predicates) > 0:
            right_predicates = right_input_predicates
            right_types = [pred.return_type() for pred in right_predicates]
            right_is_column = False
        elif isinstance(right_node._input_node, (RenameColumnsNode)):
            # Two levels deep on the right side
            right_input_input_predicates = (
                right_node._input_node._input_node.get_predicates()
            )
            if len(right_input_input_predicates) > 0:
                right_predicates = right_input_input_predicates
                right_types = [pred.return_type() for pred in right_predicates]
                right_is_column = False
            else:
                right_predicates = right_node._input_node._input_node.get_column_names()
                right_types = right_node._input_node._input_node.get_column_types()
                right_is_column = True
        else:
            right_predicates = self._right_columns
            right_types = self._right_types
            right_is_column = True
        return [
            BinaryPredicate(
                self._conn,
                lhs=left,
                lhs_type=left_type,
                lhs_is_literal=False,
                lhs_is_column=left_is_column,
                op=self._op,
                rhs=right,
                rhs_type=right_type,
                rhs_is_literal=False,
                rhs_is_column=right_is_column,
            )
            for left, left_type, right, right_type in zip(
                left_predicates, left_types, right_predicates, right_types
            )
        ]

    def get_row_labels_column_names(self):
        return self._input_node.get_row_labels_column_names()

    def data_hash(self):
        return self._input_node.data_hash()

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            parents=[self._input_node],
            extras={
                "left_columns": self._left_columns,
                "left_types": self._left_types,
                "right_columns": self._right_columns,
                "right_types": self._right_types,
                "left_suffix": self._left_suffix,
                "right_suffix": self._right_suffix,
                "op": self._op,
            },
        )


class BroadcastBinaryOpNode(QueryTreeNode):
    def __init__(self, conn, input_node, broadcast_node, op, new_columns):
        if input_node._conn != broadcast_node._conn:
            throw_exception_on_cross_database_operations()

        super(BroadcastBinaryOpNode, self).__init__(conn)
        self._input_node = input_node
        self._broadcast_node = broadcast_node
        self._op = op
        self._new_columns = new_columns

    def generate_sql(self):
        sql_query = self._conn.generate_broadcast_binary_op_query(
            self._op, self, self._input_node, self._broadcast_node, self._new_columns
        )

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def get_column_names(self):
        return self._new_columns

    def get_column_types(self):
        left_columns = self._input_node.get_column_names()
        left_types = self._input_node.get_column_types()
        right_columns = self._broadcast_node.get_column_names()
        right_types = self._broadcast_node.get_column_types()
        return [
            left_types[left_columns.index(col)]
            if col in left_columns
            else right_types[right_columns.index(col)]
            for col in self.get_column_names()
        ]

    def get_row_labels_column_names(self):
        return self._input_node.get_row_labels_column_names()

    def data_hash(self):
        return hash(
            tuple(
                dict.fromkeys(
                    (self._input_node.data_hash(), self._broadcast_node.data_hash())
                )
            )
        )

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            parents=[self._input_node, self._broadcast_node],
            extras={"op": self._op},
        )


class DotProductNode(QueryTreeNode):
    def __init__(
        self,
        conn,
        left_input_node,
        left_index,
        right_input_node,
        right_index,
        transposed=False,
        transposed_other=False,
    ):
        if left_input_node._conn != right_input_node._conn:
            throw_exception_on_cross_database_operations()

        super(DotProductNode, self).__init__(conn)
        self._transposed = transposed
        self._transposed_other = transposed_other
        self._left_node = left_input_node
        self._left_index = left_index
        self._left_column_types = left_input_node.get_column_types()
        self._right_node = right_input_node
        self._right_index = right_index
        self._right_column_types = right_input_node.get_column_types()

        if (
            not is_list_like(self._left_column_types)
            and not is_list_like(self._right_column_types)
            and not isinstance(self._left_column_types, pandas.Series)
            and not isinstance(self._right_column_types, pandas.Series)
        ):
            raise make_exception(
                TypeError,
                PonderError.DOT_PRODUCT_OPERAND_TYPES_NOT_LIST_OR_SERIES,
                f"""
                Left and right column types expected to be list or Series type,
                got {type(self._left_column_types)} and
                {type(self._right_column_types)}
                """,
            )

        if not transposed_other:
            self._column_names = [
                *self._right_node.get_column_names(),
            ]
        else:
            num_cols = len(self._right_index)
            self._column_names = [str(i) for i in range(num_cols)]

        self._row_labels_column_names = [__PONDER_ROW_LABELS_COLUMN_NAME__]

        new_col_type = None
        for col_type in list(self._left_column_types) + list(self._right_column_types):
            if "float" in str(col_type).lower():
                new_col_type = col_type

        if new_col_type is None:
            for col_type in list(self._left_column_types) + list(
                self._right_column_types
            ):
                if "int" in str(col_type).lower():
                    new_col_type = col_type
                    break

        if new_col_type is None:
            raise make_exception(
                TypeError,
                PonderError.DOT_PRODUCT_NEW_COL_TYPE_NOT_INT_OR_FLOAT,
                "Something wrong, column types neither int or float",
            )

        self._column_types = [new_col_type for i in range(len(self._column_names))]

    def get_column_names(self):
        return self._column_names

    def generate_sql(self):
        sql_query = self._conn.generate_dot_product_command(
            self._left_node,
            self._right_node,
            self._column_names,
            self._transposed,
            self._transposed_other,
        )

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def get_order_column_name(self):
        return super().get_order_column_name()

    def get_row_labels_column_names(self):
        return self._row_labels_column_names

    def get_column_types(self):
        return self._column_types

    def data_hash(self):
        return hash(
            tuple(
                dict.fromkeys(
                    (self._left_node.data_hash(), self._right_node.data_hash())
                )
            )
        )

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            parents=[self._left_node, self._right_node],
            extras={
                "transposed": self._transposed,
                "transposed_other": self._transposed_other,
                "left_index": self._left_index,
                "right_index": self._right_index,
                "left_types": self._left_column_types,
                "right_types": self._right_column_types,
            },
        )


class DerivedColumnNode(QueryTreeNode):
    def __init__(self, conn, input_node, column_node, new_column_name):
        if conn != input_node._conn:
            throw_exception_on_cross_database_operations()

        super(DerivedColumnNode, self).__init__(conn)
        self._input_node = input_node
        self._column_node = column_node
        self._new_column_name = new_column_name

    def generate_sql(self):
        sql_query = self._conn.generate_derived_columns_sql(self)

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def get_column_names(self):
        return list(self._input_node.get_column_names()) + [self._new_column_name]

    def get_column_types(self):
        return list(self._input_node.get_column_types()) + list(
            self._column_node.get_column_types()
        )

    def get_row_labels_column_names(self):
        return self._input_node.get_row_labels_column_names()

    def data_hash(self):
        return self._input_node.data_hash()

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            parents=[self._input_node, self._column_node],
            extras={"new_column_name": self._new_column_name},
        )


class MonotonicityNode(QueryTreeNode):
    def __init__(
        self,
        conn,
        input_node,
        monotonicity_check_column_name,
        result_column_name,
        increasing,
    ):
        super(MonotonicityNode, self).__init__(conn)
        self._conn = conn
        self._input_node = input_node
        self.monotonicity_check_column_name = monotonicity_check_column_name
        self._result_column_name = result_column_name
        self._increasing = increasing

    def generate_sql(self):
        sql_query = self._conn.generate_monotonicity_check_query(
            self._input_node,
            self.monotonicity_check_column_name,
            self._input_node.get_order_column_name(),
            self._result_column_name,
            self._increasing,
        )

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def get_column_names(self):
        return [self._result_column_name]

    def get_column_types(self):
        return [np.dtype(bool)]

    def data_hash(self):
        self._input_node.data_hash()

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(parents=[self._input_node])


class GetDummiesNode(QueryTreeNode):
    def __init__(
        self,
        conn,
        node,
        column,
        unique_values,
        prefix: str,
        prefix_sep: str,
    ):
        super(GetDummiesNode, self).__init__(conn)
        self._input_node = node
        self._column = column
        self._unique_vals = unique_values
        self._non_dummy_cols = [
            i for i in self._input_node.get_column_names() if i != column
        ]
        self._prefix = prefix
        self._prefix_sep = prefix_sep

    def generate_sql(self):
        sql_query = self._conn.generate_get_dummies_query(
            self._input_node,
            self._non_dummy_cols,
            self._column,
            self._unique_vals,
            self.get_order_column_name(),
            self.get_row_labels_column_names(),
            self._prefix,
            self._prefix_sep,
        )

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def get_row_labels_column_names(self):
        return self._input_node.get_row_labels_column_names()

    def get_column_names(self):
        values_columns = [
            f"{self._prefix}{self._prefix_sep}{generate_column_name_from_value(u)}"
            for u in self._unique_vals
        ]
        return self._non_dummy_cols + values_columns

    def get_column_types(self):
        column_types = []
        for column_name in self._non_dummy_cols:
            for i in range(len(self._input_node.get_column_names())):
                if column_name == self._input_node.get_column_names()[i]:
                    column_types.append(self._input_node.get_column_types()[i])
        return [*column_types, *((np.dtype("bool"),) * len(self._unique_vals))]

    def data_hash(self):
        return self._input_node.data_hash()

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            parents=[self._input_node],
            extras={
                "column": self._column,
                "unique_values": self._unique_vals,
                "prefix": self._prefix,
                "prefix_sep": self._prefix_sep,
            },
        )


class ChangeColumns(QueryTreeNode):
    def __init__(
        self,
        conn,
        node,
        column_names,
        column_expressions,
        column_types,
        order_column_name="",
        has_aggregation=False,
        new_row_labels_column_names: Optional[list[str]] = None,
        reset_order=False,
    ):
        super().__init__(conn, order_column_name)
        self._input_node = node
        self._column_names = column_names
        self._column_expressions = column_expressions
        self._column_types = column_types
        self._has_aggregation = has_aggregation
        self._reset_order = reset_order
        self._row_labels_column_names = (
            self._input_node.get_row_labels_column_names()
            if new_row_labels_column_names is None
            else new_row_labels_column_names
        )

    def get_column_names(self):
        return self._column_names

    def return_metadata(self):
        pass

    def generate_sql(self):
        sql_query = self._conn.generate_project_columns_query(
            input_node=self._input_node,
            column_names=self._column_names,
            column_expressions=self._column_expressions,
            order_column_name=self.get_order_column_name(),
            row_labels_column_names=self.get_row_labels_column_names(),
            has_aggregation=self._has_aggregation,
            reset_order=self._reset_order,
        )

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def get_expressions(self):
        # If the inputs to this node themeselves have "expressions", meaning they can
        # be derived directly from a tip (usually leaf) node, we need to express this
        # node's expressions in terms of that tip node as well.
        input_expressions = self._input_node.get_expressions()
        if len(input_expressions) == 0:
            # fall back to input_predicates if input_expressions is empty.
            input_predicates = self._input_node.get_predicates()
            if len(input_predicates) == 0:
                return self._column_expressions
            input_expressions = [str(p) for p in input_predicates]

        # replace all input column names with the corresponding predicate in
        # self._column_expressions. This string-based replace is NOT robust, but
        # because we construct ChangeColumns with SQL fragments like
        # "SELECT CAST(A AS INT) AS B", we don't have a semantic understanding of
        # column-to-column relationships, like "column B is A cast as int". So we
        # try to replace the column names in the ChangeColumns expressions with the
        # corresponding input expressions.
        # TODO: rewrite ChangeColumns so that we express each column expression as an
        # an object that explicitly tells how to use each input column.
        expressions = []
        for expression in self._column_expressions:
            fixed_expression = expression
            for column, input_expression in zip(
                self._input_node.get_column_names(), input_expressions
            ):
                fixed_expression = fixed_expression.replace(
                    self._conn.format_name(column), input_expression
                )
            expressions.append(fixed_expression)
        return expressions

    def get_predicates(self):
        return [
            BinaryPredicate(
                self._conn,
                lhs=pred,
                lhs_type=column_type,
                lhs_is_literal=False,
                # Since we only have the SQL to figure out what each expression is
                # doing, it's difficult to say whether each expression is just naming a
                # column or doing something more complex. lhs_is_column=False seems
                # safer as the default, since users of the predicate will then add
                # parentheses.
                lhs_is_column=False,
                op=None,
                rhs=None,
                rhs_type=None,
                rhs_is_literal=None,
                rhs_is_column=None,
            )
            for pred, column_type in zip(self.get_expressions(), self._column_types)
        ]

    def get_order_column_name(self):
        return super().get_order_column_name()

    def get_row_labels_column_names(self):
        return self._row_labels_column_names

    def get_column_types(self):
        return self._column_types

    def data_hash(self):
        return self._input_node.data_hash()

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            parents=[self._input_node],
            extras={
                "column_names": self._column_names,
                "column_expressions": self._column_expressions,
                "column_types": self._column_types,
            },
        )


class ReplaceValueNode(QueryTreeNode):
    def __init__(
        self, conn, node, column_name_to_replace_values_in, replace_values_dict
    ):
        super().__init__(conn, node.get_order_column_name())
        self._input_node = node
        self._replace_values_column_name = column_name_to_replace_values_in
        self._replace_values_dict = replace_values_dict

    def get_column_names(self):
        return self._input_node.get_column_names()

    def generate_sql(self):
        sql_query = self._conn.generate_replace_values_statement(
            self._input_node,
            self._replace_values_column_name,
            self._replace_values_dict,
            self.get_order_column_name(),
            self.get_row_labels_column_names(),
        )

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def get_order_column_name(self):
        return self._input_node.get_order_column_name()

    def get_row_labels_column_names(self):
        return self._input_node.get_row_labels_column_names()

    def get_column_types(self):
        return self._input_node.get_column_types()

    def get_predicates(self):
        return self._input_node.get_predicates()

    def data_hash(self):
        return self._input_node.data_hash()

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            parents=[self._input_node],
        )


class ReorderColumnsNode(QueryTreeNode):
    def __init__(
        self,
        conn,
        node,
        column_names,
    ):
        super().__init__(conn, node.get_order_column_name())
        self._input_node = node
        self._conn = conn
        self._column_names = column_names
        col_types = []
        input_column_names = (
            node.get_column_names()
            if isinstance(node.get_column_names(), pandas.Index)
            else pandas.Index(node.get_column_names())
        )
        for col in self._column_names:
            idx = input_column_names.get_loc(col)
            col_types.append(node.get_column_types()[idx])
        self._column_types = col_types

    def get_column_names(self):
        return self._column_names

    def generate_sql(self):
        sql_query = self._conn.generate_reorder_columns_statement(
            self._input_node.generate_sql(),
            self._column_names,
            self.get_order_column_name(),
            self.get_row_labels_column_names(),
        )

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def get_order_column_name(self):
        return super().get_order_column_name()

    def get_row_labels_column_names(self):
        return self._input_node.get_row_labels_column_names()

    def get_column_types(self):
        return self._column_types

    def get_predicates(self):
        return self._input_node.get_predicates()

    def data_hash(self):
        return self._input_node.data_hash()

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            parents=[self._input_node],
            extras={
                "column_names": self._column_names,
                "column_types": self._column_types,
            },
        )


class WithClauseCrossJoin(QueryTreeNode):
    """This node can be used to generate the following type of SQL query Feel
    free to hack it as per your needs as currently it only caters to
    df.rolling(window=<window>, win_type='gaussian').sum(std=<std>) WITH <view-
    name>(<c1, c2, c3...>) AS (SELECT columns FROM <input node>) SELECT <fixed-
    statements>, <IFF based clauses or other aggregations> FROM <view-name> as
    T1, <view-name> as T2 WHERE <selection predicates> AND <join-predicates>
    GROUP BY <group-by clause> ORDER BY <order-by clause>"""

    def __init__(
        self,
        conn,
        node,
        column_names,
        column_expressions,
        column_types,
        order_column_name="",
        new_row_labels_column_names: Optional[list[str]] = None,
        kwargs=None,
    ):
        super().__init__(conn, order_column_name)
        self._input_node = node
        self._conn = conn
        self._column_names = column_names
        self._column_expressions = column_expressions
        self._column_types = column_types
        self._row_labels_column_names = (
            self._input_node.get_row_labels_column_names()
            if new_row_labels_column_names is None
            else new_row_labels_column_names
        )
        self._kwargs = kwargs

    def get_column_names(self):
        return self._column_names

    def return_metadata(self):
        pass

    def generate_sql(self):
        sql_query = self._conn.generate_with_cross_join_full_command(
            self._input_node,
            self._column_names,
            self._column_expressions,
            self.get_order_column_name(),
            self.get_row_labels_column_names(),
            self._kwargs,
        )

        logger.debug(
            f"""{self.__class__.__name__}.{sys._getframe().f_code.co_name}
            {sql_query}"""
        )
        return sql_query

    def get_expressions(self):
        return self._column_expressions

    def get_order_column_name(self):
        return super().get_order_column_name()

    def get_row_labels_column_names(self):
        return self._row_labels_column_names

    def get_column_types(self):
        return self._column_types

    def data_hash(self):
        return self._input_node.data_hash()

    def depends_on(self) -> QueryTreeNodeDependency:
        return QueryTreeNodeDependency(
            parents=[self._input_node],
            extras={
                "column_names": self._column_names,
                "column_expressions": self._column_expressions,
                "column_types": self._column_types,
            },
        )
