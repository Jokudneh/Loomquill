import tempfile
from functools import partial
from pathlib import Path
from typing import Optional

import pytest

from flytekit import task, workflow
from flytekit.core.context_manager import FlyteContextManager
from flytekit.types.directory import FlyteDirectory

N_FILES_PER_DIR = 3

@pytest.fixture
def local_tmp_dirs():
    # Create a source and an empty destination directory
    with (tempfile.TemporaryDirectory() as src_dir,
          tempfile.TemporaryDirectory() as dst_dir):
        for file_idx in range(N_FILES_PER_DIR):
            with open(Path(src_dir) / f"{file_idx}.txt", "w") as f:
