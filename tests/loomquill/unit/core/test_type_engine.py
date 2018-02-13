import dataclasses
import datetime
import json
import os
import re
import sys
import tempfile
import typing
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from datetime import timedelta
from enum import Enum, auto
from typing import Dict, List, Optional, Type

import mock
import msgpack
import pytest
import typing_extensions
from dataclasses_json import DataClassJsonMixin, dataclass_json
from flyteidl.core import errors_pb2
from google.protobuf import json_format as _json_format
from google.protobuf import struct_pb2 as _struct
from marshmallow_jsonschema import JSONSchema
from mashumaro.config import BaseConfig
from mashumaro.mixins.json import DataClassJSONMixin
from mashumaro.mixins.orjson import DataClassORJSONMixin
from mashumaro.types import Discriminator
from typing_extensions import Annotated, get_args

from flytekit import dynamic, kwtypes, task, workflow
from flytekit.core.annotation import FlyteAnnotation
from flytekit.core.context_manager import FlyteContext, FlyteContextManager
from flytekit.core.data_persistence import flyte_tmp_dir
from flytekit.core.hash import HashMethod
from flytekit.core.type_engine import (
    BoolTransformer,
    DataclassTransformer,
    DictTransformer,
    EnumTransformer,
    FloatTransformer,
    IntTransformer,
    ListTransformer,
    LiteralsResolver,
    SimpleTransformer,
    StrTransformer,
    TypeEngine,
    TypeTransformer,
    TypeTransformerFailedError,
    UnionTransformer,
    convert_marshmallow_json_schema_to_python_class,
    convert_mashumaro_json_schema_to_python_class,
    dataclass_from_dict,
    get_underlying_type,
    is_annotated,
    strict_type_hint_matching,
)
from flytekit.exceptions import user as user_exceptions
from flytekit.models import types as model_types
from flytekit.models.annotation import TypeAnnotation
from flytekit.models.core.types import BlobType
from flytekit.models.literals import (
    Blob,
    BlobMetadata,
    Literal,
    LiteralCollection,
    LiteralMap,
    LiteralOffloadedMetadata,
    Primitive,
    Scalar,
    Void,
)
from flytekit.models.types import LiteralType, SimpleType, TypeStructure, UnionType
from flytekit.types.directory import TensorboardLogs
from flytekit.types.directory.types import (
    FlyteDirectory,
    FlyteDirToMultipartBlobTransformer,
)
from flytekit.types.file import FileExt, JPEGImageFile
from flytekit.types.file.file import FlyteFile, FlyteFilePathTransformer, noop
from flytekit.types.iterator.iterator import IteratorTransformer
from flytekit.types.iterator.json_iterator import JSON, JSONIterator, JSONIteratorTransformer
from flytekit.types.pickle import FlytePickle
from flytekit.types.pickle.pickle import FlytePickleTransformer
from flytekit.types.schema import FlyteSchema
from flytekit.types.structured.structured_dataset import StructuredDataset, StructuredDatasetTransformerEngine

T = typing.TypeVar("T")


def test_type_engine():
    t = int
    lt = TypeEngine.to_literal_type(t)
    assert lt.simple == model_types.SimpleType.INTEGER

    t = typing.Dict[str, typing.List[typing.Dict[str, timedelta]]]
    lt = TypeEngine.to_literal_type(t)
    assert lt.map_value_type.collection_type.map_value_type.simple == model_types.SimpleType.DURATION


def test_named_tuple():
    t = typing.NamedTuple("Outputs", [("x_str", str), ("y_int", int)])
    var_map = TypeEngine.named_tuple_to_variable_map(t)
    assert var_map.variables["x_str"].type.simple == model_types.SimpleType.STRING
    assert var_map.variables["y_int"].type.simple == model_types.SimpleType.INTEGER


def test_type_resolution():
    assert type(TypeEngine.get_transformer(typing.List[int])) == ListTransformer
    assert type(TypeEngine.get_transformer(typing.List)) == ListTransformer
    assert type(TypeEngine.get_transformer(list)) == ListTransformer

    assert type(TypeEngine.get_transformer(typing.Dict[str, int])) == DictTransformer
    assert type(TypeEngine.get_transformer(typing.Dict)) == DictTransformer
    assert type(TypeEngine.get_transformer(dict)) == DictTransformer
    assert type(TypeEngine.get_transformer(Annotated[dict, kwtypes(allow_pickle=True)])) == DictTransformer

    assert type(TypeEngine.get_transformer(int)) == SimpleTransformer
    assert type(TypeEngine.get_transformer(datetime.date)) == SimpleTransformer

    assert type(TypeEngine.get_transformer(os.PathLike)) == FlyteFilePathTransformer
    assert type(TypeEngine.get_transformer(FlytePickle)) == FlytePickleTransformer
    assert type(TypeEngine.get_transformer(typing.Any)) == FlytePickleTransformer


