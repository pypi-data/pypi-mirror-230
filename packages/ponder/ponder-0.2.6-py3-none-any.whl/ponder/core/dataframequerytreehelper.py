from enum import Enum

import pandas
from pandas.api.types import is_dict_like, is_list_like, is_number

from .index import DBMSIndex


# case fold the results from a database
class DFCaseFold(Enum):
    NO_FOLD = 1
    UPPER = 2
    LOWER = 3


class DBDFColumnNameMapping(object):
    def __init__(
        self,
        df_column_names,
        db_column_names,
        case_insensitive=False,
        df_case_fold=DFCaseFold.UPPER,
    ):
        self._db_column_names = db_column_names
        self._df_column_names = df_column_names
        self._case_insensitive = case_insensitive

        self._db_to_df = {}
        self._df_to_db = {}

        for df_col_name, db_col_name in zip(df_column_names, db_column_names):
            db_col_name_key = db_col_name
            df_col_name_key = df_col_name
            if self._case_insensitive:
                db_col_name_key = db_col_name.lower()
                df_col_name_key = df_col_name.lower()

            if df_case_fold is DFCaseFold.LOWER:
                df_col_name = df_col_name.lower()
            if df_case_fold is DFCaseFold.UPPER:
                df_col_name = df_col_name.upper()

            self._db_to_df[db_col_name_key] = df_col_name
            self._df_to_db[df_col_name_key] = db_col_name

    def get_db_name_from_df_name(self, col_name):
        if self._case_insensitive:
            col_name = col_name.lower()
        db_col_name = self._df_to_db.get(col_name, col_name)
        if db_col_name == col_name:
            if is_number(col_name):
                col_name = str(col_name)
                return self._df_to_db.get(col_name, col_name)
        return db_col_name

    def get_df_name_from_db_name(self, col_name):
        if self._case_insensitive:
            col_name = col_name.lower()
        df_col_name = self._db_to_df.get(col_name, col_name)
        if df_col_name == col_name:
            if is_number(col_name):
                df_col_name = str(col_name)
                return self._db_to_df.get(col_name, col_name)
        return df_col_name

    def get_db_to_df_map(self):
        self._db_to_df

    def get_database_names_from_dataframe_names(self, dataframe_columns):
        return [self.get_db_name_from_df_name(col) for col in dataframe_columns]

    def take_dataframe_columns(self, df_column_names):
        return type(self)(
            df_column_names=df_column_names,
            db_column_names=[
                self.get_db_name_from_df_name(col) for col in df_column_names
            ],
            case_insensitive=self._case_insensitive,
        )


def generate_new_db_column_name(column_names, column_name, connection):
    new_name = connection.generate_sanitized_name(column_name)
    if new_name in column_names:
        index = 0
        new_name = f"{new_name}_{index}"
        while new_name in column_names:
            index += 1
            new_name = f"{new_name}_{index}"
    return new_name


def generate_db_column_names(column_names, connection):
    ret_val = []
    for col_name in column_names:
        new_name = connection.generate_sanitized_name(col_name)
        if new_name not in ret_val:
            ret_val.append(new_name)
        else:
            index = 0
            new_name = f"{new_name}_{index}"
            while new_name in ret_val:
                index += 1
                new_name = f"{new_name}_{index}"
            ret_val.append(new_name)
    return ret_val


