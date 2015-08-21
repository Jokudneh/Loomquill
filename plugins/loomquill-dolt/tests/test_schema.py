import pandas
import pytest
from flytekitplugins.dolt.schema import DoltConfig, DoltTable, DoltTableNameTransformer
from google.protobuf.struct_pb2 import Struct

from flytekit.models.literals import Literal, Scalar


def test_dolt_table_to_python_value(mocker):
    mocker.patch("dolt_integrations.core.save", return_value=True)
    table = DoltTable(data=pandas.DataFrame(), config=DoltConfig(db_path="p"))

    lv = DoltTableNameTransformer.to_literal(
        self=None,
        ctx=None,
        python_val=table,
        python_type=DoltTable,
        expected=None,
    )

    assert lv.scalar.generic["config"]["branch_conf"] is None


def test_dolt_table_to_literal(mocker):
    df = pandas.DataFrame()