def test_file_formats_getting_literal_type():
    transformer = TypeEngine.get_transformer(FlyteFile)

    lt = transformer.get_literal_type(FlyteFile)
    assert lt.blob.format == ""

    # Works with formats that we define
    lt = transformer.get_literal_type(FlyteFile["txt"])
    assert lt.blob.format == "txt"

    lt = transformer.get_literal_type(FlyteFile[typing.TypeVar("jpg")])
    assert lt.blob.format == "jpg"

    # Empty default to the default
    lt = transformer.get_literal_type(FlyteFile)
    assert lt.blob.format == ""

    lt = transformer.get_literal_type(FlyteFile[typing.TypeVar(".png")])
    assert lt.blob.format == "png"


def test_file_format_getting_python_value():
    transformer = TypeEngine.get_transformer(FlyteFile)

    ctx = FlyteContext.current_context()

    temp_dir = tempfile.mkdtemp(prefix="temp_example_")
    file_path = os.path.join(temp_dir, "file.txt")
    with open(file_path, "w") as file1:
        file1.write("hello world")
    lv = Literal(
        scalar=Scalar(
            blob=Blob(
                metadata=BlobMetadata(type=BlobType(format="txt", dimensionality=0)),
                uri=file_path,
            )
        )
    )

    pv = transformer.to_python_value(ctx, lv, expected_python_type=FlyteFile["txt"])
    assert isinstance(pv, FlyteFile)
    assert pv.extension() == "txt"


def test_list_of_dict_getting_python_value():
    transformer = TypeEngine.get_transformer(typing.List)
    ctx = FlyteContext.current_context()
    lv = Literal(
        collection=LiteralCollection(
            literals=[Literal(map=LiteralMap({"foo": Literal(scalar=Scalar(primitive=Primitive(integer=1)))}))]
        )
    )

    pv = transformer.to_python_value(ctx, lv, expected_python_type=typing.List[typing.Dict[str, int]])
    assert isinstance(pv, list)


def test_list_of_single_dataclass():
    @dataclass
    class Bar(DataClassJsonMixin):
        v: typing.Optional[typing.List[int]]
        w: typing.Optional[typing.List[float]]

    @dataclass
    class Foo(DataClassJsonMixin):
        a: typing.Optional[typing.List[str]]
        b: Bar

    foo = Foo(a=["abc", "def"], b=Bar(v=[1, 2, 99], w=[3.1415, 2.7182]))
    generic = _json_format.Parse(typing.cast(DataClassJsonMixin, foo).to_json(), _struct.Struct())
    lv = Literal(collection=LiteralCollection(literals=[Literal(scalar=Scalar(generic=generic))]))

    transformer = TypeEngine.get_transformer(typing.List)
    ctx = FlyteContext.current_context()

    pv = transformer.to_python_value(ctx, lv, expected_python_type=typing.List[Foo])
    assert pv[0].a == ["abc", "def"]
    assert pv[0].b == Bar(v=[1, 2, 99], w=[3.1415, 2.7182])


@dataclass
class Bar(DataClassJSONMixin):
    v: typing.Optional[typing.List[int]]
    w: typing.Optional[typing.List[float]]


@dataclass
class Foo(DataClassJSONMixin):
    a: typing.Optional[typing.List[str]]
    b: Bar


def test_list_of_single_dataclassjsonmixin():
    foo = Foo(a=["abc", "def"], b=Bar(v=[1, 2, 99], w=[3.1415, 2.7182]))
    generic = _json_format.Parse(typing.cast(DataClassJSONMixin, foo).to_json(), _struct.Struct())
    lv = Literal(collection=LiteralCollection(literals=[Literal(scalar=Scalar(generic=generic))]))

    transformer = TypeEngine.get_transformer(typing.List)
    ctx = FlyteContext.current_context()

    pv = transformer.to_python_value(ctx, lv, expected_python_type=typing.List[Foo])
    assert pv[0].a == ["abc", "def"]
    assert pv[0].b == Bar(v=[1, 2, 99], w=[3.1415, 2.7182])


def test_annotated_type():
    class JsonTypeTransformer(TypeTransformer[T]):
        LiteralType = LiteralType(
            simple=SimpleType.STRING,
            annotation=TypeAnnotation(annotations=dict(protocol="json")),
        )

        def get_literal_type(self, t: Type[T]) -> LiteralType:
            return self.LiteralType

        def to_python_value(self, ctx: FlyteContext, lv: Literal, expected_python_type: Type[T]) -> Optional[T]:
            return json.loads(lv.scalar.primitive.string_value)

        def to_literal(
                self,
                ctx: FlyteContext,
                python_val: T,
                python_type: typing.Type[T],
                expected: LiteralType,
        ) -> Literal:
            return Literal(scalar=Scalar(primitive=Primitive(string_value=json.dumps(python_val))))

    class JSONSerialized:
        def __class_getitem__(cls, item: Type[T]):
            return Annotated[item, JsonTypeTransformer(name=f"json[{item}]", t=item)]

    MyJsonDict = JSONSerialized[typing.Dict[str, int]]
    _, test_transformer = get_args(MyJsonDict)

    assert TypeEngine.get_transformer(MyJsonDict) is test_transformer
    assert TypeEngine.to_literal_type(MyJsonDict) == JsonTypeTransformer.LiteralType

    test_dict = {"foo": 1}
    test_literal = Literal(scalar=Scalar(primitive=Primitive(string_value=json.dumps(test_dict))))

    assert (
            TypeEngine.to_python_value(
                FlyteContext.current_context(),
                test_literal,
                MyJsonDict,
            )
            == test_dict
    )

    assert (
            TypeEngine.to_literal(
                FlyteContext.current_context(),
                test_dict,
                MyJsonDict,
                JsonTypeTransformer.LiteralType,
            )
            == test_literal
    )


