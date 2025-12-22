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
        base_exn = Exception("Types need to be right!!!")
        raise user.FlyteTypeException(
            "int", "float", received_value=1, additional_msg="That was a bad idea!"
        ) from base_exn
    except Exception as e:
        assert (
            str(e) == "USER:TypeError: error=Type error!  Received: int with value: 1, Expected: float. "
            "That was a bad idea!, cause=Types need to be right!!!"
        )
        assert isinstance(e, TypeError)
        assert type(e).error_code == "USER:TypeError"
        assert isinstance(e, user.FlyteUserException)

