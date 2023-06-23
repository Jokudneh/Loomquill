import os
import tempfile
import typing
from collections import OrderedDict
from pathlib import Path
import mock
import google.cloud.bigquery
import pytest
from fsspec.utils import get_protocol
from typing_extensions import Annotated

import flytekit.configuration
from flytekit.configuration import Image, ImageConfig
from flytekit.core.base_task import kwtypes
from flytekit.core.context_manager import ExecutionState, FlyteContext, FlyteContextManager
from flytekit.core.data_persistence import FileAccessProvider
from flytekit.core.task import task
from flytekit.core.type_engine import TypeEngine
from flytekit.core.workflow import workflow
from flytekit.lazy_import.lazy_module import is_imported
from flytekit.models import literals
from flytekit.models.literals import StructuredDatasetMetadata, Literal
from flytekit.models.types import LiteralType, SchemaType, SimpleType, StructuredDatasetType
from flytekit.tools.translator import get_serializable
from flytekit.types.structured.structured_dataset import (
    PARQUET,
    StructuredDataset,
    StructuredDatasetDecoder,
    StructuredDatasetEncoder,
    StructuredDatasetTransformerEngine,
    convert_schema_type_to_structured_dataset_type,
    extract_cols_and_format,
)

pd = pytest.importorskip("pandas")
pa = pytest.importorskip("pyarrow")

my_cols = kwtypes(w=typing.Dict[str, typing.Dict[str, int]],
                  x=typing.List[typing.List[int]], y=int, z=str)

fields = [("some_int", pa.int32()), ("some_string", pa.string())]
arrow_schema = pa.schema(fields)

serialization_settings = flytekit.configuration.SerializationSettings(
    project="proj",
    domain="dom",
    version="123",
    image_config=ImageConfig(Image(name="name", fqn="asdf/fdsa", tag="123")),
    env={},
)
df = pd.DataFrame({"Name": ["Tom", "Joseph"], "Age": [20, 22]})


def test_protocol():
    assert get_protocol("s3://my-s3-bucket/file") == "s3"
    assert get_protocol("/file") == "file"


def generate_pandas() -> pd.DataFrame:
    return pd.DataFrame({"name": ["Tom", "Joseph"], "age": [20, 22]})


@pytest.fixture
def local_tmp_pqt_file():
    df = generate_pandas()

    # Create a temporary parquet file
    with tempfile.NamedTemporaryFile(delete=False, mode="w+b", suffix=".parquet") as pqt_file:
        pqt_path = pqt_file.name
        df.to_parquet(pqt_path)

    yield pqt_path

    # Cleanup
    Path(pqt_path).unlink(missing_ok=True)


def test_formats_make_sense():
    @task
    def t1(a: pd.DataFrame) -> pd.DataFrame:
        print(a)
        return generate_pandas()

    # this should be an empty string format
    assert t1.interface.outputs["o0"].type.structured_dataset_type.format == ""
    assert t1.interface.inputs["a"].type.structured_dataset_type.format == ""

    ctx = FlyteContextManager.current_context()
    with FlyteContextManager.with_context(
        ctx.with_execution_state(
            ctx.new_execution_state().with_params(
                mode=ExecutionState.Mode.LOCAL_WORKFLOW_EXECUTION)
        )
    ):
        result = t1(a=generate_pandas())
        val = result.val.scalar.value
        assert val.metadata.structured_dataset_type.format == "parquet"


def test_setting_of_unset_formats():
    custom = Annotated[StructuredDataset, "parquet"]
    example = custom(dataframe=df, uri="/path")
    # It's okay that the annotation is not used here yet.
    assert example.file_format == ""

    @task
    def t2(path: str) -> StructuredDataset:
        sd = StructuredDataset(dataframe=df, uri=path)
        return sd

    @workflow
    def wf(path: str) -> StructuredDataset:
        return t2(path=path)

    with tempfile.TemporaryDirectory() as tmp_dir:
        fname = os.path.join(tmp_dir, "somewhere")
        res = wf(path=fname)
    # Now that it's passed through an encoder however, it should be set.
    assert res.file_format == "parquet"


