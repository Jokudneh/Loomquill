import dataclasses
import datetime
import enum
import importlib
import importlib.util
import json
import logging
import os
import pathlib
import sys
import types
import typing
import typing as t
from typing import cast, get_args

import rich_click as click
import yaml
from click import Parameter
from click import __version__ as click_version
from dataclasses_json import DataClassJsonMixin, dataclass_json
from packaging.version import Version
from pytimeparse import parse

from flytekit import BlobType, FlyteContext, Literal, LiteralType, StructuredDataset
from flytekit.core.artifact import ArtifactQuery
from flytekit.core.data_persistence import FileAccessProvider
from flytekit.core.resources import Resources
from flytekit.core.type_engine import TypeEngine
from flytekit.models.types import SimpleType
from flytekit.remote.remote_fs import FlytePathResolver
from flytekit.types.directory import FlyteDirectory
from flytekit.types.file import FlyteFile
from flytekit.types.iterator.json_iterator import JSONIteratorTransformer
from flytekit.types.pickle.pickle import FlytePickleTransformer
from flytekit.types.schema.types import FlyteSchema


def is_pydantic_basemodel(python_type: typing.Type) -> bool:
    """
    Checks if the python type is a pydantic BaseModel
    """
    try:
        import pydantic  # noqa: F401
    except ImportError:
        return False
    else:
        try:
            from pydantic import BaseModel as BaseModelV2
            from pydantic.v1 import BaseModel as BaseModelV1

            return issubclass(python_type, BaseModelV1) or issubclass(python_type, BaseModelV2)
        except ImportError:
            from pydantic import BaseModel

        return issubclass(python_type, BaseModel)


def key_value_callback(_: typing.Any, param: str, values: typing.List[str]) -> typing.Optional[typing.Dict[str, str]]:
    """
    Callback for click to parse key-value pairs.
    """
    if not values:
        return None
    result = {}
    for v in values:
        if "=" not in v:
            raise click.BadParameter(f"Expected key-value pair of the form key=value, got {v}")
        k, v = v.split("=", 1)
        result[k.strip()] = v.strip()
    return result


def labels_callback(_: typing.Any, param: str, values: typing.List[str]) -> typing.Optional[typing.Dict[str, str]]:
    """
    Callback for click to parse labels.
    """
    if not values:
        return None
    result = {}
    for v in values:
        if "=" not in v:
            result[v.strip()] = ""
        else:
            k, v = v.split("=", 1)
            result[k.strip()] = v.strip()
    return result


def resource_callback(_: typing.Any, param: str, value: typing.Optional[str]) -> typing.Optional[Resources]:
    """
    Click callback to parse resource strings like 'cpu=1,mem=2Gi' into a Resources object
    """
    if not value:
        return None

    items = value.split(",")
    _allowed_keys = Resources.__annotations__.keys()
    result = {}
    for item in items:
        kv_split = item.split("=")
        if len(kv_split) != 2:
            raise click.BadParameter(
                f"Expected comma separated key-value pairs of the form 'key1=value1,key2=value2,...', got '{item}'"
            )
        k = kv_split[0].strip()
        v = kv_split[1].strip()
        if k not in _allowed_keys:
            raise click.BadParameter(f"Expected key to be one of {list(_allowed_keys)}, but got '{k}'")
        if k in result:
            raise click.BadParameter(f"Expected unique keys {list(_allowed_keys)}, but got '{k}' multiple times")
        result[k] = v

    return Resources(**result)


class DirParamType(click.ParamType):
    name = "directory path"

    def convert(
        self, value: typing.Any, param: typing.Optional[click.Parameter], ctx: typing.Optional[click.Context]
    ) -> typing.Any:
        if isinstance(value, ArtifactQuery):
            return value

        # set remote_directory to false if running pyflyte run locally. This makes sure that the original
        # directory is used and not a random one.
        remote_directory = None if getattr(ctx.obj, "is_remote", False) else False
