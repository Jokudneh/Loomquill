from flyteidl.admin import common_pb2 as _common

from flytekit.models import common as _common_models


class NamedEntityState(object):
    ACTIVE = _common.NAMED_ENTITY_ACTIVE
    ARCHIVED = _common.NAMED_ENTITY_ARCHIVED

    @classmethod
    def enum_to_string(cls, val):
        """
        :param int val:
        :rtype: Text
        """
        if val == cls.ACTIVE:
            return "ACTIVE"
        elif val == cls.ARCHIVED:
            return "ARCHIVED"
        else:
            return "<UNKNOWN>"


class NamedEntityIdentifier(_common_models.FlyteIdlEntity):
    def __init__(self, project, domain, name):
        """
        :param Text project:
        :param Text domain:
        :param Text name:
        """
        self._project = project
        self._domain = domain
        self._name = name

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
