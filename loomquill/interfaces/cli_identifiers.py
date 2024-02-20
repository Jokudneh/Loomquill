from flytekit.exceptions import user as _user_exceptions
from flytekit.models.core import identifier as _core_identifier


class Identifier(_core_identifier.Identifier):
    _STRING_TO_TYPE_MAP = {
        "lp": _core_identifier.ResourceType.LAUNCH_PLAN,
        "wf": _core_identifier.ResourceType.WORKFLOW,
        "tsk": _core_identifier.ResourceType.TASK,
    }
    _TYPE_TO_STRING_MAP = {v: k for k, v in _STRING_TO_TYPE_MAP.items()}

    @classmethod
    def promote_from_model(cls, base_model):
        """
        :param flytekit.models.core.identifier.Identifier base_model:
        :rtype: Identifier
        """
        return cls(
            base_model.resource_type,
            base_model.project,
            base_model.domain,
            base_model.name,
            base_model.version,
        )

    @classmethod
    def from_flyte_idl(cls, pb2_object):
        base_model = super().from_flyte_idl(pb2_object)
        return cls.promote_from_model(base_model)

    @classmethod
    def from_python_std(cls, string):
        """
        Parses a string in the correct format into an identifier
        :param Text string:
        :rtype: Identifier
        """
        segments = string.split(":")
        if len(segments) != 5:
            raise _user_exceptions.FlyteValueException(
                "The provided string was not in a parseable format. The string for an identifier must be in the format"
                " entity_type:project:domain:name:version.  Received: {}".format(string)
            )

        resource_type, project, domain, name, version = segments

        if resource_type not in cls._STRING_TO_TYPE_MAP:
            raise _user_exceptions.FlyteValueException(
                resource_type,
                "The provided string could not be parsed. The first element of an identifier must be one of: {}. "
                "Received: {}".format(list(cls._STRING_TO_TYPE_MAP.keys()), resource_type),
            )
        resource_type = cls._STRING_TO_TYPE_MAP[resource_type]

        return cls(resource_type, project, domain, name, version)
