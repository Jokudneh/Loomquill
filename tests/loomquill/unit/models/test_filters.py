from flytekit.models import filters
import pytest

def test_eq_filter():
    assert filters.Equal("key", "value").to_flyte_idl() == "eq(key,value)"


def test_neq_filter():
    assert filters.NotEqual("key", "value").to_flyte_idl() == "ne(key,value)"

