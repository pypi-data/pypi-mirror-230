import logging
from enum import Enum

from packaging import version

from ponder.common import __PONDER_API_URL__, NoCredentialsError
from ponder.core.error_codes import PonderError, make_exception

logger = logging.getLogger(__name__)

##########################################
#
#  Registry of supported connection types
#

try:
    import duckdb

    check_duckdb = True
    if version.parse(duckdb.__version__) < version.parse("0.8.0"):
        raise make_exception(
            AssertionError,
            PonderError.PONDER_DUCKDB_VERSION_ERROR,
            "Ponder requires duckdb>=0.8, "
            + "please `pip install ponder[duckdb]` to upgrade.",
        )
except ImportError:
    check_duckdb = False

try:
    import snowflake.connector

    check_snowflake = True
    if version.parse(snowflake.connector.__version__) < version.parse("3.0.2"):
        raise make_exception(
            AssertionError,
            PonderError.PONDER_SNOWFLAKE_VERSION_ERROR,
            "Ponder requires snowflake-connector-python[pandas]>3.0.2, "
            + "please `pip install ponder[snowflake]` to upgrade.",
        )
except ImportError:
    check_snowflake = False

try:
    from google.cloud import bigquery
    from google.cloud.bigquery import dbapi

    check_bigquery = True
    if version.parse(bigquery.__version__) < version.parse("3.8.0"):
        raise make_exception(
            AssertionError,
            PonderError.PONDER_BIGQUERY_VERSION_ERROR,
            "Ponder requires google-cloud-bigquery>=3.8.0, "
            + "please `pip install ponder[bigquery]` to upgrade.",
        )
except ImportError:
    check_bigquery = False


try:
    import psycopg

    check_postgres = True
except ImportError:
    check_postgres = False

try:
    import redshift_connector

    check_redshift = True
except ImportError:
    check_redshift = False
try:
    import polars  # noqa: F401

    check_polars = True
except ImportError:
    check_polars = False

try:
    import pymssql

    check_mssql = True
except ImportError:
    check_mssql = False


class EngineEnum(Enum):
    UNSUPPORTED = "unsupported"
    SNOWFLAKE = "snowflake"
    BIGQUERY = "bigquery"
    DUCKDB = "duckdb"
    POSTGRESQL = "postgres"
    REDSHIFT = "redshift"
    POLARS = "polars"
    MSSQL = "mssql"


def get_connection_type(con):
    if check_snowflake and isinstance(
        con, snowflake.connector.connection.SnowflakeConnection
    ):
        return EngineEnum.SNOWFLAKE
    elif check_bigquery and isinstance(con, dbapi.Connection):
        return EngineEnum.BIGQUERY
    elif check_duckdb and isinstance(con, duckdb.DuckDBPyConnection):
        return EngineEnum.DUCKDB
    elif check_postgres and isinstance(con, psycopg.Connection):
        return EngineEnum.POSTGRESQL
    elif check_redshift and isinstance(con, redshift_connector.Connection):
        return EngineEnum.REDSHIFT
    elif check_polars and isinstance(con, str) and con == "polars":
        return EngineEnum.POLARS
    elif check_mssql and isinstance(con, pymssql.Connection):
        return EngineEnum.MSSQL
    else:
        return EngineEnum.UNSUPPORTED


