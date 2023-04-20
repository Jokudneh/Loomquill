from __future__ import annotations

import json
import mimetypes
import os
import pathlib
import typing
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Dict, cast
from urllib.parse import unquote

import msgpack
from dataclasses_json import config
from google.protobuf import json_format as _json_format
from google.protobuf.struct_pb2 import Struct
from marshmallow import fields
from mashumaro.mixins.json import DataClassJSONMixin
from mashumaro.types import SerializableType

from flytekit.core.constants import MESSAGEPACK
from flytekit.core.context_manager import FlyteContext, FlyteContextManager
from flytekit.core.type_engine import (
    AsyncTypeTransformer,
    TypeEngine,
    TypeTransformerFailedError,
    get_underlying_type,
)
from flytekit.exceptions.user import FlyteAssertion
from flytekit.extras.pydantic_transformer.decorator import model_serializer, model_validator
from flytekit.loggers import logger
from flytekit.models.core import types as _core_types
from flytekit.models.core.types import BlobType
from flytekit.models.literals import Binary, Blob, BlobMetadata, Literal, Scalar
from flytekit.models.types import LiteralType
from flytekit.types.pickle.pickle import FlytePickleTransformer


def noop(): ...


class _FlyteFileDownloader:
    """Downloader for FlyteFile that uses current context when called."""

    def __init__(self, remote_path: str, local_path: str, is_multipart: bool = False):
        self.remote_path = remote_path
        self.local_path = local_path
        self.is_multipart = is_multipart

    def __call__(self):
        """Download the file using current context's synced get_data method."""
        current_ctx = FlyteContextManager.current_context()
        return current_ctx.file_access.get_data(
            remote_path=self.remote_path, local_path=self.local_path, is_multipart=self.is_multipart
        )


T = typing.TypeVar("T")


@dataclass
class FlyteFile(SerializableType, os.PathLike, typing.Generic[T], DataClassJSONMixin):
    path: typing.Union[str, os.PathLike] = field(default=None, metadata=config(mm_field=fields.String()))  # type: ignore
    metadata: typing.Optional[dict[str, str]] = None
    """
    Since there is no native Python implementation of files and directories for the Flyte Blob type, (like how int
    exists for Flyte's Integer type) we need to create one so that users can express that their tasks take
    in or return a file. There is ``pathlib.Path`` of course, (which is usable in Flytekit as a return value, though
    not a return type), but it made more sense to create a new type esp. since we can add on additional properties.

    Files (and directories) differ from the primitive types like floats and string in that Flytekit typically uploads
    the contents of the files to the blob store connected with your Flyte installation. That is, the Python native
    literal that represents a file is typically just the path to the file on the local filesystem. However in Flyte,
    an instance of a file is represented by a {{< py_class_ref Blob <flytekit.models.literals.Blob> >}} literal,
    with the ``uri`` field set to the location in the Flyte blob store (AWS/GCS etc.). Take a look at the
    :std:ref:`data handling doc <flyte:divedeep-data-management>` for a deeper discussion.

    We decided to not support ``pathlib.Path`` as an input/output type because if you wanted the automatic
    upload/download behavior, you should just use the ``FlyteFile`` type. If you do not, then a ``str`` works just as
    well.

    The prefix for where uploads go is set by the raw output data prefix setting, which should be set at registration
    time in the launch plan. See the option listed under ``flytectl register examples --help`` for more information.
    If not set in the launch plan, then your Flyte backend will specify a default. This default is itself configurable
    as well. Contact your Flyte platform administrators to change or ascertain the value.

    In short, if a task returns ``"/path/to/file"`` and the task's signature is set to return ``FlyteFile``, then the
    contents of ``/path/to/file`` are uploaded.

    You can also make it so that the upload does not happen. There are different types of
    task/workflow signatures. Keep in mind that in the backend, in Admin and in the blob store, there is only one type
    that represents files, the {{< py_class_ref Blob <flytekit.models.core.types.BlobType> >}} type.

    Whether the uploading happens or not, the behavior of the translation between Python native values and Flyte
    literal values depends on a few attributes:

    * The declared Python type in the signature. These can be
      * :class:`python:flytekit.FlyteFile`
      * :class:`python:os.PathLike`
      Note that ``os.PathLike`` is only a type in Python, you can't instantiate it.
    * The type of the Python native value we're returning. These can be
      * {{< py_class_ref flytekit.FlyteFile >}}
      * {{< py_class_ref pathlib.Path >}}
      * {{< py_class_ref str >}}
    * Whether the value being converted is a "remote" path or not. For instance, if a task returns a value of
      "http://www.google.com" as a ``FlyteFile``, obviously it doesn't make sense for us to try to upload that to the
      Flyte blob store. So no remote paths are uploaded. Flytekit considers a path remote if it starts with ``s3://``,
      ``gs://``, ``http(s)://``, or even ``file://``.

    **Converting from a Flyte literal value to a Python instance of FlyteFile**

    +-------------+---------------+---------------------------------------------+--------------------------------------+
    |             |               |              Expected Python type                                                  |
    +-------------+---------------+---------------------------------------------+--------------------------------------+
    | Type of Flyte IDL Literal   | FlyteFile                                   |  os.PathLike                         |
    +=============+===============+=============================================+======================================+
    | Blob        | uri matches   | FlyteFile object stores the original string |                                      |
    |             | http(s)/s3/gs | path, but points to a local file instead.   |                                      |
    |             |               |                                             |                                      |
    |             |               | * [fn] downloader: function that writes to  |                                      |
    |             |               |   path when open'ed.                        |                                      |
    |             |               | * [fn] download: will trigger               | Basically this signals Flyte should  |
    |             |               |   download                                  | stay out of the way. You still get   |
    |             |               | * path: randomly generated local path that  | a FlyteFile object (which implements |
    |             |               |   will not exist until downloaded           | the os.PathLike interface)           |
    |             |               | * remote_path: None                         |                                      |
    |             |               | * remote_source: original http/s3/gs path   | * [fn] downloader: noop function,    |
    |             |               |                                             |   even if it's http/s3/gs            |
    |             +---------------+---------------------------------------------+ * [fn] download: raises              |
    |             | uri matches   | FlyteFile object just wraps the string      |   exception                          |
    |             | /local/path   |                                             | * path: just the given path          |
    |             |               | * [fn] downloader: noop function            | * remote_path: None                  |
    |             |               | * [fn] download: raises exception           | * remote_source: None                |
    |             |               | * path: just the given path                 |                                      |
    |             |               | * remote_path: None                         |                                      |
    |             |               | * remote_source: None                       |                                      |
    +-------------+---------------+---------------------------------------------+--------------------------------------+

    **Converting from a Python value (FlyteFile, str, or pathlib.Path) to a Flyte literal**

    +-------------+---------------+---------------------------------------------+--------------------------------------+
    |             |               |                               Expected Python type                                 |
    +-------------+---------------+---------------------------------------------+--------------------------------------+
    | Type of Python value        | FlyteFile                                   |  os.PathLike                         |
    +=============+===============+=============================================+======================================+
    | str or      | path matches  | Blob object is returned with uri set to the given path. No uploading happens.      |
    | pathlib.Path| http(s)/s3/gs |                                                                                    |
    |             +---------------+---------------------------------------------+--------------------------------------+
    |             | path matches  | Contents of file are uploaded to the Flyte  | No warning is logged since only a    |
    |             | /local/path   | blob store (S3, GCS, etc.), in a bucket     | string is given (as opposed to a     |