def test_list_of_dataclass_getting_python_value():
    @dataclass
    class Bar(DataClassJsonMixin):
        v: typing.Union[int, None]
        w: typing.Optional[str]
        x: float
        y: str
        z: typing.Dict[str, bool]

    @dataclass
    class Foo(DataClassJsonMixin):
        u: typing.Optional[int]
        v: typing.Optional[int]
        w: int
        x: typing.List[int]
        y: typing.Dict[str, str]
        z: Bar

    foo = Foo(
        u=5,
        v=None,
        w=1,
        x=[1],
        y={"hello": "10"},
        z=Bar(v=3, w=None, x=1.0, y="hello", z={"world": False}),
    )
    generic = _json_format.Parse(typing.cast(DataClassJsonMixin, foo).to_json(), _struct.Struct())
    lv = Literal(collection=LiteralCollection(literals=[Literal(scalar=Scalar(generic=generic))]))

    transformer = TypeEngine.get_transformer(typing.List)
    ctx = FlyteContext.current_context()

    schema = JSONSchema().dump(typing.cast(DataClassJsonMixin, Foo).schema())
    foo_class = convert_marshmallow_json_schema_to_python_class(schema["definitions"], "FooSchema")

    guessed_pv = transformer.to_python_value(ctx, lv, expected_python_type=typing.List[foo_class])
    pv = transformer.to_python_value(ctx, lv, expected_python_type=typing.List[Foo])
    assert isinstance(guessed_pv, list)
    assert guessed_pv[0].u == pv[0].u
    assert guessed_pv[0].v == pv[0].v
    assert guessed_pv[0].w == pv[0].w
    assert guessed_pv[0].x == pv[0].x
    assert guessed_pv[0].y == pv[0].y
    assert guessed_pv[0].z.x == pv[0].z.x
    assert type(guessed_pv[0].u) == int
    assert guessed_pv[0].v is None
    assert type(guessed_pv[0].w) == int
    assert type(guessed_pv[0].z.v) == int
    assert type(guessed_pv[0].z.x) == float
    assert guessed_pv[0].z.v == pv[0].z.v
    assert guessed_pv[0].z.y == pv[0].z.y
    assert guessed_pv[0].z.z == pv[0].z.z
    assert pv[0] == dataclass_from_dict(Foo, asdict(guessed_pv[0]))
    assert dataclasses.is_dataclass(foo_class)


@dataclass
class Bar_getting_python_value(DataClassJSONMixin):
    v: typing.Union[int, None]
    w: typing.Optional[str]
    x: float
    y: str
    z: typing.Dict[str, bool]


@dataclass
class Foo_getting_python_value(DataClassJSONMixin):
    u: typing.Optional[int]
    v: typing.Optional[int]
    w: int
    x: typing.List[int]
    y: typing.Dict[str, str]
    z: Bar_getting_python_value


def test_list_of_dataclassjsonmixin_getting_python_value():
    foo = Foo_getting_python_value(
        u=5,
        v=None,
        w=1,
        x=[1],
        y={"hello": "10"},
        z=Bar_getting_python_value(v=3, w=None, x=1.0, y="hello", z={"world": False}),
    )
    generic = _json_format.Parse(typing.cast(DataClassJSONMixin, foo).to_json(), _struct.Struct())
    lv = Literal(collection=LiteralCollection(literals=[Literal(scalar=Scalar(generic=generic))]))

    transformer = TypeEngine.get_transformer(typing.List)
    ctx = FlyteContext.current_context()

    from mashumaro.jsonschema import build_json_schema

    schema = build_json_schema(typing.cast(DataClassJSONMixin, Foo_getting_python_value)).to_dict()
    foo_class = convert_mashumaro_json_schema_to_python_class(schema, "FooSchema")

    guessed_pv = transformer.to_python_value(ctx, lv, expected_python_type=typing.List[foo_class])
    pv = transformer.to_python_value(ctx, lv, expected_python_type=typing.List[Foo_getting_python_value])
    assert isinstance(guessed_pv, list)
    assert guessed_pv[0].u == pv[0].u
    assert guessed_pv[0].v == pv[0].v
    assert guessed_pv[0].w == pv[0].w
    assert guessed_pv[0].x == pv[0].x
    assert guessed_pv[0].y == pv[0].y
    assert guessed_pv[0].z.x == pv[0].z.x
    assert type(guessed_pv[0].u) == int
    assert guessed_pv[0].v is None
    assert type(guessed_pv[0].w) == int
    assert type(guessed_pv[0].z.v) == int
    assert type(guessed_pv[0].z.x) == float
    assert guessed_pv[0].z.v == pv[0].z.v
    assert guessed_pv[0].z.y == pv[0].z.y
    assert guessed_pv[0].z.z == pv[0].z.z
    assert pv[0] == dataclass_from_dict(Foo_getting_python_value, asdict(guessed_pv[0]))
    assert dataclasses.is_dataclass(foo_class)


