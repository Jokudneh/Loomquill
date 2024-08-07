from datetime import datetime, timedelta, timezone

import pytest

from flytekit.models import literals
from flytekit.models import types as _types
from tests.flytekit.common import parameterizers


def test_retry_strategy():
    obj = literals.RetryStrategy(3)
    assert obj.retries == 3
    assert literals.RetryStrategy.from_flyte_idl(obj.to_flyte_idl()) == obj
    assert obj != literals.RetryStrategy(4)

    with pytest.raises(Exception):
        obj = literals.RetryStrategy(-1)
        obj.to_flyte_idl()


def test_void():
    obj = literals.Void()
    assert literals.Void.from_flyte_idl(obj.to_flyte_idl()) == obj
    assert literals.Void() == obj


def test_integer_primitive():
    obj = literals.Primitive(integer=1)
    assert obj.integer == 1
    assert obj.boolean is None
    assert obj.datetime is None
    assert obj.duration is None
    assert obj.float_value is None
    assert obj.string_value is None
    assert obj.value == 1
    assert obj != literals.Primitive(integer=0)
    assert obj != literals.Primitive(boolean=False)
    assert obj != literals.Primitive(datetime=datetime.now())
    assert obj != literals.Primitive(duration=timedelta(minutes=1))
    assert obj != literals.Primitive(float_value=1.0)
    assert obj != literals.Primitive(string_value="abc")

    obj2 = literals.Primitive.from_flyte_idl(obj.to_flyte_idl())
    assert obj == obj2
    assert obj2.integer == 1
    assert obj2.boolean is None
    assert obj2.datetime is None
    assert obj2.duration is None
    assert obj2.float_value is None
    assert obj2.string_value is None
    assert obj2.value == 1
    assert obj2 != literals.Primitive(integer=0)
    assert obj2 != literals.Primitive(boolean=False)
    assert obj2 != literals.Primitive(datetime=datetime.now())
    assert obj2 != literals.Primitive(duration=timedelta(minutes=1))
    assert obj2 != literals.Primitive(float_value=1.0)
    assert obj2 != literals.Primitive(string_value="abc")

    obj3 = literals.Primitive(integer=0)
    assert obj3.value == 0

    with pytest.raises(Exception):
        literals.Primitive(integer=1.0).to_flyte_idl()


def test_boolean_primitive():
    obj = literals.Primitive(boolean=True)
    assert obj.integer is None
    assert obj.boolean is True
    assert obj.datetime is None
    assert obj.duration is None
    assert obj.float_value is None
    assert obj.string_value is None
    assert obj.value is True
    assert obj != literals.Primitive(integer=0)
    assert obj != literals.Primitive(boolean=False)
    assert obj != literals.Primitive(datetime=datetime.now())
    assert obj != literals.Primitive(duration=timedelta(minutes=1))
    assert obj != literals.Primitive(float_value=1.0)
    assert obj != literals.Primitive(string_value="abc")

    obj2 = literals.Primitive.from_flyte_idl(obj.to_flyte_idl())
    assert obj == obj2
    assert obj2.integer is None
    assert obj2.boolean is True
    assert obj2.datetime is None
    assert obj2.duration is None
    assert obj2.float_value is None
    assert obj2.string_value is None
    assert obj2.value is True
    assert obj2 != literals.Primitive(integer=0)
    assert obj2 != literals.Primitive(boolean=False)
    assert obj2 != literals.Primitive(datetime=datetime.now())
    assert obj2 != literals.Primitive(duration=timedelta(minutes=1))
    assert obj2 != literals.Primitive(float_value=1.0)
    assert obj2 != literals.Primitive(string_value="abc")

    obj3 = literals.Primitive(boolean=False)
    assert obj3.value is False

    with pytest.raises(Exception):
        literals.Primitive(boolean=datetime.now()).to_flyte_idl()


def test_datetime_primitive():
    dt = datetime.now(timezone.utc)
    obj = literals.Primitive(datetime=dt)
    assert obj.integer is None
    assert obj.boolean is None
    assert obj.datetime == dt
    assert obj.duration is None
    assert obj.float_value is None
    assert obj.string_value is None
    assert obj.value == dt
    assert obj != literals.Primitive(integer=0)
    assert obj != literals.Primitive(boolean=False)
    assert obj != literals.Primitive(datetime=dt + timedelta(seconds=1))
    assert obj != literals.Primitive(duration=timedelta(minutes=1))
    assert obj != literals.Primitive(float_value=1.0)
    assert obj != literals.Primitive(string_value="abc")

    obj2 = literals.Primitive.from_flyte_idl(obj.to_flyte_idl())
    assert obj == obj2
    assert obj2.integer is None
    assert obj2.boolean is None
    assert obj2.datetime == dt
    assert obj2.duration is None
    assert obj2.float_value is None
    assert obj2.string_value is None
    assert obj2.value == dt
    assert obj2 != literals.Primitive(integer=0)
    assert obj2 != literals.Primitive(boolean=False)
    assert obj2 != literals.Primitive(datetime=dt + timedelta(seconds=1))
    assert obj2 != literals.Primitive(duration=timedelta(minutes=1))
    assert obj2 != literals.Primitive(float_value=1.0)
    assert obj2 != literals.Primitive(string_value="abc")

    with pytest.raises(Exception):
        literals.Primitive(datetime=1.0).to_flyte_idl()


def test_duration_primitive():
    duration = timedelta(seconds=1)
    obj = literals.Primitive(duration=duration)
    assert obj.integer is None
    assert obj.boolean is None
    assert obj.datetime is None
    assert obj.duration == duration
    assert obj.float_value is None
    assert obj.string_value is None
    assert obj.value == duration
    assert obj != literals.Primitive(integer=0)
    assert obj != literals.Primitive(boolean=False)
    assert obj != literals.Primitive(datetime=datetime.now())
    assert obj != literals.Primitive(duration=timedelta(minutes=1))
    assert obj != literals.Primitive(float_value=1.0)
    assert obj != literals.Primitive(string_value="abc")

    obj2 = literals.Primitive.from_flyte_idl(obj.to_flyte_idl())
    assert obj == obj2
    assert obj2.integer is None
    assert obj2.boolean is None
