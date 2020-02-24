import typing
from pathlib import Path

import py.path

from flytekit.core.checkpointer import SyncCheckpoint

CHECKPOINT_FILE = "cp"


def create_folder_write_file(tmpdir: py.path.local) -> typing.Tuple[py.path.local, py.path.local, py.path.local]:
    outputs = tmpdir.mkdir("outputs")

    # Make an input test directory with one file called cp
    inputs = tmpdir.mkdir("inputs")
    input_file = inputs.join(CHECKPOINT_FILE)
    input_file.write_text("Hello!", encoding="utf-8")

    return inputs, input_file, outputs

