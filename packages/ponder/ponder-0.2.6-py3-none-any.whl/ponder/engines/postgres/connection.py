import copy
import logging
import os

import pandas
import psycopg

from ponder.core.common import __PONDER_ORDER_COLUMN_NAME__
from ponder.core.error_codes import PonderError, make_exception
from ponder.core.sql_connection import SQLConnection

from . import postgres_dialect

ponder_logger = logging.getLogger(__name__)
client_logger = logging.getLogger("client logger")


class PonderPostgreSQLConnection(SQLConnection):
    def __init__(self, connection, dialect=None):
        my_dialect = postgres_dialect.postgres_dialect() if dialect is None else dialect
        super().__init__(connection, my_dialect)

    # Initialization which can be overrided by subclasses
    def initialize(self, connection, dialect):
        # Use the float loader to adapt python Decimal types to float
        connection.adapters.register_loader(
            "numeric", psycopg.types.numeric.FloatLoader
        )

    def execute(self, tree_node):
        tree_node_sql = tree_node.generate_sql()
        self.run_query_and_return_results(tree_node_sql)

    def run_query_and_return_results(self, query):
        try:
            # In Psycopg, each new query results in a
            # new transaction - so both this function
            # and _execute need to be aware of the
            # transaction state in case of errors
            cur = self._execute(query)
            results = {}
            colnames = []
            if cur.rownumber is not None:
                results = cur.fetchall()
                colnames = [desc[0] for desc in cur.description]
        except Exception as e:
            raise e

        df = pandas.DataFrame(results)
        df.columns = colnames
        return df

    def _execute(self, query):
        if os.environ.get("PONDER_SHOW_SQL", "").lower() == "true":
            ponder_logger.info(
                "\n".join(
                    (
                        "*********** run postgres query ************",
                        query,
                        "*********** DONE run postgres query ************",
                    )
                )
            )
        cur = self._connection.cursor()
        runquery = str.strip(query)
        runquery = runquery if runquery.endswith(";") else runquery + ";"
        try:
            cur.execute(runquery)
        except Exception as e:
            cur.close()
            self._connection.rollback()
            raise e
        self._connection.commit()
        return cur

    def get_num_rows(self, tree_node):
        sql = tree_node.get_root().generate_sql()
        result = self.run_query_and_return_results(
            self._dialect.generate_select_count_star_statement(sql)
        )
        return result["count"][0]

    def get_max_str_splits(self, query_tree, column, pat, n):
        params_list = (column, pat, n, False)
        exp = self._dialect.generate_str_split(params_list)
        sql = f"""
            SELECT
                MAX(ARRAY_SIZE({exp}))-1
            FROM {self.generate_subselect_expression(
                    query_tree.get_root().generate_sql()
                )} """
        result = self.run_query_and_return_results(sql)
        if n <= 0:
            return result[0][0]
        else:
            return min(n, result[0][0])

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
        raise make_exception(
            NotImplementedError,
            PonderError.PONDER_POSTGRES_PROTOTYPE_NOT_IMPLEMENTED,
            "Ponder Internal Error: PostgreSQL read_csv not implemented",
        )

    def materialize_pandas_dataframe_as_table(
        self, table_name, pandas_df, order_column_name
    ):
        create_sql = self._dialect.generate_create_table_command(
            table_name,
            pandas_df.columns,
            pandas_df.dtypes,
            order_column_name,
            None,
            True,
            False,
        )
        self._execute(create_sql)
        tuples = [tuple(x) for x in pandas_df.to_numpy(na_value=None)]
        val_box = "(" + ",".join(("%s " * len(pandas_df.columns)).split()) + ")"
        query = f"INSERT INTO {self._dialect.format_table_name(table_name)} VALUES "

        def tuple_block(iterable, block_size=1000):
            length = len(iterable)
            for ndx in range(0, length, block_size):
                yield iterable[ndx : min(ndx + block_size, length)]

        try:
            for block in tuple_block(tuples, block_size=10000):
                cursor = psycopg.ClientCursor(self._connection)
                values = ",".join(cursor.mogrify(val_box, x) for x in block)
                cursor.execute(query + values)
                self._connection.commit()
                cursor.close()
        except (Exception, psycopg.Error) as error:
            self._connection.rollback()
            cursor.close()
            raise error
        cursor.close()
        return table_name

    def table_exists(self, table_name):
        read_table_metadata_command = (
            self._dialect.generate_read_table_metadata_statement(table_name)
        )
        try:
            self.run_query_and_return_results(read_table_metadata_command)
        except Exception:
            return False
        return True

    def to_pandas(self, tree_node, enforce_row_limit=True):
        tree_node_query = tree_node.generate_sql()
        column_names = copy.deepcopy(tree_node.get_column_names())

        sql = f"""
            SELECT
                {", ".join(
                    self.format_names_list((*tree_node.get_row_labels_column_names(),
                                            *column_names)))}
            FROM {self._dialect.generate_subselect_expression(tree_node_query)}
            ORDER BY {self.format_name(__PONDER_ORDER_COLUMN_NAME__)}
            {super().generate_limit_clause() if enforce_row_limit else ""}"""
        df = self.run_query_and_return_dataframe(sql, use_cache=True)
        return df

    def get_last_table_update_time(self, table_name):
        return 0
