import logging
import os
import random
import string

from ponder.core.dataframequerytreehelper import DFCaseFold
from ponder.engines.postgres.connection import PonderPostgreSQLConnection

from .redshift_dialect import redshift_dialect

ponder_logger = logging.getLogger(__name__)


class PonderRedshiftConnection(PonderPostgreSQLConnection):
    def __init__(self, connection, dialect=redshift_dialect()):
        super().__init__(connection, dialect)
        self.initialize(self._connection, self._dialect)

    def initialize(self, _connection, _dialect):
        _connection.autocommit = True
        # RedShift identifiers are case folded by default
        # This has the following implications:
        #
        #  A column names returned in result sets are always lowercase
        #  B column names in queries are case folded to lower case
        #  C when a dataframe is uploaded to redshift, the resulting
        #    table name may be mixed-case, but the columns will always
        #    be lower case.
        #  D because of (C) and (A) this can result in a casing mismatch between
        #    modin.pandas and the database
        #
        # Because of this we pick a case folding setting, and stick to it.
        #
        # Make this configurable by the user. We set this to UPPER so that
        # we can use the existing general tests.

        # This allows us to reference table names which are of mixed case
        self.run_query_no_results("SET enable_case_sensitive_identifier TO true;")
        # The following does not appear to work through python
        # self.run_query_no_results("SET describe_field_name_in_uppercase TO true;")
        _dialect.format_name = _dialect.format_name_upper
        _dialect.generate_sanitized_name = _dialect.generate_sanitized_name_upper
        pass

    # Should be configurable
    def case_insensitive_identifiers(self):
        return True

    def case_fold_identifiers(self):
        return DFCaseFold.UPPER

    # temp table names should always be lowercase in redshift
    def create_temp_table_name(self):
        return f"""ponder_{"".join(
                random.choices(string.ascii_lowercase, k=10)
            )}"""

    def run_query(self, query, cursor):
        if os.environ.get("PONDER_SHOW_SQL", "").lower() == "true":
            ponder_logger.info(
                "\n".join(
                    (
                        "*********** run redshift query ************",
                        query,
                        "*********** DONE run redshift query ************",
                    )
                )
            )
        cursor.execute(query)

    def run_query_no_results(self, query):
        # Redshift has a fixed number of cursors available
        # so these should be closed after a fetch
        cursor = self._connection.cursor()
        try:
            self.run_query(query, cursor)
        except Exception as e:
            raise e
        finally:
            cursor.close()

    def run_query_and_return_results(self, query):
        # Redshift has a fixed number of cursors available
        # so these should be closed after a fetch
        cursor = self._connection.cursor()
        try:
            self.run_query(query, cursor)
            results = cursor.fetch_dataframe()
        except Exception as e:
            raise e
        finally:
            cursor.close()

        # case fold the results of the query
        fold = self.case_fold_identifiers()
        if fold == DFCaseFold.UPPER:
            results.columns = [col.upper() for col in results.columns]
        if fold == DFCaseFold.LOWER:
            results.columns = [col.upper() for col in results.columns]
        return results

    def get_num_rows(self, tree_node):
        sql = tree_node.get_root().generate_sql()
        result = self.run_query_and_return_results(
            self._dialect.generate_select_count_star_statement(sql)
        )
        fold = self.case_fold_identifiers()
        if fold == DFCaseFold.UPPER:
            return result["COUNT"][0]
        return result["count"][0]

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
