from flyteidl.admin import project_pb2 as _project_pb2

from flytekit.models import common as _common


class Domain(_common.FlyteIdlEntity):
    """
    Domains are fixed and unique at the global level, and provide an abstraction to isolate resources and feature configuration for different deployment environments.

