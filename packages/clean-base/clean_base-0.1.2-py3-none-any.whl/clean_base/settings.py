from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    FATAL,
    INFO,
    NOTSET,
    WARN,
    WARNING,
    getLogger,
)
from os import getenv

# ? ----------------------------------------------------------------------------
# ? Build logger configurations
# ? ----------------------------------------------------------------------------


LOGGING_LEVEL = DEBUG


ENV_LOGGING_LEVEL = getenv("LOGGING_LEVEL")


if ENV_LOGGING_LEVEL is not None:
    ENV_LOGGING_LEVEL = eval(ENV_LOGGING_LEVEL.upper())

    if ENV_LOGGING_LEVEL not in [
        CRITICAL,
        DEBUG,
        ERROR,
        FATAL,
        INFO,
        NOTSET,
        WARN,
        WARNING,
    ]:
        raise ValueError(
            f"Invalid `ENV_LOGGING_LEVEL` value from env: {ENV_LOGGING_LEVEL}"
        )

    LOGGING_LEVEL = ENV_LOGGING_LEVEL  # type: ignore


# ? ----------------------------------------------------------------------------
# ? Initialize global logger
# ? ----------------------------------------------------------------------------


LOGGER = getLogger("CLEAN_BASE")


LOGGER.setLevel(LOGGING_LEVEL)


# ? ----------------------------------------------------------------------------
# ? LOCK FILE ELEMENTS
# ? ----------------------------------------------------------------------------


LOCK_FILE = "finished.lock"


LOCK_NAMED_FILE = "finished-{step}.lock"
