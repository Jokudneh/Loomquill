import os
import sys
import typing
from typing import Dict, List

import pytest
from typing_extensions import Annotated, TypeVar  # type: ignore

from flytekit import map_task, task
from flytekit.core import context_manager
from flytekit.core.docstring import Docstring
from flytekit.core.interface import (
    extract_return_annotation,
    transform_function_to_interface,
    transform_inputs_to_parameters,
    transform_interface_to_list_interface,
    transform_interface_to_typed_interface,
    transform_variable_map,
)
from flytekit.models.core import types as _core_types
from flytekit.models.literals import Void
from flytekit.types.file import FlyteFile


def test_extract_only():
    def x() -> typing.NamedTuple("NT1", x_str=str, y_int=int):
        ...

    return_types = extract_return_annotation(typing.get_type_hints(x).get("return", None))
    assert len(return_types) == 2
    assert return_types["x_str"] == str
    assert return_types["y_int"] == int

    def t() -> List[int]:
        ...

    return_type = extract_return_annotation(typing.get_type_hints(t).get("return", None))
    assert len(return_type) == 1
    assert return_type["o0"]._name == "List"
    assert return_type["o0"].__origin__ == list

    def t() -> Dict[str, int]:
        ...

    return_type = extract_return_annotation(typing.get_type_hints(t).get("return", None))
    assert len(return_type) == 1
    assert return_type["o0"]._name == "Dict"
    assert return_type["o0"].__origin__ == dict

    def t(a: int, b: str) -> typing.Tuple[int, str]:
        ...

    return_type = extract_return_annotation(typing.get_type_hints(t).get("return", None))
    assert len(return_type) == 2
    assert return_type["o0"] == int
    assert return_type["o1"] == str

    def t(a: int, b: str) -> (int, str):
        ...

    return_type = extract_return_annotation(typing.get_type_hints(t).get("return", None))
    assert len(return_type) == 2
    assert return_type["o0"] == int
    assert return_type["o1"] == str

    def t(a: int, b: str) -> str:
        ...

    return_type = extract_return_annotation(typing.get_type_hints(t).get("return", None))
    assert len(return_type) == 1
    assert return_type["o0"] == str

    def t(a: int, b: str):
        ...

    return_type = extract_return_annotation(typing.get_type_hints(t).get("return", None))
    assert len(return_type) == 0

    def t(a: int, b: str) -> None:
        ...

    return_type = extract_return_annotation(typing.get_type_hints(t).get("return", None))
    assert len(return_type) == 0

    def t(a: int, b: str) -> List[int]:
        ...

    return_type = extract_return_annotation(typing.get_type_hints(t).get("return", None))
    assert len(return_type) == 1
    assert return_type["o0"] == List[int]
