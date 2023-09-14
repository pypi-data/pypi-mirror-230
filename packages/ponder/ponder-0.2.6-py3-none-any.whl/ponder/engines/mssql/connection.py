import copy
import logging
import os
import random
import string

import pandas
import pymssql

from ponder.core.common import (
    __PONDER_ORDER_COLUMN_NAME__,
    __PONDER_ROW_LABELS_COLUMN_NAME__,
    get_execution_configuration,
)
from ponder.core.sql_connection import SQLConnection
from ponder.engines.mssql.mssql_dialect import MSSQLDialect

ponder_logger = logging.getLogger(__name__)
client_logger = logging.getLogger("client logger")


class MSSQLConnection(SQLConnection):
    def __init__(self, connection, dialect=None):
        my_dialect = MSSQLDialect() if dialect is None else dialect
        super().__init__(connection, my_dialect)

    # Initialization which can be overrided by subclasses
    def initialize(self, connection, dialect):
        connection.autocommit(True)
        pass

    def get_max_str_splits(self, query_tree, column, pat, n):
        pass

    def get_project_columns(self, tree_node, fn):
        pass

    def materialize_csv_file_as_table(
        self,
        table_name,
        column_names,
        column_types,
        file_path,
        sep,
        header,
        na_values,
        on_bad_lines,
        order_column_name,
    ):
        pass

    def create_temp_table_name(self):
        return f"#ponder_{''.join(random.choices(string.ascii_lowercase, k=10))}"

    def get_num_rows(self, tree_node):
        sql = tree_node.get_root().generate_sql()
        result = self.run_query_and_return_results(
            self._dialect.generate_select_count_star_statement(sql)
        )
        return int(result["COUNT_PONDER"][0])

    def materialize_pandas_dataframe_as_table(
        self, table_name, pandas_dataframe, order_column_name
    ):
        try:
            table_name = self.default_materialize_pandas_dataframe_as_table(
                table_name, pandas_dataframe, order_column_name
            )
        except Exception as e:
            raise e
        finally:
            self._connection.commit()
        return table_name

    def run_query(self, query, cursor):
        if os.environ.get("PONDER_SHOW_SQL", "").lower() == "true":
            ponder_logger.info(
                "\n".join(
                    (
                        "*********** Run MSSQL query ************",
                        query,
                        "*********** DONE run MSSQL query ************",
                    )
                )
            )

        cursor.execute(query)

    def DBAPI_to_pandas(self, results, description):
        # Map the exported DBAPI types to pandas types
        # See also mssql_type_to_pandas_type_map - we
        # might be able to consolidate some of this code
        # See: src/pymssql/_pymssql.pyx

        dbapi_to_pandas_map = {
            pymssql._mssql.STRING: "string",
            pymssql._mssql.BINARY: "object",
            pymssql._mssql.NUMBER: "float64",
            pymssql._mssql.DATETIME: "datetime64[ns]",
            pymssql._mssql.DECIMAL: "float64",
            pymssql._pymssql.Date: "datetime64[ns]",
            pymssql._pymssql.Time: "datetime64[ns]",
            pymssql._pymssql.Timestamp: "datetime64[ns]",
            pymssql._pymssql.DateFromTicks: "datetime64[ns]",
            pymssql._pymssql.TimeFromTicks: "datetime64[ns]",
            pymssql._pymssql.Binary: "object",
        }

        df = pandas.DataFrame(results)
        if description is not None:
            column_names = list(map(lambda x: x[0], description))
            if len(df.columns) == 0:
                # we have an empty data frame, with column names
                # and result types which will be set as dtypes
                # shortly
                df = pandas.DataFrame(columns=column_names)
            else:
                df.columns = column_names
            dtypes = list(map(lambda x: dbapi_to_pandas_map[x[1]], description))
            for i in range(len(df.columns.values)):
                df[df.columns[i]] = df[df.columns[i]].astype(dtypes[i])
        return df

    def run_query_and_return_results(self, query):
        cursor = self._connection.cursor()
        results = {}
        description = ()
        try:
            self.run_query(query, cursor)
            description = cursor.description
            results = cursor.fetchall()
        except pymssql._pymssql.ProgrammingError as e:
            raise e
        except pymssql._pymssql.OperationalError as e:  # noqa
            # swallow these errors for now, they occur when there
            # is no resultset to fetch
            if isinstance(e.args[0], str) and "statement has no resultset" in e.args[0]:
                pass
            else:
                raise e
        except Exception as e:
            raise e
        df = self.DBAPI_to_pandas(results, description)
        return df

    def get_temp_table_metadata(self, table_name):
        read_metadata_command = self._dialect.generate_read_table_metadata_statement(
            table_name
        )
        # Unlike other connections, where we infer the types from the pandas
        # result, here we actually query the metadata of the server and map
        # the types directly.
        df = self.run_query_and_return_dataframe(read_metadata_command, use_cache=False)

        df = df.loc[df["name"] != __PONDER_ORDER_COLUMN_NAME__]
        df = df.loc[df["name"] != __PONDER_ROW_LABELS_COLUMN_NAME__]
        df = df.dropna()
        # map df['system_type_name'] to pandas types
        mssql_types = df["system_type_name"].values

        pandas_types = list(
            map(
                lambda x: pandas.api.types.pandas_dtype(
                    self._dialect.mssql_type_to_pandas_type_map[x]
                ),
                mssql_types,
            )
        )
        return (df["name"].values.tolist(), pandas_types)

    def table_exists(self, table_name):
        pass

    def generate_limit_clause(self):
        return f"TOP {get_execution_configuration().row_transfer_limit + 1}"

    def to_pandas(self, tree_node, enforce_row_limit=True):
        tree_node_query = tree_node.generate_sql()
        column_names = copy.deepcopy(tree_node.get_column_names())
        sql = f"""
            SELECT {self.generate_limit_clause() if enforce_row_limit else ""}
                {", ".join(
                    self.format_names_list((*tree_node.get_row_labels_column_names(),
                                            *column_names)))}
            FROM {self._dialect.generate_subselect_expression(tree_node_query)}
            ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
            """
        df = self.run_query_and_return_dataframe(sql, use_cache=True)
        return df

    # don't bother with table updates for prototype databases
    def get_last_table_update_time(self, table_name):
        return 0
