import os
import sys

import pytest
from flytekitplugins.papermill import NotebookTask
from flytekitplugins.spark import Spark

from flytekit import kwtypes
from flytekit.types.schema import FlyteSchema


def _get_nb_path(name: str, suffix: str = "", abs: bool = True, ext: str = ".ipynb") -> str:
    """
    Creates a correct path no matter where the test is run from
    """
    _local_path = os.path.dirname(__file__)
    path = f"{_local_path}/testdata/{name}{suffix}{ext}"
    return os.path.abspath(path) if abs else path