def generate_join_schema(
    left_df_columns, right_df_columns, how, left_on, right_on, suffixes, indicator
):
    on_columns_added = []
    left_column_list = [col for col in left_df_columns]
    if left_on:
        for col in left_on:
            if col not in left_column_list:
                left_column_list.append(col)
                on_columns_added.append(col)

    right_column_list = [col for col in right_df_columns]
    if right_on:
        for col in right_on:
            if col not in right_column_list:
                right_column_list.append(col)
                if col not in on_columns_added:
                    on_columns_added.append(col)

    left_list = [i for i in range(len(left_column_list))]
    right_list = [i for i in range(len(right_column_list))]
    left_df = pandas.Series(left_list).to_frame()
    right_df = pandas.Series(right_list).to_frame()
    left_df = left_df.transpose()
    right_df = right_df.transpose()

    left_df.columns = left_column_list
    right_df.columns = right_column_list

    new_columns = left_df.merge(
        right_df,
        how=how,
        left_on=left_on,
        right_on=right_on,
        suffixes=(suffixes[0], suffixes[1]),
        indicator=indicator,
    ).columns

    new_columns = [col for col in new_columns]

    for col in on_columns_added:
        new_columns.remove(col)
    return new_columns


def generate_merge_asof_schema(
    left_df_columns,
    right_df_columns,
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
):
    on_columns_added = []
    left_column_list = [col for col in left_df_columns]
    if left_on:
        for col in left_on:
            if col not in left_column_list:
                left_column_list.append(col)
                on_columns_added.append(col)
    if left_by:
        for col in left_by:
            if col not in left_column_list:
                left_column_list.append(col)
                on_columns_added.append(col)

    right_column_list = [col for col in right_df_columns]
    if right_on:
        for col in right_on:
            if col not in right_column_list:
                right_column_list.append(col)
                if col not in on_columns_added:
                    on_columns_added.append(col)

    if right_by:
        for col in right_by:
            if col not in right_column_list:
                right_column_list.append(col)
                if col not in on_columns_added:
                    on_columns_added.append(col)

    left_list = [i for i in range(len(left_column_list))]
    right_list = [i for i in range(len(right_column_list))]
    left_df = pandas.Series(left_list).to_frame()
    right_df = pandas.Series(right_list).to_frame()
    left_df = left_df.transpose()
    right_df = right_df.transpose()

    left_df.columns = left_column_list
    right_df.columns = right_column_list

    new_columns = pandas.merge_asof(
        left_df,
        right_df,
        left_on=left_on,
        right_on=right_on,
        left_index=left_index,
        right_index=right_index,
        left_by=left_by,
        right_by=right_by,
        suffixes=(suffixes[0], suffixes[1]),
        tolerance=1,
        allow_exact_matches=allow_exact_matches,
        direction=direction,
    ).columns

    new_columns = [col for col in new_columns]
    for col in on_columns_added:
        new_columns.remove(col)
    return new_columns


def generate_dataframe_names_from_database_names(
    df_names, operators, new_db_col_names, old_db_col_names, column_name_mappings
):
    new_df_names = []
    if all(item in df_names for item in new_db_col_names):
        return new_db_col_names

    if all(item in old_db_col_names for item in new_db_col_names):
        return [
            column_name_mappings.get_df_name_from_db_name(col_name)
            for col_name in new_db_col_names
        ]

    for db_column_name in new_db_col_names:
        no_match_found = True
        if is_list_like(operators):
            for operator in operators:
                agg_name = operator.__name__ if callable(operator) else operator
                if db_column_name.endswith(agg_name):
                    original_db_column_name = db_column_name[: -(len(agg_name) + 1)]
                    original_df_column_name = (
                        column_name_mappings.get_df_name_from_db_name(
                            original_db_column_name
                        )
                    )
                    if original_df_column_name in df_names:
                        new_df_names.append(f"{original_df_column_name}_{agg_name}")
                    no_match_found = False
                    break
            if no_match_found:
                df_column_name = column_name_mappings.get_df_name_from_db_name(
                    db_column_name
                )
                new_df_names.append(df_column_name)
        else:
            df_column_name = column_name_mappings.get_df_name_from_db_name(
                db_column_name
            )
            if df_column_name == db_column_name:
                if db_column_name.endswith("_RENAMED"):
                    original_db_column_name = db_column_name[: -(len("_RENAMED"))]
                    original_df_column_name = (
                        column_name_mappings.get_df_name_from_db_name(
                            original_db_column_name
                        )
                    )
                    df_column_name = f"{original_df_column_name}_RENAMED"
            new_df_names.append(df_column_name)
    return new_df_names


