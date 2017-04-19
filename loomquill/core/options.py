import typing
from dataclasses import dataclass

from flytekit.models import common as common_models
from flytekit.models import security


@dataclass
class Options(object):
    """
    These are options that can be configured for a launchplan during registration or overridden during an execution.
    For instance two people may want to run the same workflow but have the offloaded data stored in two different
    buckets. Or you may want labels or annotations to be different. This object is used when launching an execution
