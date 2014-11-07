import mock

from flytekit.core.task import task


@mock.patch("flytekit.remote.remote.FlyteRemote")
def test_mocking_remote(mock_remote) -> None:
