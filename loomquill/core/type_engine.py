from __future__ import annotations

import asyncio
import collections
import copy
import dataclasses
import datetime
import enum
import inspect
import json
import mimetypes
import os
import sys
import textwrap
import threading
import typing
from abc import ABC, abstractmethod
from collections import OrderedDict
from functools import lru_cache, reduce
from types import GenericAlias
from typing import Any, Dict, List, NamedTuple, Optional, Type, cast

import msgpack
from cachetools import LRUCache
from dataclasses_json import DataClassJsonMixin, dataclass_json
from flyteidl.core import literals_pb2
from fsspec.asyn import _run_coros_in_chunks  # pylint: disable=W0212
from google.protobuf import json_format as _json_format
from google.protobuf import struct_pb2 as _struct
from google.protobuf.json_format import MessageToDict as _MessageToDict
from google.protobuf.json_format import ParseDict as _ParseDict
from google.protobuf.message import Message
from google.protobuf.struct_pb2 import Struct
from mashumaro.codecs.json import JSONDecoder, JSONEncoder
from mashumaro.codecs.msgpack import MessagePackDecoder, MessagePackEncoder
from mashumaro.mixins.json import DataClassJSONMixin
from typing_extensions import Annotated, get_args, get_origin

from flytekit.core.annotation import FlyteAnnotation
from flytekit.core.constants import CACHE_KEY_METADATA, FLYTE_USE_OLD_DC_FORMAT, MESSAGEPACK, SERIALIZATION_FORMAT
from flytekit.core.context_manager import FlyteContext
from flytekit.core.hash import HashMethod
from flytekit.core.type_helpers import load_type_from_tag
from flytekit.core.type_match_checking import literal_types_match
from flytekit.core.utils import load_proto_from_file, str2bool, timeit
from flytekit.exceptions import user as user_exceptions
from flytekit.interaction.string_literals import literal_map_string_repr
from flytekit.lazy_import.lazy_module import is_imported
from flytekit.loggers import logger
from flytekit.models import interface as _interface_models
from flytekit.models import types as _type_models
from flytekit.models.annotation import TypeAnnotation as TypeAnnotationModel
from flytekit.models.core import types as _core_types
from flytekit.models.literals import Binary, Literal, LiteralCollection, LiteralMap, Primitive, Scalar, Union, Void
from flytekit.models.types import LiteralType, SimpleType, TypeStructure, UnionType
from flytekit.utils.asyn import loop_manager

if typing.TYPE_CHECKING:
    from flytekit.core.interface import Interface

T = typing.TypeVar("T")
DEFINITIONS = "definitions"
TITLE = "title"

_TYPE_ENGINE_COROS_BATCH_SIZE = int(os.environ.get("_F_TE_MAX_COROS", "10"))


# In Mashumaro, the default encoder uses strict_map_key=False, while the default decoder uses strict_map_key=True.
# This is relevant for cases like Dict[int, str].
# If strict_map_key=False is not used, the decoder will raise an error when trying to decode keys that are not strictly typed.｀
def _default_msgpack_decoder(data: bytes) -> Any:
    return msgpack.unpackb(data, strict_map_key=False)


class BatchSize:
    """
    This is used to annotate a FlyteDirectory when we want to download/upload the contents of the directory in batches. For example,

    ```python
    @task
    def t1(directory: Annotated[FlyteDirectory, BatchSize(10)]) -> Annotated[FlyteDirectory, BatchSize(100)]:
        ...
        return FlyteDirectory(...)
    ```

    In the above example flytekit will download all files from the input `directory` in chunks of 10, i.e. first it
    downloads 10 files, loads them to memory, then writes those 10 to local disk, then it loads the next 10, so on
    and so forth. Similarly, for outputs, in this case flytekit is going to upload the resulting directory in chunks of
    100.
    """

    def __init__(self, val: int):
        self._val = val

    @property
    def val(self) -> int:
        return self._val


def get_batch_size(t: Type) -> Optional[int]:
    if is_annotated(t):
        for annotation in get_args(t)[1:]:
            if isinstance(annotation, BatchSize):
                return annotation.val
    return None


