import os
import socket
import subprocess
import sys
import tarfile
import tempfile
import time
from hashlib import md5
from pathlib import Path

import pytest

from flytekit.constants import CopyFileDetection
from flytekit.tools.fast_registration import (
    FAST_FILEENDING,
    FAST_PREFIX,
    FastPackageOptions,
    compute_digest,
    fast_package,
    get_additional_distribution_loc,
)
from flytekit.tools.ignore import DockerIgnore, GitIgnore, Ignore, IgnoreGroup, StandardIgnore
from tests.flytekit.unit.tools.test_ignore import make_tree


@pytest.fixture
def flyte_project(tmp_path):
    tree = {
        "data": {"large.file": "", "more.files": ""},
        "src": {
            "workflows": {
                "__pycache__": {"some.pyc": ""},
                "hello_world.py": "print('Hello World!')",
            },
        },
        "utils": {
            "util.py": "print('Hello from utils!')",
        },
        ".venv": {"lots": "", "of": "", "packages": ""},
        ".env": "supersecret",
        "some.bar": "",
        "some.foo": "",
        "keep.foo": "",
        ".gitignore": "\n".join([".env", ".venv", "# A comment", "data", "*.foo", "!keep.foo"]),
        ".dockerignore": "\n".join(["data", "*.bar", ".git"]),
    }

    make_tree(tmp_path, tree)
    os.symlink(str(tmp_path) + "/utils/util.py", str(tmp_path) + "/src/util")
    subprocess.run(["git", "init", str(tmp_path)])
    return tmp_path


