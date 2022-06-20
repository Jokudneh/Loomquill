from __future__ import annotations

import gzip
import hashlib
import os
import pathlib
import posixpath
import shutil
import stat
import subprocess
import tarfile
import tempfile
import time
import typing
from dataclasses import dataclass
from typing import List, Optional, Union

import click
from rich import print as rich_print
from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
)
from rich.tree import Tree

from flytekit.constants import CopyFileDetection
from flytekit.core.context_manager import FlyteContextManager
from flytekit.core.python_auto_container import PICKLE_FILE_PATH
from flytekit.core.utils import timeit
from flytekit.exceptions.user import FlyteDataNotFoundException
from flytekit.loggers import is_display_progress_enabled, logger
from flytekit.tools.ignore import DockerIgnore, FlyteIgnore, GitIgnore, Ignore, IgnoreGroup, StandardIgnore
from flytekit.tools.script_mode import _filehash_update, _pathhash_update, ls_files, tar_strip_file_attributes

FAST_PREFIX = "fast"
FAST_FILEENDING = ".tar.gz"


@dataclass(frozen=True)
class FastPackageOptions:
    """
    FastPackageOptions is used to set configuration options when packaging files.
    """

    ignores: list[Ignore]
    keep_default_ignores: bool = True
    copy_style: Optional[CopyFileDetection] = None
    show_files: bool = False


def print_ls_tree(source: os.PathLike, ls: typing.List[str]):
    click.secho("Files to be copied for fast registration...", fg="bright_blue")

    tree_root = Tree(
        f":open_file_folder: [link file://{source}]{source} (detected source root)",
        guide_style="bold bright_blue",
    )
    trees = {pathlib.Path(source): tree_root}

    for f in ls:
        fpp = pathlib.Path(f)
        if fpp.parent not in trees:
            # add trees for all intermediate folders
            current = tree_root
            current_path = pathlib.Path(source)
            for subdir in fpp.parent.relative_to(source).parts:
                current_path = current_path / subdir
                if current_path not in trees:
                    current = current.add(f"{subdir}", guide_style="bold bright_blue")
                    trees[current_path] = current
