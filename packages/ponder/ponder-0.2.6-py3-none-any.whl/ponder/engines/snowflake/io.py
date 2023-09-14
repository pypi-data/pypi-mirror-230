from __future__ import annotations

import logging

import pandas._libs.lib as lib
from modin.core.io.io import BaseIO
from pandas._typing import StorageOptions
from pandas.api.extensions import no_default

from ponder.core.query_tree import QueryTree

from .connection import PonderSnowflakeConnection

client_logger = logging.getLogger("client logger")


class SnowflakeIO(BaseIO):
    ponder_snowflake_connection = None

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

        if cls.ponder_snowflake_connection is None:
            cls.ponder_snowflake_connection = PonderSnowflakeConnection(con)
        elif cls.ponder_snowflake_connection.get_user_connection() is not con:
            client_logger.info("resetting Snowflake connection to new connection")
            cls.ponder_snowflake_connection = PonderSnowflakeConnection(con)
        return QueryTree.make_tree_from_csv(
            cls.ponder_snowflake_connection,
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
        if cls.ponder_snowflake_connection is None:
            cls.ponder_snowflake_connection = PonderSnowflakeConnection(con)
        elif con is not cls.ponder_snowflake_connection.get_user_connection():
            client_logger.info("Resetting Snowflake connection to new connection")
            cls.ponder_snowflake_connection = PonderSnowflakeConnection(con)
        return QueryTree.make_tree_from_table(cls.ponder_snowflake_connection, sql)

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
        ponder_snowflake_con = con
        if cls.ponder_snowflake_connection is None:
            cls.ponder_snowflake_connection = PonderSnowflakeConnection(
                ponder_snowflake_con
            )
        elif (
            ponder_snowflake_con
            is not cls.ponder_snowflake_connection.get_user_connection()
        ):
            client_logger.info("Resetting Snowflake connection to new connection")
            cls.ponder_snowflake_connection = PonderSnowflakeConnection(
                ponder_snowflake_con
            )

        return QueryTree.make_tree_from_parquet(
            cls.ponder_snowflake_connection,
            file_path=path,
            engine=engine,
            columns=columns,
            storage_options=storage_options,
            use_nullable_dtypes=use_nullable_dtypes,
        )

    @classmethod
    def from_pandas(cls, pdf, snowflake_connection):
        if cls.ponder_snowflake_connection is None:
            cls.ponder_snowflake_connection = PonderSnowflakeConnection(
                snowflake_connection
            )
        elif (
            snowflake_connection
            is not cls.ponder_snowflake_connection.get_user_connection()
        ):
            client_logger.info("Resetting Snowflake connection to new connection")
            cls.ponder_snowflake_connection = PonderSnowflakeConnection(
                snowflake_connection
            )
        return QueryTree.make_tree_from_pdf(cls.ponder_snowflake_connection, pdf)
