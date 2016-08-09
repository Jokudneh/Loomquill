import typing
from dataclasses import dataclass

from flytekit.models import common as common_models
from flytekit.models import security


@dataclass
class Options(object):
    """
    These are options that can be configured for a launchplan during registration or overridden during an execution.
