"""Tests for FlyteFile, FlyteDirectory, and StructuredDataset inside nested Pydantic models.

Verifies that these special types roundtrip correctly through
TypeEngine.to_literal / to_python_value when nested in containers
(List, Dict, Optional) within Pydantic BaseModel classes.
"""

import dataclasses
import typing

from pydantic import BaseModel

from flytekit.core.context_manager import FlyteContext
from flytekit.core.type_engine import TypeEngine
from flytekit.types.directory import FlyteDirectory
from flytekit.types.file import FlyteFile
from flytekit.types.structured import StructuredDataset

# -- Models --


class ModelWithFile(BaseModel):
    file: FlyteFile


class ModelWithDir(BaseModel):
    dir: FlyteDirectory


class ModelWithListOfFiles(BaseModel):
    files: typing.List[FlyteFile]


class ModelWithDictOfFiles(BaseModel):
    file_map: typing.Dict[str, FlyteFile]


class ModelWithListOfDirs(BaseModel):
    dirs: typing.List[FlyteDirectory]


class ModelWithDictOfDirs(BaseModel):
    dir_map: typing.Dict[str, FlyteDirectory]


class ModelWithNestedFiles(BaseModel):
    nested_files: typing.List[typing.List[FlyteFile]]


class ModelWithOptionalFile(BaseModel):
    file: typing.Optional[FlyteFile] = None


class ModelWithOptionalDir(BaseModel):
    dir: typing.Optional[FlyteDirectory] = None


class ModelWithStructuredDataset(BaseModel):
    df: StructuredDataset


class ModelWithListOfStructuredDatasets(BaseModel):
    dfs: typing.List[StructuredDataset]


class ModelWithOptionalStructuredDataset(BaseModel):
    df: typing.Optional[StructuredDataset] = None


class CombinedModel(BaseModel):
    files: typing.List[FlyteFile]
    dir_map: typing.Dict[str, FlyteDirectory]
    df: StructuredDataset
    optional_file: typing.Optional[FlyteFile] = None


# -- FlyteFile tests --


def test_file_in_model_roundtrip():
    ctx = FlyteContext.current_context()
    input_val = ModelWithFile(file=FlyteFile.from_source("s3://bucket/dummy.txt"))
    lit = TypeEngine.to_literal_type(ModelWithFile)
    lv = TypeEngine.to_literal(ctx, input_val, ModelWithFile, lit)
    assert lv

    pv = TypeEngine.to_python_value(ctx, lv, ModelWithFile)
    assert isinstance(pv.file, FlyteFile)
    assert pv.file._remote_source == "s3://bucket/dummy.txt"


def test_list_of_files_roundtrip():
    ctx = FlyteContext.current_context()
    input_val = ModelWithListOfFiles(
        files=[FlyteFile.from_source("s3://bucket/a.txt"), FlyteFile.from_source("s3://bucket/b.txt")]
    )
    lit = TypeEngine.to_literal_type(ModelWithListOfFiles)
    lv = TypeEngine.to_literal(ctx, input_val, ModelWithListOfFiles, lit)
    assert lv

    pv = TypeEngine.to_python_value(ctx, lv, ModelWithListOfFiles)
    assert len(pv.files) == 2
    assert pv.files[0]._remote_source == "s3://bucket/a.txt"
    assert pv.files[1]._remote_source == "s3://bucket/b.txt"


def test_dict_of_files_roundtrip():
    ctx = FlyteContext.current_context()
    input_val = ModelWithDictOfFiles(
        file_map={"x": FlyteFile.from_source("s3://bucket/c.txt"), "y": FlyteFile.from_source("s3://bucket/d.txt")}
    )
    lit = TypeEngine.to_literal_type(ModelWithDictOfFiles)
    lv = TypeEngine.to_literal(ctx, input_val, ModelWithDictOfFiles, lit)
    assert lv

    pv = TypeEngine.to_python_value(ctx, lv, ModelWithDictOfFiles)
    assert pv.file_map["x"]._remote_source == "s3://bucket/c.txt"
    assert pv.file_map["y"]._remote_source == "s3://bucket/d.txt"


def test_nested_list_of_files_roundtrip():
    ctx = FlyteContext.current_context()
    input_val = ModelWithNestedFiles(
        nested_files=[
            [FlyteFile.from_source("s3://bucket/a.txt")],
            [FlyteFile.from_source("s3://bucket/b.txt"), FlyteFile.from_source("s3://bucket/c.txt")],
        ]
    )
    lit = TypeEngine.to_literal_type(ModelWithNestedFiles)
    lv = TypeEngine.to_literal(ctx, input_val, ModelWithNestedFiles, lit)
    assert lv

    pv = TypeEngine.to_python_value(ctx, lv, ModelWithNestedFiles)
    assert len(pv.nested_files) == 2
    assert len(pv.nested_files[0]) == 1
    assert len(pv.nested_files[1]) == 2
    assert pv.nested_files[0][0]._remote_source == "s3://bucket/a.txt"
    assert pv.nested_files[1][0]._remote_source == "s3://bucket/b.txt"
    assert pv.nested_files[1][1]._remote_source == "s3://bucket/c.txt"


def test_optional_file_with_value_roundtrip():
    ctx = FlyteContext.current_context()
    input_val = ModelWithOptionalFile(file=FlyteFile.from_source("s3://bucket/e.txt"))
    lit = TypeEngine.to_literal_type(ModelWithOptionalFile)
    lv = TypeEngine.to_literal(ctx, input_val, ModelWithOptionalFile, lit)
    assert lv

    pv = TypeEngine.to_python_value(ctx, lv, ModelWithOptionalFile)
    assert isinstance(pv.file, FlyteFile)
