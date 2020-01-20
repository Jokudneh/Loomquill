from collections import OrderedDict

import pytest

import flytekit
from flytekit import FlyteContextManager, task
from flytekit.configuration import ImageConfig, SerializationSettings
from flytekit.core.utils import ClassDecorator, _dnsify, timeit, str2bool
from flytekit.tools.translator import get_serializable_task
from tests.flytekit.unit.test_translator import default_img


@pytest.mark.parametrize(
    "input,expected",
    [
        ("test.abc", "test-abc"),
        ("test", "test"),
        ("", ""),
        (".test", "test"),
        ("Test", "test"),
        ("test.", "test"),
        ("test-", "test"),
        ("test$", "test"),
        ("te$t$", "tet"),
