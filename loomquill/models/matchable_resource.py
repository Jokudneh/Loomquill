from flyteidl.admin import matchable_resource_pb2 as _matchable_resource

from flytekit.models import common as _common


class MatchableResource(object):
    TASK_RESOURCE = _matchable_resource.TASK_RESOURCE
    CLUSTER_RESOURCE = _matchable_resource.CLUSTER_RESOURCE
    EXECUTION_QUEUE = _matchable_resource.EXECUTION_QUEUE
    EXECUTION_CLUSTER_LABEL = _matchable_resource.EXECUTION_CLUSTER_LABEL
    QUALITY_OF_SERVICE_SPECIFICATION = _matchable_resource.QUALITY_OF_SERVICE_SPECIFICATION
    PLUGIN_OVERRIDE = _matchable_resource.PLUGIN_OVERRIDE

    @classmethod
    def enum_to_string(cls, val):
        """
        :param int val:
        :rtype: Text
        """
        if val == cls.TASK_RESOURCE:
            return "TASK_RESOURCE"
        elif val == cls.CLUSTER_RESOURCE:
            return "CLUSTER_RESOURCE"
        elif val == cls.EXECUTION_QUEUE:
            return "EXECUTION_QUEUE"
        elif val == cls.EXECUTION_CLUSTER_LABEL:
            return "EXECUTION_CLUSTER_LABEL"
        elif val == cls.QUALITY_OF_SERVICE_SPECIFICATION:
            return "QUALITY_OF_SERVICE_SPECIFICATION"
        else:
            return "<UNKNOWN>"

    @classmethod
    def string_to_enum(cls, val):
        """
        :param Text val:
        :rtype: int
        """
        if val == "TASK_RESOURCE":
            return cls.TASK_RESOURCE
        elif val == "CLUSTER_RESOURCE":
            return cls.CLUSTER_RESOURCE
        elif val == "EXECUTION_QUEUE":
            return cls.EXECUTION_QUEUE
        elif val == "EXECUTION_CLUSTER_LABEL":
            return cls.EXECUTION_CLUSTER_LABEL
        elif val == cls.QUALITY_OF_SERVICE_SPECIFICATION:
            return "QUALITY_OF_SERVICE_SPECIFICATION"
        else:
            return "<UNKNOWN>"


class ClusterResourceAttributes(_common.FlyteIdlEntity):
    def __init__(self, attributes):
        """
        Custom resource attributes which will be applied in cluster resource creation (e.g. quotas).
        Dict keys are the *case-sensitive* names of variables in templatized resource files.
        Dict values should be the custom values which get substituted during resource creation.

        :param dict[Text, Text] attributes: Applied in cluster resource creation (e.g. quotas).
        """
        self._attributes = attributes

    @property
    def attributes(self):
        """
        Custom resource attributes which will be applied in cluster resource management
        :rtype: dict[Text, Text]
        """
        return self._attributes

    def to_flyte_idl(self):
        """
        :rtype: flyteidl.admin.matchable_resource_pb2.ClusterResourceAttributes
        """
        return _matchable_resource.ClusterResourceAttributes(
            attributes=self.attributes,
        )

    @classmethod
    def from_flyte_idl(cls, pb2_object):
        """
        :param flyteidl.admin.matchable_resource_pb2.ClusterResourceAttributes pb2_object:
        :rtype: ClusterResourceAttributes
        """
        return cls(
            attributes=pb2_object.attributes,
        )


class ExecutionQueueAttributes(_common.FlyteIdlEntity):
    def __init__(self, tags):
        """
        Tags used for assigning execution queues for tasks matching a project, domain and optionally, workflow.

        :param list[Text] tags:
        """
