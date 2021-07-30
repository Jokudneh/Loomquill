import importlib
import os
import subprocess
import sys
from typing import Dict, Optional

from flyteidl.core import literals_pb2 as _literals_pb2

import flytekit
from flytekit.core import utils
from flytekit.core.context_manager import FlyteContextManager
from flytekit.core.type_engine import TypeEngine
from flytekit.interactive.constants import EXIT_CODE_SUCCESS
from flytekit.models import literals as _literal_models


def load_module_from_path(module_name, path):
    """
    Imports a Python module from a specified file path.

    Args:
        module_name (str): The name you want to assign to the imported module.
        path (str): The file system path to the Python file (.py) that contains the module you want to import.

    Returns:
        module: The imported module.

    Raises:
        ImportError: If the module cannot be loaded from the provided path, an ImportError is raised.
    """
    spec = importlib.util.spec_from_file_location(module_name, path)
