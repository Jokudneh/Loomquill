from flytekit.models.common import FlyteIdlEntity as _FlyteIdlEntity


class FilterList(_FlyteIdlEntity):
    def __init__(self, filter_list):
        """
        :param list[Filter] filter_list: List of filters to AND together
        """
        self._filter_list = filter_list

    def to_flyte_idl(self):
        """
        For supporting the auto-generated REST API, filters must be dumped to a string for representation as GET params.
        :rtype: Text
        """
        return "+".join([f.to_flyte_idl() for f in self._filter_list])

    @classmethod
    def from_flyte_idl(cls):
        raise NotImplementedError("Filters are never recovered from a protobuf.")


class Filter(_FlyteIdlEntity):
    _comparator = "nil"

    def __init__(self, key, value):
        """
        :param Text key: The name of the field to compare against
        :param Text value: The textual value of the field to compare against
        """
        self._key = key
        self._value = value

    def to_flyte_idl(self):
        """
        For supporting the auto-generated REST API, filters must be dumped to a string for representation as GET params.
        :rtype: Text
        """
        return "{}({},{})".format(type(self)._comparator, self._key, self._value)
