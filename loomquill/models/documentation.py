from dataclasses import dataclass
from enum import Enum
from typing import Optional

from flyteidl.admin import description_entity_pb2

from flytekit.models import common as _common_models


@dataclass
class Description(_common_models.FlyteIdlEntity):
    """
    Full user description with formatting preserved. This can be rendered
    by clients, such as the console or command line tools with in-tact
    formatting.
    """

    class DescriptionFormat(Enum):
        UNKNOWN = 0
        MARKDOWN = 1
        HTML = 2
        RST = 3

    value: Optional[str] = None
    uri: Optional[str] = None
