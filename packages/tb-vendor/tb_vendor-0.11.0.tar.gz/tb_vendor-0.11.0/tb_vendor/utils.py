import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def parse_host(url: str) -> str:
    """Parse host domain from URL and remove port and any other parameter.

    Args:
        url: URL to parse

    Returns:
        Only domain name.

    Raises:
        ValueError.
    """
    domain_name = urlparse(url).netloc.split(':')[0]
    if not domain_name:
        msg = f'Invalid parameter url: {url}'
        logger.error(msg)
        raise ValueError(msg)
    return domain_name


class Singleton:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance
