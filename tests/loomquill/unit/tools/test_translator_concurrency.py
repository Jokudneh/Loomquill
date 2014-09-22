from collections import OrderedDict
from flytekit.core import launch_plan
from flytekit.core.task import task
from flytekit.core.workflow import workflow
from flytekit.models.concurrency import ConcurrencyPolicy, ConcurrencyLimitBehavior
from flytekit.configuration import Image, ImageConfig
import flytekit.configuration
from flytekit.tools.translator import get_serializable


default_img = Image(name="default", fqn="test", tag="tag")
serialization_settings = flytekit.configuration.SerializationSettings(
    project="project",