def get_connection_attributes(connection_type):
    # TODO: This function can be merged with _get_connection_type into
    # a proper connection registry class, where dialects can be assigned
    # and so-forth
    name = "Unknown"
    dbtype = None
    read_sql_fn = None
    read_csv_fn = None
    read_parquet_fn = None
    from_pandas_fn = None
    db_license_key = None
    scope_error_code = PonderError.PONDER_UNKNOWN_USAGE_NOT_ENABLED

    if connection_type is EngineEnum.SNOWFLAKE:
        from ponder.engines.snowflake.io import SnowflakeIO

        name = "Snowflake"
        dbtype = "snowflake"
        db_license_key = dbtype
        read_sql_fn = SnowflakeIO.read_sql
        read_csv_fn = SnowflakeIO.read_csv
        read_parquet_fn = SnowflakeIO.read_parquet
        from_pandas_fn = SnowflakeIO.from_pandas
        scope_error_code = PonderError.PONDER_SNOWFLAKE_USAGE_NOT_ENABLED

    elif connection_type is EngineEnum.BIGQUERY:
        from ponder.engines.bigquery.io import BigQueryIO

        name = "Google BigQuery"
        dbtype = "bigquery"
        # The license key for GBQ is different from the
        # connection class name
        db_license_key = "gbq"
        read_sql_fn = BigQueryIO.read_sql
        read_csv_fn = BigQueryIO.read_csv
        read_parquet_fn = None
        from_pandas_fn = BigQueryIO.from_pandas
        scope_error_code = PonderError.PONDER_BIGQUERY_USAGE_NOT_ENABLED

    elif connection_type is EngineEnum.DUCKDB:
        from ponder.engines.duckdb.io import DuckDBIO

        name = "DuckDB"
        dbtype = "duckdb"
        db_license_key = dbtype
        read_sql_fn = DuckDBIO.read_sql
        read_csv_fn = DuckDBIO.read_csv
        read_parquet_fn = DuckDBIO.read_parquet
        from_pandas_fn = DuckDBIO.from_pandas
        scope_error_code = PonderError.PONDER_DUCKDB_USAGE_NOT_ENABLED

    elif connection_type is EngineEnum.POSTGRESQL:
        from ponder.engines.postgres.io import PostgresIO

        name = "PostgreSQL"
        dbtype = "postgres"
        db_license_key = dbtype
        read_sql_fn = PostgresIO.read_sql
        read_csv_fn = PostgresIO.read_csv
        read_parquet_fn = PostgresIO.read_parquet
        from_pandas_fn = PostgresIO.from_pandas
        scope_error_code = PonderError.PONDER_POSTGRES_USAGE_NOT_ENABLED

    elif connection_type is EngineEnum.POLARS:
        from ponder.engines.polars.io import PolarsIO

        name = "Polars"
        dbtype = "polars"
        db_license_key = dbtype
        read_sql_fn = PolarsIO.read_sql
        read_csv_fn = PolarsIO.read_csv
        read_parquet_fn = PolarsIO.read_parquet
        from_pandas_fn = PolarsIO.from_pandas
        scope_error_code = PonderError.PONDER_POLARS_USAGE_NOT_ENABLED

    elif connection_type is EngineEnum.REDSHIFT:
        from ponder.engines.redshift.io import RedshiftIO

        name = "Amazon Redshift"
        dbtype = "redshift"
        db_license_key = dbtype
        read_sql_fn = RedshiftIO.read_sql
        read_csv_fn = RedshiftIO.read_csv
        read_parquet_fn = RedshiftIO.read_parquet
        from_pandas_fn = RedshiftIO.from_pandas
        scope_error_code = PonderError.PONDER_REDSHIFT_USAGE_NOT_ENABLED

    elif connection_type is EngineEnum.MSSQL:
        from ponder.engines.mssql.io import MSSQLIO

        name = "Microsoft SQL Server"
        dbtype = "mssql"
        db_license_key = dbtype
        read_sql_fn = MSSQLIO.read_sql
        read_csv_fn = MSSQLIO.read_csv
        read_parquet_fn = MSSQLIO.read_parquet
        from_pandas_fn = MSSQLIO.from_pandas
        scope_error_code = PonderError.PONDER_MSSQL_USAGE_NOT_ENABLED

    return {
        "name": name,
        "dbtype": dbtype,
        "db_license_key": db_license_key,
        "read_sql_fn": read_sql_fn,
        "read_csv_fn": read_csv_fn,
        "read_parquet_fn": read_parquet_fn,
        "from_pandas_fn": from_pandas_fn,
        "scope_error_code": scope_error_code,
    }


allowed_engines = None


