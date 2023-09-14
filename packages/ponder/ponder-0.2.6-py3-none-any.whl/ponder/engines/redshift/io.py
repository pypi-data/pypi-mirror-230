import logging

from pandas.api.extensions import no_default

from ponder.core.query_tree import QueryTree
from ponder.engines.postgres.io import PostgresIO

from .connection import PonderRedshiftConnection

client_logger = logging.getLogger("client logger")


class RedshiftIO(PostgresIO):
    ponder_redshift_connection = None

    @classmethod
    def _maybe_set_connection(cls, redshift_connection):
        if cls.ponder_redshift_connection is None:
            cls.ponder_redshift_connection = PonderRedshiftConnection(
                redshift_connection
            )
            return

        if (
            cls.ponder_redshift_connection.get_user_connection()
            is not redshift_connection
        ):
            client_logger.info("Resetting Redshift connection to new connection")
            cls.ponder_redshift_connection = PonderRedshiftConnection(
                redshift_connection
            )

    @classmethod
    def read_sql(
        cls,
        sql,
        con,
        index_col=None,
        coerce_float=True,
        params=None,
        parse_dates=None,
        columns=None,
        chunksize=None,
        dtype_backend=no_default,
        dtype=None,
    ):
        if cls.ponder_redshift_connection is None:
            cls.ponder_redshift_connection = PonderRedshiftConnection(con)
        elif con is not cls.ponder_redshift_connection.get_user_connection():
            client_logger.info("Resetting Redshift connection to new connection")
            cls.ponder_redshift_connection = PonderRedshiftConnection(con)
        return QueryTree.make_tree_from_table(cls.ponder_redshift_connection, sql)

    @classmethod
    def from_pandas(cls, pdf, con):
        cls._maybe_set_connection(con)
        return QueryTree.make_tree_from_pdf(cls.ponder_redshift_connection, pdf)
