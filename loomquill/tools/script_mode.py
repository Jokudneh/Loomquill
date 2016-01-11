from __future__ import annotations

import gzip
import hashlib
import os
import shutil
import site
import stat
import sys
import tarfile
import tempfile
import typing
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import List, Optional, Tuple, Union

import flytekit
from flytekit.constants import CopyFileDetection
from flytekit.loggers import logger
from flytekit.tools.ignore import IgnoreGroup


def compress_scripts(source_path: str, destination: str, modules: List[ModuleType]):
    """
    Compresses the single script while maintaining the folder structure for that file.

    For example, given the follow file structure:
    .
    ├── flyte
    │   ├── __init__.py
    │   └── workflows
    │       ├── example.py
    │       ├── another_example.py
    │       ├── yet_another_example.py
    │       ├── unused_example.py
    │       └── __init__.py

    Let's say you want to compress `example.py` imports `another_example.py`. And `another_example.py`
    imports on `yet_another_example.py`. This will  produce a tar file that contains only that
    file alongside with the folder structure, i.e.:

    .
    ├── flyte
    │   ├── __init__.py
    │   └── workflows
    │       ├── example.py
    │       ├── another_example.py
    │       ├── yet_another_example.py
    │       └── __init__.py

    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        destination_path = os.path.join(tmp_dir, "code")
        os.mkdir(destination_path)
        add_imported_modules_from_source(source_path, destination_path, modules)

        tar_path = os.path.join(tmp_dir, "tmp.tar")
        with tarfile.open(tar_path, "w") as tar:
            tmp_path: str = os.path.join(tmp_dir, "code")
            files: typing.List[str] = os.listdir(tmp_path)
            for ws_file in files:
                tar.add(os.path.join(tmp_path, ws_file), arcname=ws_file, filter=tar_strip_file_attributes)
        with gzip.GzipFile(filename=destination, mode="wb", mtime=0) as gzipped:
            with open(tar_path, "rb") as tar_file:
                gzipped.write(tar_file.read())


# Takes in a TarInfo and returns the modified TarInfo:
# https://docs.python.org/3/library/tarfile.html#tarinfo-objects
# intended to be passed as a filter to tarfile.add
# https://docs.python.org/3/library/tarfile.html#tarfile.TarFile.add
def tar_strip_file_attributes(tar_info: tarfile.TarInfo) -> tarfile.TarInfo:
    # set time to epoch timestamp 0, aka 00:00:00 UTC on 1 January 1980
    # note that when extracting this tarfile, this time will be shown as the modified date
    tar_info.mtime = datetime(1980, 1, 1, tzinfo=timezone.utc).timestamp()

    # user/group info
    tar_info.uid = 0
    tar_info.uname = ""
    tar_info.gid = 0
    tar_info.gname = ""

