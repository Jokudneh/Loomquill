import os
import tempfile
from dataclasses import dataclass
from typing import List

import msgpack
import pytest
from dataclasses_json import DataClassJsonMixin

from flytekit.configuration import Image, ImageConfig, SerializationSettings
from flytekit.core.context_manager import ExecutionState, FlyteContextManager
from flytekit.core.dynamic_workflow_task import dynamic
from flytekit.core.type_engine import TypeEngine
from flytekit.types.directory import FlyteDirectory
from flytekit.types.file import FlyteFile


@dataclass
class MyProxyConfiguration(DataClassJsonMixin):
    # File and directory paths kept as 'str' so Flyte doesn't manage these static resources
    splat_data_dir: str
    apriori_file: str


@dataclass
class MyProxyParameters(DataClassJsonMixin):
    id: str
    job_i_step: int


@dataclass
class MyAprioriConfiguration(DataClassJsonMixin):
    static_data_dir: FlyteDirectory
    external_data_dir: FlyteDirectory


@dataclass
class MyInput(DataClassJsonMixin):
    main_product: FlyteFile
    apriori_config: MyAprioriConfiguration
    proxy_config: MyProxyConfiguration
    proxy_params: MyProxyParameters


@pytest.fixture
def folders_and_files_setup():
    tmp_dir = tempfile.TemporaryDirectory()
    fd, path = tempfile.mkstemp(dir=tmp_dir.name)
    tmp_dir_static_data = tempfile.TemporaryDirectory()
    tmp_dir_external_data = tempfile.TemporaryDirectory()

    try:
        with os.fdopen(fd, "w") as tmp:
            tmp.write("Hello world")
        yield path, tmp_dir_static_data.name, tmp_dir_external_data.name
    finally:
        tmp_dir.cleanup()
        tmp_dir_static_data.cleanup()
        tmp_dir_external_data.cleanup()


