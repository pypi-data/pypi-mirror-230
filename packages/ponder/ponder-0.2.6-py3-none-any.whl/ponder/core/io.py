import logging
import os
import random
import string

import modin
import pandas
from modin.core.io.io import BaseIO

from ponder.core import registry
from ponder.core.dataframe import DBMSDataframe
from ponder.core.error_codes import PonderError, make_exception
from ponder.core.query_compiler import DBMSQueryCompiler
from ponder.core.query_tree import QueryTree
from ponder.core.registry import (
    EngineEnum,
    get_connection_attributes,
    get_connection_type,
)

client_logger = logging.getLogger("client logger")
modin_logger = modin.logging.get_logger()


def _log_dataframe_shape(compiler):
    # NOTE: the length check is triggering a COUNT(*) query, which may be costly.
    modin_logger.info(
        f"_ponder_dataframe_shape: {len(compiler.index)}, {len(compiler.columns)}"
    )


class DBMSIO(BaseIO):
    _default_connection = None
    _connection_type = None
    query_compiler_cls = DBMSQueryCompiler

    if registry.allowed_engines is None:
        # This check runs when DBMSIO is imported, and prevents monkeypatching
        # the object into modin to bypass licensing
        raise make_exception(
            RuntimeError,
            PonderError.REGISTRY_NO_SCOPE_VALIDATION,
            "API key was not validated.",
        )

    def _default_connection_setter(self, con):
        self._default_connection = con
        self._connection_type = get_connection_type(con)

    def _default_connection_getter(self):
        return self._default_connection

    default_connection = property(
        _default_connection_getter, _default_connection_setter
    )

    @staticmethod
    def _sanitize_path(path):
        if not isinstance(path, str):
            if isinstance(path, os.PathLike):
                return path.__fspath__()
            else:
                raise make_exception(
                    NotImplementedError,
                    PonderError.IO_PATH_NOT_STR_OR_PATHLIKE,
                    "Ponder I/O currently only supports str and os.PathLike paths",
                )
        return path

    @classmethod
    def create_query_compiler_from_query_tree(cls, query_tree):
        dataframe = DBMSDataframe(
            query_tree,
            new_column_labels=query_tree.get_dataframe_column_names(),
            new_dtypes=query_tree.get_column_types(),
        )
        client_logger.info("Ponder DataFrame successfully configured in Snowflake")
        qc = DBMSQueryCompiler(dataframe)
        _log_dataframe_shape(qc)
        return qc

    @classmethod
    def read_sql(cls, sql, con, **kwargs) -> DBMSQueryCompiler:
        connection_type = get_connection_type(con)
        connection_registry = get_connection_attributes(connection_type)
        read_sql_fn = connection_registry["read_sql_fn"]
        if read_sql_fn is not None:
            modin_logger.info(f"START::Connected to {connection_type}")
            query_tree = read_sql_fn(sql, con, **kwargs)
        else:
            try:
                con.cursor
            except AttributeError:
                # matching pandas exception for objects without cursors.
                raise
            raise make_exception(
                NotImplementedError,
                PonderError.READ_SQL_UNSUPPORTED_CONNECTION_TYPE,
                "read_sql() does not support reading from connection of type "
                + f"{type(con).__name__}",
            )
        return cls.create_query_compiler_from_query_tree(query_tree)

    @classmethod
    def read_csv(cls, filepath_or_buffer, **kwargs):
        """Read CSV data from given filepath or buffer.

        Parameters
        ----------
        filepath_or_buffer : str, path object or file-like object
            `filepath_or_buffer` parameter of read functions.
        **kwargs : dict
            Parameters of ``read_csv`` function.

        Returns
        -------
        ClientQueryCompiler
            Query compiler with CSV data read in.
        """
        if cls.default_connection is None:
            raise make_exception(
                ConnectionError,
                PonderError.READ_CSV_MISSING_CONNECTION,
                "Missing server connection. Please call ponder.configure() with the "
                + "parameter `default_connection`.",
            )
        cls._connection_type = get_connection_type(cls.default_connection)
        filepath_or_buffer = DBMSIO._sanitize_path(filepath_or_buffer)
        connection_registry = get_connection_attributes(cls._connection_type)
        read_csv_fn = connection_registry["read_csv_fn"]
        if read_csv_fn is not None:
            modin_logger.info(f"START::Connected to {connection_registry['name']}")
            query_tree = read_csv_fn(
                filepath_or_buffer, cls.default_connection, **kwargs
            )
        else:
            raise make_exception(
                RuntimeError,
                PonderError.READ_CSV_UNKNOWN_CONNECTION_TYPE,
                "Internal error: unknown data connection type"
                + f"{type(cls.default_connection).__name__}",
            )
        return cls.create_query_compiler_from_query_tree(query_tree)

    @classmethod
    def read_parquet(cls, path, **kwargs):
        if cls.default_connection is None:
            raise make_exception(
                ConnectionError,
                PonderError.READ_PARQUET_MISSING_CONNECTION,
                "Missing server connection. Please call ponder.configure() with the "
                + "parameter `default_connection`.",
            )
        cls._connection_type = get_connection_type(cls.default_connection)
        path = DBMSIO._sanitize_path(path)
        connection_registry = get_connection_attributes(cls._connection_type)
        read_parquet_fn = connection_registry["read_parquet_fn"]
        if read_parquet_fn is not None:
            modin_logger.info(f"START::Connected to {connection_registry['name']}")
            query_tree = read_parquet_fn(path, cls.default_connection, **kwargs)
        else:
            raise make_exception(
                RuntimeError,
                PonderError.READ_PARQUET_UNKNOWN_CONNECTION_TYPE,
                "Internal error: unknown data connection type",
            )
        return cls.create_query_compiler_from_query_tree(query_tree)

    @classmethod
    def to_sql(cls, qc, **kwargs):
        con = kwargs["con"]
        if con is None:
            con = cls.default_connection
        if con is not qc._dataframe._query_tree._conn.get_user_connection():
            random_str = "".join(random.choices(string.ascii_lowercase, k=5))
            path = f"ponder_to_sql_{random_str}.csv"
            qc._dataframe.to_csv(
                path_or_buf=path, sep=",", header=True, date_format=None, na_rep=""
            )
            cls.default_connection = con
            target_qc = cls.read_csv(filepath_or_buffer=path)
            os.remove(path)
            return target_qc._dataframe.to_sql(**kwargs)
        else:
            return qc._dataframe.to_sql(**kwargs)

    @classmethod
    def to_csv(cls, qc, **kwargs):
        return qc.to_csv(**kwargs)

    @classmethod
    def from_pandas(cls, df: pandas.DataFrame) -> DBMSQueryCompiler:
        """Create a Modin `query_compiler` from a `pandas.DataFrame`.

        Parameters
        ----------
        df : pandas.DataFrame
            The pandas DataFrame to convert from.

        Returns
        -------
        DBMSQueryCompiler
            QueryCompiler containing data from the `pandas.DataFrame`.
        """
        if cls.default_connection is None:
            raise make_exception(
                ConnectionError,
                PonderError.FROM_PANDAS_MISSING_CONNECTION,
                "Missing server connection. Please call ponder.configure() with the "
                + "parameter `default_connection` set to your desired db connection.",
            )
        cls._connection_type = get_connection_type(cls.default_connection)
        conn_attr = registry.get_connection_attributes(cls._connection_type)

        if cls._connection_type is EngineEnum.POLARS:
            modin_logger.info("START::Connected to Polars")
            from ponder.engines.polars.io import PolarsIO

            frame = PolarsIO.from_pandas(df)
            qc = DBMSQueryCompiler(frame)
            _log_dataframe_shape(qc)
            return qc
        elif conn_attr["dbtype"] is not None:
            modin_logger.info(f"START::Connected to {conn_attr['name']}")
            query_tree = conn_attr["from_pandas_fn"](df, cls.default_connection)
        else:
            raise make_exception(
                RuntimeError,
                PonderError.FROM_PANDAS_UNKNOWN_CONNECTION_TYPE,
                f"Internal error: unknown data connection type {cls._connection_type}",
            )
        return cls.create_query_compiler_from_query_tree(query_tree)

    @classmethod
    def _from_raw_sql(
        cls, connection, sql_query, column_names, column_types, order_column_name
    ):
        query_tree = QueryTree.make_tree_from_raw_sql(
            connection, sql_query, column_names, column_types, order_column_name
        )
        return cls.create_query_compiler_from_query_tree(query_tree)