def replace_dtype_column_names(dtypes, df_names):
    if isinstance(dtypes, list):
        ret_val = pandas.Series(data=dtypes, index=df_names, dtype=object)
    else:
        if isinstance(dtypes, tuple):
            return pandas.Series(data=[entry for entry in dtypes], index=df_names)
        data = []
        for _, value in dtypes.items():
            data.append(value)
        ret_val = pandas.Series(data=data, index=df_names, dtype=object)
    return ret_val


def replace_map_with_database_columns(map, column_name_mappings):
    if is_dict_like(map):
        ret_map = None
        if map is not None:
            ret_map = {}
            for key, val in map.items():
                ret_map[column_name_mappings.get_db_name_from_df_name(key)] = val
        return ret_map
    return map


def replace_multi_index_column_names(index, column_name_mappings):
    if column_name_mappings is None:
        return index
    new_names = [
        column_name_mappings.get_df_name_from_db_name(column_name)
        for column_name in index.names
    ]
    ret_val = pandas.MultiIndex(index.levels, codes=index.codes, names=new_names)
    return ret_val


def get_column_names_and_types_from_query_tree(query_tree, column_name_mappings):
    new_column_labels = [
        column_name_mappings.get_df_name_from_db_name(col_name)
        for col_name in query_tree.get_column_names()
    ]
    new_dtypes = replace_dtype_column_names(
        query_tree.get_column_types(), new_column_labels
    )
    return (new_column_labels, new_dtypes)


def get_renamed_query_tree_with_df_column_names(df):
    query_tree = df._query_tree
    column_name_mappings = df.get_db_to_df_map()
    row_labels_column_name_mappings = (
        df.index.get_db_to_df_map() if isinstance(df.index, DBMSIndex) else None
    )
    column_renames = {}
    for col in query_tree.get_column_names():
        column_renames[col] = column_name_mappings.get_df_name_from_db_name(col)
    if row_labels_column_name_mappings is not None:
        for col in query_tree._root.get_row_labels_column_names():
            column_renames[
                col
            ] = row_labels_column_name_mappings.get_df_name_from_db_name(col)
    renamed_query_tree = query_tree.add_column_rename(column_renames)
    return renamed_query_tree


def get_dataframe_column_names_for_pivot(
    df_values_column_name,
    db_values_column_name,
    db_column_names,
    column_name_mappings,
    values_dict,
    prefix_sep=None,
    db_prefix_sep=None,
):
    df_column_names = []

    if prefix_sep is None:
        prefix_sep = "_"
    for db_column_name in db_column_names:
        if db_column_name.startswith(db_values_column_name):
            if prefix_sep is not None:
                column_suffix = db_column_name[
                    len(f"{db_values_column_name}{db_prefix_sep}") :
                ]
            else:
                column_suffix = db_column_name[len(db_values_column_name) :]
                column_suffix = column_suffix[1:]
            new_df_column_name = (
                f"{df_values_column_name}{prefix_sep}{column_suffix}"
                if values_dict is None
                else f"""{df_values_column_name}{prefix_sep}{
                    values_dict.get(column_suffix, column_suffix)}"""
            )
        elif values_dict is not None and db_column_name in values_dict:
            new_df_column_name = values_dict.get(db_column_name, db_column_name)
        else:
            new_df_column_name = column_name_mappings.get_df_name_from_db_name(
                db_column_name
            )
        df_column_names.append(new_df_column_name)
    return df_column_names


def copy_index_with_qt_df_having_same_column_names(df):
    if not isinstance(df._row_labels_cache, DBMSIndex):
        return df._row_labels_cache
    return df._row_labels_cache.copy(same_column_names_in_qt_df=True)


def generate_add_compare_post_join_columns(columns, suffixes):
    ret_column_names = [f"{col}_{suffix}" for col in columns for suffix in suffixes]
    return ret_column_names
