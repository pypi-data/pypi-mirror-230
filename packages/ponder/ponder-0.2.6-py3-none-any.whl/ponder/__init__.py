import modin.pandas as pd
import requests

from . import _version
from .common import __PONDER_API_URL__, configure, init

__version__ = _version.get_versions()["version"]

__all__ = ["init", "configure"]

try:
    latest_ponder_version = requests.get(
        "https://pypi.org/pypi/ponder/json", timeout=5
    ).json()["info"]["version"]
except Exception:
    latest_ponder_version = "0+unknown"


class ApiKeyExpiredError(Exception):
    pass


old_dataframe = pd.DataFrame.__init__
old_series = pd.Series.__init__
old_read_clipboard = pd.read_clipboard
old_read_csv = pd.read_csv
old_read_excel = pd.read_excel
old_read_feather = pd.read_feather
old_read_fwf = pd.read_fwf
old_read_gbq = pd.read_gbq
old_read_hdf = pd.read_hdf
old_read_html = pd.read_html
old_read_json = pd.read_json
old_read_orc = pd.read_orc
old_read_parquet = pd.read_parquet
old_read_pickle = pd.read_pickle
old_read_sas = pd.read_sas
old_read_spss = pd.read_spss
old_read_sql = pd.read_sql
old_read_sql_query = pd.read_sql_query
old_read_sql_table = pd.read_sql_table
old_read_stata = pd.read_stata
old_read_table = pd.read_table
old_read_xml = pd.read_xml


def remind_to_init_ponder(*args, **kwargs):
    class PonderInitError(Exception):
        pass

    raise PonderInitError(
        "Ponder is not yet initialized, to start run `ponder.init()`. "
        "To use Modin without Ponder mode run `ponder.restore_modin()`."
    )


def restore_modin():
    pd.DataFrame.__init__ = old_dataframe
    pd.Series.__init__ = old_series
    pd.read_clipboard = old_read_clipboard
    pd.read_csv = old_read_csv
    pd.read_excel = old_read_excel
    pd.read_feather = old_read_feather
    pd.read_fwf = old_read_fwf
    pd.read_gbq = old_read_gbq
    pd.read_hdf = old_read_hdf
    pd.read_html = old_read_html
    pd.read_json = old_read_json
    pd.read_orc = old_read_orc
    pd.read_parquet = old_read_parquet
    pd.read_pickle = old_read_pickle
    pd.read_sas = old_read_sas
    pd.read_spss = old_read_spss
    pd.read_sql = old_read_sql
    pd.read_sql_query = old_read_sql_query
    pd.read_sql_table = old_read_sql_table
    pd.read_stata = old_read_stata
    pd.read_table = old_read_table
    pd.read_xml = old_read_xml


(
    pd.DataFrame.__init__,
    pd.Series.__init__,
    pd.read_clipboard,
    pd.read_csv,
    pd.read_excel,
    pd.read_feather,
    pd.read_fwf,
    pd.read_gbq,
    pd.read_hdf,
    pd.read_html,
    pd.read_json,
    pd.read_orc,
    pd.read_parquet,
    pd.read_pickle,
    pd.read_sas,
    pd.read_spss,
    pd.read_sql,
    pd.read_sql_query,
    pd.read_sql_table,
    pd.read_stata,
    pd.read_table,
    pd.read_xml,
) = (remind_to_init_ponder,) * 22

_IPYTHON_MISSING_ATTRIBUTES = [
    "_ipython_canary_method_should_not_exist_",
    "_ipython_display_",
    "_repr_mimebundle_",
]


# ipython seems to trigger multiple loops through the data when any one of these
# internal non-existent methods are called on a Modin Series:
# - _ipython_canary_method_should_not_exist_
# - _ipython_display_
# - _repr_mimebundle_
#
# it triggers a lookup for each value EVERY TIME one of these are called, and on
# repr each of them are called, and one of them
# (_ipython_canary_method_should_not_exist_) is called twice, so we effectively
# loop through the data four times looking up each row number in the database.
#
# So we need to add it to the _ATTRS_NOLOOKUP in Series so that it doesn't trigger
# large amounts of computation on the engine.
pd.series._ATTRS_NO_LOOKUP.update(_IPYTHON_MISSING_ATTRIBUTES)


