import dataclasses
import typing
from enum import Enum

from pydantic import BaseModel

from flytekit.core.context_manager import FlyteContext
from flytekit.core.type_engine import TypeEngine, _get_element_type

# -- Models --


class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Inner(BaseModel):
    name: str
    value: int


class ListOfLists(BaseModel):
    matrix: typing.List[typing.List[int]]


class ListOfDicts(BaseModel):
    records: typing.List[typing.Dict[str, int]]


class DictOfDicts(BaseModel):
    nested_map: typing.Dict[str, typing.Dict[str, int]]


class ListOfListOfModels(BaseModel):
    nested: typing.List[typing.List[Inner]]


class ListOfDictOfModels(BaseModel):
    records: typing.List[typing.Dict[str, Inner]]


class DictOfDictOfModels(BaseModel):
    nested_map: typing.Dict[str, typing.Dict[str, Inner]]


class ModelWithEnum(BaseModel):
    name: str
    status: Status


class ListOfEnumModels(BaseModel):
    jobs: typing.List[ModelWithEnum]


class DictOfEnumModels(BaseModel):
    jobs_by_id: typing.Dict[str, ModelWithEnum]


class ComplexModel(BaseModel):
    """Combines lists, dicts, enums, and nested models all together."""

    nested_list: typing.List[typing.List[Inner]]
    dict_of_models: typing.Dict[str, Inner]
    list_of_dicts: typing.List[typing.Dict[str, int]]
    enum_models: typing.List[ModelWithEnum]
    optional_inner: typing.Optional[Inner] = None


class ListOfOptionalModels(BaseModel):
    items: typing.List[typing.Optional[Inner]]


# -- Nested arrays --


def test_list_of_list_of_int_schema():
    """List[List[int]] should resolve the inner element to List[int], not str."""
    schema = ListOfLists.model_json_schema()
