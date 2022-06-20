import tempfile
import typing
from dataclasses import dataclass
from typing import Type

import dolt_integrations.core as dolt_int
from dataclasses_json import DataClassJsonMixin
from google.protobuf.json_format import MessageToDict
from google.protobuf.struct_pb2 import Struct

from flytekit import FlyteContext, lazy_module
from flytekit.extend import TypeEngine, TypeTransformer
from flytekit.models import types as _type_models
from flytekit.models.literals import Literal, Scalar
from flytekit.models.types import LiteralType

# dolt_int = lazy_module("dolt_integrations")
dolt = lazy_module("doltcli")
pandas = lazy_module("pandas")


@dataclass
class DoltConfig(DataClassJsonMixin):
    db_path: str
    tablename: typing.Optional[str] = None
    sql: typing.Optional[str] = None
    io_args: typing.Optional[dict] = None
    branch_conf: typing.Optional[dolt_int.Branch] = None
    meta_conf: typing.Optional[dolt_int.Meta] = None
    remote_conf: typing.Optional[dolt_int.Remote] = None


@dataclass
class DoltTable(DataClassJsonMixin):
    config: DoltConfig
    data: typing.Optional[pandas.DataFrame] = None


class DoltTableNameTransformer(TypeTransformer[DoltTable]):
    def __init__(self):
        super().__init__(name="DoltTable", t=DoltTable)