def verify_key_and_scopes():
    """
    Retrieves and validates the user's API key, and updates the global `allowed_engines`
    variable with which backends the user has permission to use.
    """
    global allowed_engines

    def set_up():
        """Sets up configuration for ponder."""
        import os
        from configparser import ConfigParser

        def get_platform_setup():
            import pathlib

            if pathlib.Path("~/.secrets/access_token").expanduser().exists():
                offering = "platform"
                location = "~/work/.ponder"
            else:
                offering = "custom"
                location = "~/.ponder"
            return offering, location

        _, location = get_platform_setup()
        config = ConfigParser()
        try:
            config_location = os.getenv("CONFIG_FILE", os.path.expanduser(location))
            # config doesn't error when file not found on read.
            with open(config_location) as f:
                config.read_file(f)
            return config
        except FileNotFoundError:
            api_key = os.getenv("PONDER_API_KEY", None)
            if api_key:
                return {"PONDER": {"API KEY": api_key}}
            logger.error(
                "Ponder configuration file not found. Please login, reset or"
                " provide correct configuration file"
            )
            raise

    try:
        _api_key = set_up()["PONDER"]
        try:
            _api_key = _api_key["API KEY"]
            _api_key = _api_key.strip()
        except KeyError:
            raise make_exception(
                ValueError,
                PonderError.REGISTRY_FOUND_API_KEY_WITH_INVALID_FORMAT,
                "Run `ponder reset && ponder login` and enter your API key.\n"
                "Your API key can be retrieved from https://app.ponder.io",
            )
    except (KeyError, FileNotFoundError):
        raise make_exception(
            NoCredentialsError,
            PonderError.REGISTRY_FOUND_NO_API_KEY,
            "Run `ponder login` and enter your API key.\n"
            "Your API key can be retrieved from https://app.ponder.io",
        )
    if len(_api_key) != 40:
        raise make_exception(
            ValueError,
            PonderError.REGISTRY_FOUND_API_KEY_WITH_WRONG_LENGTH,
            "Run `ponder reset && ponder login` and enter your API key.\n"
            "Your API key can be retrieved from https://app.ponder.io",
        )

    def _verify_api_key(key) -> dict:
        import requests

        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {key}"}
        url = f"{__PONDER_API_URL__}/api-key/verify"
        return requests.get(url, headers=headers).json()

    # Check that the reverse of the API Key is not authorized.
    # This is done because we want to make sure that no funny business
    # with monkey patching the requests library is possible.

    verification_response = _verify_api_key(_api_key[::-1])
    if "email" in verification_response:
        raise make_exception(
            ValueError,
            PonderError.REGISTRY_FOUND_BACKWARDS_API_KEY_WAS_VALID,
            "Network connectivity issue. Authentication not possible.",
        )

    # This is the actual verification.
    verification_response = _verify_api_key(_api_key)
    if "email" not in verification_response or (
        "detail" in verification_response
        and verification_response["detail"] == "API key not authorized"
    ):
        raise make_exception(
            ValueError,
            PonderError.REGISTRY_FOUND_API_KEY_WAS_INVALID,
            "Invalid API Key. API Key can be retrieved from https://app.ponder.io",
        )

    scopes_dict = verification_response.get("scopes", {})
    allowed_engines = {
        engine for engine, permission in scopes_dict.items() if permission == "allow"
    }


def validate_engine_license(connection):
    """
    Verifies that the user has permission to use the backend corresponding to the
    connection object, and raises the appropriate exception if not.
    """
    if connection is None:
        # This occurs in some test cases, where dummy connections are created to
        # test specific components. This should never be reached in user code.
        return
    if allowed_engines is None:
        raise make_exception(
            RuntimeError,
            PonderError.REGISTRY_NO_SCOPE_VALIDATION,
            "API key was not validated.",
        )
    attrs = get_connection_attributes(get_connection_type(connection))
    if attrs["name"] == "Unknown":
        raise make_exception(
            RuntimeError,
            attrs["scope_error_code"],
            f"Unsupported connection object {connection}. Ponder supports the following"
            + " connections: "
            + f"{', '.join(e.value for e in EngineEnum if e.value != 'unsupported')}",
        )
    db_license_key = attrs["db_license_key"]
    if db_license_key not in allowed_engines:
        raise make_exception(
            RuntimeError,
            attrs["scope_error_code"],
            f"Your Ponder subscription does not include {attrs['name']} support. Please"
            + " upgrade your subscription at https://app.ponder.io/subscription",
        )
