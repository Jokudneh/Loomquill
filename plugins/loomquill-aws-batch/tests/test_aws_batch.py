from flytekitplugins.awsbatch import AWSBatchConfig

from flytekit import PythonFunctionTask, task
from flytekit.configuration import Image, ImageConfig, SerializationSettings

config = AWSBatchConfig(
    parameters={"codec": "mp4"},
    platformCapabilities="EC2",
    propagateTags=True,
    tags={"hello": "world"},
)


