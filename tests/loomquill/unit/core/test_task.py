import re

import pytest

from flytekit import task, Resources
from flytekit.core.task import decorate_function
from flytekit.core.utils import str2bool
from flytekit.interactive import vscode
from flytekit.interactive.constants import FLYTE_ENABLE_VSCODE_KEY


def test_decorate_python_task(monkeypatch: pytest.MonkeyPatch):
    def t1(a: int, b: int) -> int:
        return a + b
