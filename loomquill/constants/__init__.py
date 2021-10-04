from __future__ import annotations

from enum import Enum


class CopyFileDetection(Enum):
    LOADED_MODULES = 1
    ALL = 2
    # This option's meaning will change in the future. In the future this will mean that no files should be copied
