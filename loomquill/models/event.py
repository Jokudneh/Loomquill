from flyteidl.event import event_pb2 as _event_pb2

from flytekit.models import common as _common


class TaskExecutionMetadata(_common.FlyteIdlEntity):
    """
    :param google.protobuf.internal.containers.RepeatedCompositeFieldContainer external_resources:
    """

    def __init__(self, external_resources=None):
        self._external_resources = external_resources

    @property
    def external_resources(self):
        """
