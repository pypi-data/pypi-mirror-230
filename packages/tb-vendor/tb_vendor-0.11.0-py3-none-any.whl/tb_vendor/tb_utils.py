"""Thingsboard utilites."""

import logging
from typing import Callable

import requests
from tb_vendor.models import TbPagination
from tb_vendor.rest.models import TbRestVersion


logger = logging.getLogger(__name__)


def tb_paginate(
    func: Callable, *, page_size: int, page: int = 0, max_pages: int = None, **kwargs
) -> list:
    """Paginate Thingsboard rest client methods.

    Args:
        func: method of TB rest client.
        page_size: page size.
        page: page number start from 0.
        max_pages: maximum number of pages to be requests.
        **kwargs: keyword arguments for that method.

    Returns:
        List of data.

    Raises:
        ValueError: if max_pages is invalid
    """
    n_max, n = 0, page
    container = []
    if max_pages:
        n_max = max_pages
    if max_pages and max_pages <= 0:
        raise ValueError(f"Invalid max_pages: {max_pages}. Must be grater than 0.")
    while True:
        logger.debug(f"{func.__name__} Request Page: {n}")
        result: TbPagination = func(page=n, page_size=page_size, **kwargs)
        container += result.data
        if result.has_next is False:
            break
        if n_max and n_max >= n:
            break
        page += 1
    return container


def get_tb_rest_version_v1(tb_base_url: str) -> str:
    """Get TB REST version.

    White label endpoint  only exists on PE.

    Returns:
        TB REST version: CE or PE.

    Raises:
        - requests.exceptions.HTTPError
        - requests.exceptions.ConnectionError
    """
    _path = "/api/noauth/whiteLabel/loginWhiteLabelParams"
    try:
        r = requests.get(tb_base_url + _path)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        data = e.response.json()
        if (
            e.response.status_code == 404
            and data
            and "path" in data
            and data["path"] == _path
        ):
            logger.debug("TB REST version is CE")
            return "CE"
        else:
            logger.debug(f"Unknown rest client: {data}")
            raise
    except requests.exceptions.ConnectionError:
        logger.error("No connection")
        raise
    logger.debug("TB REST version is PE")
    return "PE"


def validate_tb_rest_version(base_url: str, tb_rest_version: TbRestVersion) -> None:
    """_summary_

    Args:
        base_url (str): Thingsboard base url.
        tb_rest_version: CE or PE

    Raises:
        ValueError: _description_
    """
    logger.debug("Detecting REST client")
    rest_version = get_tb_rest_version_v1(base_url)
    if rest_version != tb_rest_version:
        raise ValueError(f"TB_REST_VERSION is not compatible with {rest_version}")
    logger.debug(f"{tb_rest_version} REST client version is OK")
