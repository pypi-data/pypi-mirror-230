import logging
import os
import random
import string

import pandas._libs.lib as lib
from modin.core.io.io import BaseIO
from pandas.api.extensions import no_default

from ponder.core.query_tree import QueryTree

from .connection import PonderBigQueryConnection

client_logger = logging.getLogger("client logger")


class BigQueryIO(BaseIO):
    dbms_connection = None

    @classmethod
    def read_csv(cls, filepath_or_buffer, con, **kwargs):
        sep = kwargs.get("sep", ",")
        if sep == lib.no_default:
            sep = ","
        header = kwargs.get("header", 0)
        skipfooter = kwargs.get("skipfooter", 0)
        parse_dates = kwargs.get("parse_dates", None)
        date_format = kwargs.get("date_format", None)
        na_values = kwargs.get("na_values", "")
        names = kwargs.get("names", lib.no_default)
        dtype = kwargs.get("dtype", None)
        on_bad_lines = kwargs.get("on_bad_lines", "skip")

        if cls.dbms_connection is None:
            cls.dbms_connection = PonderBigQueryConnection(con)
        elif cls.dbms_connection.get_user_connection() is not con:
            client_logger.info("resetting bigquery connection to new connection")
            cls.dbms_connection = PonderBigQueryConnection(con)
        return QueryTree.make_tree_from_csv(
            cls.dbms_connection,
            filepath_or_buffer,
            sep=sep,
            header=header,
            skipfooter=skipfooter,
            parse_dates=parse_dates,
            date_format=date_format,
            na_values=na_values,
            names=names,
            dtype=dtype,
            on_bad_lines=on_bad_lines,
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
        if cls.dbms_connection is None:
            cls.dbms_connection = PonderBigQueryConnection(con)
        elif con is not cls.dbms_connection.get_user_connection():
            client_logger.info("resetting bigquery connection to new connection")
            cls.dbms_connection = PonderBigQueryConnection(con)
        return QueryTree.make_tree_from_table(cls.dbms_connection, sql)

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
    def from_pandas(cls, pdf, bigquery_connection):
        if cls.dbms_connection is None:
            cls.dbms_connection = PonderBigQueryConnection(bigquery_connection)
        elif bigquery_connection is not cls.dbms_connection.get_user_connection():
            client_logger.info("resetting bigquery connection to new connection")
            cls.dbms_connection = PonderBigQueryConnection(bigquery_connection)
        return QueryTree.make_tree_from_pdf(cls.dbms_connection, pdf)
