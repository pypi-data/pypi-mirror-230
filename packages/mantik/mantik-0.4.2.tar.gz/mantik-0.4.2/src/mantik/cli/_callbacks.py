import logging

logger = logging.getLogger(__name__)


def set_verbose_logging(ctx, param, value) -> None:  # noqa
    """
    Callback function to set log level from a --verbose flag.

    Note: Unused arguments are part of the click callback signature and
    must be present.
    """
    if value:
        logger.root.setLevel(level=logging.DEBUG)
        logger.debug("Using logging level DEBUG")
    else:
        logger.root.setLevel(level=logging.WARNING)
        logging.basicConfig(level=logging.WARNING)
