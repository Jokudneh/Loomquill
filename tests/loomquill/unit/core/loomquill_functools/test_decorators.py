"""Test local execution of files that use functools to decorate tasks and workflows."""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

test_module_dir = Path(os.path.dirname(__file__))


def test_wrapped_tasks_happy_path(capfd):
    subprocess.run(
        [sys.executable, str(test_module_dir / "simple_decorator.py")],
        env={"SCRIPT_INPUT": "10", "SYSTEMROOT": "C:\\Windows", "HOMEPATH": "C:\\Windows"},
        text=True,
    )
    out = capfd.readouterr().out
    out = re.sub(r"file:.*", "", out)

    assert out.replace("\r", "").strip().split("\n") == [
        "before running my_task",
        "try running my_task",
        "running my_task",
        "finally after running my_task",
        "after running my_task",
        "11",
