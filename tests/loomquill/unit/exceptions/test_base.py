from flytekit.exceptions import base


def test_flyte_exception():
    try:
        raise base.FlyteException("bad")
