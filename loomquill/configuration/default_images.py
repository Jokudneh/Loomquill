import enum
import os
import sys
import typing
from contextlib import suppress

from flytekit.core.constants import FLYTE_INTERNAL_IMAGE_ENV_VAR


class PythonVersion(enum.Enum):
    PYTHON_3_8 = (3, 8)
    PYTHON_3_9 = (3, 9)
    PYTHON_3_10 = (3, 10)
    PYTHON_3_11 = (3, 11)
    PYTHON_3_12 = (3, 12)
    PYTHON_3_13 = (3, 13)
    PYTHON_3_14 = (3, 14)


class DefaultImages(object):
    """
