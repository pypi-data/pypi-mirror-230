from __future__ import annotations

import copy
import logging
import os
import tempfile
import warnings
from decimal import Decimal

import numpy as np
import pandas
from modin.core.io.file_dispatcher import OpenFile
from pandas.api.types import (
    is_datetime64tz_dtype,
    is_string_dtype,
    is_timedelta64_dtype,
)

from ponder.core.common import __PONDER_ORDER_COLUMN_NAME__
from ponder.core.error_codes import PonderError, make_exception
from ponder.core.sql_connection import SQLConnection

from . import duckdb_dialect

ponder_logger = logging.getLogger(__name__)
client_logger = logging.getLogger("client logger")


class PonderDuckDBConnection(SQLConnection):
    def __init__(self, connection, dialect=duckdb_dialect.duckdb_dialect()):
        super().__init__(connection, dialect)

    def initialize(self, connection, dialect):
        pass

    def execute(self, tree_node):
        # interpret the tree
        # fire off execution
        tree_node_sql = tree_node.generate_sql()
        self.run_query_and_return_results(tree_node_sql)

    def get_project_columns(self, tree_node, fn):
        tree_node_query = tree_node.generate_sql()
        sql = f"""
            WITH INNER_QUERY AS (
                {tree_node_query}
            )
            SELECT
                {fn.format(tree_node_query)}
            FROM
                INNER_QUERY
            LIMIT 1;"""
        df = pandas.DataFrame(
            self.run_query_and_return_results(sql),
            columns=tree_node.get_column_names(),
        )
        cols = list(df.columns[df.iloc[0]])
        return cols

    def get_max_str_splits(self, query_tree, column, pat, n):
        params_list = (column, pat, n, False)
        exp = self._dialect.generate_str_split(params_list)
        sql = f"""
            SELECT
                MAX(ARRAY_LENGTH({exp}))-1
            FROM (
                {query_tree.get_root().generate_sql()}
            )"""
        result = self.run_query_and_return_results(sql)
        if n <= 0:
            return result[0][0]
        else:
            return min(n, result[0][0])

    def get_last_table_update_time(self, table_name):
        # if the table name passed to us is really a query, we'll have to parse
        # the query to find the individual table names.  We can cross that
        # bridge when we get to it. For now return null.
        return None

    def materialize_table(self, table_name, materialized_table_name):
        materialize_table = True
        most_recent_table_update_time = self.get_last_table_update_time(table_name)
        if (
            most_recent_table_update_time is not None
            and table_name in self.table_materialization_time
        ):
            if (
                most_recent_table_update_time
                <= self.table_materialization_time[table_name]
            ) is True:
                materialize_table = False

        if materialize_table is False and table_name in self.materialized_tables:
            return self.materialized_tables[table_name]

        if self._dialect.is_query_like(table_name) or "." in table_name:
            materialization_query = (
                self._dialect.generate_create_temp_table_with_rowid_command(
                    materialized_table_name, table_name
                )
            )
            self.run_query_and_return_results(materialization_query)
        else:
            # if its an existing table - we don't need to create a temp table
            materialized_table_name = table_name
        self.materialized_tables[table_name] = materialized_table_name
        self.table_materialization_time[table_name] = most_recent_table_update_time
        return materialized_table_name

    def materialize_parquet_files_as_table(
        self,
        table_name,
        column_names,
        column_types,
        files,
        storage_options,  # not used for now, will be needed for credentials
        fs,
        hive_partitioning,
    ):
        create_statement = self._dialect.generate_create_table_command(
            table_name,
            column_names,
            column_types,
            __PONDER_ORDER_COLUMN_NAME__,
            None,
            True,
            False,
        )
        client_logger.info("Preparing table in DuckDB using Parquet file(s)...")
        self.run_query_and_return_results(create_statement)
        # registering the fsspec filesystem is an experimental duckdb feature [1] that
        # lets us read from paths like the ones for azure storage that duckdb httpfs
        # doesn't support yet. It also lets us set up the filesystem with storage
        # options like the azure credentials
        # [1] https://duckdb.org/docs/guides/python/filesystems.html
        # TODO(https://ponderdata.atlassian.net/browse/POND-1539): See if we can fix the
        # problem of adlfs trying to close the credential.
        self._connection.register_filesystem(fs)
        copy_into_table_command = (
            self._dialect.generate_copy_into_table_parquet_command(
                table_name, column_names, files, hive_partitioning
            )
        )
        client_logger.info("Configuring Ponder DataFrame in DuckDB...")
        self.run_query_and_return_results(copy_into_table_command)
        client_logger.info("Ponder DataFrame successfully configured in DuckDB")

        return table_name

    def to_pandas(self, tree_node, enforce_row_limit=True):
        tree_node_query = tree_node.generate_sql()
        column_names = copy.deepcopy(tree_node.get_column_names())

        sql = f"""
            SELECT
                {", ".join(
                    self._dialect.format_names_list((*tree_node.get_row_labels_column_names(),
                                            *column_names)))}
            FROM (
                {tree_node_query}
            )
            ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
            {super().generate_limit_clause() if enforce_row_limit else ""}"""
        # Assume that to_pandas() only depends on temporary ponder tables that we never
        # modify, so we can cache query results.
        df = self.run_query_and_return_dataframe(sql, use_cache=True)

        tree_dtypes = tree_node.dtypes
        for column in df:
            if is_string_dtype(df.dtypes[column]):
                # work around https://github.com/duckdb/duckdb/issues/8652
                df[column] = df[column].replace(np.nan, None)
            if column in tree_dtypes:
                # "_PONDER_ROW_LABELS_" has not yet been dropped as a column
                # and since it is not present in tree_dtypes, will cause
                # tree_dtypes[column] to result in KeyError

                # Note: There may be cases like `df.sample()` where there are
                # multiple columns of the same name and type. In this case,
                # df[column] only selects the first of those columns.
                if is_datetime64tz_dtype(tree_dtypes[column]):
                    df[column] = df[column].astype(tree_dtypes[column])
                if is_timedelta64_dtype(tree_dtypes[column]):
                    # Special case conversion to timedelta types. There is
                    # no timedelta type in DuckDB, so we assume we've calculated
                    # the delta in microseconds.
                    df[column] = pandas.to_timedelta(df[column], unit="us")
        return df

    def _copy_file_locally_if_needed(self, file_path, temp_dir):
        temp_file_path = file_path

        if "://" in temp_file_path:
            import os
            import urllib.request

            file_name = self.generate_subquery_table_name()

            file_name_with_path = os.path.join(temp_dir, file_name)

            # S3 path handling
            if file_path.startswith("s3://") or file_path.startswith("S3://"):
                with OpenFile(file_path) as open_file:
                    open_file.fs.download(open_file.path, file_name_with_path)
            else:
                urllib.request.urlretrieve(file_path, file_name_with_path)
            return file_name_with_path
        else:
            return file_path

    def materialize_csv_file_as_table(
        self,
        table_name,
        column_names,
        column_types,
        file_path,
        sep,
        header,
        skipfooter,
        parse_dates,
        date_format,
        na_values,
        on_bad_lines,
        order_column_name,
    ):
        import duckdb

        if header == "infer":
            header = 0

        create_statement = self._dialect.generate_create_table_command(
            table_name,
            column_names,
            column_types,
            order_column_name,
            None,
            True,
            False,
        )
        client_logger.info("Preparing table in DuckDB using CSV file...")
        self.run_query_and_return_results(create_statement)

        with tempfile.TemporaryDirectory() as temp_dir:
            copy_file_path = self._copy_file_locally_if_needed(file_path, temp_dir)
            sep = sep.replace("\\", "")
            load_statement = self._dialect.generate_load_table_from_csv_command(
                copy_file_path,
                table_name,
                column_names,
                column_types,
                sep,
                header,
                date_format,
                na_values,
                on_bad_lines,
            )
            client_logger.info("Configuring Ponder DataFrame in DuckDB...")
            try:
                self.run_query_and_return_results(load_statement)
            except duckdb.InvalidInputException:
                # Fall back to pandas for loading the file. It looks like duckdb's
                # ignore errors parameter doesn't work. The workaround here is to
                # fall back to using Pandas to create a data frame and load it into
                # duckdb. This is ok to do for duckdb because everything runs in-proc
                # in the service anyway.

                # First we clean up the table and sequences we created before because
                # duckdb requires that the pandas dataframe schema match the table
                # schema exactly. So we can't use columns based on sequences.
                ponder_logger.debug(
                    f"Falling back to pandas to load CSV {file_path} into DuckDB..."
                )
                self.run_query_and_return_results(
                    self._dialect.generate_drop_table_command(table_name)
                )

                pandas_df = pandas.read_csv(
                    file_path,
                    sep=sep,
                    header=header,
                    skipfooter=skipfooter,
                    parse_dates=parse_dates,
                    date_format=date_format,
                    na_values=na_values,
                    on_bad_lines=on_bad_lines,
                )
                pandas_df.columns = column_names
                self.materialize_pandas_dataframe_as_table(
                    table_name, pandas_df, order_column_name
                )

            client_logger.info("Ponder DataFrame successfully configured in DuckDB")
            return table_name

    def materialize_rows_to_table(
        self,
        table_name,
        column_names,
        column_types,
        if_exists,
        index,
        index_label,
        row_labels_column_names: list[str],
        row_labels_types: list[np.dtype],
        input_query,
    ):
        table_already_exists = self.table_exists(table_name)
        drop_table_before_create = False
        if if_exists == "fail" and table_already_exists:
            raise make_exception(
                ValueError,
                PonderError.DUCKDB_MATERIALIZE_ROWS_TO_TABLE_THAT_ALREADY_EXISTS,
                f"{table_name} already exists.",
            )

        if if_exists == "replace" and table_already_exists:
            drop_table_before_create = True
            table_already_exists = False

        if not table_already_exists:
            create_columns_list = [
                column_name
                for column_name in column_names
                if column_name not in row_labels_column_names
            ]

            if index:
                create_columns_list.extend(row_labels_column_names)

            create_order_column_name = None
            create_order_column_type = None

            create_columns_types = [
                column_types[i]
                for i in range(len(column_types))
                if column_names[i] not in row_labels_column_names
            ]

            if index:
                create_columns_types.extend(row_labels_types)

            # First do no harm. If there are duplicate column names
            # the database table creation will not succeed. In this
            # scenario - abort early.  The duplication can happen
            # because of how we handle index columns upstream.
            columns_set = set(create_columns_list)
            if len(columns_set) != len(create_columns_list):
                raise RuntimeError(
                    "Dataframe has duplicate column names. Cannot write to database"
                )

            if drop_table_before_create:
                self.drop_table(table_name)

            create_command = self._dialect.generate_create_table_command(
                table_name,
                create_columns_list,
                create_columns_types,
                create_order_column_name,
                create_order_column_type,
                False,
                False,
            )
            self.run_query_and_return_results(create_command)

        insert_rows_command = self._dialect.generate_insert_rows_command(
            table_name,
            column_names,
            row_labels_column_names,
            index,
            index_label,
            input_query,
        )
        self.run_query_and_return_results(insert_rows_command)

        if table_name in self.materialized_tables:
            warnings.warn(
                f"Database table {table_name} was updated."
                + " Dataframes created from this table previously might throw errors."
            )

    def table_exists(self, table_name):
        read_table_metadata_command = (
            self._dialect.generate_read_table_metadata_statement(table_name)
        )
        try:
            self.run_query_and_return_results(read_table_metadata_command)
        except Exception:
            return False
        return True

    def _run_query_and_return_dataframe_uncached(self, query):
        self._execute(query)

        dict_columns = [
            name
            for name, type_code, *_ in self._connection.description
            if type_code == "dict"
        ]
        df = self._connection.df()

        def _convert(struct_dict):
            if pandas.isna(struct_dict):
                return struct_dict
            python_type = struct_dict["_ponder_python_object_type"]
            if python_type != "pandas.Interval":
                raise make_exception(
                    RuntimeError,
                    PonderError.DUCKDB_CANNOT_DESERIALIZE_JSON_OBJECT,
                    f"Cannot deserialize JSON object of type {python_type}",
                )
            data = struct_dict["data"]

            # writing the left and right bounds to JSON objects in duckdb and converting
            # them back to pandas sometimes changes their types to the more precise
            # Decimal. Constructing intervals with Decimal type is not allowed, so
            # downcast to float.
            def _maybe_to_float(value):
                return float(value) if isinstance(value, Decimal) else value

            return pandas.Interval(
                _maybe_to_float(data["left"]),
                _maybe_to_float(data["right"]),
                closed=data["closed"],
            )

        df[dict_columns] = df[dict_columns].applymap(_convert)
        return df

    def run_query_and_return_results(self, query):
        return self._execute(query).fetchall()

    def _execute(self, query):
        if os.environ.get("PONDER_SHOW_SQL", "").lower() == "true":
            ponder_logger.info(
                "\n".join(
                    (
                        "*********** run duckdb query ************",
                        query,
                        "*********** DONE run duckdb query ************",
                    )
                )
            )
        return self._connection.execute(query)

    def materialize_pandas_dataframe_as_table(
        self, table_name, pandas_df, order_column_name
    ):
        pandas_df_copy = self.update_pandas_df_with_supplementary_columns(pandas_df)
        create_table_from_dataframe_statement = (
            self._dialect.generate_create_table_from_dataframe(
                table_name, "pandas_df_copy"
            )
        )
        self._connection.register("pandas_df_copy", pandas_df_copy)
        self.run_query_and_return_results(create_table_from_dataframe_statement)
        return table_name

    def generate_select_with_renamed_columns(
        self, table_name, column_list, renamed_column_list, non_renamed_columns=None
    ):
        formatted_table_name = self.format_name(table_name)

        select_fields_fragment = ", ".join(
            [
                f"{self.format_name(column_list[i])} AS {renamed_column_list[i]}"
                for i in range(len(column_list))
            ]
        )

        if non_renamed_columns:
            select_fields_fragment = (
                select_fields_fragment
                + ", "
                + ", ".join([f" rowid AS {column}" for column in non_renamed_columns])
            )

        return (
            f"SELECT {select_fields_fragment} FROM {formatted_table_name} ORDER BY"
            f" {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}"
        )
