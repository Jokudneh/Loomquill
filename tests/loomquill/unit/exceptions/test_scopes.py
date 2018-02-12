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
