from collections import OrderedDict
from unittest import mock

from flytekitplugins.openai import ChatGPTTask

from flytekit.configuration import Image, ImageConfig, SerializationSettings
from flytekit.extend import get_serializable
from flytekit.models.types import SimpleType


async def mock_acreate(*args, **kwargs) -> str:
    mock_response = mock.MagicMock()
    mock_choice = mock.MagicMock()
    mock_choice.message.content = "mocked_message"
    mock_response.choices = [mock_choice]
    return mock_response


