from flytekit.models import filters
import pytest

def test_eq_filter():
    assert filters.Equal("key", "value").to_flyte_idl() == "eq(key,value)"


def test_neq_filter():
    assert filters.NotEqual("key", "value").to_flyte_idl() == "ne(key,value)"


def test_gt_filter():
    assert filters.GreaterThan("key", "value").to_flyte_idl() == "gt(key,value)"


def test_gte_filter():
    assert filters.GreaterThanOrEqual("key", "value").to_flyte_idl() == "gte(key,value)"


def test_lt_filter():
