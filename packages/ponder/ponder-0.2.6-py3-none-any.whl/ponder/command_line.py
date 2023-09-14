import argparse
import logging
import logging.handlers
import os
import pathlib
from configparser import ConfigParser

import requests

from ponder.common import __PONDER_API_URL__

logger = logging.getLogger(__name__)

client_logger = logging.getLogger("client logger")
welcome = r"""
+----------------------------------------+
|               WELCOME TO               |
|     ____                  __           |
|    / __ \____  ____  ____/ /__  _____  |
|   / /_/ / __ \/ __ \/ __  / _ \/ ___/  |
|  / ____/ /_/ / / / / /_/ /  __/ /      |
| /_/    \____/_/ /_/\__,_/\___/_/       |
+----------------------------------------+
"""


class ApiKeyNotValidError(Exception):
    """Exception raised when API KEY is not valid."""

    def __init__(self, message="API key is not valid"):
        self.message = message
        super().__init__(self.message)


def _get_configfile_path():
    if pathlib.Path("~/.secrets/access_token").expanduser().exists():
        return pathlib.Path("~/work/.ponder")
    else:
        return pathlib.Path("~/.ponder")


def configure():
    location = _get_configfile_path()
    if location.expanduser().exists():
        raise Exception("Ponder already configured, to reset run `ponder reset`")
    config = ConfigParser()
    auto_api_key = os.environ.get("PONDER_API_KEY", None)
    if auto_api_key:
        api_key = auto_api_key
    else:
        client_logger.warn(
            "\n"
            f"{welcome}\n"
            "Please enter your product key below. "
            "You can find your product key at https://app.ponder.io/account-settings.\n"
            "If you don't have a Ponder account, "
            "sign up at: https://app.ponder.io/signup\n"
        )
        api_key = input("Enter Product Key: ")

    api_key = api_key.strip()

    if len(api_key) != 40:
        raise ApiKeyNotValidError
    base_url = __PONDER_API_URL__
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    verification_url = f"{base_url}/api-key/verify"
    verification = requests.get(verification_url, headers=headers)
    if verification.status_code != 200:
        raise ApiKeyNotValidError
    client_logger.warn("Login was successful")
    config["PONDER"] = {"API KEY": api_key}
    with open(os.path.expanduser(location), "w+") as config_file:
        config.write(config_file)


def reset():
    location = _get_configfile_path()
    if location.expanduser().exists():
        client_logger.warn("Removing Ponder Credentials...")
        location.expanduser().unlink()
    # A little weary of doing this as this is not something we set;
    # however, seems prudent.
    # .unsetenv() it seems doesn't update os.environ.
    env_var = os.environ.pop("CONFIG_FILE", None)
    if env_var:
        client_logger.warn("Removed the environment variable CONFIG_FILE")


def intro():
    client_logger.warn(
        f"{welcome}\n"
        "To get started:\n"
        "1. Create an account at: https://app.ponder.io/signup\n"
        "2. Run `ponder login` and enter your product key\n"
        "3. Check out our quickstart guide: "
        "https://docs.ponder.io/getting_started/quickstart.html\n"
        "Contact us at support@ponder.io for any issues or questions.\n"
    )


def main(prog="ponder"):
    parser = argparse.ArgumentParser(prog=prog, description="Ponder utilities.")
    parser.add_argument("setup", choices=["login", "reset"])
    try:
        args = parser.parse_args()
        if args.setup == "login":
            configure()
        if args.setup == "reset":
            reset()
    except SystemExit:
        intro()