def test_file_no_downloader_default():
    # The idea of this test is to assert that if a FlyteFile is created with no download specified,
    # then it should return the set path itself. This matches if we use open method
    transformer = TypeEngine.get_transformer(FlyteFile)

    ctx = FlyteContext.current_context()
    temp_dir = tempfile.mkdtemp(prefix="temp_example_")
    local_file = os.path.join(temp_dir, "file.txt")
    with open(local_file, "w") as file:
        file.write("hello world")

    lv = Literal(
        scalar=Scalar(
            blob=Blob(
                metadata=BlobMetadata(type=BlobType(format="", dimensionality=0)),
                uri=local_file,
            )
        )
    )

    pv = transformer.to_python_value(ctx, lv, expected_python_type=FlyteFile)
    assert isinstance(pv, FlyteFile)
    assert pv.download() == local_file


def test_dir_no_downloader_default():
    # The idea of this test is to assert that if a FlyteFile is created with no download specified,
    # then it should return the set path itself. This matches if we use open method
    transformer = TypeEngine.get_transformer(FlyteDirectory)

    ctx = FlyteContext.current_context()

    local_dir = tempfile.mkdtemp(prefix="temp_example_")

    lv = Literal(
        scalar=Scalar(
            blob=Blob(
                metadata=BlobMetadata(type=BlobType(format="", dimensionality=1)),
                uri=local_dir,
            )
        )
    )

    pv = transformer.to_python_value(ctx, lv, expected_python_type=FlyteDirectory)
    assert isinstance(pv, FlyteDirectory)
    assert pv.download() == local_dir


def test_dict_transformer():
    d = DictTransformer()

    def assert_struct(lit: LiteralType):
        assert lit is not None
        assert lit.simple == SimpleType.STRUCT

    def recursive_assert(
            lit: LiteralType,
            expected: LiteralType,
            expected_depth: int = 1,
            curr_depth: int = 0,
    ):
        assert curr_depth <= expected_depth
        assert lit is not None
        if lit.map_value_type is None:
            assert lit == expected
            return
        recursive_assert(lit.map_value_type, expected, expected_depth, curr_depth + 1)

    # Type inference
    assert_struct(d.get_literal_type(dict))
    assert_struct(d.get_literal_type(Annotated[dict, kwtypes(allow_pickle=True)]))
    assert_struct(d.get_literal_type(typing.Dict[int, int]))
    recursive_assert(d.get_literal_type(typing.Dict[str, str]), LiteralType(simple=SimpleType.STRING))
    recursive_assert(
        d.get_literal_type(typing.Dict[str, int]),
        LiteralType(simple=SimpleType.INTEGER),
    )
    recursive_assert(
        d.get_literal_type(typing.Dict[str, datetime.datetime]),
        LiteralType(simple=SimpleType.DATETIME),
    )
    recursive_assert(
        d.get_literal_type(typing.Dict[str, datetime.timedelta]),
        LiteralType(simple=SimpleType.DURATION),
    )
    recursive_assert(
        d.get_literal_type(typing.Dict[str, datetime.date]),
        LiteralType(simple=SimpleType.DATETIME),
    )
    recursive_assert(
        d.get_literal_type(typing.Dict[str, dict]),
        LiteralType(
            simple=SimpleType.STRUCT,
            annotation=TypeAnnotation({"cache-key-metadata": {"serialization-format": "msgpack"}})
        ),
    )
    recursive_assert(
        d.get_literal_type(typing.Dict[str, typing.Dict[str, str]]),
        LiteralType(simple=SimpleType.STRING),
        expected_depth=2,
    )
    recursive_assert(
        d.get_literal_type(typing.Dict[str, typing.Dict[int, str]]),
        LiteralType(
            simple=SimpleType.STRUCT,
            annotation=TypeAnnotation({"cache-key-metadata": {"serialization-format": "msgpack"}})
        ),
        expected_depth=2,
    )
    recursive_assert(
        d.get_literal_type(typing.Dict[str, typing.Dict[str, typing.Dict[str, str]]]),
        LiteralType(simple=SimpleType.STRING),
        expected_depth=3,
    )
    recursive_assert(
        d.get_literal_type(typing.Dict[str, typing.Dict[str, typing.Dict[str, dict]]]),
        LiteralType(
            simple=SimpleType.STRUCT,
            annotation=TypeAnnotation({"cache-key-metadata": {"serialization-format": "msgpack"}})
        ),
        expected_depth=3,
    )
    recursive_assert(
        d.get_literal_type(typing.Dict[str, typing.Dict[str, typing.Dict[int, dict]]]),
        LiteralType(
            simple=SimpleType.STRUCT,
            annotation=TypeAnnotation({"cache-key-metadata": {"serialization-format": "msgpack"}})
        ),
        expected_depth=2,
    )

    ctx = FlyteContext.current_context()

    lit = d.to_literal(ctx, {}, typing.Dict, LiteralType(SimpleType.STRUCT))
    pv = d.to_python_value(ctx, lit, typing.Dict)
    assert pv == {}

    lit_empty = Literal(map=LiteralMap(literals={}))
    pv_empty = d.to_python_value(ctx, lit_empty, typing.Dict[str, str])
    assert pv_empty == {}

    # Literal to python
    with pytest.raises(TypeError):
        d.to_python_value(ctx, Literal(scalar=Scalar(primitive=Primitive(integer=10))), dict)
    with pytest.raises(TypeError):
        d.to_python_value(ctx, Literal(), dict)
    with pytest.raises(TypeError):
        d.to_python_value(ctx, Literal(map=LiteralMap(literals={"x": None})), dict)
    with pytest.raises(TypeError):
        d.to_python_value(ctx, Literal(map=LiteralMap(literals={"x": None})), typing.Dict[int, str])

    with pytest.raises(TypeError):
        d.to_literal(
            ctx,
            {"x": datetime.datetime(2024, 5, 5)},
            dict,
            LiteralType(simple=SimpleType.STRUCT),
        )

    lv = d.to_literal(
        ctx,
        {"x": datetime.datetime(2024, 5, 5)},
        Annotated[dict, kwtypes(allow_pickle=True)],
        LiteralType(simple=SimpleType.STRUCT),
    )
    assert lv.metadata["format"] == "pickle"
    assert d.to_python_value(ctx, lv, dict) == {"x": datetime.datetime(2024, 5, 5)}

    d.to_python_value(
        ctx,
        Literal(map=LiteralMap(literals={"x": Literal(scalar=Scalar(primitive=Primitive(integer=1)))})),
        typing.Dict[str, int],
    )

    lv = d.to_literal(
        ctx,
        {"x": "hello"},
        dict,
        LiteralType(simple=SimpleType.STRUCT),
    )

    lv._metadata = None
    assert d.to_python_value(ctx, lv, dict) == {"x": "hello"}


def test_convert_marshmallow_json_schema_to_python_class():
    @dataclass
    class Foo(DataClassJsonMixin):
        x: int
        y: str

    schema = JSONSchema().dump(typing.cast(DataClassJsonMixin, Foo).schema())
    foo_class = convert_marshmallow_json_schema_to_python_class(schema["definitions"], "FooSchema")
    foo = foo_class(x=1, y="hello")
    foo.x = 2
    assert foo.x == 2
    assert foo.y == "hello"
    with pytest.raises(AttributeError):
        _ = foo.c
    assert dataclasses.is_dataclass(foo_class)


def test_convert_mashumaro_json_schema_to_python_class():
    @dataclass
    class Foo(DataClassJSONMixin):
        x: int
        y: str

    # schema = JSONSchema().dump(typing.cast(DataClassJSONMixin, Foo).schema())
    from mashumaro.jsonschema import build_json_schema

    schema = build_json_schema(typing.cast(DataClassJSONMixin, Foo)).to_dict()
    foo_class = convert_mashumaro_json_schema_to_python_class(schema, "FooSchema")
    foo = foo_class(x=1, y="hello")
    foo.x = 2
    assert foo.x == 2
    assert foo.y == "hello"
    with pytest.raises(AttributeError):
        _ = foo.c
    assert dataclasses.is_dataclass(foo_class)


def test_list_transformer():
    l0 = Literal(scalar=Scalar(primitive=Primitive(integer=3)))
    l1 = Literal(scalar=Scalar(primitive=Primitive(integer=4)))
    lc = LiteralCollection(literals=[l0, l1])
    lit = Literal(collection=lc)

    ctx = FlyteContext.current_context()
    xx = TypeEngine.to_python_value(ctx, lit, typing.List[int])
    assert xx == [3, 4]


