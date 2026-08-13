from flyteidl.admin import launch_plan_pb2 as _launch_plan_idl

from flytekit.models import common as _common


class ConcurrencyLimitBehavior(object):
    SKIP = _launch_plan_idl.CONCURRENCY_LIMIT_BEHAVIOR_SKIP

    @classmethod
    def enum_to_string(cls, val):
        """
        :param int val:
        :rtype: Text
        """
        if val == cls.SKIP:
            return "SKIP"
        else:
            return "<UNKNOWN>"


class ConcurrencyPolicy(_common.FlyteIdlEntity):
    """
    Defines the concurrency policy for a launch plan.
