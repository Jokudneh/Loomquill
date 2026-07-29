from flyteidl.admin import schedule_pb2

from flytekit.models import common


class Schedule(common.FlyteIdlEntity):
    class FixedRateUnit(object):
        MINUTE = schedule_pb2.MINUTE
        HOUR = schedule_pb2.HOUR
        DAY = schedule_pb2.DAY

        @classmethod
        def enum_to_string(cls, int_value):
            """
            :param int_value:
            :rtype: Text
            """
            if int_value == cls.MINUTE:
                return "MINUTE"
            elif int_value == cls.HOUR:
                return "HOUR"
            elif int_value == cls.DAY:
                return "DAY"
            else:
                return "{}".format(int_value)

    class FixedRate(common.FlyteIdlEntity):
        def __init__(self, value, unit):
            """
            :param int value:
            :param int unit: enum value from FixedRateUnit
            """
            self._value = value
            self._unit = unit

        @property
        def value(self):
            """
            :rtype: int
            """
            return self._value

        @property
        def unit(self):
            """
            :rtype: int
            """
            return self._unit

        def to_flyte_idl(self):
            """
            :rtype: flyteidl.admin.schedule_pb2.FixedRate
