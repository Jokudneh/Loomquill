import datetime
import os
import typing
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from dataclasses_json import DataClassJsonMixin

from flytekit import FlyteContext, lazy_module
from flytekit.extend import TypeEngine, TypeTransformer
from flytekit.loggers import logger
from flytekit.models import types as _type_models
from flytekit.models.literals import Literal, Primitive, Scalar
from flytekit.models.types import LiteralType
from flytekit.types.file.file import FlyteFile, FlyteFilePathTransformer
from flytekit.types.schema.types import FlyteSchema, FlyteSchemaTransformer

from .task import BatchRequestConfig

ge = lazy_module("great_expectations")


@dataclass
class GreatExpectationsFlyteConfig(DataClassJsonMixin):
    """
    Use this configuration to configure GreatExpectations Plugin.

    Args:
        datasource_name: tell where your data lives and how to get it
        expectation_suite_name: suite which consists of the data expectations
        data_connector_name: connector to identify data batches
        data_asset_name: name of the data asset (to be used for RuntimeBatchRequest)
        local_file_path: dataset file path useful for FlyteFile and FlyteSchema
        checkpoint_params: optional SimpleCheckpoint parameters
        batch_request_config: batchrequest config
        context_root_dir: directory in which GreatExpectations' configuration resides
    """

    datasource_name: str
    expectation_suite_name: str
    data_connector_name: str
    data_asset_name: Optional[str] = None
    """
    local_file_path is a must in two scenrios:
    * When using FlyteSchema
    * When using FlyteFile for remote paths
    This is because base directory which has the dataset file 'must' be given in GreatExpectations' config file
    """
    local_file_path: Optional[str] = None
    checkpoint_params: Optional[Dict[str, Union[str, List[str]]]] = None
    batch_request_config: Optional[BatchRequestConfig] = None
    context_root_dir: str = "./great_expectations"


class GreatExpectationsType(object):
    """
    Use this class to send the GreatExpectationsFlyteConfig.

    Args:
        config: GreatExpectations Plugin configuration

    TODO: Connect Data Docs to Flyte Console.
    """

    @classmethod
    def config(cls) -> Tuple[Type, GreatExpectationsFlyteConfig]:
        return (
            str,
            GreatExpectationsFlyteConfig(datasource_name="", data_connector_name="", expectation_suite_name=""),
        )

    def __class_getitem__(cls, config: Tuple[Type, GreatExpectationsFlyteConfig]) -> Any:
        if not (isinstance(config, tuple) or len(config) != 2):
            raise AssertionError("GreatExpectationsType must have both datatype and GreatExpectationsFlyteConfig")

        class _GreatExpectationsTypeClass(GreatExpectationsType):
            __origin__ = GreatExpectationsType

            @classmethod
            def config(cls) -> Tuple[Type, GreatExpectationsFlyteConfig]:
                return config

        return _GreatExpectationsTypeClass


class GreatExpectationsTypeTransformer(TypeTransformer[GreatExpectationsType]):
    def __init__(self):
        super().__init__(name="GreatExpectations Transformer", t=GreatExpectationsType)

    @staticmethod
    def get_config(
        t: Type[GreatExpectationsType],
    ) -> Tuple[Type, GreatExpectationsFlyteConfig]:
        return t.config()
