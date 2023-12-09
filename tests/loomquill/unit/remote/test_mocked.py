import mock

from flytekit.core.task import task


@mock.patch("flytekit.remote.remote.FlyteRemote")
def test_mocking_remote(mock_remote) -> None:
    """
    This is a test that showing one way to mock fetched tasks, since the flytekit.testing elements don't work on remote
    entities.
    """

