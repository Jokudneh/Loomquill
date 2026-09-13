import pytest

from flytekit.exceptions import scopes, system, user
from flytekit.models.core import errors as _error_models


@scopes.user_entry_point
def _user_func(ex_to_raise):
    raise ex_to_raise


@scopes.system_entry_point
def _system_func(ex_to_raise):
    raise ex_to_raise


def test_base_scope():
    with pytest.raises(ValueError) as e:
        _user_func(ValueError("Bad value"))
    assert "Bad value" in str(e.value)

    with pytest.raises(ValueError) as e:
        _system_func(ValueError("Bad value"))
    assert "Bad value" in str(e.value)

    with pytest.raises(user.FlyteAssertion) as e:
        _user_func(user.FlyteAssertion("Bad assert"))
    assert "Bad assert" in str(e.value)

    with pytest.raises(system.FlyteSystemAssertion) as e:
        _user_func(system.FlyteSystemAssertion("Bad assert"))
    assert "Bad assert" in str(e.value)

    with pytest.raises(user.FlyteAssertion) as e:
        _system_func(user.FlyteAssertion("Bad assert"))
    assert "Bad assert" in str(e.value)

    with pytest.raises(system.FlyteSystemAssertion) as e:
        _system_func(system.FlyteSystemAssertion("Bad assert"))
    assert "Bad assert" in str(e.value)


@scopes.user_entry_point
def test_intercepted_scope_non_flyte_exception():
    value_error = ValueError("Bad value")
    with pytest.raises(scopes.FlyteScopedUserException) as e:
        _user_func(value_error)

    e = e.value
    assert e.value == value_error
    assert "Bad value" in e.verbose_message
    assert "User error." in e.verbose_message