def modify_literal_uris(lit: Literal):
    """
    Modifies the literal object recursively to replace the URIs with the native paths in case they are of
    type "flyte://"
    """
    from flytekit.remote.remote_fs import FlytePathResolver

    if lit.collection:
        for l in lit.collection.literals:
            modify_literal_uris(l)
    elif lit.map:
        for k, v in lit.map.literals.items():
            modify_literal_uris(v)
    elif lit.scalar:
        if lit.scalar.blob and lit.scalar.blob.uri and lit.scalar.blob.uri.startswith(FlytePathResolver.protocol):
            lit.scalar.blob._uri = FlytePathResolver.resolve_remote_path(lit.scalar.blob.uri)
        elif lit.scalar.union:
            modify_literal_uris(lit.scalar.union.value)
        elif (
            lit.scalar.structured_dataset
            and lit.scalar.structured_dataset.uri
            and lit.scalar.structured_dataset.uri.startswith(FlytePathResolver.protocol)
        ):
            lit.scalar.structured_dataset._uri = FlytePathResolver.resolve_remote_path(
                lit.scalar.structured_dataset.uri
            )


class TypeTransformerFailedError(TypeError, AssertionError, ValueError): ...


class TypeTransformer(typing.Generic[T]):
    """
    Base transformer type that should be implemented for every python native type that can be handled by flytekit
    """

    def __init__(self, name: str, t: Type[T], enable_type_assertions: bool = True):
        self._t = t
        self._name = name
        self._type_assertions_enabled = enable_type_assertions
        self._msgpack_encoder: Dict[Type, MessagePackEncoder] = dict()
        self._msgpack_decoder: Dict[Type, MessagePackDecoder] = dict()

    @property
    def name(self):
        return self._name

    @property
    def python_type(self) -> Type[T]:
        """
        This returns the python type
        """
        return self._t

    @property
    def is_async(self) -> bool:
        return False

    @property
    def type_assertions_enabled(self) -> bool:
        """
        Indicates if the transformer wants type assertions to be enabled at the core type engine layer
        """
        return self._type_assertions_enabled

    def isinstance_generic(self, obj, generic_alias):
        origin = get_origin(generic_alias)  # list from list[int])

        if not isinstance(obj, origin):
            raise TypeTransformerFailedError(f"Value '{obj}' is not of container type {origin}")

    def assert_type(self, t: Type[T], v: T):
        if sys.version_info >= (3, 10):
            import types

            if isinstance(t, types.GenericAlias):
                return self.isinstance_generic(v, t)

        if not hasattr(t, "__origin__") and not isinstance(v, t):
            raise TypeTransformerFailedError(f"Expected value of type {t} but got '{v}' of type {type(v)}")

    @abstractmethod
    def get_literal_type(self, t: Type[T]) -> LiteralType:
        """
        Converts the python type to a Flyte LiteralType
        """
        raise NotImplementedError("Conversion to LiteralType should be implemented")

    def guess_python_type(self, literal_type: LiteralType) -> Type[T]:
        """
        Converts the Flyte LiteralType to a python object type.
        """
        raise ValueError("By default, transformers do not translate from Flyte types back to Python types")

    @abstractmethod
    def to_literal(self, ctx: FlyteContext, python_val: T, python_type: Type[T], expected: LiteralType) -> Literal:
        """
        Converts a given python_val to a Flyte Literal, assuming the given python_val matches the declared python_type.
        Implementers should refrain from using type(python_val) instead rely on the passed in python_type. If these
        do not match (or are not allowed) the Transformer implementer should raise an AssertionError, clearly stating
        what was the mismatch
        :param ctx: A FlyteContext, useful in accessing the filesystem and other attributes
        :param python_val: The actual value to be transformed
        :param python_type: The assumed type of the value (this matches the declared type on the function)
        :param expected: Expected Literal Type
        """
        raise NotImplementedError(f"Conversion to Literal for python type {python_type} not implemented")

    @abstractmethod
    def to_python_value(self, ctx: FlyteContext, lv: Literal, expected_python_type: Type[T]) -> Optional[T]:
        """
        Converts the given Literal to a Python Type. If the conversion cannot be done an AssertionError should be raised
        :param ctx: FlyteContext
        :param lv: The received literal Value
        :param expected_python_type: Expected native python type that should be returned
        """
        raise NotImplementedError(
            f"Conversion to python value expected type {expected_python_type} from literal not implemented"
        )

    def schema_match(self, schema: dict) -> bool:
        """Check if a JSON schema fragment matches this transformer's python_type.

        For BaseModel subclasses, automatically compares the schema's title, type, and
        required fields against the type's own JSON schema. For other types, returns
        False by default — override if needed.
        """
        if not isinstance(schema, dict):
            return False
        try:
            from pydantic import BaseModel

            if hasattr(self.python_type, "model_json_schema") and self.python_type is not BaseModel:
                this_schema = self.python_type.model_json_schema()  # type: ignore[attr-defined]
                return (
                    schema.get("title") == this_schema.get("title")
                    and schema.get("type") == this_schema.get("type")
                    and set(schema.get("required", [])) == set(this_schema.get("required", []))
                )
        except Exception:
            pass
        return False

    def from_binary_idl(self, binary_idl_object: Binary, expected_python_type: Type[T]) -> Optional[T]:
        """
        This function primarily handles deserialization for untyped dicts, dataclasses, Pydantic BaseModels, and attribute access.｀

        For untyped dict, dataclass, and pydantic basemodel:
        Life Cycle (Untyped Dict as example):
            python val -> msgpack bytes -> binary literal scalar -> msgpack bytes -> python val
                          (to_literal)                             (from_binary_idl)

        For attribute access:
        Life Cycle:
            python val -> msgpack bytes -> binary literal scalar -> resolved golang value -> binary literal scalar -> msgpack bytes -> python val
                          (to_literal)                            (propeller attribute access)                       (from_binary_idl)
        """
        if binary_idl_object.tag == MESSAGEPACK:
            try:
                decoder = self._msgpack_decoder[expected_python_type]
            except KeyError:
                decoder = MessagePackDecoder(expected_python_type, pre_decoder_func=_default_msgpack_decoder)
                self._msgpack_decoder[expected_python_type] = decoder
            python_val = decoder.decode(binary_idl_object.value)

            return python_val
        else:
            raise TypeTransformerFailedError(f"Unsupported binary format `{binary_idl_object.tag}`")

    def from_generic_idl(self, generic: Struct, expected_python_type: Type[T]) -> Optional[T]:
        """
        TODO: Support all Flyte Types.
        This is for dataclass attribute access from input created from the Flyte Console.

        Note:
        - This can be removed in the future when the Flyte Console support generate Binary IDL Scalar as input.
        """
        raise NotImplementedError(f"Conversion from generic idl to python type {expected_python_type} not implemented")

    def to_html(self, ctx: FlyteContext, python_val: T, expected_python_type: Type[T]) -> str:
        """
        Converts any python val (dataframe, int, float) to a html string, and it will be wrapped in the HTML div
        """
        return str(python_val)

    def __repr__(self):
        return f"{self._name} Transforms ({self._t}) to Flyte native"

    def __str__(self):
        return str(self.__repr__())


class AsyncTypeTransformer(TypeTransformer[T]):
    def __init__(self, name: str, t: Type[T], enable_type_assertions: bool = True):
        super().__init__(name, t, enable_type_assertions)

    @property
    def is_async(self) -> bool:
        return True

    @abstractmethod
    async def async_to_literal(
        self, ctx: FlyteContext, python_val: T, python_type: Type[T], expected: LiteralType
    ) -> Literal:
        """
        Converts a given python_val to a Flyte Literal, assuming the given python_val matches the declared python_type.
        Implementers should refrain from using type(python_val) instead rely on the passed in python_type. If these
        do not match (or are not allowed) the Transformer implementer should raise an AssertionError, clearly stating
        what was the mismatch
        :param ctx: A FlyteContext, useful in accessing the filesystem and other attributes
        :param python_val: The actual value to be transformed
        :param python_type: The assumed type of the value (this matches the declared type on the function)
        :param expected: Expected Literal Type
        """

        raise NotImplementedError(f"Conversion to Literal for python type {python_type} not implemented")

    @abstractmethod
    async def async_to_python_value(self, ctx: FlyteContext, lv: Literal, expected_python_type: Type[T]) -> Optional[T]:
        """
        Converts the given Literal to a Python Type. If the conversion cannot be done an AssertionError should be raised
        :param ctx: FlyteContext
        :param lv: The received literal Value
        :param expected_python_type: Expected native python type that should be returned
        """
        raise NotImplementedError(
            f"Conversion to python value expected type {expected_python_type} from literal not implemented"
        )

    def to_literal(
        self, ctx: FlyteContext, python_val: typing.Any, python_type: Type[T], expected: LiteralType
    ) -> Literal:
        synced = loop_manager.synced(self.async_to_literal)
        result = synced(ctx, python_val, python_type, expected)
        return result

    def to_python_value(self, ctx: FlyteContext, lv: Literal, expected_python_type: Type[T]) -> Optional[T]:
        synced = loop_manager.synced(self.async_to_python_value)
        result = synced(ctx, lv, expected_python_type)
        return result


class SimpleTransformer(TypeTransformer[T]):
    """
    A Simple implementation of a type transformer that uses simple lambdas to transform and reduces boilerplate
    """

    def __init__(
        self,
        name: str,
        t: Type[T],
        lt: LiteralType,
        to_literal_transformer: typing.Callable[[T], Literal],
        from_literal_transformer: typing.Callable[[Literal], T],
    ):
        super().__init__(name, t)
        self._type = t
        self._lt = lt
        self._to_literal_transformer = to_literal_transformer
        self._from_literal_transformer = from_literal_transformer

    @property
    def base_type(self) -> Type:
        return self._type

    def get_literal_type(self, t: Optional[Type[T]] = None) -> LiteralType:
        return LiteralType.from_flyte_idl(self._lt.to_flyte_idl())

    def to_literal(self, ctx: FlyteContext, python_val: T, python_type: Type[T], expected: LiteralType) -> Literal:
        if type(python_val) != self._type:
            raise TypeTransformerFailedError(
                f"Expected value of type {self._type} but got '{python_val}' of type {type(python_val)}"
            )
        return self._to_literal_transformer(python_val)

    def from_binary_idl(self, binary_idl_object: Binary, expected_python_type: Type[T]) -> Optional[T]:
        if binary_idl_object.tag == MESSAGEPACK:
            if expected_python_type in [datetime.date, datetime.datetime, datetime.timedelta]:
                """
                MessagePack doesn't support datetime, date, and timedelta.
                However, mashumaro's MessagePackEncoder and MessagePackDecoder can convert them to str and vice versa.
                That's why we need to use mashumaro's MessagePackDecoder here.
                """
                try:
                    decoder = self._msgpack_decoder[expected_python_type]
                except KeyError:
                    decoder = MessagePackDecoder(expected_python_type, pre_decoder_func=_default_msgpack_decoder)
                    self._msgpack_decoder[expected_python_type] = decoder
                python_val = decoder.decode(binary_idl_object.value)
            else:
                python_val = msgpack.loads(binary_idl_object.value)
                """
                In the case below, when using Union Transformer + Simple Transformer, then `a`
                can be converted to int, bool, str and float if we use MessagePackDecoder[expected_python_type].

                Life Cycle:
                1 -> msgpack bytes -> (1, true, "1", 1.0)

                Example Code:
                @dataclass
                class DC:
                    a: Union[int, bool, str, float]
                    b: Union[int, bool, str, float]

                @task(container_image=custom_image)
                def add(a: Union[int, bool, str, float], b: Union[int, bool, str, float]) -> Union[int, bool, str, float]:
                    return a + b

                @workflow
                def wf(dc: DC) -> Union[int, bool, str, float]:
                    return add(dc.a, dc.b)

                wf(DC(1, 1))
                """
                assert type(python_val) == expected_python_type

            return python_val
        else:
            raise TypeTransformerFailedError(f"Unsupported binary format `{binary_idl_object.tag}`")

    def to_python_value(self, ctx: FlyteContext, lv: Literal, expected_python_type: Type[T]) -> T:
        expected_python_type = get_underlying_type(expected_python_type)

        if expected_python_type != self._type:
            raise TypeTransformerFailedError(
                f"Cannot convert to type {expected_python_type}, only {self._type} is supported"
            )

        if lv.scalar and lv.scalar.binary:
            return self.from_binary_idl(lv.scalar.binary, expected_python_type)  # type: ignore

        try:  # todo(maximsmol): this is quite ugly and each transformer should really check their Literal
            res = self._from_literal_transformer(lv)
            if type(res) != self._type:
                raise TypeTransformerFailedError(f"Cannot convert literal {lv} to {self._type}")
            return res
        except AttributeError:
            # Assume that this is because a property on `lv` was None
            raise TypeTransformerFailedError(f"Cannot convert literal {lv} to {self._type}")

    def guess_python_type(self, literal_type: LiteralType) -> Type[T]:
        if literal_type.simple is not None and literal_type.simple == self._lt.simple:
            return self.python_type
        raise ValueError(f"Transformer {self} cannot reverse {literal_type}")


