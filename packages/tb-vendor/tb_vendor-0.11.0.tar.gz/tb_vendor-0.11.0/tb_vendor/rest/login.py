import logging
from time import sleep

import requests
from tb_rest_client.rest_client_base import RestClientBase

from tb_vendor.exceptions import TbLoginError
from tb_vendor.rest.models import RestClientType

logger = logging.getLogger(__name__)


def validate_login(rest_client: RestClientBase) -> None:
    """Validate if TB login was successful or raise an exception.

    Args:
        client: RestClientType

    Raises:
        TbLoginError: if login was not successful
    """
    if rest_client.token_info["token"] is None:
        logger.error(
            "Problem when login to ThingsBoard (username, password): " "No token"
        )
        raise TbLoginError("Error in Authentication")


def login_wait(
    rest_client: RestClientType,
    username: str,
    password: str,
    retry_for_timeout: int,
    max_retries: int = 100,
) -> None:
    """Try to authenticate in TB Server and wait until login.

    Args:
        rest_client: RestClientType instance.
        username: username for login.
        password: password for login.
        retry_for_timeout: retry timeout if something go wrong.

    Returns:
        This function is expected to return None when login was successful
    """
    cnt = 0
    while True:
        cnt += 1
        logger.info("Try to login in TB Server")
        try:
            rest_client.login(username, password)
        except requests.exceptions.ConnectionError as e:
            logger.error(f"ConnectionError for login: {e}")
            sleep(retry_for_timeout)
        except Exception:
            logger.exception("Error for login")
            sleep(retry_for_timeout)
        else:
            break
        if cnt > max_retries:
            raise TbLoginError(
                f"Login failed. Max retries reached: {max_retries}"
            )
