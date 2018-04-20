import typing as t

import pytest
from flytekitplugins.omegaconf.type_information import extract_node_type
from omegaconf import DictConfig, ListConfig, OmegaConf

from tests.conftest import ExampleConfig, ExampleConfigWithNonAnnotatedSubtree


class TestExtractNodeType:
    def test_extract_type_and_string_representation(self) -> None:
        """Tests type extraction and string representation."""

        python_val = OmegaConf.structured(ExampleConfig(union_key="1337", optional_key=None))

        # test int
        node_type, type_name = extract_node_type(python_val, key="int_key")
        assert node_type == int
        assert type_name == "builtins.int"

        # test union
        node_type, type_name = extract_node_type(python_val, key="union_key")
        assert node_type == t.Union[int, str]
        assert type_name == "typing.Union[builtins.int, builtins.str]"

        # test any
        node_type, type_name = extract_node_type(python_val, key="any_key")
