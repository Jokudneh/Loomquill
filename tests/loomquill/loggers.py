import sys
from subprocess import run


def test_error(tmp_path):
    EXAMPLE = "import flytekit"