def test_types_pandas():
    pt = pd.DataFrame
    lt = TypeEngine.to_literal_type(pt)
    assert lt.structured_dataset_type is not None
    assert lt.structured_dataset_type.format == ""
    assert lt.structured_dataset_type.columns == []

    pt = Annotated[pd.DataFrame, "csv"]
    lt = TypeEngine.to_literal_type(pt)
    assert lt.structured_dataset_type.format == "csv"


def test_annotate_extraction():
    xyz = Annotated[pd.DataFrame, "myformat"]
    a, b, c, d = extract_cols_and_format(xyz)
    assert a is pd.DataFrame
    assert b is None
    assert c == "myformat"
    assert d is None

    a, b, c, d = extract_cols_and_format(pd.DataFrame)
    assert a is pd.DataFrame
    assert b is None
    assert c == ""
    assert d is None


def test_types_annotated():
    pt = Annotated[pd.DataFrame, my_cols]
    lt = TypeEngine.to_literal_type(pt)
    assert len(lt.structured_dataset_type.columns) == 4
    assert lt.structured_dataset_type.columns[0].literal_type.map_value_type.map_value_type.simple == SimpleType.INTEGER
    assert (
        lt.structured_dataset_type.columns[1].literal_type.collection_type.collection_type.simple == SimpleType.INTEGER
    )
    assert lt.structured_dataset_type.columns[2].literal_type.simple == SimpleType.INTEGER
    assert lt.structured_dataset_type.columns[3].literal_type.simple == SimpleType.STRING

    pt = Annotated[pd.DataFrame, PARQUET, arrow_schema]
    lt = TypeEngine.to_literal_type(pt)
    assert lt.structured_dataset_type.external_schema_type == "arrow"
    assert "some_string" in str(
        lt.structured_dataset_type.external_schema_bytes)

    pt = Annotated[pd.DataFrame, kwtypes(a=None)]
    with pytest.raises(AssertionError, match="type None is currently not supported by StructuredDataset"):
        TypeEngine.to_literal_type(pt)


def test_types_sd():
    pt = StructuredDataset
    lt = TypeEngine.to_literal_type(pt)
    assert lt.structured_dataset_type is not None

    pt = Annotated[StructuredDataset, my_cols]
    lt = TypeEngine.to_literal_type(pt)
    assert len(lt.structured_dataset_type.columns) == 4

    pt = Annotated[StructuredDataset, my_cols, "csv"]
    lt = TypeEngine.to_literal_type(pt)
    assert len(lt.structured_dataset_type.columns) == 4
    assert lt.structured_dataset_type.format == "csv"

    pt = Annotated[StructuredDataset, {}, "csv"]
    lt = TypeEngine.to_literal_type(pt)
    assert len(lt.structured_dataset_type.columns) == 0
    assert lt.structured_dataset_type.format == "csv"


def test_retrieving():
    assert StructuredDatasetTransformerEngine.get_encoder(
        pd.DataFrame, "file", PARQUET) is not None
    # Asking for a generic means you're okay with any one registered for that
    # type assuming there's just one.
    assert StructuredDatasetTransformerEngine.get_encoder(
        pd.DataFrame, "file", ""
    ) is StructuredDatasetTransformerEngine.get_encoder(pd.DataFrame, "file", PARQUET)

    class TempEncoder(StructuredDatasetEncoder):
        def __init__(self, protocol):
            super().__init__(MyDF, protocol)

        def encode(self):
            ...

    StructuredDatasetTransformerEngine.register(
        TempEncoder("gs"), default_for_type=False)
    with pytest.raises(ValueError):
        StructuredDatasetTransformerEngine.register(
            TempEncoder("gs://"), default_for_type=False)

    with pytest.raises(ValueError, match="Use None instead"):
        e = TempEncoder("")
        e._protocol = ""
        StructuredDatasetTransformerEngine.register(e)

    class TempEncoder:
        pass

    with pytest.raises(TypeError, match="We don't support this type of handler"):
        StructuredDatasetTransformerEngine.register(
            TempEncoder, default_for_type=False)


def test_to_literal():
    ctx = FlyteContextManager.current_context()
    lt = TypeEngine.to_literal_type(pd.DataFrame)
    df = generate_pandas()

    fdt = StructuredDatasetTransformerEngine()

    lit = fdt.to_literal(ctx, df, python_type=pd.DataFrame, expected=lt)
