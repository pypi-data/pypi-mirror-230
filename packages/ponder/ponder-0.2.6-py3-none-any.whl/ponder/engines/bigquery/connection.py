from __future__ import annotations

import copy
import json
import logging
import os
import re
import sys

import numpy as np
import pandas
from pandas.api.types import is_timedelta64_dtype

from ponder.core.common import (
    __PONDER_ORDER_COLUMN_NAME__,
    __PONDER_ROW_LABELS_COLUMN_NAME__,
    __SQL_QUERY_LEN_LIMIT__,
    get_execution_configuration,
)
from ponder.core.error_codes import PonderError, make_exception
from ponder.core.sql_connection import SQLConnection

from . import bigquery_dialect

logger = logging.getLogger(__name__)

valid_name_regex_pattern = re.compile("^[a-zA-Z_][a-zA-Z0-9_]*")


class PonderBigQueryConnection(SQLConnection):
    def __init__(self, connection, dialect=bigquery_dialect.bigquery_dialect()):
        super().__init__(connection, dialect)

    def initialize(self, connection, dialect):
        from google.cloud import bigquery

        self._jobconf_init = bigquery.QueryJobConfig(
            allow_large_results=True, create_session=True
        )
        self._jobconf_session = None
        self._session_id = None
        self._connection_properties = None
        self._cur = connection._client
        self._valid_name_regex_pattern = re.compile(valid_name_regex_pattern)

    def create_temp_table_same_session(self, query, temp_table_name):
        if os.environ.get("PONDER_SHOW_SQL", "").lower() == "true":
            logger.info(
                "\n".join(
                    (
                        "*********** run bigquery query ************",
                        query,
                        "*********** DONE run bigquery query ************",
                    )
                )
            )
        try:
            qdata = self._cur.query(query, job_config=self._jobconf_session)
            qdata.result()
            query_job = self._cur.get_job(qdata.job_id, location=qdata.location)
            while query_job.state == "RUNNING":
                query_job = self._cur.get_job(qdata.job_id, location=qdata.location)

        except Exception as err:
            raise make_exception(
                RuntimeError,
                PonderError.BIGQUERY_CREATE_TEMP_TABLE_SAME_SESSION_FAILED,
                f"Unable to create {temp_table_name} due to {err}",
            ) from err

    def run_query_create_session(self, query, temp_table_name):
        from google.cloud import bigquery

        if self._session_id is not None:
            self.create_temp_table_same_session(query, temp_table_name)
            return
        if os.environ.get("PONDER_SHOW_SQL", "").lower() == "true":
            logger.info(
                "\n".join(
                    (
                        "*********** run bigquery query ************",
                        query,
                        "*********** DONE run bigquery query ************",
                    )
                )
            )
        try:
            qdata = self._cur.query(query, job_config=self._jobconf_init)
            if qdata.errors is not None:
                raise make_exception(
                    RuntimeError,
                    PonderError.BIGQUERY_RUN_QUERY_CREATE_SESSION_HAD_ERRORS,
                    qdata.errors,
                )
            qdata.result()
            query_job = self._cur.get_job(qdata.job_id, location=qdata.location)
            while query_job.state == "RUNNING":
                query_job = self._cur.get_job(qdata.job_id, location=qdata.location)
        except Exception as err:
            raise make_exception(
                RuntimeError,
                PonderError.BIGQUERY_RUN_QUERY_CREATE_SESSION_FAILED_AFTER_SUBMITTING_JOB,  # noqa: E501
                f"Unable to create {temp_table_name} due to {err}",
            ) from err

        self._session_id = qdata.session_info.session_id
        self._connection_properties = [
            bigquery.ConnectionProperty(key="session_id", value=self._session_id)
        ]
        self._jobconf_session = bigquery.QueryJobConfig(
            allow_large_results=True, connection_properties=self._connection_properties
        )

    def run_query_and_return_results(self, query):
        if os.environ.get("PONDER_SHOW_SQL", "").lower() == "true":
            logger.info(
                "\n".join(
                    (
                        "*********** run bigquery query ************",
                        query,
                        "*********** DONE run bigquery query ************",
                    )
                )
            )
        try:
            qdata = self._cur.query(query, job_config=self._jobconf_session)
            qdata.result()
            if qdata.errors is not None:
                raise make_exception(
                    RuntimeError,
                    PonderError.BIGQUERY_RUN_QUERY_AND_RETURN_RESULTS_HAD_ERRORS,
                    qdata.errors,
                )
            return qdata
        except Exception as err:
            raise make_exception(
                RuntimeError,
                PonderError.BIGQUERY_RUN_QUERY_AND_RETURN_RESULTS_HAD_ERRORS_2,
                f"Error in {query} because {err}",
            ) from err

    def _run_query_and_return_dataframe_uncached(self, query):
        try:
            qdata = self.run_query_and_return_results(query)
            # TODO(https://github.com/googleapis/python-bigquery/issues/1604): get types
            # without using private attributes.
            # See the following code for QData.to_dataframe for the
            # type conversion notes
            # https://github.com/googleapis/python-bigquery/blob/3e021a46d387a0e3cb69913a281062fc221bb926/google/cloud/bigquery/table.py#L1931

            # The following ensures that the native pandas dtype is used
            # instead of casting to the smallest type, unfortunately the
            # use of int_dtype has an impact on other columns such as
            # floats when using joins.
            # df = qdata.to_dataframe(bool_dtype=None, int_dtype=None)

            df = qdata.to_dataframe(bool_dtype=None)

            json_columns = [
                schema_field.name
                for schema_field in qdata._query_results.schema
                if schema_field.field_type == "JSON"
            ]

            def _convert(json_string):
                if pandas.isna(json_string):
                    return json_string
                json_dict = json.loads(json_string)
                if not isinstance(json_dict, dict):
                    return json_dict
                python_type = json_dict["_ponder_python_object_type"]
                if python_type != "pandas.Interval":
                    raise make_exception(
                        RuntimeError,
                        PonderError.BIGQUERY_CANNOT_DESERIALIZE_JSON_OBJECT,
                        f"Cannot deserialize JSON object of type {python_type}",
                    )
                data = json_dict["data"]
                return pandas.Interval(
                    data["left"],
                    data["right"],
                    closed=data["closed"],
                )

            df[json_columns] = df[json_columns].applymap(_convert)
            return df

        except Exception as err:
            raise make_exception(
                RuntimeError,
                PonderError.BIGQUERY_RUN_QUERY_AND_RETURN_DATAFRAME_FAILED,
                f"Error in getting table metadata {query} because {err}",
            ) from err

    def get_temp_table_metadata(self, table_name):
        read_metadata_command = self._dialect.generate_read_table_metadata_statement(
            table_name
        )
        df = self.run_query_and_return_dataframe(read_metadata_command, use_cache=True)
        df = df.loc[
            :,
            ~df.columns.isin(
                (__PONDER_ORDER_COLUMN_NAME__, __PONDER_ROW_LABELS_COLUMN_NAME__)
            ),
        ]
        for column in df:
            if df[column].dtype.name == "dbdate":
                # BigQuery uses a dbdate type extension to pandas to represent
                # dates. https://googleapis.dev/python/db-dtypes/latest
                # we convert this to datetime64 here for consistency
                df[column] = df[column].astype("datetime64[ns]")
        return (df.columns.tolist(), df.dtypes.tolist())

    def get_num_rows(self, tree_node):
        sql = tree_node.get_root().generate_sql()
        result = self.run_query_and_return_results(
            self._dialect.generate_select_count_star_statement(sql)
        )
        for row in result:
            return row[0]

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
            self.run_query_and_return_results(sql).to_dataframe(bool_dtype=None),
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
        # Use run_query_and_return_dataframe for BigQuery
        result = self.run_query_and_return_dataframe(sql, use_cache=True)
        if n <= 0:
            return result.iloc[0][0]
        else:
            return min(n, result.iloc[0][0])

    def get_last_table_update_time(self, table_name):
        if self._dialect.is_query_like(table_name):
            return None
        sql_query = self._dialect.generate_find_last_altered_time_command(table_name)
        result = self.run_query_and_return_results(sql_query)
        if result.errors is not None:
            raise make_exception(
                RuntimeError,
                PonderError.BIGQUERY_GET_LAST_TABLE_UPDATE_TIME_HAD_ERRORS,
                result.errors,
            )

        for row in result:
            return row[0]

    def materialize_table(self, table_name, materialized_table_name):
        if "." not in table_name and not self._dialect.is_query_like(table_name):
            table_name = (
                f"{get_execution_configuration().bigquery_dataset}.{table_name}"
            )
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

        materialization_query = (
            self._dialect.generate_create_temp_table_with_rowid_command(
                materialized_table_name, table_name
            )
        )
        self.run_query_create_session(materialization_query, materialized_table_name)
        self.materialized_tables[table_name] = materialized_table_name
        self.table_materialization_time[table_name] = most_recent_table_update_time
        return materialized_table_name

    def to_pandas(self, tree_node, enforce_row_limit=True):
        tree_node_query = tree_node.generate_sql()
        column_names = copy.deepcopy(tree_node.get_column_names())

        sql = f"""
            SELECT
                {", ".join(
                    self.format_names_list((*tree_node.get_row_labels_column_names(),
                                            *column_names)))}
            FROM (
                {tree_node_query}
            )
            ORDER BY {__PONDER_ORDER_COLUMN_NAME__}
            {super().generate_limit_clause() if enforce_row_limit else ""}"""
        df = self.run_query_and_return_dataframe(sql, use_cache=True)
        tree_dtypes = tree_node.dtypes
        for column in df:
            if column in tree_dtypes:
                # "_PONDER_ROW_LABELS_" has not yet been dropped as a column
                # and since it is not present in tree_dtypes, will cause
                # tree_dtypes[column] to result in KeyError

                # Note: There may be cases like `df.sample()` where there are
                # multiple columns of the same name and type. In this case,
                # df[column] only selects the first of those columns.
                if df[column].dtype.name == "dbdate":
                    # BigQuery uses a dbdate type extension to pandas to represent
                    # dates. https://googleapis.dev/python/db-dtypes/latest
                    # we convert this to datetime64 here for consistency
                    df[column] = df[column].astype("datetime64[ns]")
                if is_timedelta64_dtype(tree_dtypes[column]):
                    # Special case conversion to timedelta types. There is
                    # no timedelta type in BigQuery, so we assume we've calculated
                    # the delta in microseconds.
                    df[column] = pandas.to_timedelta(df[column], unit="us")

        return df

    def materialize_pandas_dataframe_as_table(
        self, table_name, pandas_df, order_column_name
    ):
        from google.cloud import bigquery

        pandas_df_copy = self.update_pandas_df_with_supplementary_columns(pandas_df)
        pandas_df_copy = pandas_df.copy(deep=True)
        pandas_df_copy[__PONDER_ORDER_COLUMN_NAME__] = pandas_df_copy[
            __PONDER_ROW_LABELS_COLUMN_NAME__
        ] = range(len(pandas_df_copy))

        if "." not in table_name:
            #  way to load a CSV into a temp table, and if you are loading a CSV to a
            #  non-temp table, you need at least the dataset name
            if get_execution_configuration().bigquery_dataset is None:
                make_exception(
                    ValueError,
                    PonderError.BIGQUERY_MATERIALIZE_PANDAS_DATAFRAME_MISSING_DATASET,
                    "Bigquery needs the name of a dataset it should read CSVs to. "
                    + "Please call ponder.configure() with the parameter "
                    + "`bigquery_dataset`.",
                )
            logger.debug("Adding default bigquery dataset to table name.")
            table_name = (
                get_execution_configuration().bigquery_dataset + "." + table_name
            )

        create_statement = self._dialect.generate_create_table_command(
            table_name,
            pandas_df_copy.columns,
            pandas_df_copy.dtypes,
            order_column_name,
            None,
            True,
            False,
            True,
        )
        self.run_query_create_session(create_statement, table_name)
        pandas_job_config = bigquery.LoadJobConfig()
        pandas_job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
        job = self._cur.load_table_from_dataframe(
            pandas_df_copy,
            table_name,
            job_config=pandas_job_config,
        )
        job.result()
        return table_name

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
        new_column_types = {
            column_name: column_type
            for column_name, column_type in zip(column_names, column_types)
        }
        # pandas documentation says that you should pass header=0 if you are over-riding
        # the column nmaes.  In our case we got the column names from the file in the
        # first place.  We don't want to infer the header again. So we set it to 0 if
        # the parameter was set to "infer".  If it was set to anything else, we
        # use it.  Also the low_memory=False parameter is not compatible with multibyte
        # separators so we only set it if the separator has only one character.
        pandas_df = pandas.read_csv(
            file_path,
            sep=sep,
            header=0 if header == "infer" else header,
            skipfooter=skipfooter,
            parse_dates=parse_dates,
            date_format=date_format,
            names=column_names,
            dtype=new_column_types,
            na_values=na_values,
            on_bad_lines=on_bad_lines,
            low_memory=False if len(sep) == 1 else True,
        )
        return self.materialize_pandas_dataframe_as_table(
            table_name, pandas_df, order_column_name
        )

    def table_exists(self, table_name):
        read_table_metadata_command = (
            self._dialect.generate_read_table_metadata_statement(table_name)
        )
        try:
            qdata = self.run_query_and_return_results(read_table_metadata_command)
        except Exception as err:
            # An exception is expected here if the table doesn't exist.
            err = err
            return False
        if qdata.errors is None:
            return True
        return False

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
        if "." not in table_name:
            table_name = (
                f"{get_execution_configuration().bigquery_dataset}.{table_name}"
            )
        table_already_exists = self.table_exists(table_name)
        if if_exists == "fail" and table_already_exists:
            raise make_exception(
                ValueError,
                PonderError.BIGQUERY_MATERIALIZE_ROWS_TO_TABLE_THAT_ALREADY_EXISTS,
                f"Table {table_name} already exists.",
            )

        if if_exists == "replace" and table_already_exists:
            self.drop_table(table_name)
            table_already_exists = False

        if table_already_exists is not True:
            create_columns_list = [
                column_name
                for column_name in column_names
                if column_name not in row_labels_column_names
            ]

            if index:
                create_columns_list.extend(row_labels_column_names)

            create_order_column_name = None
            create_order_column_type = None
            # if index:
            #    if len(index_label or "") > 0:
            #        create_order_column_name = index_label
            #    else:
            #        create_order_column_name = order_column_name
            #    create_order_column_type = [
            #        column_types[i]
            #        for i in range(len(column_names))
            #        if column_names[i] == order_column_name
            #    ][0]

            create_columns_types = [
                column_types[i]
                for i in range(len(column_types))
                if column_names[i] not in row_labels_column_names
            ]

            if index:
                create_columns_types.extend(row_labels_types)

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

    # BigQuery version differs from the super class in how temp tables
    # can be used to mitigate issues with large select in statements. Some
    # of the bug fixes made in this function may not be copied over to
    # snowflake or other databases.
    def generate_select_from_in(self, node):
        if node._col_labels is None:
            stringified_columns = "*"
        else:
            stringified_columns = ", ".join(
                (
                    self.get_order_and_labels_column_strings(node),
                    *[self.format_name(column) for column in node._col_labels],
                )
            )
        input_node_sql = node._input_node.generate_sql()

        if (
            get_execution_configuration().mask_with_temp_table
            and len(input_node_sql) >= __SQL_QUERY_LEN_LIMIT__
        ):
            temp_table_name = self.create_temp_table_name()
            (
                temp_table_create_sql,
                temp_table_project_sql,
            ) = self._dialect.generate_temp_table_for_subquery(
                temp_table_name, input_node_sql
            )

            logger.debug(
                f"""
                {self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} being created
                """
            )
            self.run_query_and_return_results(temp_table_create_sql)
            logger.debug(
                f"""
                {self.__class__.__name__}.{sys._getframe().f_code.co_name}
                {temp_table_name} DONE
                """
            )
            input_node_sql = temp_table_project_sql
        column_type_for_filter = None
        if node._row_labels is not None:
            # Big Query cannot use an IN operator w/ Date and Timestamp
            # so we cast if required
            column_type_for_filter = type(node._row_labels[0])
            if len(node._column_names_for_filter) > 1:
                raise make_exception(
                    NotImplementedError,
                    PonderError.BIGQUERY_IN_FILTER_ON_MULTIPLE_COLUMNS,
                    "Ponder Internal Error: cannot filter with a condition on "
                    + "multiple columns yet",
                )
            if len(node._row_labels) == 1:
                single_label = node._row_labels[0]
                if isinstance(single_label, str):
                    single_label = self.format_value(single_label)
                elif isinstance(single_label, pandas.Timestamp):
                    single_label = self.format_value_by_type(single_label)
                row_positions = f"({single_label})"

            elif len(node._row_labels) == 0:
                # Edge case where we drop all rows
                pass
            else:
                row_positions = (
                    "("
                    + ", ".join(self.format_value_by_type(p) for p in node._row_labels)
                    + ")"
                )

            formatted_name_type = self.format_name_cast_to_type(
                node._column_names_for_filter[0], column_type_for_filter
            )
            output_sql = f"""
                SELECT
                    {stringified_columns}
                FROM (
                    {input_node_sql}
                )
                WHERE
                    {formatted_name_type} IN {row_positions}
"""
        else:
            output_sql = f"SELECT {stringified_columns} FROM ({input_node_sql})"
        return output_sql

    def generate_sanitized_values(self, value_list):
        sanitized_value_dict = {}
        for value in value_list:
            if not self._valid_name_regex_pattern.fullmatch(str(value)):
                # if any value in the list needs sanitizing - we make all of them
                # sanitized because otherwise you can run into type mismatches.
                # Sanitizing involves generating string values while the input
                # could be of any type.
                for value in value_list:
                    sanitized_value_dict[value] = self.generate_sanitized_name(value)
                return sanitized_value_dict
        return None
