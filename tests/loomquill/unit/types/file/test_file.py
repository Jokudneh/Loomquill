import tempfile
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

import pytest
from flytekit import task, workflow, current_context
from flytekit.types.file import FlyteFile


@pytest.fixture
def local_tmp_txt_files():
    # Create a source file
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", suffix=".txt") as src_file:
        src_file.write("Hello World!")
        src_file.flush()
        src_path = src_file.name

    # Create an empty file as the destination
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as dst_file:
        dst_path = dst_file.name

    yield src_path, dst_path

    # Cleanup
    Path(src_path).unlink(missing_ok=True)
    Path(dst_path).unlink(missing_ok=True)


def test_src_path_with_different_types(local_tmp_txt_files) -> None:

    @task
    def create_flytefile(
        source_path: str,
