import copy
import gzip
import json
import logging
import os
import random
import shutil
import string
import tempfile

import fsspec
import numpy as np
import pandas
from modin.core.io.file_dispatcher import OpenFile
from pandas.api.types import is_datetime64tz_dtype, is_timedelta64_dtype

from ponder.core.common import __PONDER_ORDER_COLUMN_NAME__, get_execution_configuration
from ponder.core.error_codes import PonderError, make_exception
from ponder.core.sql_connection import SQLConnection

from . import snowflake_dialect

logger = logging.getLogger(__name__)
client_logger = logging.getLogger("client logger")


class PonderSnowflakeConnection(SQLConnection):
    def __init__(
        self, snowflake_connection, dialect=snowflake_dialect.snowflake_dialect()
    ):
        super().__init__(
            snowflake_connection,
            dialect,
        )

    def initialize(self, connection, dialect):
        self._cur = self._connection.cursor()

        if self._query_timeout is not None:
            self.run_query_and_return_results(
                self._dialect.generate_query_timeout_command(
                    get_execution_configuration().query_timeout
                )
            )

        self.run_query_and_return_results(self._dialect.generate_query_tag_command())
        self.run_query_and_return_results(
            self._dialect.generate_abort_detached_queries_command()
        )

        # The current database and schema might be defaults specified by the
        # administrator and may not have been passed as part of the connection
        # string. So retrieve them here.
        result = self.run_query_and_return_results(
            self._dialect.generate_get_current_database_command()
        )
        self._database = result[0][0]

        result = self.run_query_and_return_results(
            self._dialect.generate_get_current_schema_command()
        )
        self._schema = result[0][0]

    def run_query(self, query):
        from snowflake.connector.errors import ProgrammingError

        if os.environ.get("PONDER_SHOW_SQL", "").lower() == "true":
            logger.info(
                "\n".join(
                    (
                        "*********** run snowflake query ************",
                        query,
                        "*********** DONE run snowflake query ************",
                    )
                )
            )
        try:
            self._cur.execute(query)
        except ProgrammingError as err:
            if err.errno == 630:
                raise make_exception(
                    RuntimeError,
                    PonderError.SNOWFLAKE_RUN_QUERY_TIMED_OUT,
                    (
                        "Snowflake query timed out after "
                        + f"{self._query_timeout} second(s). To avoid this error, "
                        + "override the default query timeout by using "
                        + "ponder.configure(query_timeout = your_new_timeout)."
                    ),
                ) from err
            raise err

    def run_query_and_return_results(self, query):
        try:
            self.run_query(query)
        except Exception:
            raise
        return self._cur.fetchall()

    def _run_query_and_return_dataframe_uncached(self, query):
        from snowflake.connector.cursor import ResultMetadata

        self.run_query(query)
        cursor_columns: list[ResultMetadata] = self._cur.description
        df = self._cur.fetch_pandas_all()

        for column_metadata in cursor_columns:
            column = column_metadata.name
            # type codes specified here:
            # https://docs.snowflake.com/en/user-guide/python-connector-api.html#type-codes
            # col type 0 is numeric that isn't always mapped correctly by Snowflake.
            if column_metadata.type_code == 0:
                # examples where the arrow representation of numeric types
                # may not be what we expect on the python side
                if df[column].dtype == "int8":
                    if column_metadata.precision >= 18 and column_metadata.scale == 0:
                        df[column] = df[column].astype("int64")
                if df[column].dtype == "O":
                    # POND-838 df.value_counts(normalize=true) results in type issue
                    df[column] = pandas.to_numeric(df[column])
            # col type 3 is DATE that isn't mapped correctly by Snowflake.
            elif column_metadata.type_code == 3:
                df[column] = pandas.to_datetime(df[column])
            elif column_metadata.type_code in (5, 9, 10):
                # column type 5 is VARIANT. strings in variant columns get double quotes
                # around them: "By default, when VARCHARs, DATEs, TIMEs, and TIMESTAMPs
                # are retrieved from a VARIANT column, the values are surrounded by
                # double quotes." source:
                # https://docs.snowflake.com/en/sql-reference/data-types-semistructured.html#using-values-in-a-variant
                # replace any string s with json.loads(s)
                # other people seem to do the same thing:
                # https://github.com/snowflakedb/snowflake-connector-python/issues/544
                # also do the same with OBJECT, which has type code 9.
                # also do the same with ARRAY, which has type code 10.
                def _extract(json_string):
                    json_value = json.loads(json_string)
                    if not isinstance(json_value, dict) or pandas.isna(json_value):
                        return json_value
                    python_type = json_value["_ponder_python_object_type"]
                    if python_type != "pandas.Interval":
                        raise make_exception(
                            RuntimeError,
                            PonderError.SNOWFLAKE_CANNOT_DESERIALIZE_JSON_OBJECT,
                            f"Cannot deserialize JSON object of type {python_type}",
                        )
                    data = json_value["data"]
                    return pandas.Interval(
                        data["left"],
                        data["right"],
                        closed=data["closed"],
                    )

                df[column] = df[column].apply(
                    lambda s: _extract(s) if isinstance(s, str) else s
                )

        return df

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
            self.run_query_and_return_results(sql), columns=tree_node.get_column_names()
        )
        cols = list(df.columns[df.iloc[0]])
        return cols

    def get_max_str_splits(self, query_tree, column, pat, n):
        params_list = (self.format_name(column), pat, n, False)
        exp = self._dialect.generate_str_split(params_list)
        sql = f"""
            SELECT
                MAX(ARRAY_SIZE({exp}))-1
            FROM (
                {query_tree.get_root().generate_sql()}
            )"""
        result = self.run_query_and_return_results(sql)
        if n <= 0:
            return result[0][0]
        else:
            return min(n, result[0][0])

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
        # Assume that to_pandas() only depends on temporary ponder tables that we never
        # modify, so we can cache query results.
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
                if is_datetime64tz_dtype(tree_dtypes[column]):
                    # type code 7 is TIMESTAMP_TZ, which is stored as a timestamp
                    # together with an offset from UTC. In pandas, it seems that
                    # timestamps are stored with a particular zone,
                    # e.g. "America/Tijuana". Snowflake pandas connector always
                    # returns timestamps in the timezone of session parameter
                    # TIMEZONE, which default to "America/Los_Angeles". Because
                    # Snowflake stores the offset but not the time zone, there's
                    # no way it to know
                    df[column] = df[column].astype(tree_dtypes[column])
                if is_timedelta64_dtype(tree_dtypes[column]):
                    # Special case conversion to timedelta types. There is
                    # no timedelta type in Snowflake, so we assume we've calculated
                    # the delta in nanoseconds.
                    df[column] = pandas.to_timedelta(df[column], unit="ns")

        return df

    def _move_file_to_snowflake_staging(self, file_path, table_name):
        temp_file_path = file_path

        if "://" in temp_file_path:
            import os
            import tempfile
            import urllib.request

            with tempfile.TemporaryDirectory() as temp_dir:
                file_name = "".join(random.sample(string.ascii_lowercase, 10)) + ".csv"

                file_name_with_path = os.path.join(temp_dir, file_name)

                # S3 path handling
                if file_path.startswith("s3://") or file_path.startswith("S3://"):
                    with OpenFile(file_path) as open_file:
                        open_file.fs.download(open_file.path, file_name_with_path)
                else:
                    urllib.request.urlretrieve(file_path, file_name_with_path)

                put_command = self._dialect.generate_put_command(
                    file_name_with_path, table_name
                )

                self.run_query_and_return_results(put_command)
        else:
            put_command = self._dialect.generate_put_command(file_path, table_name)
            self.run_query_and_return_results(put_command)

    def _move_parquet_files_to_snowflake_staging(
        self, files, table_name, storage_options
    ):
        import os
        import tempfile
        import urllib.request

        with tempfile.TemporaryDirectory() as temp_dir:
            for i, file_path in enumerate(files):
                if "://" in file_path and not file_path.startswith("file://"):
                    file_name = f"file-{i}.parquet"
                    full_file_path = os.path.join(temp_dir, file_name)

                    if file_path.startswith("https://") or file_path.startswith(
                        "http://"
                    ):
                        urllib.request.urlretrieve(file_path, full_file_path)
                    else:
                        # For now we copy files locally using fsspec, but what we really
                        # should be doing is a COPY INTO -> interal stage. In general
                        # it seems to be a good idea to move things to staging.
                        openfile = fsspec.open(file_path, **storage_options)
                        openfile.fs.download(openfile.path, full_file_path)

                    put_command = self._dialect.generate_put_command(
                        full_file_path, table_name
                    )

                    self.run_query_and_return_results(put_command)
                else:
                    put_command = self._dialect.generate_put_command(
                        file_path, table_name
                    )
                    self.run_query_and_return_results(put_command)

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
        if header == "infer":
            header = 0
        create_statement = self._dialect.generate_create_table_command(
            table_name, column_names, column_types, order_column_name, None, True, False
        )
        client_logger.info("Preparing table in Snowflake using CSV file...")
        self.run_query_and_return_results(create_statement)
        self._move_file_to_snowflake_staging(file_path, table_name)
        sep = sep.replace("\\", "")
        copy_into_table_command = self._dialect.generate_copy_into_table_command(
            table_name,
            column_names,
            column_types,
            sep,
            header,
            date_format,
            na_values,
            on_bad_lines,
        )
        client_logger.info("Configuring Ponder DataFrame in Snowflake...")
        self.run_query_and_return_results(copy_into_table_command)
        client_logger.info("Ponder DataFrame successfully configured in Snowflake")
        return table_name

    def to_csv(self, path, node, sep=",", header=True, date_format=None, na_rep=""):
        file_name = "".join(random.sample(string.ascii_lowercase, 10)) + ".gz"
        columns_list = node.get_column_names()
        copy_command = self._dialect.generate_copy_into_stage_command(
            columns_list,
            query=node.generate_sql(),
            file_name=file_name,
            sep=sep,
            header=header,
            date_format=date_format,
            na_rep=na_rep,
        )

        try:
            client_logger.info("Moving query data into snowflake staging area")
            self.run_query_and_return_results(copy_command)

            with tempfile.TemporaryDirectory() as temp_dir:
                get_command = self._dialect.generate_get_command(
                    f"~/{file_name}", temp_dir
                )

                self.run_query_and_return_results(get_command)

                file_name_with_path = os.path.join(temp_dir, file_name)

                if path.endswith("gz"):
                    shutil.copyfile(file_name_with_path, path)
                else:
                    with gzip.open(file_name_with_path, "rb") as f_in:
                        with open(path, "wb") as f_out:
                            shutil.copyfileobj(f_in, f_out)
        finally:
            delete_command = self._dialect.generate_remove_file_from_staging_command(
                f"~/{file_name}"
            )
            self.run_query_and_return_results(delete_command)

    def materialize_parquet_files_as_table(
        self,
        table_name,
        column_names,
        column_types,
        files,
        storage_options,
        fs,
        hive_partitioning,  # not used for now, will be needed later
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
        client_logger.info("Preparing table in Snowflake using Parquet file(s)...")
        self.run_query_and_return_results(create_statement)
        self._move_parquet_files_to_snowflake_staging(
            files, table_name, storage_options
        )

        copy_into_table_command = (
            self._dialect.generate_copy_into_table_parquet_command(
                table_name,
                column_names,
            )
        )
        client_logger.info("Configuring Ponder DataFrame in Snowflake...")
        self.run_query_and_return_results(copy_into_table_command)
        client_logger.info("Ponder DataFrame successfully configured in Snowflake")

        return table_name

    def table_exists(self, table_name):
        import snowflake.connector

        read_table_metadata_command = (
            self._dialect.generate_read_table_metadata_statement(table_name)
        )
        try:
            self.run_query_and_return_results(read_table_metadata_command)
        except snowflake.connector.errors.ProgrammingError as e:
            if e is not None:
                return False
            raise e
        return True

    def setup_udtf(
        self,
        function_name,
        func,
        input_column_names,
        input_column_types,
        output_column_names,
        output_column_types,
        order_column_names,
        row_label_column_names,
        row_label_dtypes,
        apply_type,
        na_action,
        func_args,
        func_kwargs,
    ):
        # Bit of a hack, but we need the order column name/dtype and row label
        # column name/dtype
        metadata_cols = [order_column_names] + row_label_column_names
        metadata_col_dtypes = [np.dtype(int)] + row_label_dtypes

        input_column_names += metadata_cols
        output_column_names += metadata_cols
        if isinstance(input_column_types, pandas.Series):
            input_column_types = input_column_types.tolist()
        input_column_types += metadata_col_dtypes
        if isinstance(output_column_types, pandas.Series):
            output_column_types = output_column_types.tolist()
        output_column_types += metadata_col_dtypes

        input_column_aliases = [f"F{i}" for i in range(len(input_column_names))]
        input_column_aliases_fragment = ", ".join(input_column_aliases)
        input_column_names_without_metadata = [
            input_column_name
            for input_column_name in input_column_names
            if input_column_name not in metadata_cols
        ]

        output_column_aliases = []
        output_col_aliases_map = {}
        for i, col_name in enumerate(output_column_names):
            alias = f"F{i}"
            output_column_aliases.append(alias)
            output_col_aliases_map[alias] = col_name

        # Get the udtf input params with dtypes
        # Should be something like: (F0 BIGINT, F1 REAL, ...)
        input_db_types = [
            self._dialect.get_database_type_for_pandas_type(input_df_type)
            for input_df_type in input_column_types
        ]
        udtf_params_fragment = ", ".join(
            f"{column_name} {column_type}"
            for (column_name, column_type) in zip(input_column_aliases, input_db_types)
        )

        output_db_types = [
            self._dialect.get_database_type_for_pandas_type(output_column_type)
            for output_column_type in output_column_types
        ]
        udtf_return_fragment = ", ".join(
            f"{column_name} {column_type}"
            for (column_name, column_type) in zip(
                output_column_aliases, output_db_types
            )
        )
        handler_class_name = f"{function_name}_class"

        # The name of the returned function is going to be "func"
        # N.B. we currently only support simple cases for func.
        function_body = self._dialect.generate_udf_function_body(
            apply_type, na_action, func_args, func_kwargs
        )

        sql_statement = f"""
        create temp function {function_name} ({udtf_params_fragment})
        returns TABLE ({udtf_return_fragment})
        language python
        runtime_version = '3.8'
        packages = ('pandas', 'numpy', 'cloudpickle', 'modin')
        handler = '{handler_class_name}'
        as
        $$
import pandas
import cloudpickle
from _snowflake import vectorized

class {handler_class_name}:
    def __init__(self):
        self._func = cloudpickle.loads({func})

    def process(self, {input_column_aliases_fragment}):
        params = pandas.Series(data=[{input_column_aliases_fragment}],
                index={input_column_names})
        ret_val = self.{function_name}(params)
        yield(ret_val)

    def {function_name}(self, params):
        {function_body}
        func_res = func(params[{input_column_names_without_metadata}])
        if not isinstance(func_res, pandas.Series):
            if isinstance(func_res, list):
                func_res = pandas.Series([func_res])
            else:
                func_res = pandas.Series(func_res)
        dfs = [func_res, params[{metadata_cols}]]
        return tuple(pandas.concat(dfs, axis=0))
        $$;"""

        self.run_query(sql_statement)

        return output_column_aliases, output_col_aliases_map

    def setup_stored_procedure_temp_table(
        self,
        input_query,
        pickled_function,
        function_name,
        output_table_name,
        output_column_names,
        output_column_types,
        row_labels_column_name,
        row_labels_dtype,
    ):
        create_statement = self._dialect.generate_create_table_for_sp_command(
            output_table_name,
            output_column_names,
            output_column_types,
            row_labels_column_name,
            row_labels_dtype,
        )

        self.run_query_and_return_results(create_statement)

        full_output_columns = [row_labels_column_name]
        full_output_columns.extend(output_column_names)
        full_output_columns_list = ", ".join(
            self.format_name(col_name) for col_name in full_output_columns
        )

        sql_statement = f"""
        create temp procedure {function_name} (input_query string, to_table string,
            row_labels_column_name string)
        returns int
        language python
        runtime_version = '3.8'
        packages = (
            'pandas', 'cloudpickle', 'snowflake-snowpark-python'
        )
        handler = 'run'
        as
        $$
import pandas
import cloudpickle
import math
from datetime import date

def run(snowpark_session, input_query, to_table, row_labels_column_name):


    def format_value(value):
        if value is None:
            return "NULL"
        if isinstance(value, float):
            if math.isnan(value):
                return "NULL"
            return str(value)
        elif isinstance(value, date):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(value, str):
            if "'" in value:
                value = value.replace("'", "''")
            return "'" + value + "'"
        else:
            return str(value)

    def materialize_result_into_table(snowpark_session, pandas_df, table_name):
        num_cols = len(pandas_df.columns)
        num_rows = len(pandas_df)

        insert_starter = f'INSERT INTO {{table_name}}({full_output_columns_list})'
        insert_starter += ' VALUES '

        num_recs = 0
        values_statement = ""
        for index, row in pandas_df.iterrows():
            one_record = "( " + ", ".join([format_value(value) for value in row])
            one_record += "), "
            values_statement = values_statement + one_record
            num_recs+=1
            if num_recs % 1000 == 0:
                insert_statement = insert_starter + values_statement[:-2] + ";"
                snowpark_session.sql(insert_statement).collect()
                values_statement = ""

        if (len(values_statement) > 0):
            insert_statement = insert_starter + values_statement[:-2]  + ";"
            snowpark_session.sql(insert_statement).collect()
        return num_recs

    func = cloudpickle.loads({pickled_function})
    df_snowflake = snowpark_session.sql(input_query)
    df_pandas = df_snowflake.to_pandas()
    if '_PONDER_ROW_NUMBER_' in df_pandas.columns:
        df_pandas.drop(columns=['_PONDER_ROW_NUMBER_'], inplace=True)
    if '_PONDER_ROW_LABELS_' in df_pandas.columns:
        df_pandas.drop(columns=['_PONDER_ROW_LABELS_'], inplace=True)
    apply_df = df_pandas.apply(func, axis=0)
    if isinstance(apply_df, pandas.Series):
        apply_df = apply_df.to_frame()
    apply_df.reset_index(inplace=True)
    return materialize_result_into_table(snowpark_session, apply_df, to_table)

        $$;"""

        self.run_query(sql_statement)

        sp_query = self._dialect.generate_stored_procedure_call(
            input_query,
            function_name,
            output_table_name,
            row_labels_column_name,
        )

        self.run_query_and_return_results(sp_query)
        return self._dialect.generate_read_sp_temp_table(
            output_table_name,
            output_column_names,
            row_labels_column_name,
        )

    def generate_apply_command(
        self,
        input_node_sql,
        function_name,
        func,
        input_column_names,
        input_column_types,
        output_column_names,
        output_alias_map,
        order_column_names,
        row_label_column_names,
        apply_type,
        na_action,
        func_args,
        func_kwargs,
    ):
        return self._dialect.generate_apply_command(
            input_node_sql,
            function_name,
            input_column_names,
            input_column_types,
            output_column_names,
            output_alias_map,
        )

    def materialize_pandas_dataframe_as_table(
        self, table_name, pandas_df, order_column_name
    ):
        from snowflake.connector.pandas_tools import write_pandas

        pandas_df_copy = self.update_pandas_df_with_supplementary_columns(pandas_df)
        write_pandas(
            self._connection,
            pandas_df_copy,
            table_name,
            table_type="temp",
            auto_create_table=True,
        )
        return table_name
