import copy

import pytest
from enum import Enum
from dataclasses_json import DataClassJsonMixin
from mashumaro.mixins.json import DataClassJSONMixin
import os
import sys
import tempfile
from dataclasses import dataclass, fields, field
from typing import List, Dict, Optional, Union, Any
from typing_extensions import Annotated
from flytekit.types.schema import FlyteSchema
from flytekit.core.type_engine import TypeEngine
from flytekit.core.context_manager import FlyteContextManager
from flytekit.core.type_engine import DataclassTransformer
from flytekit import task, workflow
from flytekit.types.directory import FlyteDirectory
from flytekit.types.file import FlyteFile
from flytekit.types.structured import StructuredDataset

@pytest.fixture(autouse=True)
def prepare_env_variable():
    try:
        origin_env = copy.deepcopy(os.environ.copy())
        os.environ["FLYTE_USE_OLD_DC_FORMAT"] = "True"
        yield
    finally:
        os.environ = origin_env

@pytest.fixture
def local_dummy_txt_file():
    fd, path = tempfile.mkstemp(suffix=".txt")
    try:
        with os.fdopen(fd, "w") as tmp:
            tmp.write("Hello World")
        yield path
    finally:
        os.remove(path)

@pytest.fixture
def local_dummy_directory():
    temp_dir = tempfile.TemporaryDirectory()
    try:
        with open(os.path.join(temp_dir.name, "file"), "w") as tmp:
            tmp.write("Hello world")
        yield temp_dir.name
    finally:
        temp_dir.cleanup()

def test_dataclass():
    @dataclass
    class AppParams(DataClassJsonMixin):
        snapshotDate: str
        region: str
        preprocess: bool
        listKeys: List[str]

    @task
    def t1() -> AppParams:
        ap = AppParams(snapshotDate="4/5/2063", region="us-west-3", preprocess=False, listKeys=["a", "b"])
        return ap

    @workflow
    def wf() -> AppParams:
        return t1()

    res = wf()
    assert res.region == "us-west-3"


def test_dataclass_assert_works_for_annotated():
    @dataclass
    class MyDC(DataClassJSONMixin):
        my_str: str

    d = Annotated[MyDC, "tag"]
    DataclassTransformer().assert_type(d, MyDC(my_str="hi"))

def test_pure_dataclasses_with_python_types():
    @dataclass
    class DC:
        string: Optional[str] = None

    @dataclass
    class DCWithOptional:
        string: Optional[str] = None
        dc: Optional[DC] = None
        list_dc: Optional[List[DC]] = None
        list_list_dc: Optional[List[List[DC]]] = None
        dict_dc: Optional[Dict[str, DC]] = None
        dict_dict_dc: Optional[Dict[str, Dict[str, DC]]] = None
        dict_list_dc: Optional[Dict[str, List[DC]]] = None
        list_dict_dc: Optional[List[Dict[str, DC]]] = None

    @task
    def t1() -> DCWithOptional:
        return DCWithOptional(string="a", dc=DC(string="b"),
                              list_dc=[DC(string="c"), DC(string="d")],
                              list_list_dc=[[DC(string="e"), DC(string="f")]],
                              list_dict_dc=[{"g": DC(string="h"), "i": DC(string="j")},
                                            {"k": DC(string="l"), "m": DC(string="n")}],
                              dict_dc={"o": DC(string="p"), "q": DC(string="r")},
                              dict_dict_dc={"s": {"t": DC(string="u"), "v": DC(string="w")}},
                              dict_list_dc={"x": [DC(string="y"), DC(string="z")],
                                            "aa": [DC(string="bb"), DC(string="cc")]},)

    @task
    def t2() -> DCWithOptional:
        return DCWithOptional()

    output = DCWithOptional(string="a", dc=DC(string="b"),
                            list_dc=[DC(string="c"), DC(string="d")],
                            list_list_dc=[[DC(string="e"), DC(string="f")]],
                            list_dict_dc=[{"g": DC(string="h"), "i": DC(string="j")},
                                          {"k": DC(string="l"), "m": DC(string="n")}],
                            dict_dc={"o": DC(string="p"), "q": DC(string="r")},
                            dict_dict_dc={"s": {"t": DC(string="u"), "v": DC(string="w")}},
                            dict_list_dc={"x": [DC(string="y"), DC(string="z")],
                                          "aa": [DC(string="bb"), DC(string="cc")]}, )

    dc1 = t1()
    dc2 = t2()

    assert dc1 == output
    assert dc2.string is None
    assert dc2.dc is None

    DataclassTransformer().assert_type(DCWithOptional, dc1)
    DataclassTransformer().assert_type(DCWithOptional, dc2)


def test_pure_dataclasses_with_python_types_get_literal_type_and_to_python_value():
    @dataclass
    class DC:
        string: Optional[str] = None

    @dataclass
    class DCWithOptional:
        string: Optional[str] = None
        dc: Optional[DC] = None
        list_dc: Optional[List[DC]] = None
        list_list_dc: Optional[List[List[DC]]] = None
        dict_dc: Optional[Dict[str, DC]] = None
        dict_dict_dc: Optional[Dict[str, Dict[str, DC]]] = None
        dict_list_dc: Optional[Dict[str, List[DC]]] = None
        list_dict_dc: Optional[List[Dict[str, DC]]] = None

    ctx = FlyteContextManager.current_context()


    o = DCWithOptional()
    lt = TypeEngine.to_literal_type(DCWithOptional)
    lv = TypeEngine.to_literal(ctx, o, DCWithOptional, lt)
    assert lv is not None
    pv = TypeEngine.to_python_value(ctx, lv, DCWithOptional)
    assert isinstance(pv, DCWithOptional)
    DataclassTransformer().assert_type(DCWithOptional, pv)

    o = DCWithOptional(string="a", dc=DC(string="b"),
                      list_dc=[DC(string="c"), DC(string="d")],
                      list_list_dc=[[DC(string="e"), DC(string="f")]],
                      list_dict_dc=[{"g": DC(string="h"), "i": DC(string="j")},
                                    {"k": DC(string="l"), "m": DC(string="n")}],
                      dict_dc={"o": DC(string="p"), "q": DC(string="r")},
                      dict_dict_dc={"s": {"t": DC(string="u"), "v": DC(string="w")}},
                      dict_list_dc={"x": [DC(string="y"), DC(string="z")],
                                    "aa": [DC(string="bb"), DC(string="cc")]})
    lt = TypeEngine.to_literal_type(DCWithOptional)
    lv = TypeEngine.to_literal(ctx, o, DCWithOptional, lt)
    assert lv is not None
    pv = TypeEngine.to_python_value(ctx, lv, DCWithOptional)
    assert isinstance(pv, DCWithOptional)
    DataclassTransformer().assert_type(DCWithOptional, pv)


def test_pure_dataclasses_with_flyte_types(local_dummy_txt_file, local_dummy_directory):
    @dataclass
    class FlyteTypes:
        flytefile: Optional[FlyteFile] = None
        flytedir: Optional[FlyteDirectory] = None
        structured_dataset: Optional[StructuredDataset] = None

    @dataclass
    class NestedFlyteTypes:
        flytefile: Optional[FlyteFile] = None
        flytedir: Optional[FlyteDirectory] = None
