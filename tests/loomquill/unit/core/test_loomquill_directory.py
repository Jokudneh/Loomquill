import os
import pathlib
import pickle
import shutil
import tempfile
import typing
from dataclasses import dataclass
from unittest.mock import MagicMock

import mock
import pytest

import flytekit.configuration
from flytekit.configuration import Config, Image, ImageConfig
from flytekit.core import context_manager
from flytekit.core.context_manager import ExecutionState, FlyteContextManager
from flytekit.core.data_persistence import FileAccessProvider
from flytekit.core.dynamic_workflow_task import dynamic
from flytekit.core.task import task
from flytekit.core.type_engine import TypeEngine
from flytekit.core.workflow import workflow
from flytekit.exceptions.user import FlyteAssertion
from flytekit.models.core.types import BlobType
from flytekit.models.literals import LiteralMap, Blob, BlobMetadata
from flytekit.types.directory.types import FlyteDirectory, FlyteDirToMultipartBlobTransformer
from google.protobuf import json_format as _json_format
from google.protobuf import struct_pb2 as _struct
from flytekit.models.literals import Literal, Scalar
import json

# Fixture that ensures a dummy local file


@pytest.fixture
def local_dummy_directory():
    temp_dir = tempfile.TemporaryDirectory()
    try:
        with open(os.path.join(temp_dir.name, "file"), "w") as tmp:
            tmp.write("Hello world")
        yield temp_dir.name
    finally:
        temp_dir.cleanup()


def test_engine():
    t = FlyteDirectory
    lt = TypeEngine.to_literal_type(t)
    assert lt.blob is not None
    assert lt.blob.dimensionality == BlobType.BlobDimensionality.MULTIPART
    assert lt.blob.format == ""

    t2 = FlyteDirectory["csv"]
    lt = TypeEngine.to_literal_type(t2)
    assert lt.blob is not None
    assert lt.blob.dimensionality == BlobType.BlobDimensionality.MULTIPART
    assert lt.blob.format == "csv"


def test_transformer_to_literal_local():
    random_dir = context_manager.FlyteContext.current_context(
    ).file_access.get_random_local_directory()
    fs = FileAccessProvider(
        local_sandbox_dir=random_dir,
        raw_output_prefix=os.path.join(
            random_dir,
            "raw"))
    ctx = context_manager.FlyteContext.current_context()
    with context_manager.FlyteContextManager.with_context(ctx.with_file_access(fs)) as ctx:
        p = tempfile.mkdtemp(prefix="temp_example_")

        # Create an empty directory and call to literal on it
        if os.path.exists(p):
            shutil.rmtree(p)
        pathlib.Path(p).mkdir(parents=True)

        tf = FlyteDirToMultipartBlobTransformer()
        lt = tf.get_literal_type(FlyteDirectory)
        literal = tf.to_literal(ctx, FlyteDirectory(p), FlyteDirectory, lt)
        assert literal.scalar.blob.uri.startswith(random_dir)

        # Create a FlyteDirectory where remote_directory is False
        literal = tf.to_literal(
            ctx,
            FlyteDirectory(
                p,
                remote_directory=False),
            FlyteDirectory,
            lt)
        assert literal.scalar.blob.uri.startswith(p)

        # Create a director with one file in it
        if os.path.exists(p):
            shutil.rmtree(p)
        pathlib.Path(p).mkdir(parents=True)
        with open(os.path.join(p, "xyz"), "w") as fh:
            fh.write("Hello world\n")
        literal = tf.to_literal(ctx, FlyteDirectory(p), FlyteDirectory, lt)

        mock_remote_files = os.listdir(literal.scalar.blob.uri)
        assert mock_remote_files == ["xyz"]

        # The only primitives allowed are strings
        with pytest.raises(AssertionError):
            tf.to_literal(ctx, 3, FlyteDirectory, lt)

        with pytest.raises(TypeError, match="No automatic conversion from <class 'int'>"):
            TypeEngine.to_literal(ctx, 3, FlyteDirectory, lt)


def test_transformer_to_literal_local_path():
    random_dir = context_manager.FlyteContext.current_context(
    ).file_access.get_random_local_directory()
    fs = FileAccessProvider(
        local_sandbox_dir=random_dir,
        raw_output_prefix=os.path.join(
            random_dir,
            "raw"))
    ctx = context_manager.FlyteContext.current_context()
    with context_manager.FlyteContextManager.with_context(ctx.with_file_access(fs)) as ctx:
        tf = FlyteDirToMultipartBlobTransformer()
        lt = tf.get_literal_type(FlyteDirectory)
        # Can't use if it's not a directory
        with pytest.raises(FlyteAssertion):
            p = ctx.file_access.get_random_local_path()
            path = pathlib.Path(p)
            try:
                path.unlink()
