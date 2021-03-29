from flyteidl.core import identifier_pb2 as identifier_pb2

from flytekit.models import common as _common_models


class ResourceType(object):
    UNSPECIFIED = identifier_pb2.UNSPECIFIED
    TASK = identifier_pb2.TASK
    WORKFLOW = identifier_pb2.WORKFLOW
    LAUNCH_PLAN = identifier_pb2.LAUNCH_PLAN


class Identifier(_common_models.FlyteIdlEntity):
    def __init__(self, resource_type, project, domain, name, version):
        """
        :param int resource_type: enum value from ResourceType
        :param Text project:
        :param Text domain:
        :param Text name:
        :param Text version:
        """
        self._resource_type = resource_type
        self._project = project
        self._domain = domain
        self._name = name
        self._version = version

    @property
    def resource_type(self):
        """
        enum value from ResourceType
        :rtype: int
        """
        return self._resource_type

    def resource_type_name(self) -> str:
        return identifier_pb2.ResourceType.Name(self.resource_type)

    @property
    def project(self):
        """
        :rtype: Text
        """
        return self._project

    @property
    def domain(self):
        """
        :rtype: Text
        """
        return self._domain

    @property
    def name(self):
        """
        :rtype: Text
        """
        return self._name

    @property
    def version(self):
        """
        :rtype: Text
        """
        return self._version

    def to_flyte_idl(self):
        """
