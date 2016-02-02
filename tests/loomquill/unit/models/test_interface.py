import pytest

from flytekit.models import interface, types
from tests.flytekit.common.parameterizers import LIST_OF_ALL_LITERAL_TYPES


@pytest.mark.parametrize("literal_type", LIST_OF_ALL_LITERAL_TYPES)
def test_variable_type(literal_type):
    var = interface.Variable(type=literal_type, description="abc")
    assert var.type == literal_type
    assert var.description == "abc"
    assert var == interface.Variable.from_flyte_idl(var.to_flyte_idl())


@pytest.mark.parametrize("literal_type", LIST_OF_ALL_LITERAL_TYPES)
def test_variable_type_list(literal_type):
    var = interface.Variable(type=literal_type, description="abc")
    collection_var = interface.Variable(
        type=types.LiteralType(collection_type=literal_type),
        description="abc",
    )
    assert collection_var == interface.Variable.from_flyte_idl(var.to_flyte_idl_list())