def _verify(api_key, client_logger):
    import requests

    from .command_line import ApiKeyNotValidError

    api_key_error = (
        f"API KEY is not valid. API KEY can be obtained from {__PONDER_API_URL__}"
    )
    # API KEY is not valid
    if len(api_key) != 40:
        raise ApiKeyNotValidError(api_key_error)
    # Verify API KEY is valid
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    verification = requests.patch(
        f"{__PONDER_API_URL__}/api-key/verify", headers=headers, params={"count": 1}
    )
    if (
        verification.status_code == 401
        and "API key has expired" in verification.json().get("detail", "")
    ):
        raise ApiKeyExpiredError(
            "Your API key has expired. Please contact ponder support at "
            + "support@ponder.io"
        )
    if not verification.ok:
        # TODO: should we raise an error here instead of just logging? That would be
        # consistent with how we handle other kinds of verification errors.
        client_logger.error("API key verification with ponder.io failed")
        return False
    elif verification.status_code != 200:
        raise ApiKeyNotValidError(api_key_error)
    # NOTE: We could check for some keys in response if we really need to.
    return True


def authenticate_and_verify():
    def add_as_only_handler(logger, handler):
        # we may have already added a handler in an earlier ponder import, so replace
        # any existing handlers with the new one.
        logger.handlers.clear()
        logger.addHandler(handler)

    import atexit
    import hashlib
    import inspect
    import json
    import logging
    import os
    import platform
    import re
    import secrets
    import socket
    import sys
    import threading
    import time
    from configparser import ConfigParser
    from datetime import datetime

    import psutil
    import requests
    import schedule
    from packaging import version
    from requests.adapters import HTTPAdapter, Retry

    from .command_line import _get_configfile_path

    # This three lines below are necessary to coerce Colab into
    # good behavior. The root loggers default handler should be initialized
    # the first time a logging event at a level above the one set is logged.
    # In colab, however, root comes with a default stderr at NOTSET.
    # The three lines below ensure the root logger is cleared and a NullHandler
    # is set. This will ensure INFO messages are not printed when the default
    # level is WARN.
    set_root_null = os.getenv("SET_ROOT_NULL", "TRUE")
    if set_root_null == "TRUE":
        root = logging.getLogger()
        root.handlers.clear()
        root.addHandler(logging.NullHandler())
    # This is the package-level logger. logging.getLogger(__name__)
    # anywhere else will propogate here. Root logger is the parent
    # of this logger. Not setting a handler for this will propogate
    # up to the root loggers handler
    ponder_logger = logging.getLogger(__name__)
    ponder_log_level = os.getenv("PONDER_LOG_LEVEL", "INFO")
    ponder_logger.setLevel(getattr(logging, ponder_log_level))
    ponder_log_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(funcName)s - %(levelname)s - %(message)s"
    )
    ponder_log_handler.setFormatter(formatter)
    add_as_only_handler(ponder_logger, ponder_log_handler)
    # Add a client facing logger and set level to INFO
    # This should be a separate logger (as opposed to adding
    # this handler to the root logger).
    formatter = logging.Formatter("%(asctime)s - %(message)s", "%Y-%m-%d %H:%M:%S")
    client_log_handler = logging.StreamHandler()
    client_log_level = os.getenv("CLIENT_LOG_LEVEL", "WARN")
    client_log_handler.setLevel(client_log_level)
    client_log_handler.setFormatter(formatter)
    client_logger = logging.getLogger("client logger")
    client_logger.setLevel(logging.INFO)
    add_as_only_handler(client_logger, client_log_handler)

    if version.parse(latest_ponder_version) > version.parse(__version__):
        client_logger.warning(
            "New version of Ponder is available! "
            "`pip install --upgrade ponder` to install!"
        )

    location = _get_configfile_path()
    config_location = os.getenv("CONFIG_FILE", location.expanduser())
    config_available = False
    verified = False

    try:
        config = ConfigParser()
        # config doesn't error when file not found on read.
        # so the below is necessary.
        # TODO: switch to toml
        with open(config_location) as f:
            config.read_file(f)
        config_available = True
    except FileNotFoundError:
        # Assume file is not present and allow module to be imported
        # without shenanigans. This is necessary for ponder login.
        # Assume here that setup will do its job and block user on
        # invalid API KEY etc
        pass

    if config_available:
        if not config.has_option("PONDER", "API KEY"):
            # config file is present; however it is not valid
            client_logger.error(
                "Ponder config file is invalid. "
                "Delete the file or run ponder reset. "
                "Then run ponder login"
            )
        else:
            # config file is present. Check if API KEY is valid
            api_key = config["PONDER"]["API KEY"].strip()
            verified = _verify(api_key, client_logger)
    else:
        potential_key = os.getenv("PONDER_API_KEY", None)
        if potential_key:
            api_key = potential_key.strip()
            verified = _verify(api_key, client_logger)

    # Begin remote logging setup
    # At this point assume the api_key has been verified and the user is legit.
    def telemetry_setup(option_name: str):
        if option_name not in [
            "REMOTE LOGGING",
            "REMOTE MODIN LOGGING",
            "REMOTE LOGGING INTERVAL",
        ]:
            raise ValueError(
                "Options for setup parameters are"
                " REMOTE LOGGING/REMOTE MODIN LOGGING/REMOTE LOGGING INTERVAL"
            )
        if not config.has_option("TELEMETRY", option_name):
            if "interval" not in option_name.lower():
                preference = os.getenv(option_name.replace(" ", "_"), "TRUE")
            else:
                preference = os.getenv(option_name.replace(" ", "_"), "1800")
        else:
            preference = config["TELEMETRY"][option_name]
        preference = preference.strip().lower()
        if "interval" in option_name.lower():
            if preference > "7200" or preference <= "0":
                # Pretty random; however, we probably don't want it too large
                raise ValueError("0 < Logging Interval < two hours")
        elif preference not in ["false", "true"]:
            raise ValueError(
                f"Options for {option_name} are TRUE/FALSE not {preference}"
            )

        return preference

    if verified:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        atexit.register(
            requests.patch,
            url=f"{__PONDER_API_URL__}/api-key/verify",
            headers=headers,
            params={"count": -1},
        )
        remote_logging = telemetry_setup("REMOTE LOGGING")
        remote_modin_logging = telemetry_setup("REMOTE MODIN LOGGING")
        remote_logging_interval = int(telemetry_setup("REMOTE LOGGING INTERVAL"))

        # DO NOT DELETE -- Needed for tests
        client_logger.info(
            "Ponder package successfully imported"
        )  # test_auth::test_authentication

        if remote_logging == "true":
            # set up session
            session_key = secrets.token_urlsafe(42)[:42]
            client_logger.info(f"Creating session {session_key}")

            def raw_post_to_logger(message: str, join: bool = False):
                # TODO: Look into merging this and _post_message if possible
                log_message = json.dumps(
                    {
                        "time": datetime.now()
                        .astimezone()
                        .strftime("%Y-%m-%d %H:%M:%S%z %Z"),
                        "message": message,
                        "session": f"{session_key}",
                    }
                )
                t = threading.Thread(
                    target=requests.post,
                    args=(f"{__PONDER_API_URL__}/logger",),
                    kwargs={"headers": headers, "data": log_message},
                )
                t.start()
                if join:
                    t.join()

            # DO NOT DELETE -- Needed for tests
            raw_post_to_logger(
                "Ponder package successfully imported"
            )  # test_logger::test_logging_service
            client_data = json.dumps(
                {
                    "host_hash": hashlib.md5(
                        socket.getfqdn().encode("utf-8")
                    ).hexdigest(),
                    "os": platform.platform(),
                    "cpu": platform.processor(),
                    "mem": psutil.virtual_memory().total,
                    "python_version": platform.python_version(),
                    "ponder_version": __version__,
                }
            )
            raw_post_to_logger(client_data)
            # This does not work for ctrl-z in repl and kernel interrupt in Jupyter
            atexit.register(
                raw_post_to_logger,
                message="Ponder package successfully exited",
                join=True,
            )

        if remote_logging == "true" and remote_modin_logging == "true":

            class APILogHandler(logging.Handler):
                modin_log_start_regex = re.compile("^START::(.+)$")
                exception_regex = re.compile(r"\[PONDER-([a-e0-9]{6})\]")
                shape_regex = re.compile(r"^_ponder_dataframe_shape: (\d+), (\d+)")

                def __init__(self, url: str, token: str):
                    self._modin_log_records = []
                    self._modin_error_log_records = []
                    self._url = url
                    self._token = token
                    self._url = f"{url}/logger"
                    self._MAX_POOLSIZE = 50
                    self._session = requests.Session()
                    self._session.headers.update(
                        {
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {self._token}",
                        }
                    )
                    self._session.mount(
                        "http://",
                        HTTPAdapter(
                            max_retries=Retry(
                                total=5,
                                backoff_factor=0.1,
                                status_forcelist=[500, 502, 503, 504],
                            ),
                            pool_connections=self._MAX_POOLSIZE,
                            pool_maxsize=self._MAX_POOLSIZE,
                        ),
                    )

                    super().__init__()

                def flush(self):
                    if (
                        len(self._modin_log_records) == 0
                        and len(self._modin_error_log_records) == 0
                    ):
                        return

                    from collections import Counter

                    api_call_counts_by_key = Counter()
                    shape_counts_by_key = Counter()
                    for record in self._modin_log_records:
                        method_names = self.modin_log_start_regex.findall(record.msg)
                        if len(method_names) == 1:
                            api_call_counts_by_key[method_names[0]] += 1
                        elif len(method_names) > 1:
                            # should be impossible to get here because there is
                            # only one capturing group in the regex.
                            ponder_logger.error(
                                "internal error: logger parsed multiple method names "
                                + f"from line {record.msg}"
                            )
                        else:
                            shapes = self.shape_regex.findall(record.msg)
                            if len(shapes) == 1:
                                shape_counts_by_key[
                                    tuple(int(d) for d in shapes[0])
                                ] += 1
                            elif len(shapes) > 0:
                                # should be impossible to get here because the pattern
                                # should only match at most once.
                                ponder_logger.error(
                                    "internal error: parsed multiple dataframe "
                                    + f"shapes from log line {record.msg}"
                                )
                        # ignore likes like "Total Cores: 16" that neither regex matches
                    ponder_error_counts_by_code = Counter()
                    external_error_counts = Counter()
                    for record in self._modin_error_log_records:
                        exception_message = getattr(
                            record.exc_info[1], "message", str(record.exc_info[1])
                        )
                        match = re.search(self.exception_regex, exception_message)
                        if match is not None:
                            ponder_error_counts_by_code[match.group(1)] += 1
                        else:
                            if not (
                                # pandas cache_readonly routinely fails to find
                                # the _cache attribute the first time you try to get
                                # certain attributes [1]. No need to send telemetry
                                # about this error.
                                # [1] https://github.com/pandas-dev/pandas/blob/bdfaca634e9946c0612c497456332fee80e7db37/pandas/_libs/properties.pyx#L19 # noqa: E501
                                exception_message
                                == "'DataFrame' object has no attribute '_cache'"
                                or exception_message
                                == "'Series' object has no attribute '_cache'"
                                # ipython often tries and fails to get these attributes.
                                # we know they're missing, so no need to send telemetry
                                # about them.
                                or any(
                                    a in exception_message
                                    for a in _IPYTHON_MISSING_ATTRIBUTES
                                )
                            ):
                                external_error_counts[
                                    json.dumps(
                                        {
                                            "error": ".".join(
                                                (
                                                    record.exc_info[0].__module__,
                                                    record.exc_info[0].__name__,
                                                )
                                            ),
                                            **(
                                                {
                                                    "from": (
                                                        record._ponder_exception_origin
                                                    )
                                                }
                                                if hasattr(
                                                    record,
                                                    "_ponder_exception_origin",
                                                )
                                                else {}
                                            ),
                                        }
                                    )
                                ] += 1
                    events = [
                        *(
                            {"event": f"api.{event}", "count": count}
                            for event, count in api_call_counts_by_key.items()
                        ),
                        *(
                            {
                                "event": "initial_df_shape",
                                "event_param": f"{length},{width}",
                                "count": count,
                            }
                            for (length, width), count in shape_counts_by_key.items()
                        ),
                        *(
                            {
                                "event": "error",
                                "event_param": event,
                                "count": count,
                            }
                            for event, count in ponder_error_counts_by_code.items()
                        ),
                        *(
                            {
                                "event": "external_error",
                                "event_param": event,
                                "count": count,
                            }
                            for event, count in external_error_counts.items()
                        ),
                    ]

                    modin_data = json.dumps({"events": events})
                    try:
                        self._post_message(modin_data, join=True)
                    except Exception:
                        raise
                    self._modin_log_records.clear()
                    self._modin_error_log_records.clear()

                def emit(self, record: logging.LogRecord):
                    """This gets called when a log event is emitted."""
                    if record.exc_info is not None:
                        # not sure this will always work; @mvashishtha recalls that
                        # inspect() is not always reliable. getmodule() may return None.
                        # ignore any errors.
                        try:
                            trace = inspect.trace()
                            record._ponder_exception_origin = inspect.getmodule(
                                trace[-1].frame
                            ).__name__
                        except Exception:
                            ponder_logger.error(
                                "failed to find origin of exception "
                                + f"{record.exc_info[1]}"
                            )
                            pass
                        self._modin_error_log_records.append(record)
                    else:
                        self._modin_log_records.append(record)

                def _post_message(self, modin_data, join=False):
                    """Post a log message over HTTPS."""
                    data = json.dumps(
                        {
                            "time": datetime.now()
                            .astimezone()
                            .strftime("%Y-%m-%d %H:%M:%S%z %Z"),
                            "session": f"{session_key}",
                            "message": modin_data,
                        }
                    )
                    t = threading.Thread(
                        target=self._session.post,
                        args=(self._url,),
                        kwargs={"data": data},
                    )
                    t.start()
                    if join:
                        t.join()

            remote_log_handler = APILogHandler(
                # For dev point to http://localhost:80/logger
                # docker setup is in ponder-api
                url=__PONDER_API_URL__,
                token=api_key,
            )
            remote_log_handler.setLevel(logging.INFO)
            import modin.config
            import modin.logging

            modin.config.LogMode.enable_api_only()
            modin_logger = modin.logging.get_logger()
            # Remove any and all pre-existing handlers.
            # This will remove the file handlers
            modin_logger.handlers.clear()
            modin_logger.addHandler(remote_log_handler)
            modin_error_logger = modin.logging.get_logger("modin.logger.errors")
            add_as_only_handler(modin_error_logger, remote_log_handler)

            def run_logging_continuously(interval=remote_logging_interval):
                class Scheduler(threading.Thread):
                    @classmethod
                    def run(cls):
                        while True:
                            schedule.run_pending()
                            time.sleep(interval)

                Scheduler(daemon=True).start()

            schedule.every(remote_logging_interval).seconds.do(remote_log_handler.flush)
            run_logging_continuously()

            # TODO(https://ponderdata.atlassian.net/browse/POND-1138): add a handler to
            # modin error logger too


authenticate_and_verify()

common = command_line = pushdown_service = None
del command_line
del pushdown_service
del requests
del common
