import json
import os
import tempfile
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union

import pytest
from google.protobuf import json_format as _json_format
from google.protobuf import struct_pb2 as _struct
from mashumaro.codecs.json import JSONEncoder
from mashumaro.codecs.msgpack import MessagePackEncoder

from flytekit import task, workflow
from flytekit.core.constants import MESSAGEPACK
from flytekit.core.context_manager import FlyteContextManager
from flytekit.core.type_engine import DataclassTransformer, TypeEngine
from flytekit.models.literals import Binary, Literal, Scalar
from flytekit.types.directory import FlyteDirectory
from flytekit.types.file import FlyteFile


class Status(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


def test_simple_type_transformer():
    ctx = FlyteContextManager.current_context()

    int_inputs = [1, 2, 20240918, -1, -2, -20240918]
    encoder = MessagePackEncoder(int)
    for int_input in int_inputs:
        int_msgpack_bytes = encoder.encode(int_input)
        lv = Literal(
            scalar=Scalar(binary=Binary(value=int_msgpack_bytes, tag=MESSAGEPACK))
        )
        int_output = TypeEngine.to_python_value(ctx, lv, int)
        assert int_input == int_output

    float_inputs = [2024.0918, 5.0, -2024.0918, -5.0]
    encoder = MessagePackEncoder(float)
    for float_input in float_inputs:
        float_msgpack_bytes = encoder.encode(float_input)
        lv = Literal(
            scalar=Scalar(binary=Binary(value=float_msgpack_bytes, tag=MESSAGEPACK))
        )
        float_output = TypeEngine.to_python_value(ctx, lv, float)
        assert float_input == float_output

    bool_inputs = [True, False]
    encoder = MessagePackEncoder(bool)
    for bool_input in bool_inputs:
        bool_msgpack_bytes = encoder.encode(bool_input)
        lv = Literal(
            scalar=Scalar(binary=Binary(value=bool_msgpack_bytes, tag=MESSAGEPACK))
        )
        bool_output = TypeEngine.to_python_value(ctx, lv, bool)
        assert bool_input == bool_output

    str_inputs = ["hello", "world", "flyte", "kit", "is", "awesome"]
    encoder = MessagePackEncoder(str)
    for str_input in str_inputs:
        str_msgpack_bytes = encoder.encode(str_input)
        lv = Literal(
            scalar=Scalar(binary=Binary(value=str_msgpack_bytes, tag=MESSAGEPACK))
        )
        str_output = TypeEngine.to_python_value(ctx, lv, str)
        assert str_input == str_output

    datetime_inputs = [
        datetime.now(),
        datetime(2024, 9, 18),
        datetime(2024, 9, 18, 1),
        datetime(2024, 9, 18, 1, 1),
        datetime(2024, 9, 18, 1, 1, 1),
        datetime(2024, 9, 18, 1, 1, 1, 1),
    ]
    encoder = MessagePackEncoder(datetime)
    for datetime_input in datetime_inputs:
        datetime_msgpack_bytes = encoder.encode(datetime_input)
        lv = Literal(
            scalar=Scalar(binary=Binary(value=datetime_msgpack_bytes, tag=MESSAGEPACK))
        )
        datetime_output = TypeEngine.to_python_value(ctx, lv, datetime)
        assert datetime_input == datetime_output

    date_inputs = [date.today(), date(2024, 9, 18)]
    encoder = MessagePackEncoder(date)
    for date_input in date_inputs:
        date_msgpack_bytes = encoder.encode(date_input)
        lv = Literal(
            scalar=Scalar(binary=Binary(value=date_msgpack_bytes, tag=MESSAGEPACK))
        )
        date_output = TypeEngine.to_python_value(ctx, lv, date)
        assert date_input == date_output

    timedelta_inputs = [
        timedelta(days=1),
        timedelta(days=1, seconds=1),
        timedelta(days=1, seconds=1, microseconds=1),
        timedelta(days=1, seconds=1, microseconds=1, milliseconds=1),
        timedelta(days=1, seconds=1, microseconds=1, milliseconds=1, minutes=1),
        timedelta(
            days=1, seconds=1, microseconds=1, milliseconds=1, minutes=1, hours=1
        ),
        timedelta(
            days=1,
            seconds=1,
            microseconds=1,
            milliseconds=1,
            minutes=1,
            hours=1,
            weeks=1,
        ),
        timedelta(
            days=-1,
            seconds=-1,
            microseconds=-1,
            milliseconds=-1,
            minutes=-1,
            hours=-1,
            weeks=-1,
        ),
    ]
    encoder = MessagePackEncoder(timedelta)
    for timedelta_input in timedelta_inputs:
        timedelta_msgpack_bytes = encoder.encode(timedelta_input)
        lv = Literal(
            scalar=Scalar(binary=Binary(value=timedelta_msgpack_bytes, tag=MESSAGEPACK))
        )
        timedelta_output = TypeEngine.to_python_value(ctx, lv, timedelta)
        assert timedelta_input == timedelta_output


def test_untyped_dict():
    ctx = FlyteContextManager.current_context()

    dict_inputs = [
        # Basic key-value combinations with int, str, bool, float
        {1: "a", "key": 2.5, True: False, 3.14: 100},
        {"a": 1, -2: "b", 3.5: True, False: 3.1415},
        {
            1: [-1, "a", 2.5, False],
            "key_list": ["str", 3.14, True, 42],
            True: [False, 2.718, "test"],
        },
        {
            "nested_dict": {-1: 2, "key": "value", True: 3.14, False: "string"},
            3.14: {"pi": 3.14, "e": 2.718, 42: True},
        },
        {
            "list_in_dict": [
                {"inner_dict_1": [1, -2.5, "a"], "inner_dict_2": [True, False, 3.14]},
                [1, -2, 3, {"nested_list_dict": [False, "test"]}],
            ]
        },
        {
            "complex_nested": {
                1: {"nested_dict": {True: [-1, "a", 2.5]}},
                "string_key": {False: {-3.14: {"deep": [1, "deep_value"]}}},
            }
        },
        {
            "list_of_dicts": [{"a": 1, "b": -2}, {"key1": "value1", "key2": "value2"}],
            10: [{"nested_list": [-1, "value", 3.14]}, {"another_list": [True, False]}],
        },
        # More nested combinations of list and dict
        {
            "outer_list": [
                [1, -2, 3],
                {
                    "inner_dict": {"key1": [True, "string", -3.14], "key2": [1, -2.5]}
                },  # Dict inside list
            ],
            "another_dict": {
                "key1": {"subkey": [1, -2, "str"]},
                "key2": [False, -3.14, "test"],
            },
        },
    ]

    for dict_input in dict_inputs:
        # dict_msgpack_bytes = msgpack.dumps(dict_input)
        dict_msgpack_bytes = MessagePackEncoder(dict).encode(dict_input)
        lv = Literal(
            scalar=Scalar(binary=Binary(value=dict_msgpack_bytes, tag=MESSAGEPACK))
        )
        dict_output = TypeEngine.to_python_value(ctx, lv, dict)
        assert dict_input == dict_output


def test_list_transformer():
    ctx = FlyteContextManager.current_context()

    list_int_input = [1, -2, 3]
    encoder = MessagePackEncoder(List[int])
    list_int_msgpack_bytes = encoder.encode(list_int_input)
    lv = Literal(
        scalar=Scalar(binary=Binary(value=list_int_msgpack_bytes, tag=MESSAGEPACK))
    )
    list_int_output = TypeEngine.to_python_value(ctx, lv, List[int])
    assert list_int_input == list_int_output

    list_float_input = [1.0, -2.0, 3.0]
    encoder = MessagePackEncoder(List[float])
    list_float_msgpack_bytes = encoder.encode(list_float_input)
    lv = Literal(
        scalar=Scalar(binary=Binary(value=list_float_msgpack_bytes, tag=MESSAGEPACK))
    )
    list_float_output = TypeEngine.to_python_value(ctx, lv, List[float])
    assert list_float_input == list_float_output

    list_str_input = ["a", "b", "c"]
    encoder = MessagePackEncoder(List[str])
    list_str_msgpack_bytes = encoder.encode(list_str_input)
    lv = Literal(
        scalar=Scalar(binary=Binary(value=list_str_msgpack_bytes, tag=MESSAGEPACK))
    )
    list_str_output = TypeEngine.to_python_value(ctx, lv, List[str])
    assert list_str_input == list_str_output

    list_bool_input = [True, False, True]
    encoder = MessagePackEncoder(List[bool])
    list_bool_msgpack_bytes = encoder.encode(list_bool_input)
    lv = Literal(
        scalar=Scalar(binary=Binary(value=list_bool_msgpack_bytes, tag=MESSAGEPACK))
    )
    list_bool_output = TypeEngine.to_python_value(ctx, lv, List[bool])
    assert list_bool_input == list_bool_output

    list_list_int_input = [[1, -2], [-3, 4]]
    encoder = MessagePackEncoder(List[List[int]])
    list_list_int_msgpack_bytes = encoder.encode(list_list_int_input)
    lv = Literal(
        scalar=Scalar(binary=Binary(value=list_list_int_msgpack_bytes, tag=MESSAGEPACK))
    )
    list_list_int_output = TypeEngine.to_python_value(ctx, lv, List[List[int]])
    assert list_list_int_input == list_list_int_output

    list_list_float_input = [[1.0, -2.0], [-3.0, 4.0]]
    encoder = MessagePackEncoder(List[List[float]])
    list_list_float_msgpack_bytes = encoder.encode(list_list_float_input)
    lv = Literal(
        scalar=Scalar(
            binary=Binary(value=list_list_float_msgpack_bytes, tag=MESSAGEPACK)
        )
    )
    list_list_float_output = TypeEngine.to_python_value(ctx, lv, List[List[float]])
    assert list_list_float_input == list_list_float_output

    list_list_str_input = [["a", "b"], ["c", "d"]]
    encoder = MessagePackEncoder(List[List[str]])
    list_list_str_msgpack_bytes = encoder.encode(list_list_str_input)
    lv = Literal(
        scalar=Scalar(binary=Binary(value=list_list_str_msgpack_bytes, tag=MESSAGEPACK))
    )
    list_list_str_output = TypeEngine.to_python_value(ctx, lv, List[List[str]])
    assert list_list_str_input == list_list_str_output

    list_list_bool_input = [[True, False], [False, True]]
    encoder = MessagePackEncoder(List[List[bool]])
    list_list_bool_msgpack_bytes = encoder.encode(list_list_bool_input)
    lv = Literal(
        scalar=Scalar(
            binary=Binary(value=list_list_bool_msgpack_bytes, tag=MESSAGEPACK)
        )
    )
    list_list_bool_output = TypeEngine.to_python_value(ctx, lv, List[List[bool]])
    assert list_list_bool_input == list_list_bool_output

    list_dict_str_int_input = [{"key1": -1, "key2": 2}]
    encoder = MessagePackEncoder(List[Dict[str, int]])
    list_dict_str_int_msgpack_bytes = encoder.encode(list_dict_str_int_input)
    lv = Literal(
        scalar=Scalar(
            binary=Binary(value=list_dict_str_int_msgpack_bytes, tag=MESSAGEPACK)
        )
    )
    list_dict_str_int_output = TypeEngine.to_python_value(ctx, lv, List[Dict[str, int]])
    assert list_dict_str_int_input == list_dict_str_int_output

    list_dict_str_float_input = [{"key1": 1.0, "key2": -2.0}]
    encoder = MessagePackEncoder(List[Dict[str, float]])
    list_dict_str_float_msgpack_bytes = encoder.encode(list_dict_str_float_input)
    lv = Literal(
        scalar=Scalar(
            binary=Binary(value=list_dict_str_float_msgpack_bytes, tag=MESSAGEPACK)
        )
    )
    list_dict_str_float_output = TypeEngine.to_python_value(
        ctx, lv, List[Dict[str, float]]
    )
    assert list_dict_str_float_input == list_dict_str_float_output

    list_dict_str_str_input = [{"key1": "a", "key2": "b"}]
    encoder = MessagePackEncoder(List[Dict[str, str]])
    list_dict_str_str_msgpack_bytes = encoder.encode(list_dict_str_str_input)
    lv = Literal(
        scalar=Scalar(
            binary=Binary(value=list_dict_str_str_msgpack_bytes, tag=MESSAGEPACK)
        )
    )
    list_dict_str_str_output = TypeEngine.to_python_value(ctx, lv, List[Dict[str, str]])
    assert list_dict_str_str_input == list_dict_str_str_output

    list_dict_str_bool_input = [{"key1": True, "key2": False}]
    encoder = MessagePackEncoder(List[Dict[str, bool]])
    list_dict_str_bool_msgpack_bytes = encoder.encode(list_dict_str_bool_input)
    lv = Literal(
        scalar=Scalar(
            binary=Binary(value=list_dict_str_bool_msgpack_bytes, tag=MESSAGEPACK)
        )
    )
    list_dict_str_bool_output = TypeEngine.to_python_value(
        ctx, lv, List[Dict[str, bool]]
    )
    assert list_dict_str_bool_input == list_dict_str_bool_output

    @dataclass
    class InnerDC:
        a: int = -1
        b: float = 2.1
        c: str = "Hello, Flyte"
        d: bool = False
        e: List[int] = field(default_factory=lambda: [0, 1, 2, -1, -2])
        f: List[List[int]] = field(default_factory=lambda: [[0], [1], [-1]])
        g: List[Dict[int, bool]] = field(
            default_factory=lambda: [{0: False}, {1: True}, {-1: True}]
        )
        h: Dict[int, bool] = field(
            default_factory=lambda: {0: False, 1: True, -1: False}
        )
        i: Dict[int, List[int]] = field(default_factory=lambda: {0: [0, 1, -1]})
        j: Dict[int, Dict[int, int]] = field(default_factory=lambda: {1: {-1: 0}})
        k: dict = field(default_factory=lambda: {"key": "value"})
        enum_status: Status = field(default=Status.PENDING)

    @dataclass
    class DC:
        a: int = -1
        b: float = 2.1
        c: str = "Hello, Flyte"
        d: bool = False
        e: List[int] = field(default_factory=lambda: [0, 1, 2, -1, -2])
        f: List[List[int]] = field(default_factory=lambda: [[0], [1], [-1]])
        g: List[Dict[int, bool]] = field(
            default_factory=lambda: [{0: False}, {1: True}, {-1: True}]
        )
        h: Dict[int, bool] = field(
            default_factory=lambda: {0: False, 1: True, -1: False}
        )
        i: Dict[int, List[int]] = field(default_factory=lambda: {0: [0, 1, -1]})
        j: Dict[int, Dict[int, int]] = field(default_factory=lambda: {1: {-1: 0}})
        k: dict = field(default_factory=lambda: {"key": "value"})
        inner_dc: InnerDC = field(default_factory=lambda: InnerDC())
        enum_status: Status = field(default=Status.PENDING)

    list_dict_int_inner_dc_input = [{1: InnerDC(), -1: InnerDC(), 0: InnerDC()}]
    encoder = MessagePackEncoder(List[Dict[int, InnerDC]])
    list_dict_int_inner_dc_msgpack_bytes = encoder.encode(list_dict_int_inner_dc_input)
    lv = Literal(
        scalar=Scalar(
            binary=Binary(value=list_dict_int_inner_dc_msgpack_bytes, tag=MESSAGEPACK)
        )
    )
    list_dict_int_inner_dc_output = TypeEngine.to_python_value(
        ctx, lv, List[Dict[int, InnerDC]]
    )
    assert list_dict_int_inner_dc_input == list_dict_int_inner_dc_output

    list_dict_int_dc_input = [{1: DC(), -1: DC(), 0: DC()}]
    encoder = MessagePackEncoder(List[Dict[int, DC]])
    list_dict_int_dc_msgpack_bytes = encoder.encode(list_dict_int_dc_input)
    lv = Literal(
        scalar=Scalar(
            binary=Binary(value=list_dict_int_dc_msgpack_bytes, tag=MESSAGEPACK)
        )
    )
    list_dict_int_dc_output = TypeEngine.to_python_value(ctx, lv, List[Dict[int, DC]])
    assert list_dict_int_dc_input == list_dict_int_dc_output

    list_list_inner_dc_input = [[InnerDC(), InnerDC(), InnerDC()]]
    encoder = MessagePackEncoder(List[List[InnerDC]])
    list_list_inner_dc_msgpack_bytes = encoder.encode(list_list_inner_dc_input)
    lv = Literal(
        scalar=Scalar(
            binary=Binary(value=list_list_inner_dc_msgpack_bytes, tag=MESSAGEPACK)
        )
    )
    list_list_inner_dc_output = TypeEngine.to_python_value(ctx, lv, List[List[InnerDC]])
