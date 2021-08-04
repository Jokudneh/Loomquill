import sys
import typing

import pytest
from typing_extensions import Annotated

from flytekit import kwtypes
from flytekit.core.context_manager import FlyteContextManager
from flytekit.core.type_engine import LiteralsResolver, TypeEngine
from flytekit.models import interface as interface_models
from flytekit.models.literals import Literal, LiteralCollection, LiteralMap, Primitive, Scalar
from flytekit.types.structured.structured_dataset import StructuredDataset
from flytekit.core.interface import Interface


@pytest.mark.parametrize(
    "literal_value,python_type,expected_python_value",
    [
        (
            Literal(
                collection=LiteralCollection(
                    literals=[
                        Literal(scalar=Scalar(primitive=Primitive(integer=1))),
                        Literal(scalar=Scalar(primitive=Primitive(integer=2))),
                        Literal(scalar=Scalar(primitive=Primitive(integer=3))),
                    ]
                )
            ),
            typing.List[int],
            [1, 2, 3],
        ),
        (
            Literal(
                map=LiteralMap(
                    literals={
                        "k1": Literal(scalar=Scalar(primitive=Primitive(string_value="v1"))),
                        "k2": Literal(scalar=Scalar(primitive=Primitive(string_value="2"))),
                    },
                )
            ),
