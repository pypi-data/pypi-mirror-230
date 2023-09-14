from __future__ import annotations

import logging
import os
import random
import string

import pandas
import pandas._libs.lib as lib
from modin.core.io.io import BaseIO
from pandas._typing import StorageOptions
from pandas.api.extensions import no_default

from ponder.core.error_codes import PonderError, make_exception
from ponder.core.query_tree import QueryTree

from .connection import PonderPostgreSQLConnection

client_logger = logging.getLogger("client logger")


class PostgresIO(BaseIO):
    postgres_connection = None

    @classmethod
    def _maybe_set_connection(cls, postgres_connection):
        if cls.postgres_connection is None:
            cls.postgres_connection = PonderPostgreSQLConnection(postgres_connection)
            return

        if cls.postgres_connection.get_user_connection() is not postgres_connection:
            client_logger.info("Resetting PostgreSQL connection to new connection")
            cls.postgres_connection = PonderPostgreSQLConnection(postgres_connection)

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
        if cls.postgres_connection is None:
            cls.postgres_connection = PonderPostgreSQLConnection(con)
        elif con is not cls.postgres_connection.get_user_connection():
            client_logger.info("Resetting PostgreSQL connection to new connection")
            cls.postgres_connection = PonderPostgreSQLConnection(con)
        return QueryTree.make_tree_from_table(cls.postgres_connection, sql)

    @classmethod
    def read_csv(cls, filepath_or_buffer, con, **kwargs):
        cls._maybe_set_connection(con)
        pdf = pandas.read_csv(
            filepath_or_buffer,
            sep=kwargs.get("sep", ","),
            header=kwargs.get("header", 0),
            skipfooter=kwargs.get("skipfooter", 0),
            parse_dates=kwargs.get("parse_dates", None),
            date_format=kwargs.get("date_format", None),
            na_values=kwargs.get("na_values", ""),
            dtype=kwargs.get("dtype", None),
            names=kwargs.get("names", lib.no_default),
            on_bad_lines=kwargs.get("on_bad_lines", "skip"),
        )
        return QueryTree.make_tree_from_pdf(cls.postgres_connection, pdf)

    @classmethod
    def read_parquet(
        cls,
        path,
        con,
        engine: str = "auto",
        columns: list[str] | None = None,
        storage_options: StorageOptions = None,
        use_nullable_dtypes: bool = no_default,
        dtype_backend=no_default,
        **kwargs,
    ):
        raise make_exception(
            NotImplementedError,
            PonderError.PONDER_POSTGRES_PROTOTYPE_NOT_IMPLEMENTED,
            "Ponder Internal Error: PostgreSQL read_parquet implemented",
        )

    @classmethod
    def to_sql(cls, qc, **kwargs):
        con = kwargs["con"]
        if con is not qc._dataframe._query_tree._conn.get_user_connection():
            random_str = "".join(random.choices(string.ascii_lowercase, k=5))
            path = f"ponder_to_sql_{random_str}.csv"
            qc._dataframe.to_csv(
                path_or_buf=path, sep=",", header=True, date_format=None, na_rep=""
            )
            cls.default_connection = con
            target_qc = cls.read_csv(filepath_or_buffer=path, con=con)
            os.remove(path)
            return target_qc._dataframe.to_sql(**kwargs)
        else:
            return qc._dataframe.to_sql(**kwargs)

    @classmethod
    def from_pandas(cls, pdf, con):
        cls._maybe_set_connection(con)
        return QueryTree.make_tree_from_pdf(cls.postgres_connection, pdf)
