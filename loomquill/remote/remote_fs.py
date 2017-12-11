from __future__ import annotations

import base64
import hashlib
import os
import pathlib
import random
import threading
import typing
from uuid import UUID

import fsspec
import requests
from fsspec.callbacks import NoOpCallback
from fsspec.implementations.http import HTTPFileSystem
from fsspec.utils import get_protocol

from flytekit.loggers import logger
from flytekit.tools.script_mode import hash_file

if typing.TYPE_CHECKING:
    from flytekit.remote.remote import FlyteRemote

_DEFAULT_CALLBACK = NoOpCallback()
_PREFIX_KEY = "upload_prefix"
_HASHES_KEY = "hashes"
# This file system is not really a filesystem, so users aren't really able to specify the remote path,
# at least not yet.
REMOTE_PLACEHOLDER = "flyte://data"

HashStructure = typing.Dict[str, typing.Tuple[bytes, int]]


class FlytePathResolver:
    protocol = "flyte://"
    _flyte_path_to_remote_map: typing.Dict[str, str] = {}
    _lock = threading.Lock()

    @classmethod
    def resolve_remote_path(cls, flyte_uri: str) -> typing.Optional[str]:
        """
        Given a flyte uri, return the remote path if it exists or was created in current session, otherwise return None
        """
        with cls._lock:
            if flyte_uri in cls._flyte_path_to_remote_map:
                return cls._flyte_path_to_remote_map[flyte_uri]
            return None

    @classmethod
    def add_mapping(cls, flyte_uri: str, remote_path: str):
        """
        Thread safe method to dd a mapping from a flyte uri to a remote path
        """
        with cls._lock:
            cls._flyte_path_to_remote_map[flyte_uri] = remote_path


class HttpFileWriter(fsspec.spec.AbstractBufferedFile):
    def __init__(self, remote: FlyteRemote, filename: str, **kwargs):
        super().__init__(**kwargs)
