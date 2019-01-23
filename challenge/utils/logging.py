import logging
from dynaconf import settings


def create_logger():
    """Create a simple Python logger."""
    logger = logging.Logger('challenge', level=logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s')

    handler = logging.StreamHandler()
    handler.setLevel(settings.LOG_LEVEL)
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


logger = create_logger()