def test_protos():
    ctx = FlyteContext.current_context()

    pb = errors_pb2.ContainerError(code="code", message="message")
    lt = TypeEngine.to_literal_type(errors_pb2.ContainerError)
    assert lt.simple == SimpleType.STRUCT
    assert lt.metadata["pb_type"] == "flyteidl.core.errors_pb2.ContainerError"

    lit = TypeEngine.to_literal(ctx, pb, errors_pb2.ContainerError, lt)
    new_python_val = TypeEngine.to_python_value(ctx, lit, errors_pb2.ContainerError)
    assert new_python_val == pb

    # Test error
    l0 = Literal(scalar=Scalar(primitive=Primitive(integer=4)))
    with pytest.raises(AssertionError):
        TypeEngine.to_python_value(ctx, l0, errors_pb2.ContainerError)

    default_proto = errors_pb2.ContainerError()
    lit = TypeEngine.to_literal(ctx, default_proto, errors_pb2.ContainerError, lt)
    assert lit.scalar
    assert lit.scalar.generic is not None
    new_python_val = TypeEngine.to_python_value(ctx, lit, errors_pb2.ContainerError)
    assert new_python_val == default_proto


def test_guessing_basic():
    b = model_types.LiteralType(simple=model_types.SimpleType.BOOLEAN)
    pt = TypeEngine.guess_python_type(b)
    assert pt is bool

    lt = model_types.LiteralType(simple=model_types.SimpleType.INTEGER)
    pt = TypeEngine.guess_python_type(lt)
    assert pt is int

    lt = model_types.LiteralType(simple=model_types.SimpleType.STRING)
    pt = TypeEngine.guess_python_type(lt)
    assert pt is str

    lt = model_types.LiteralType(simple=model_types.SimpleType.DURATION)
    pt = TypeEngine.guess_python_type(lt)
    assert pt is timedelta

    lt = model_types.LiteralType(simple=model_types.SimpleType.DATETIME)
    pt = TypeEngine.guess_python_type(lt)
    assert pt is datetime.datetime

    lt = model_types.LiteralType(simple=model_types.SimpleType.FLOAT)
    pt = TypeEngine.guess_python_type(lt)
    assert pt is float

    lt = model_types.LiteralType(simple=model_types.SimpleType.NONE)
    pt = TypeEngine.guess_python_type(lt)
    assert pt is type(None)  # noqa: E721

    lt = model_types.LiteralType(
        blob=BlobType(
            format=FlytePickleTransformer.PYTHON_PICKLE_FORMAT,
            dimensionality=BlobType.BlobDimensionality.SINGLE,
        )
    )
    pt = TypeEngine.guess_python_type(lt)
    assert pt is FlytePickle


def test_guessing_containers():
    b = model_types.LiteralType(simple=model_types.SimpleType.BOOLEAN)
    lt = model_types.LiteralType(collection_type=b)
    pt = TypeEngine.guess_python_type(lt)
    assert pt == typing.List[bool]

    dur = model_types.LiteralType(simple=model_types.SimpleType.DURATION)
    lt = model_types.LiteralType(map_value_type=dur)
    pt = TypeEngine.guess_python_type(lt)
    assert pt == typing.Dict[str, timedelta]


def test_zero_floats():
    ctx = FlyteContext.current_context()

    l0 = Literal(scalar=Scalar(primitive=Primitive(integer=0)))
    l1 = Literal(scalar=Scalar(primitive=Primitive(float_value=0.0)))

    assert TypeEngine.to_python_value(ctx, l0, float) == 0
    assert TypeEngine.to_python_value(ctx, l1, float) == 0


def test_dataclass_transformer():
    @dataclass
    class InnerStruct(DataClassJsonMixin):
        a: int
        b: typing.Optional[str]
        c: typing.List[int]

    @dataclass
    class TestStruct(DataClassJsonMixin):
        s: InnerStruct
        m: typing.Dict[str, str]

    @dataclass
    class TestStructB(DataClassJsonMixin):
        s: InnerStruct
        m: typing.Dict[int, str]
        n: typing.Optional[typing.List[typing.List[int]]] = None
        o: typing.Optional[typing.Dict[int, typing.Dict[int, int]]] = None

    @dataclass
    class TestStructC(DataClassJsonMixin):
        s: InnerStruct
        m: typing.Dict[str, int]

    @dataclass
    class TestStructD(DataClassJsonMixin):
        s: InnerStruct
        m: typing.Dict[str, typing.List[int]]

    class UnsupportedSchemaType:
        def __init__(self):
            self._a = "Hello"

    @dataclass
    class UnsupportedNestedStruct(DataClassJsonMixin):
        a: int
        s: UnsupportedSchemaType

    schema = {
        "type": "object",
        "title": "TestStruct",
        "properties": {
            "s": {
                "type": "object",
                "title": "InnerStruct",
                "properties": {
                    "a": {
                        "type": "integer"
                    },
                    "b": {
                        "anyOf": [
                            {
                                "type": "string"
                            },
                            {
                                "type": "null"
                            }
                        ]
                    },
                    "c": {
                        "type": "array",
                        "items": {
                            "type": "integer"
                        }
                    }
                },
                "additionalProperties": False,
                "required": ["a", "b", "c"]
            },
            "m": {
                "type": "object",
                "additionalProperties": {
                    "type": "string"
                },
                "propertyNames": {
                    "type": "string"
                }
            }
        },
        "additionalProperties": False,
        "required": ["s", "m"]
    }
    tf = DataclassTransformer()
    t = tf.get_literal_type(TestStruct)
    assert t is not None
    assert t.simple is not None
    assert t.simple == SimpleType.STRUCT
    assert t.metadata is not None
    assert t.metadata == schema

    t = TypeEngine.to_literal_type(TestStruct)
    assert t is not None
    assert t.simple is not None
    assert t.simple == SimpleType.STRUCT
    assert t.metadata is not None
    assert t.metadata == schema

    t = tf.get_literal_type(UnsupportedNestedStruct)
    assert t is not None
    assert t.simple is not None
    assert t.simple == SimpleType.STRUCT
    assert t.metadata is None


