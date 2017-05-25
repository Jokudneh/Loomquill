import importlib.util
import logging
import os
import typing

if importlib.util.find_spec("pythonjsonlogger.json"):
    # Module was renamed: https://github.com/nhairs/python-json-logger/releases/tag/v3.1.0
    from pythonjsonlogger import json as jsonlogger
else:
    from pythonjsonlogger import jsonlogger

from .tools import interactive

# Note:
# The environment variable controls exposed to affect the individual loggers should be considered to be beta.
# The ux/api may change in the future.
# At time of writing, the code was written to preserve existing default behavior
# For now, assume this is the environment variable whose usage will remain unchanged and controls output for all
# loggers defined in this file.
LOGGING_ENV_VAR = "FLYTE_SDK_LOGGING_LEVEL"
# The environment variable controls the logging level for the developer logger.
LOGGING_DEV_ENV_VAR = "FLYTE_SDK_DEV_LOGGING_LEVEL"
LOGGING_FMT_ENV_VAR = "FLYTE_SDK_LOGGING_FORMAT"
LOGGING_RICH_FMT_ENV_VAR = "FLYTE_SDK_RICH_TRACEBACKS"

# By default, the root flytekit logger to debug so everything is logged, but enable fine-tuning
logger = logging.getLogger("flytekit")
user_space_logger = logging.getLogger("user_space")
developer_logger = logging.getLogger("developer")

# Stop propagation so that configuration is isolated to this file (so that it doesn't matter what the
# global Python root logger is set to).
logger.propagate = False


def set_flytekit_log_properties(
    handler: typing.Optional[logging.Handler] = None,
    filter: typing.Optional[logging.Filter] = None,
    level: typing.Optional[int] = None,
):
    """
    flytekit logger, refers to the framework logger. It is possible to selectively tune the logging for flytekit.

    Sets the flytekit logger to the specified handler, filter, and level. If any of the parameters are None, then
    the corresponding property on the flytekit logger will not be set.

    :param handler: logging.Handler to add to the flytekit logger
    :param filter: logging.Filter to add to the flytekit logger
    :param level: logging level to set the flytekit logger to
    """
    global logger
    if handler is not None:
        logger.handlers.clear()
        logger.addHandler(handler)
    if filter is not None:
        logger.addFilter(filter)
    if level is not None:
        logger.setLevel(level)