class RestrictedTypeError(Exception):
    pass


class RestrictedTypeTransformer(TypeTransformer[T], ABC):
    """
    Types registered with the RestrictedTypeTransformer are not allowed to be converted to and from literals. In other words,
    Restricted types are not allowed to be used as inputs or outputs of tasks and workflows.
    """

    def __init__(self, name: str, t: Type[T]):
        super().__init__(name, t)

    def get_literal_type(self, t: Optional[Type[T]] = None) -> LiteralType:
        raise RestrictedTypeError(f"Transformer for type {self.python_type} is restricted currently")

    def to_literal(self, ctx: FlyteContext, python_val: T, python_type: Type[T], expected: LiteralType) -> Literal:
        raise RestrictedTypeError(f"Transformer for type {self.python_type} is restricted currently")

    def to_python_value(self, ctx: FlyteContext, lv: Literal, expected_python_type: Type[T]) -> T:
        raise RestrictedTypeError(f"Transformer for type {self.python_type} is restricted currently")


class DataclassTransformer(TypeTransformer[object]):
    """
        The Dataclass Transformer provides a type transformer for dataclasses.

        The dataclass is converted to and from MessagePack Bytes by the mashumaro library
        and is transported between tasks using the Binary IDL representation.
        Also, the type declaration will try to extract the JSON Schema for the
        object, if possible, and pass it with the definition.

        The lifecycle of the dataclass in the Flyte type system is as follows:

        1. Serialization: The dataclass transformer converts the dataclass to MessagePack Bytes.
            (1) Handle dataclass attributes to make them serializable with mashumaro.
            (2) Use the mashumaro API to serialize the dataclass to MessagePack Bytes.
            (3) Use MessagePack Bytes to create a Flyte Literal.
            (4) Serialize the Flyte Literal to a Binary IDL Object.

        2. Deserialization: The dataclass transformer converts the MessagePack Bytes back to a dataclass.
            (1) Convert MessagePack Bytes to a dataclass using mashumaro.
            (2) Handle dataclass attributes to ensure they are of the correct types.

        For Json Schema, we use https://github.com/fuhrysteve/marshmallow-jsonschema library.

        Example

        ```python
        @dataclass
        class Test(DataClassJsonMixin):
            a: int
            b: str

        from marshmallow_jsonschema import JSONSchema
        t = Test(a=10,b="e")
        JSONSchema().dump(t.schema())
        ```

        Output will look like

        ```python
        {'$schema': 'http://json-schema.org/draft-07/schema#',
            'definitions': {'TestSchema': {'properties': {'a': {'title': 'a',
                'type': 'number',
                'format': 'integer'},
            'b': {'title': 'b', 'type': 'string'}},
            'type': 'object',
            'additionalProperties': False}},
            '$ref': '#/definitions/TestSchema'}
    ```

        > [!NOTE]
        > The schema support is experimental and is useful for auto-completing in the UI/CLI

    """

    def __init__(self) -> None:
        super().__init__("Object-Dataclass-Transformer", object)
        self._json_encoder: Dict[Type, JSONEncoder] = dict()
        self._json_decoder: Dict[Type, JSONDecoder] = dict()

    def assert_type(self, expected_type: Type[DataClassJsonMixin], v: T):
        # Skip iterating all attributes in the dataclass if the type of v already matches the expected_type
        expected_type = get_underlying_type(expected_type)
        if type(v) == expected_type or issubclass(type(v), expected_type):
            return

        # @dataclass
        # class Foo(DataClassJsonMixin):
        #     a: int = 0
        #
        # @task
        # def t1(a: Foo):
        #     ...
        #
        # In above example, the type of v may not equal to the expected_type in some cases
        # For example,
        # 1. The input of t1 is another dataclass (bar), then we should raise an error
        # 2. when using flyte remote to execute the above task, the expected_type is guess_python_type (FooSchema) by default.
        # However, FooSchema is created by flytekit and it's not equal to the user-defined dataclass (Foo).
        # Therefore, we should iterate all attributes in the dataclass and check the type of value in dataclass matches the expected_type.

        expected_fields_dict = {}

        for f in dataclasses.fields(expected_type):
            expected_fields_dict[f.name] = f.type

        if isinstance(v, dict):
            original_dict = v

            # Find the Optional keys in expected_fields_dict
            optional_keys = {k for k, t in expected_fields_dict.items() if UnionTransformer.is_optional_type(t)}

            # Remove the Optional keys from the keys of original_dict
            original_key = set(original_dict.keys()) - optional_keys
            expected_key = set(expected_fields_dict.keys()) - optional_keys

            # Check if original_key is missing any keys from expected_key
            missing_keys = expected_key - original_key
            if missing_keys:
                raise TypeTransformerFailedError(
                    f"The original fields are missing the following keys from the dataclass fields: {list(missing_keys)}"
                )

            # Check if original_key has any extra keys that are not in expected_key
            extra_keys = original_key - expected_key
            if extra_keys:
                raise TypeTransformerFailedError(
                    f"The original fields have the following extra keys that are not in dataclass fields: {list(extra_keys)}"
                )

            for k, v in original_dict.items():
                if k in expected_fields_dict:
                    if isinstance(v, dict):
                        self.assert_type(expected_fields_dict[k], v)
                    else:
                        expected_type = expected_fields_dict[k]
                        original_type = type(v)
                        if UnionTransformer.is_optional_type(expected_type):
                            expected_type = UnionTransformer.get_sub_type_in_optional(expected_type)
                        if original_type != expected_type:
                            raise TypeTransformerFailedError(
                                f"Type of Val '{original_type}' is not an instance of {expected_type}"
                            )

        else:
            for f in dataclasses.fields(type(v)):  # type: ignore
                original_type = f.type
                if f.name not in expected_fields_dict:
                    raise TypeTransformerFailedError(
                        f"Field '{f.name}' is not present in the expected dataclass fields {expected_type.__name__}"
                    )
                expected_type = expected_fields_dict[f.name]

                if UnionTransformer.is_optional_type(original_type):
                    original_type = UnionTransformer.get_sub_type_in_optional(original_type)
                if UnionTransformer.is_optional_type(expected_type):
                    expected_type = UnionTransformer.get_sub_type_in_optional(expected_type)

                val = v.__getattribute__(f.name)
                if dataclasses.is_dataclass(val):
                    self.assert_type(expected_type, val)
                elif original_type != expected_type:
                    raise TypeTransformerFailedError(
                        f"Type of Val '{original_type}' is not an instance of {expected_type}"
                    )

    def get_literal_type(self, t: Type[T]) -> LiteralType:
        """
        Extracts the Literal type definition for a Dataclass and returns a type Struct.
        If possible also extracts the JSONSchema for the dataclass.
        """

        if is_annotated(t):
            args = get_args(t)
            for x in args[1:]:
                if isinstance(x, FlyteAnnotation):
                    raise ValueError(
                        "Flytekit does not currently have support for FlyteAnnotations applied to Dataclass."
                        f"Type {t} cannot be parsed."
                    )
            logger.info(f"These annotations will be skipped for dataclasses = {args[1:]}")
            # Drop all annotations and handle only the dataclass type passed in.
            t = args[0]

        schema = None
        try:
            # This produce JSON SCHEMA draft 2020-12
            from mashumaro.jsonschema import build_json_schema

            schema = build_json_schema(cast(DataClassJSONMixin, self._get_origin_type_in_annotation(t))).to_dict()
        except Exception as e:
            logger.error(
                f"Failed to extract schema for object {t}, error: {e}\n"
                f"Please remove `DataClassJsonMixin` and `dataclass_json` decorator from the dataclass definition"
            )

        if schema is None:
            try:
                # This produce JSON SCHEMA draft 2020-12
                from marshmallow_enum import EnumField, LoadDumpOptions

                if issubclass(t, DataClassJsonMixin):
                    s = cast(DataClassJsonMixin, self._get_origin_type_in_annotation(t)).schema()
                    for _, v in s.fields.items():
                        # marshmallow-jsonschema only supports enums loaded by name.
                        # https://github.com/fuhrysteve/marshmallow-jsonschema/blob/81eada1a0c42ff67de216923968af0a6b54e5dcb/marshmallow_jsonschema/base.py#L228
                        if isinstance(v, EnumField):
                            v.load_by = LoadDumpOptions.name
                    # check if DataClass mixin
                    from marshmallow_jsonschema import JSONSchema

                    schema = JSONSchema().dump(s)
            except Exception as e:
                # https://github.com/lovasoa/marshmallow_dataclass/issues/13
                logger.warning(
                    f"Failed to extract schema for object {t}, (will run schemaless) error: {e}"
                    f"If you have postponed annotations turned on (PEP 563) turn it off please. Postponed"
                    f"evaluation doesn't work with json dataclasses"
                )

        # Recursively construct the dataclass_type which contains the literal type of each field
        literal_type = {}

        hints = typing.get_type_hints(t)
        # Get the type of each field from dataclass
        for field in t.__dataclass_fields__.values():  # type: ignore
            try:
                name = field.name
                python_type = hints.get(name, field.type)
                literal_type[name] = TypeEngine.to_literal_type(python_type)
            except Exception as e:
                logger.debug(
                    f"Field {field.name} of type {field.type} cannot be converted to a literal type. Error: {e}"
                )

        # This is for attribute access in FlytePropeller.
        ts = TypeStructure(tag="", dataclass_type=literal_type)

        return _type_models.LiteralType(
            simple=_type_models.SimpleType.STRUCT,
            metadata=schema,
            structure=ts,
            annotation=TypeAnnotationModel({CACHE_KEY_METADATA: {SERIALIZATION_FORMAT: MESSAGEPACK}}),
        )

    def to_generic_literal(
        self, ctx: FlyteContext, python_val: T, python_type: Type[T], expected: LiteralType
    ) -> Literal:
        """
        Serializes a dataclass or dictionary to a Flyte literal, handling both JSON and MessagePack formats.
        Set `FLYTE_USE_OLD_DC_FORMAT=true` to use the old JSON-based format.
        Note: This is deprecated and will be removed in the future.
        """
        if isinstance(python_val, dict):
            json_str = json.dumps(python_val)
            return Literal(scalar=Scalar(generic=_json_format.Parse(json_str, _struct.Struct())))

        if not dataclasses.is_dataclass(python_val):
            raise TypeTransformerFailedError(
                f"{type(python_val)} is not of type @dataclass, only Dataclasses are supported for "
                f"user defined datatypes in Flytekit"
            )

        self._make_dataclass_serializable(python_val, python_type)

        # JSON serialization using mashumaro's DataClassJSONMixin
        if isinstance(python_val, DataClassJSONMixin):
            json_str = python_val.to_json()
        else:
            try:
                encoder = self._json_encoder[python_type]
            except KeyError:
                encoder = JSONEncoder(python_type)
                self._json_encoder[python_type] = encoder

            try:
                json_str = encoder.encode(python_val)
            except NotImplementedError:
                raise NotImplementedError(
                    f"{python_type} should inherit from mashumaro.types.SerializableType"
                    f" and implement _serialize and _deserialize methods."
                )

        return Literal(scalar=Scalar(generic=_json_format.Parse(json_str, _struct.Struct())))  # type: ignore

    def to_literal(self, ctx: FlyteContext, python_val: T, python_type: Type[T], expected: LiteralType) -> Literal:
        if str2bool(os.getenv(FLYTE_USE_OLD_DC_FORMAT)):
            return self.to_generic_literal(ctx, python_val, python_type, expected)

        if isinstance(python_val, dict):
            msgpack_bytes = msgpack.dumps(python_val)
            return Literal(scalar=Scalar(binary=Binary(value=msgpack_bytes, tag=MESSAGEPACK)))

        if not dataclasses.is_dataclass(python_val):
            raise TypeTransformerFailedError(
                f"{type(python_val)} is not of type @dataclass, only Dataclasses are supported for "
                f"user defined datatypes in Flytekit"
            )

        self._make_dataclass_serializable(python_val, python_type)

        # The `to_json` integrated through mashumaro's `DataClassJSONMixin` allows for more
        # functionality than JSONEncoder
        # We can't use hasattr(python_val, "to_json") here because we rely on mashumaro's API to customize the serialization behavior for Flyte types.
        if isinstance(python_val, DataClassJSONMixin):
            json_str = python_val.to_json()
            dict_obj = json.loads(json_str)
            msgpack_bytes = msgpack.dumps(dict_obj)
        else:
            # The function looks up or creates a MessagePackEncoder specifically designed for the object's type.
            # This encoder is then used to convert a data class into MessagePack Bytes.
            try:
                encoder = self._msgpack_encoder[python_type]
            except KeyError:
                encoder = MessagePackEncoder(python_type)
                self._msgpack_encoder[python_type] = encoder

            try:
                msgpack_bytes = encoder.encode(python_val)
            except NotImplementedError:
                # you can refer FlyteFile, FlyteDirectory and StructuredDataset to see how flyte types can be implemented.
                raise NotImplementedError(
                    f"{python_type} should inherit from mashumaro.types.SerializableType"
                    f" and implement _serialize and _deserialize methods."
                )

        return Literal(scalar=Scalar(binary=Binary(value=msgpack_bytes, tag=MESSAGEPACK)))

    def _get_origin_type_in_annotation(self, python_type: Type[T]) -> Type[T]:
        # dataclass will try to hash python type when calling dataclass.schema(), but some types in the annotation is
        # not hashable, such as Annotated[StructuredDataset, kwtypes(...)]. Therefore, we should just extract the origin
        # type from annotated.
        if get_origin(python_type) is list:
            return typing.List[self._get_origin_type_in_annotation(get_args(python_type)[0])]  # type: ignore
        elif get_origin(python_type) is dict:
            return typing.Dict[  # type: ignore
                self._get_origin_type_in_annotation(get_args(python_type)[0]),
                self._get_origin_type_in_annotation(get_args(python_type)[1]),
            ]
        elif is_annotated(python_type):
            return get_args(python_type)[0]
        elif dataclasses.is_dataclass(python_type):
            for field in dataclasses.fields(copy.deepcopy(python_type)):
                field.type = self._get_origin_type_in_annotation(field.type)
        return python_type

    def _make_dataclass_serializable(self, python_val: T, python_type: Type[T]) -> typing.Any:
        """
        If any field inside the dataclass is flyte type, we should use flyte type transformer for that field.
        Since Flyte types are already serializable, this function is intended for using strings instead of directly creating Flyte files and directories in the dataclass.
        An example shows the lifecycle:

        @dataclass
        class DC:
            ff: FlyteFile

        @task
        def t1() -> DC:
            return DC(ff="s3://path")

        Lifecycle: DC(ff="s3://path") -> to_literal() -> DC(ff=FlyteFile(path="s3://path")) -> msgpack -> to_python_value() -> DC(ff=FlyteFile(path="s3://path"))
        """
        from flytekit.types.directory import FlyteDirectory
        from flytekit.types.file import FlyteFile
        from flytekit.types.structured import StructuredDataset

        # Handle Optional and Union Types
        if _is_union_type(python_type):

            def get_expected_type(python_val: T, types: tuple) -> Type[T | None]:
                if len(set(types) & {FlyteFile, FlyteDirectory, StructuredDataset}) > 1:
                    raise ValueError(
                        "Cannot have more than one Flyte type in the Union when attempting to use the string shortcut. Please specify the full object (e.g. FlyteFile(...)) instead of just passing a string."
                    )

                for t in types:
