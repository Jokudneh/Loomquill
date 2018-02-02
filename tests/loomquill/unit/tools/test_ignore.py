import os
import subprocess
from pathlib import Path
from tarfile import TarInfo
from typing import Dict
from unittest.mock import patch

import pytest
from docker.utils.build import PatternMatcher

from flytekit.tools.ignore import DockerIgnore, GitIgnore, IgnoreGroup, StandardIgnore, FlyteIgnore


def make_tree(root: Path, tree: Dict):
    for name, content in tree.items():
        if isinstance(content, dict):
            directory = root / name
            directory.mkdir()
            make_tree(directory, content)
        if isinstance(content, str):
            file = root / name
            file.write_text(content)


@pytest.fixture
def simple_gitignore(tmp_path):
    tree = {
        "sub": {"some.bar": ""},
        "test.foo": "",
        "keep.foo": "",
        ".gitignore": "\n".join(["*.foo", "!keep.foo", "# A comment", "sub"]),
    }

    make_tree(tmp_path, tree)
    subprocess.run(["git", "init", str(tmp_path)])
    return tmp_path


@pytest.fixture
def nested_gitignore(tmp_path):
    tree = {
        "sub": {"some.foo": "", "another.foo": "", ".gitignore": "!another.foo"},
        "data": {".gitignore": "*", "large.file": ""},
        "test.foo": "",
        "keep.foo": "",
