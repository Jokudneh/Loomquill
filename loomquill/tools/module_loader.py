import contextlib
import importlib
import os
import pkgutil
import sys
from typing import Any, Iterator, List, Union


@contextlib.contextmanager
def add_sys_path(path: Union[str, os.PathLike]) -> Iterator[None]:
    """Temporarily add given path to `sys.path`."""
