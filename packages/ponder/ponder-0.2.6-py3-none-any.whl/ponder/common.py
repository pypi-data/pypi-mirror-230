import logging
import os

import cloudpickle  # noqa: F401: dummy import for build-- we need to add this to modin

# as modin uses this in apply. it shouldn't be a dependency of soda at all.
from modin.config import Engine, StorageFormat
from modin.core.execution.dispatching.factories import factories

import ponder
from ponder.core.common import (
    ExecutionConfiguration,
    get_execution_configuration,
    set_execution_configuration,
)
from ponder.core.error_codes import PonderError, make_exception

from .instrumentation import PonderInstrumentation

logger = logging.getLogger(__name__)


__PONDER_API_URL__ = "https://api.ponder.io"


class NoCredentialsError(Exception):
    pass


def configure(
    *,
    default_connection=None,
    query_timeout=600,
    row_transfer_limit=10000,
    # TODO(https://ponderdata.atlassian.net/browse/POND-1009): We don't want to expose
    # this parameter, but we have to for now.
    bigquery_dataset=None,
    bigquery_approximate_quantiles=False,
) -> None:
    """Configure ponder.

    Parameters
    ----------
    default_connection: Any
        The database connection to use to store data that's not already in a database,
        e.g. on read_csv. Acceptable connection classes: duckdb.Connection,
        snowflake.connector.Connection, google.cloud.bigquery.dbapi.Connection
    bigquery_dataset: Optional[str]
        The bigquery dataset to use when reading CSV files into BigQuery. Normally,
        bigquery execution uses temporary tables, which don't need a dataset qualifier,
        but we have to read CSV files into a table qualified with a dataset. Note that
        this parameter only has an effect when ingesting data from outside of BigQuery.
        You can still read data from BigQuery tables using their qualified names without
        specifying this parameter.
    query_timeout: int, default: 600
        The query timeout for SNOWFLAKE queries only.
    row_transfer_limit: int, default: 10_000
        The maximum number of rows to transfer from the server to the client.
    bigquery_approximate_quantiles: bool, default: False
        Whether to use approximate quantiles for BigQuery execution. Approximate
        quantiles are easier to compute, but they are less accurate than the exact
        quantiles that pandas would produce.
    """
    from ponder.core.registry import validate_engine_license, verify_key_and_scopes

    try:
        verify_key_and_scopes()
    except NoCredentialsError:
        raise make_exception(
            NoCredentialsError,
            PonderError.CONFIGURE_CALLED_WITHOUT_CREDENTIALS,
            "User is not authenticated, please run `ponder login` in your terminal "
            + "or pass your API Key to `ponder.init`",
        )

    # Importing DBMSIO errors if imported before license is validated
    from ponder.core.io import DBMSIO

    DBMSIO.default_connection = default_connection
    if default_connection is not None:
        # If default_connection is None, users can still perform read_sql
        # In that case, validation is redone by the SQLConnection class; this
        # statement is placed here for ergonomics so users get an error before
        # they attempt to run any actual pandas code
        validate_engine_license(default_connection)

    if not isinstance(row_transfer_limit, int):
        raise RuntimeError(
            "row_transfer_limit must be an integer, but got "
            + f"{row_transfer_limit} of type"
            + f"{type(row_transfer_limit)}"
        )
    if row_transfer_limit <= 0:
        raise RuntimeError(
            "row_transfer_limit must be positive," + f"but got {row_transfer_limit}"
        )

    # TODO(https://ponderdata.atlassian.net/browse/POND-1008): a connection will ignore
    # updates to query timeout after we construct it.
    if query_timeout is not None:
        if not isinstance(query_timeout, int):
            raise RuntimeError(
                "query_timeout must be an integer, but got "
                + f"{query_timeout} of type {type(query_timeout)}"
            )
        if query_timeout <= 0:
            raise RuntimeError(
                f"query_timeout must be positive, but got {query_timeout}"
            )

    set_execution_configuration(
        ExecutionConfiguration(
            row_transfer_limit=row_transfer_limit,
            mask_with_temp_table=True,
            query_timeout=query_timeout,
            bigquery_dataset=bigquery_dataset,
            bigquery_approximate_quantiles=bigquery_approximate_quantiles,
        )
    )


_initialized = False


def init(api_key=None) -> None:
    """Initialize ponder.

    After you call this function, modin.pandas will execute on the
    backends of your choice.

    Parameters
    ----------
    api_key : str
        The API Key to use to authenticate with Ponder.
    """
    if _initialized:
        return

    setup_telemetry = False
    if api_key:
        os.environ["PONDER_API_KEY"] = api_key
        setup_telemetry = True

    # Import here to avoid circular dependency
    from ponder.core.registry import verify_key_and_scopes

    verify_key_and_scopes()

    """
    Importing DBMSIO triggers the API key validation. As soon as anyone imports anything
    from ponder, ponder will get the init() definition from this file. If we import
    DBMSIO at the top of this file, even "ponder configure"  will trigger the API key
    check because it imports the "main" method from ponder.
    """
    from ponder.core.io import DBMSIO

    # Instrumentation must be done after the key is verified, because instrumentation
    # imports DBMSIO
    if (
        os.environ.get("PONDER_INSTRUMENTATION") is not None
        and os.environ.get("PONDER_INSTRUMENTATION").lower() == "true"
    ):
        PonderInstrumentation()

    class DBMSExecutionFactory(factories.BaseFactory):
        @classmethod
        def prepare(cls):
            cls.io_cls = DBMSIO

    factories.DatabaseOnPonderFactory = DBMSExecutionFactory
    StorageFormat.add_option("Database")
    Engine.add_option("Ponder")
    StorageFormat._put_nocallback("Database")
    Engine.put("Ponder")
    # it's possible the user has already configured ponder.
    if get_execution_configuration() is None:
        configure()

    if setup_telemetry:
        # we do this because we need to set up telemetry, and telemetry isn't setup
        # until we have actually been authenticated.
        ponder.authenticate_and_verify()
    ponder.restore_modin()
