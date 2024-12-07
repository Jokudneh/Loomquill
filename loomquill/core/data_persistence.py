"""
The Data persistence module is used by core flytekit and most of the core TypeTransformers to manage data fetch & store,
between the durable backend store and the runtime environment. This is designed to be a pluggable system, with a default
simple implementation that ships with the core.
"""

import asyncio
import importlib
import io
import os
import pathlib
import tempfile
import typing
from time import sleep
from typing import Any, Dict, Optional, Union, cast
from uuid import UUID

import fsspec
from decorator import decorator
from fsspec.asyn import AsyncFileSystem
from fsspec.registry import known_implementations as fsspec_known_implementations
from fsspec.registry import registry as fsspec_registry
from fsspec.utils import get_protocol
from typing_extensions import Unpack

from flytekit import configuration
from flytekit.configuration import DataConfig
from flytekit.core.local_fsspec import FlyteLocalFileSystem
from flytekit.core.utils import timeit
from flytekit.exceptions.system import FlyteDownloadDataException, FlyteUploadDataException
from flytekit.exceptions.user import FlyteAssertion, FlyteDataNotFoundException
from flytekit.interfaces.random import random
from flytekit.loggers import logger
from flytekit.utils.asyn import loop_manager

# Refer to https://github.com/fsspec/s3fs/blob/50bafe4d8766c3b2a4e1fc09669cf02fb2d71454/s3fs/core.py#L198
# for key and secret
_FSSPEC_S3_KEY_ID = "key"
_FSSPEC_S3_SECRET = "secret"
_ANON = "anon"

Uploadable = typing.Union[str, os.PathLike, pathlib.Path, bytes, io.BufferedReader, io.BytesIO, io.StringIO]

# This is the default chunk size flytekit will use for writing to S3 and GCS. This is set to 25MB by default and is
# configurable by the user if needed. This is used when put() is called on filesystems.
_WRITE_SIZE_CHUNK_BYTES = int(os.environ.get("_F_P_WRITE_CHUNK_SIZE", "26214400"))  # 25 * 2**20


def s3_setup_args(s3_cfg: configuration.S3Config, anonymous: bool = False) -> Dict[str, Any]:
    kwargs: Dict[str, Any] = {
        "cache_regions": True,
    }
    if s3_cfg.access_key_id:
        kwargs[_FSSPEC_S3_KEY_ID] = s3_cfg.access_key_id

    if s3_cfg.secret_access_key:
        kwargs[_FSSPEC_S3_SECRET] = s3_cfg.secret_access_key

    # S3fs takes this as a special arg
    if s3_cfg.endpoint is not None:
        kwargs["client_kwargs"] = {"endpoint_url": s3_cfg.endpoint}

    if s3_cfg.adressing_style:
        kwargs["config_kwargs"] = {"s3": {"addressing_style": "virtual"}}

    if anonymous:
        kwargs[_ANON] = True

    return kwargs


def azure_setup_args(azure_cfg: configuration.AzureBlobStorageConfig, anonymous: bool = False) -> Dict[str, Any]:
    kwargs: Dict[str, Any] = {}

    if azure_cfg.account_name:
        kwargs["account_name"] = azure_cfg.account_name
    if azure_cfg.account_key:
        kwargs["account_key"] = azure_cfg.account_key
    if azure_cfg.client_id:
        kwargs["client_id"] = azure_cfg.client_id
    if azure_cfg.client_secret:
        kwargs["client_secret"] = azure_cfg.client_secret
    if azure_cfg.tenant_id:
        kwargs["tenant_id"] = azure_cfg.tenant_id
    kwargs[_ANON] = anonymous
    return kwargs


def get_fsspec_storage_options(
    protocol: str, data_config: typing.Optional[DataConfig] = None, anonymous: bool = False, **kwargs
) -> Dict[str, Any]:
    data_config = data_config or DataConfig.auto()

    if protocol == "file":
        return {"auto_mkdir": True, **kwargs}
    if protocol == "s3":
        return {**s3_setup_args(data_config.s3, anonymous=anonymous), **kwargs}
    if protocol == "gs":
        if anonymous:
            kwargs["token"] = _ANON
        return kwargs
    if protocol in ("abfs", "abfss"):
        return {**azure_setup_args(data_config.azure, anonymous=anonymous), **kwargs}
    return {}


# Protocols whose fsspec implementation flytekit passes implementation-specific kwargs to (s3fs, gcsfs, adlfs).
_CANONICAL_FS_PROTOCOLS = ("s3", "gs", "abfs", "abfss")


def _canonical_fs_class(protocol: str) -> type:
    """
    Returns the fsspec implementation to use for the protocol. flytekit relies on the constructor and call kwargs
    of fsspec's default implementations (e.g. s3fs.S3FileSystem for s3, and ContentType on put), so a registered
    implementation is only used if it extends the default one, as flytekitplugins-async-fsspec does. Otherwise,
    e.g. when another library has registered an unrelated implementation with clobber=True, the default is used.
    """
    impl = fsspec_known_implementations[protocol]
    module_name, class_name = impl["class"].rsplit(".", 1)
    try:
        default_cls = getattr(importlib.import_module(module_name), class_name)
    except ImportError as e:
        raise ImportError(impl.get("err")) from e
    registered_cls = fsspec_registry.get(protocol)
    if registered_cls is not None and issubclass(registered_cls, default_cls):
        return registered_cls
    return default_cls


def get_additional_fsspec_call_kwargs(protocol: typing.Union[str, tuple], method_name: str) -> Dict[str, Any]:
    """
    These are different from the setup args functions defined above. Those kwargs are applied when asking fsspec
    to create the filesystem. These kwargs returned here are for when the filesystem's methods are invoked.