def test_dataclass_transformer_with_dataclassjsonmixin():
    @dataclass
    class InnerStruct_transformer(DataClassJSONMixin):
        a: int
        b: typing.Optional[str]
        c: typing.List[int]

    @dataclass
    class TestStruct_transformer(DataClassJSONMixin):
        s: InnerStruct_transformer
        m: typing.Dict[str, str]

    class UnsupportedSchemaType:
        def __init__(self):
            self._a = "Hello"

    @dataclass
    class UnsupportedNestedStruct(DataClassJsonMixin):
        a: int
        s: UnsupportedSchemaType

    schema = {
        "type": "object",
        "title": "TestStruct_transformer",
        "properties": {
            "s": {
                "type": "object",
                "title": "InnerStruct_transformer",
                "properties": {
                    "a": {"type": "integer"},
                    "b": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                    "c": {"type": "array", "items": {"type": "integer"}},
                },
                "additionalProperties": False,
                "required": ["a", "b", "c"],
            },
            "m": {
                "type": "object",
                "additionalProperties": {"type": "string"},
                "propertyNames": {"type": "string"},
            },
        },
        "additionalProperties": False,
        "required": ["s", "m"],
    }

    tf = DataclassTransformer()
    t = tf.get_literal_type(TestStruct_transformer)
    assert t is not None
    assert t.simple is not None
    assert t.simple == SimpleType.STRUCT
    assert t.metadata is not None
    assert t.metadata == schema

    t = TypeEngine.to_literal_type(TestStruct_transformer)
    assert t is not None
    assert t.simple is not None
    assert t.simple == SimpleType.STRUCT
    assert t.metadata is not None
    assert t.metadata == schema

    t = tf.get_literal_type(UnsupportedNestedStruct)
    assert t is not None
    assert t.simple is not None
    assert t.simple == SimpleType.STRUCT
    assert t.metadata is None


def test_dataclass_int_preserving():
    @dataclass
    class InnerStruct(DataClassJsonMixin):
        a: int
        b: typing.Optional[str]
        c: typing.List[int]

    @dataclass
    class TestStructB(DataClassJsonMixin):
        s: InnerStruct
        m: typing.Dict[int, str]
        n: typing.Optional[typing.List[typing.List[int]]] = None
        o: typing.Optional[typing.Dict[int, typing.Dict[int, int]]] = None

    @dataclass
    class TestStructC(DataClassJsonMixin):
        s: InnerStruct
        m: typing.Dict[str, int]

    @dataclass
    class TestStructD(DataClassJsonMixin):
        s: InnerStruct
        m: typing.Dict[str, typing.List[int]]

    ctx = FlyteContext.current_context()
    o = InnerStruct(a=5, b=None, c=[1, 2, 3])
    tf = DataclassTransformer()
    lv = tf.to_literal(ctx, o, InnerStruct, tf.get_literal_type(InnerStruct))
    ot = tf.to_python_value(ctx, lv=lv, expected_python_type=InnerStruct)
    assert ot == o

    o = TestStructB(
        s=InnerStruct(a=5, b=None, c=[1, 2, 3]),
        m={5: "b"},
        n=[[1, 2, 3], [4, 5, 6]],
        o={1: {2: 3}, 4: {5: 6}},
    )
    lv = tf.to_literal(ctx, o, TestStructB, tf.get_literal_type(TestStructB))
    ot = tf.to_python_value(ctx, lv=lv, expected_python_type=TestStructB)
    assert ot == o

    o = TestStructC(s=InnerStruct(a=5, b=None, c=[1, 2, 3]), m={"a": 5})
    lv = tf.to_literal(ctx, o, TestStructC, tf.get_literal_type(TestStructC))
    ot = tf.to_python_value(ctx, lv=lv, expected_python_type=TestStructC)
    assert ot == o

    o = TestStructD(s=InnerStruct(a=5, b=None, c=[1, 2, 3]), m={"a": [5]})
    lv = tf.to_literal(ctx, o, TestStructD, tf.get_literal_type(TestStructD))
    ot = tf.to_python_value(ctx, lv=lv, expected_python_type=TestStructD)
    assert ot == o


