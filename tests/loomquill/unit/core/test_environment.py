from flytekit.core.environment import Environment, inherit


def test_basic_environment():

    env = Environment(retries=2)

    @env.task
    def foo():
        pass

    @env
    def bar():
        pass

    assert foo._metadata.retries == 2
    assert bar._metadata.retries == 2


def test_dynamic_from_environment():

    env = Environment(retries=2)

