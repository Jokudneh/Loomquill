import pytest

from flytekit.exceptions import base, user


def test_flyte_user_exception():
    try:
        base_exn = Exception("everywhere is bad")
        raise user.FlyteUserException("bad") from base_exn
    except Exception as e:
        assert str(e) == "USER:Unknown: error=bad, cause=everywhere is bad"
        assert isinstance(type(e), base._FlyteCodedExceptionMetaclass)
        assert type(e).error_code == "USER:Unknown"
        assert isinstance(e, base.FlyteException)

def test_flyte_user_runtime_exception():
    try:
        base_exn = Exception("everywhere is bad")
        raise user.FlyteUserRuntimeException("bad") from base_exn
    except Exception as e:
        assert str(e) == "USER:RuntimeError: error=bad, cause=everywhere is bad"
        assert isinstance(type(e), base._FlyteCodedExceptionMetaclass)
        assert type(e).error_code == "USER:RuntimeError"
        assert isinstance(e, base.FlyteException)
        assert isinstance(e, user.FlyteUserRuntimeException)

def test_flyte_type_exception():
    try:
