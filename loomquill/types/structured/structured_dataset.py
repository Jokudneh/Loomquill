from __future__ import annotations

import _datetime
import collections
import json
import types
import typing
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, is_dataclass
from typing import Dict, Generator, Generic, List, Optional, Type, Union

import msgpack
from dataclasses_json import config
from fsspec.utils import get_protocol
from google.protobuf import json_format as _json_format
from google.protobuf.struct_pb2 import Struct
from marshmallow import fields
from mashumaro.mixins.json import DataClassJSONMixin
from mashumaro.types import SerializableType
from typing_extensions import Annotated, TypeAlias, get_args, get_origin

from flytekit import lazy_module
from flytekit.core.constants import MESSAGEPACK
from flytekit.core.context_manager import FlyteContext, FlyteContextManager
from flytekit.core.type_engine import AsyncTypeTransformer, TypeEngine, TypeTransformerFailedError, modify_literal_uris
from flytekit.deck.renderer import Renderable
from flytekit.extras.pydantic_transformer.decorator import model_serializer, model_validator
from flytekit.loggers import developer_logger, logger
from flytekit.models import literals
from flytekit.models import types as type_models
from flytekit.models.literals import Binary, Literal, Scalar, StructuredDatasetMetadata
from flytekit.models.types import LiteralType, SchemaType, StructuredDatasetType
from flytekit.utils.asyn import loop_manager

if typing.TYPE_CHECKING:
    import pandas as pd
    import pyarrow as pa
else:
    pd = lazy_module("pandas")
    pa = lazy_module("pyarrow")

T = typing.TypeVar("T")  # StructuredDataset type or a dataframe type
DF = typing.TypeVar("DF")  # Dataframe type

# For specifying the storage formats of StructuredDatasets. It's just a string, nothing fancy.
StructuredDatasetFormat: TypeAlias = str

# Storage formats
PARQUET: StructuredDatasetFormat = "parquet"
CSV: StructuredDatasetFormat = "csv"
GENERIC_FORMAT: StructuredDatasetFormat = ""
GENERIC_PROTOCOL: str = "generic protocol"


@dataclass
class StructuredDataset(SerializableType, DataClassJSONMixin):
    """
    This is the user facing StructuredDataset class. Please don't confuse it with the literals.StructuredDataset
    class (that is just a model, a Python class representation of the protobuf).
    """

    uri: typing.Optional[str] = field(default=None, metadata=config(mm_field=fields.String()))
    file_format: typing.Optional[str] = field(default=GENERIC_FORMAT, metadata=config(mm_field=fields.String()))

    def _serialize(self) -> Dict[str, Optional[str]]:
        # dataclass case
        lv = StructuredDatasetTransformerEngine().to_literal(
            FlyteContextManager.current_context(), self, type(self), None
        )
        sd = StructuredDataset(uri=lv.scalar.structured_dataset.uri)
        sd.file_format = lv.scalar.structured_dataset.metadata.structured_dataset_type.format
        return {
            "uri": sd.uri,
            "file_format": sd.file_format,
        }

    @classmethod
    def _deserialize(cls, value) -> "StructuredDataset":
        uri = value.get("uri", None)
        file_format = value.get("file_format", None)

        if uri is None:
            raise ValueError("StructuredDataset's uri and file format should not be None")

        return StructuredDatasetTransformerEngine().to_python_value(
            FlyteContextManager.current_context(),
            Literal(
                scalar=Scalar(
                    structured_dataset=literals.StructuredDataset(
                        metadata=StructuredDatasetMetadata(
                            structured_dataset_type=StructuredDatasetType(format=file_format)
                        ),
                        uri=uri,
                    )
                )
            ),
            cls,
        )

    @model_serializer
    def serialize_structured_dataset(self) -> Dict[str, Optional[str]]:
        # pydantic case
        lv = StructuredDatasetTransformerEngine().to_literal(
            FlyteContextManager.current_context(), self, type(self), None
        )
        sd = StructuredDataset(uri=lv.scalar.structured_dataset.uri)
        sd.file_format = lv.scalar.structured_dataset.metadata.structured_dataset_type.format
        return {
            "uri": sd.uri,
            "file_format": sd.file_format,
        }

    @model_validator(mode="after")
    def deserialize_structured_dataset(self, info) -> StructuredDataset:
        if info.context is None or info.context.get("deserialize") is not True:
            return self

        return StructuredDatasetTransformerEngine().to_python_value(
            FlyteContextManager.current_context(),
            Literal(
                scalar=Scalar(
                    structured_dataset=literals.StructuredDataset(
                        metadata=StructuredDatasetMetadata(
                            structured_dataset_type=StructuredDatasetType(format=self.file_format)
                        ),
                        uri=self.uri,
                    )
                )
            ),
            type(self),
        )

    @classmethod
    def columns(cls) -> typing.Dict[str, typing.Type]:
        return {}

    @classmethod
    def column_names(cls) -> typing.List[str]:
        return [k for k, v in cls.columns().items()]

    def __init__(
        self,
        dataframe: typing.Optional[typing.Any] = None,
        uri: typing.Optional[str] = None,
        metadata: typing.Optional[literals.StructuredDatasetMetadata] = None,
        **kwargs,
    ):
        self._dataframe = dataframe
        # Make these fields public, so that the dataclass transformer can set a value for it
        # https://github.com/flyteorg/flytekit/blob/bcc8541bd6227b532f8462563fe8aac902242b21/flytekit/core/type_engine.py#L298
        self.uri = uri
        # When dataclass_json runs from_json, we need to set it here, otherwise the format will be empty string
        self.file_format = kwargs["file_format"] if "file_format" in kwargs else GENERIC_FORMAT
        # This is a special attribute that indicates if the data was either downloaded or uploaded
        self._metadata = metadata
        # This is not for users to set, the transformer will set this.
        self._literal_sd: Optional[literals.StructuredDataset] = None
        # Not meant for users to set, will be set by an open() call
        self._dataframe_type: Optional[DF] = None  # type: ignore
        self._already_uploaded = False

    @property
    def dataframe(self) -> Optional[DF]:
        return self._dataframe

    @property
    def metadata(self) -> Optional[StructuredDatasetMetadata]:
        return self._metadata

    @property
    def literal(self) -> Optional[literals.StructuredDataset]:
        return self._literal_sd

    def open(self, dataframe_type: Type[DF]):
        from flytekit.types.structured import lazy_import_structured_dataset_handler

        """
        Load the handler if needed. For the use case like:
        @task
        def t1(sd: StructuredDataset):
          import pandas as pd
          sd.open(pd.DataFrame).all()

        pandas is imported inside the task, so pandnas handler won't be loaded during deserialization in type engine.
        """
        lazy_import_structured_dataset_handler()
        self._dataframe_type = dataframe_type
        return self

    def all(self) -> DF:  # type: ignore
        if self._dataframe_type is None:
            raise ValueError("No dataframe type set. Use open() to set the local dataframe type you want to use.")
        ctx = FlyteContextManager.current_context()

        if self.uri is not None and self.dataframe is None:
            expected = TypeEngine.to_literal_type(StructuredDataset)
            self._set_literal(ctx, expected)

        return flyte_dataset_transformer.open_as(ctx, self.literal, self._dataframe_type, self.metadata)

    def _set_literal(self, ctx: FlyteContext, expected: LiteralType) -> None:
        """
        Explicitly set the StructuredDataset Literal to handle the following cases:

        1. Read a dataframe from a StructuredDataset with an uri, for example:

        @task
        def return_sd() -> StructuredDataset:
            sd = StructuredDataset(uri="s3://my-s3-bucket/s3_flyte_dir/df.parquet", file_format="parquet")
            df = sd.open(pd.DataFrame).all()
            return df

        For details, please refer to this issue: https://github.com/flyteorg/flyte/issues/5954.

        2. Need access to self._literal_sd when converting task output LiteralMap back to flyteidl, please see:
        https://github.com/flyteorg/flytekit/blob/f938661ff8413219d1bea77f6914a58c302d5c6c/flytekit/bin/entrypoint.py#L326

        For details, please refer to this issue: https://github.com/flyteorg/flyte/issues/5956.
        """
        to_literal = loop_manager.synced(flyte_dataset_transformer.async_to_literal)
        self._literal_sd = to_literal(ctx, self, StructuredDataset, expected).scalar.structured_dataset
        if self.metadata is None:
            self._metadata = self._literal_sd.metadata

    def set_literal(self, ctx: FlyteContext, expected: LiteralType) -> None:
        """
        A public wrapper method to set the StructuredDataset Literal.

        This method provides external access to the internal _set_literal method.
        """
        return self._set_literal(ctx, expected)

    def iter(self) -> Generator[DF, None, None]:
        if self._dataframe_type is None:
            raise ValueError("No dataframe type set. Use open() to set the local dataframe type you want to use.")
        ctx = FlyteContextManager.current_context()
        return flyte_dataset_transformer.iter_as(
