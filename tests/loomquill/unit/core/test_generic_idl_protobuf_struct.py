import sys
import tempfile
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List

import pytest
from flytekit import task, workflow
from flytekit.types.file import FlyteFile
from flytekit.types.directory import FlyteDirectory
from flytekit.types.structured import StructuredDataset
from flytekit.types.schema import FlyteSchema
from flytekit import task, workflow
from enum import Enum


@pytest.fixture
def local_tmp_file():
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt") as tmp_file:
        tmp_file.write("Hello World!")
        tmp_file.flush()
        tmp_file_path = tmp_file.name

        yield tmp_file_path


@pytest.fixture
def local_tmp_dir():
    with tempfile.TemporaryDirectory() as tmp_dir:
        with open(Path(tmp_dir) / "example.txt", "w") as f:
            f.write("Hello World!")

        yield tmp_dir


@pytest.fixture
def local_pqt_file():
    return Path(__file__).parents[2] / "integration/remote/workflows/basic/data/df.parquet"


@pytest.mark.skipif("pandas" not in sys.modules, reason="Pandas is not installed.")
def test_all_dc_attrs(local_tmp_file, local_tmp_dir, local_pqt_file):
    import os
    import pandas as pd

    # Enable generating protobuf struct in the generic IDL
    # Please refer to https://github.com/flyteorg/flyte/issues/5959
    os.environ["FLYTE_USE_OLD_DC_FORMAT"] = "True"


    class Status(Enum):
        PENDING = "pending"
        APPROVED = "approved"
        REJECTED = "rejected"

    @dataclass
    class InnerDC:
        a: int = -1
        b: float = 2.1
        c: str = "Hello, Flyte"
        d: bool = False
        e: List[int] = field(default_factory=lambda: [0, 1, 2, -1, -2])
        f: List[FlyteFile] = field(default_factory=lambda: [FlyteFile(local_tmp_file)])
        g: List[List[int]] = field(default_factory=lambda: [[0], [1], [-1]])
        h: List[Dict[int, bool]] = field(default_factory=lambda: [{0: False}, {1: True}, {-1: True}])
        i: Dict[int, bool] = field(default_factory=lambda: {0: False, 1: True, -1: False})
        j: Dict[int, FlyteFile] = field(default_factory=lambda: {
            0: FlyteFile(local_tmp_file), 1: FlyteFile(local_tmp_file), -1: FlyteFile(local_tmp_file)
        })
        k: Dict[int, List[int]] = field(default_factory=lambda: {0: [0, 1, -1]})
        l: Dict[int, Dict[int, int]] = field(default_factory=lambda: {1: {-1: 0}})
        m: dict = field(default_factory=lambda: {"key": "value"})
        n: FlyteFile = field(default_factory=lambda: FlyteFile(local_tmp_file))
        o: FlyteDirectory = field(default_factory=lambda: FlyteDirectory(local_tmp_dir))
        enum_status: Status = field(default=Status.PENDING)
        sd: StructuredDataset = field(default_factory=lambda: StructuredDataset(uri=local_pqt_file, file_format="parquet"))
        fsc: FlyteSchema = field(default_factory=lambda: FlyteSchema(local_path=local_pqt_file))

    @dataclass
    class DC:
        a: int = -1
        b: float = 2.1
        c: str = "Hello, Flyte"
        d: bool = False
        e: List[int] = field(default_factory=lambda: [0, 1, 2, -1, -2])
        f: List[FlyteFile] = field(default_factory=lambda: [FlyteFile(local_tmp_file)])
        g: List[List[int]] = field(default_factory=lambda: [[0], [1], [-1]])
        h: List[Dict[int, bool]] = field(default_factory=lambda: [{0: False}, {1: True}, {-1: True}])
        i: Dict[int, bool] = field(default_factory=lambda: {0: False, 1: True, -1: False})
        j: Dict[int, FlyteFile] = field(default_factory=lambda: {
            0: FlyteFile(local_tmp_file), 1: FlyteFile(local_tmp_file), -1: FlyteFile(local_tmp_file)
        })
        k: Dict[int, List[int]] = field(default_factory=lambda: {0: [0, 1, -1]})
        l: Dict[int, Dict[int, int]] = field(default_factory=lambda: {1: {-1: 0}})
        m: dict = field(default_factory=lambda: {"key": "value"})
        n: FlyteFile = field(default_factory=lambda: FlyteFile(local_tmp_file))
        o: FlyteDirectory = field(default_factory=lambda: FlyteDirectory(local_tmp_dir))
        enum_status: Status = field(default=Status.PENDING)
        sd: StructuredDataset = field(default_factory=lambda: StructuredDataset(uri=local_pqt_file, file_format="parquet"))
        fsc: FlyteSchema = field(default_factory=lambda: FlyteSchema(local_path=local_pqt_file))

        # Define a nested dataclass
        inner_dc: InnerDC = field(default_factory=lambda: InnerDC())
