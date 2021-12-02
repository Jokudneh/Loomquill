import mock

from flytekit.clis.flyte_cli.main import _get_client
from flytekit.configuration import AuthType, PlatformConfig


@mock.patch("flytekit.clients.friendly.SynchronousFlyteClient")
@mock.patch("click.get_current_context")
def test_get_client(click_current_ctx, mock_flyte_client):
    # This class helps in the process of overriding __getitem__ in an object.
    class FlexiMock(mock.MagicMock):
