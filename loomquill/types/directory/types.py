from __future__ import annotations

import asyncio
import json
import os
import pathlib
import random
import typing
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
from typing import Any, Dict, Generator, Tuple
from uuid import UUID

import fsspec
import msgpack
from dataclasses_json import DataClassJsonMixin, config
from fsspec.utils import get_protocol
from google.protobuf import json_format as _json_format
from google.protobuf.struct_pb2 import Struct
from marshmallow import fields
from mashumaro.types import SerializableType

from flytekit.core.constants import MESSAGEPACK
from flytekit.core.context_manager import FlyteContext, FlyteContextManager
from flytekit.core.type_engine import (
    AsyncTypeTransformer,
    TypeEngine,
    TypeTransformerFailedError,
    get_batch_size,
)
from flytekit.exceptions.user import FlyteAssertion
from flytekit.extras.pydantic_transformer.decorator import (
    model_serializer,
    model_validator,
)
from flytekit.models import types as _type_models
from flytekit.models.core import types as _core_types
from flytekit.models.core.types import BlobType
from flytekit.models.literals import Binary, Blob, BlobMetadata, Literal, Scalar
from flytekit.models.types import LiteralType
from flytekit.types.file import FileExt, FlyteFile
from flytekit.utils.asyn import loop_manager

T = typing.TypeVar("T")
PathType = typing.Union[str, os.PathLike]


def noop(): ...


class _FlyteDirectoryDownloader:
    """Downloader for FlyteDirectory that uses current context when called."""

    def __init__(
        self, remote_path: str, local_path: str, is_multipart: bool = True, batch_size: typing.Optional[int] = None
    ):
        self.remote_path = remote_path
        self.local_path = local_path
        self.is_multipart = is_multipart
        self.batch_size = batch_size

    def __call__(self):
        """Download the directory using current context's synced get_data method."""
        current_ctx = FlyteContextManager.current_context()
        return current_ctx.file_access.get_data(
            remote_path=self.remote_path,
            local_path=self.local_path,
            is_multipart=self.is_multipart,
            batch_size=self.batch_size,
        )


@dataclass
class FlyteDirectory(SerializableType, DataClassJsonMixin, os.PathLike, typing.Generic[T]):
    path: PathType = field(default=None, metadata=config(mm_field=fields.String()))  # type: ignore
    """
    > [!WARNING]
    > This class should not be used on very large datasets, as merely listing the dataset will cause
        the entire dataset to be downloaded. Listing on S3 and other backend object stores is not consistent
        and we should not need data to be downloaded to list.

    Please first read through the comments on the {{< py_class_ref flytekit.types.file.FlyteFile >}} class as the
    implementation here is similar.

    One thing to note is that the ``os.PathLike`` type that comes with Python was used as a stand-in for ``FlyteFile``.
    That is, if a task's output signature is an ``os.PathLike``, Flyte takes that to mean ``FlyteFile``. There is no
    easy way to distinguish an ``os.PathLike`` where the user means a File and where the user means a Directory. As
    such, if you want to use a directory, you must declare all types as ``FlyteDirectory``. You'll still be able to
    return a string literal though instead of a full-fledged ``FlyteDirectory`` object assuming the str is a directory.

    **Converting from a Flyte literal value to a Python instance of FlyteDirectory**

    +-----------------------------+------------------------------------------------------------------------------------+
    | Type of Flyte IDL Literal   |    FlyteDirectory                                                                  |
    +=============+===============+====================================================================================+
    | Multipart   | uri matches   | FlyteDirectory object stores the original string                                   |
    | Blob        | http(s)/s3/gs | path, but points to a local file instead.                                          |
    |             |               |                                                                                    |
    |             |               | * [fn] downloader: function that writes to path when open'ed.                      |
    |             |               | * [fn] download: will trigger download                                             |
    |             |               | * path: randomly generated local path that will not exist until downloaded         |
    |             |               | * remote_path: None                                                                |
    |             |               | * remote_source: original http/s3/gs path                                          |
    |             |               |                                                                                    |
    |             +---------------+------------------------------------------------------------------------------------+
    |             | uri matches   | FlyteDirectory object just wraps the string                                        |
    |             | /local/path   |                                                                                    |
    |             |               | * [fn] downloader: noop function                                                   |
    |             |               | * [fn] download: raises exception                                                  |
    |             |               | * path: just the given path                                                        |
    |             |               | * remote_path: None                                                                |
    |             |               | * remote_source: None                                                              |
    +-------------+---------------+------------------------------------------------------------------------------------+

    -----------

    **Converting from a Python value (FlyteDirectory, str, or pathlib.Path) to a Flyte literal**

    +-----------------------------------+------------------------------------------------------------------------------+
    | Type of Python value              | FlyteDirectory                                                               |
    +===================+===============+==============================================================================+
    | str or            | path matches  | Blob object is returned with uri set to the given path.                      |
    | pathlib.Path or   | http(s)/s3/gs | Nothing is uploaded.                                                         |
    | FlyteDirectory    +---------------+------------------------------------------------------------------------------+
    |                   | path matches  | Contents of file are uploaded to the Flyte blob store (S3, GCS, etc.), in    |
    |                   | /local/path   | a bucket determined by the raw_output_data_prefix setting. If                |
    |                   |               | remote_path is given, then that is used instead of the random path. Blob     |
    |                   |               | object is returned with uri pointing to the blob store location.             |
    |                   |               |                                                                              |
    +-------------------+---------------+------------------------------------------------------------------------------+

    As inputs ::

        def t1(in1: FlyteDirectory):
            ...

        def t1(in1: FlyteDirectory["svg"]):
            ...

    As outputs:

    The contents of this local directory will be uploaded to the Flyte store. ::

        return FlyteDirectory("/path/to/dir/")

        return FlyteDirectory["svg"]("/path/to/dir/", remote_path="s3://special/output/location")

    Similar to the FlyteFile example, if you give an already remote location, it will not be copied to Flyte's
    durable store, the uri will just be stored as is. ::

        return FlyteDirectory("s3://some/other/folder")

    Note if you write a path starting with http/s, if anything ever tries to read it (i.e. use the literal
    as an input, it'll fail because the http proxy doesn't know how to download whole directories.

    The format [] bit is still there because in Flyte, directories are stored as Blob Types also, just like files, and
    the Blob type has the format field. The difference in the type field is represented in the ``dimensionality``
    field in the ``BlobType``.
    """

    def _serialize(self) -> typing.Dict[str, str]:
        lv = FlyteDirToMultipartBlobTransformer().to_literal(
            FlyteContextManager.current_context(), self, type(self), None
        )
        return {"path": lv.scalar.blob.uri}

    @classmethod
    def _deserialize(cls, value) -> "FlyteDirectory":
        return FlyteDirToMultipartBlobTransformer().dict_to_flyte_directory(dict_obj=value, expected_python_type=cls)
