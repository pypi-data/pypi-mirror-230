import logging
import logging.handlers


FORMAT = '[%(asctime)s | %(module)s | %(levelname)s | %(lineno)d]: %(message)s'
DATETIME_FMT = '%Y-%m-%d %H:%M:%S'


def config_logging(logger_level: str = "INFO") -> None:
    """Config logger for the application.

    Call once in main module.
    Change the logging level for external depencencies and the format of the
    logger.

    Example: For the main module or app entrypoint.

    ..code::
        # main.py o any
        import logging
        ...
        import setup_logger # or the name of the this module
        ...
        setup_logger.config_logging()  # or the name of this function
        logger = logging.getLogger(__name__)
        ...

        # For any other module use the standar
        import logging
        ...
        logger = logging.getLogger(__name__)

    For other logger is possible to configure separete as
    setLevel or Propagate:

    .. code::
        logging.getLogger("pkg_name").setLevel("LEVEL")
        logging.getLogger("pkg_name").propagate = False
    """
    stream_handler = logging.StreamHandler()
    logging.basicConfig(
        level=logger_level,
        format=FORMAT,
        datefmt='%Y-%m-%dT%H:%M:%S%z',
        handlers=(stream_handler,)
    )
    #
    # Configure other loggers for this application
    #
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests_oauthlib.oauth2_session").setLevel(logging.WARNING)
    # logging.getLogger("requests").setLevel(logging.INFO)
    #
    # print(logging.root.level, flush=True)


def _show_loggers() -> None:
    """Print all loggers for entire application.

    Require import all modules to show all loggers available.

    ..code::

        import A
        import B
        ...

    Ref: https://stackoverflow.com/a/36208664/4112006
    """
    import requests  # noqa: F401
    # import ubicquia  # noqa: F401
    print('Available loggers:')
    for logger in logging.Logger.manager.loggerDict:
        print(logger)


def get_logger(logger_name, level: int = logging.INFO) -> logging.Logger:
    config_logging(level)
    return logging.getLogger(logger_name)


if __name__ == '__main__':
    _show_loggers()
