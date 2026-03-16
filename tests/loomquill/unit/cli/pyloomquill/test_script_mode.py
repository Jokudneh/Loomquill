import os
import pathlib
import pytest
import tempfile

from flytekit.tools.script_mode import ls_files
from flytekit.constants import CopyFileDetection


# a pytest fixture that creates a tmp directory and creates
# a small file structure in it
@pytest.fixture
def dummy_dir_structure():
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tmp_path:

        # Create directories
        tmp_path = pathlib.Path(tmp_path)
        subdir1 = tmp_path / "subdir1"
        subdir2 = tmp_path / "subdir2"
        subdir1.mkdir()