@mock.patch("flytekit.core.data_persistence.FileAccessProvider.async_put_data")
def test_dataclass_with_postponed_annotation(mock_put_data):
    remote_path = "s3://tmp/file"
    mock_put_data.return_value = remote_path

    @dataclass
    class Data:
        a: int
        f: "FlyteFile"

    ctx = FlyteContext.current_context()
    tf = DataclassTransformer()
    t = tf.get_literal_type(Data)
    assert t.simple == SimpleType.STRUCT
    with tempfile.TemporaryDirectory() as tmp:
        test_file = os.path.join(tmp, "abc.txt")
        with open(test_file, "w") as f:
            f.write("123")

        pv = Data(a=1, f=FlyteFile(test_file, remote_path=remote_path))
        lt = tf.to_literal(ctx, pv, Data, t)
        msgpack_bytes = lt.scalar.binary.value
        dict_obj = msgpack.loads(msgpack_bytes)
        assert dict_obj["f"]["path"] == remote_path


@mock.patch("flytekit.core.data_persistence.FileAccessProvider.async_put_data")
def test_optional_flytefile_in_dataclass(mock_upload_dir):
    mock_upload_dir.return_value = True

    @dataclass
    class A(DataClassJsonMixin):
        a: int

    @dataclass
    class TestFileStruct(DataClassJsonMixin):
        a: FlyteFile
        b: typing.Optional[FlyteFile]
        b_prime: typing.Optional[FlyteFile]
        c: typing.Union[FlyteFile, None]
        c_prime: typing.Union[None, int, bool, FlyteFile]
        d: typing.List[FlyteFile]
        e: typing.List[typing.Optional[FlyteFile]]
        e_prime: typing.List[typing.Optional[FlyteFile]]
        f: typing.Dict[str, FlyteFile]
        g: typing.Dict[str, typing.Optional[FlyteFile]]
        g_prime: typing.Dict[str, typing.Optional[FlyteFile]]
        h: typing.Optional[FlyteFile] = None
        h_prime: typing.Optional[FlyteFile] = None
        i: typing.Optional[A] = None
        i_prime: typing.Optional[A] = field(default_factory=lambda: A(a=99))
        j: typing.Union[int, FlyteFile] = 0

    remote_path = "s3://tmp/file"
    # set the return value to the remote path since that's what put_data does
    mock_upload_dir.return_value = remote_path
    with tempfile.TemporaryFile() as f:
        f.write(b"abc")
        f1 = FlyteFile("f1", remote_path=remote_path)
        o = TestFileStruct(
            a=f1,
            b=f1,
            b_prime=None,
            c=f1,
            c_prime=f1,
            d=[f1],
            e=[f1],
            e_prime=[None],
            f={"a": f1},
            g={"a": f1},
            g_prime={"a": None},
            h=f1,
            i=A(a=42),
            j=remote_path,
        )

        ctx = FlyteContext.current_context()
        tf = DataclassTransformer()
        lt = tf.get_literal_type(TestFileStruct)
        lv = tf.to_literal(ctx, o, TestFileStruct, lt)

        msgpack_bytes = lv.scalar.binary.value
        dict_obj = msgpack.loads(msgpack_bytes)

        assert dict_obj["a"]["path"] == remote_path
        assert dict_obj["b"]["path"] == remote_path
        assert dict_obj["b_prime"] is None
        assert dict_obj["c"]["path"] == remote_path
        assert dict_obj["c_prime"]["path"] == remote_path
        assert dict_obj["d"][0]["path"] == remote_path
        assert dict_obj["e"][0]["path"] == remote_path
        assert dict_obj["e_prime"][0] is None
        assert dict_obj["f"]["a"]["path"] == remote_path
        assert dict_obj["g"]["a"]["path"] == remote_path
        assert dict_obj["g_prime"]["a"] is None
        assert dict_obj["h"]["path"] == remote_path
        assert dict_obj["h_prime"] is None
        assert dict_obj["i"]["a"] == 42
        assert dict_obj["i_prime"]["a"] == 99
        assert dict_obj["j"]["path"] == remote_path

        ot = tf.to_python_value(ctx, lv=lv, expected_python_type=TestFileStruct)

        assert o.a.remote_path == ot.a.remote_source
        assert o.b.remote_path == ot.b.remote_source
        assert ot.b_prime is None
        assert o.c.remote_path == ot.c.remote_source
        assert o.c_prime.remote_path == ot.c_prime.remote_source
        assert o.d[0].remote_path == ot.d[0].remote_source
        assert o.e[0].remote_path == ot.e[0].remote_source
        assert o.e_prime == [None]
        assert o.f["a"].remote_path == ot.f["a"].remote_source
        assert o.g["a"].remote_path == ot.g["a"].remote_source
        assert o.g_prime == {"a": None}
        assert o.h.remote_path == ot.h.remote_source
        assert ot.h_prime is None
        assert o.i == ot.i
        assert o.i_prime == A(a=99)
        assert o.j == FlyteFile(remote_path)
