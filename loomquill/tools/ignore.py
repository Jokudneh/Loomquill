import os
import subprocess
import tarfile
from abc import ABC, abstractmethod
from fnmatch import fnmatch
from pathlib import Path
from shutil import which
from typing import List, Optional, Type

from docker.utils.build import PatternMatcher

from flytekit.loggers import logger

STANDARD_IGNORE_PATTERNS = ["*.pyc", ".cache", ".cache/*", "__pycache__/*", "**/__pycache__/*"]


class Ignore(ABC):
    """Base for Ignores, implements core logic. Children have to implement _is_ignored"""

    def __init__(self, root: str):
        self.root = root

    def is_ignored(self, path: str) -> bool:
        if os.path.isabs(path):
            path = os.path.relpath(path, self.root)
        return self._is_ignored(path)

    def tar_filter(self, tarinfo: tarfile.TarInfo) -> Optional[tarfile.TarInfo]:
        if self.is_ignored(tarinfo.name):
            return None
        return tarinfo

    @abstractmethod
