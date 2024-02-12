from flytekit.exceptions import base, system


def test_flyte_system_exception():
    try:
        base_exn = Exception("system exploded somewhere else")
        raise system.FlyteSystemException("bad") from base_exn
    except Exception as e:
        assert str(e) == "SYSTEM:Unknown: error=bad, cause=system exploded somewhere else"
        assert isinstance(type(e), base._FlyteCodedExceptionMetaclass)
        assert type(e).error_code == "SYSTEM:Unknown"
        assert isinstance(e, base.FlyteException)


def test_flyte_not_implemented_exception():
    try:
        base_exn = Exception("somewhere else didn't implement this")
        raise system.FlyteNotImplementedException("I'm lazy so I didn't implement this.") from base_exn
    except Exception as e:
        assert (
            str(e)
            == "SYSTEM:NotImplemented: error=I'm lazy so I didn't implement this., cause=somewhere else didn't implement this"
        )
        assert isinstance(e, NotImplementedError)
        assert type(e).error_code == "SYSTEM:NotImplemented"
        assert isinstance(e, system.FlyteSystemException)


def test_flyte_entrypoint_not_loadable_exception():
    try:
        base_exn = Exception("somewhere else couldn't load this")
        raise system.FlyteEntrypointNotLoadable("fake.module") from base_exn
    except Exception as e:
