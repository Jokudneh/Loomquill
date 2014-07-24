import os
from dataclasses import field
import json
import sys
import tempfile
import typing
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

import click
import mock
import pytest
import yaml

from flytekit import FlyteContextManager
from flytekit.core.artifact import Artifact
from flytekit.core.resources import ResourceSpec, Resources
from flytekit.core.type_engine import TypeEngine
from flytekit.interaction.click_types import (
    DateTimeType,
    DirParamType,
    DurationParamType,
    EnumParamType,
    FileParamType,
    FlyteLiteralConverter,
    JsonParamType,
    PickleParamType,
    StructuredDatasetParamType,
    UnionParamType,
    key_value_callback,
    resource_callback,
)

dummy_param = click.Option(["--dummy"], type=click.STRING, default="dummy")

def test_dir_param():
    import os
    m = mock.MagicMock()
    current_file_directory = os.path.dirname(os.path.abspath(__file__))
    l = DirParamType().convert(current_file_directory, m, m)
    assert l.path == current_file_directory
    r = DirParamType().convert("https://tmp/dir", m, m)
    assert r.path == "https://tmp/dir"

def test_file_param():
    m = mock.MagicMock()
    l = FileParamType().convert(__file__, m, m)
    assert l.path == __file__
    r = FileParamType().convert("https://tmp/file", m, m)
    assert r.path == "https://tmp/file"


class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


@pytest.mark.parametrize(
    "python_type, python_value",
    [
        (typing.Union[typing.List[int], str, Color], "flyte"),
        (typing.Union[typing.List[int], str, Color], "red"),
        (typing.Union[typing.List[int], str, Color], [1, 2, 3]),
        (typing.List[int], [1, 2, 3]),
        (typing.Dict[str, int], {"flyte": 2}),
    ],
)
def test_literal_converter(python_type, python_value):
    ctx = FlyteContextManager.current_context()
    lt = TypeEngine.to_literal_type(python_type)

    lc = FlyteLiteralConverter(
        ctx,
        literal_type=lt,
        python_type=python_type,
        is_remote=True,
    )

    click_ctx = click.Context(click.Command("test_command"), obj={"remote": True})
    assert lc.convert(click_ctx, dummy_param, python_value) == TypeEngine.to_literal(ctx, python_value, python_type, lt)


def test_literal_converter_query():
    ctx = FlyteContextManager.current_context()
    lt = TypeEngine.to_literal_type(int)

    lc = FlyteLiteralConverter(
        ctx,
        literal_type=lt,
        python_type=int,
        is_remote=True,
    )

    a = Artifact(name="test-artifact")
