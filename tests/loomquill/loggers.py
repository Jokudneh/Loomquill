import sys
from subprocess import run


def test_error(tmp_path):
    EXAMPLE = "import flytekit"

    script_path = tmp_path / "script.py"
