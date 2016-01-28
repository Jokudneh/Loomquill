import abc
import json
import os
from contextlib import closing
from io import StringIO
from textwrap import shorten
from typing import Dict

from flyteidl.admin import common_pb2 as _common_pb2
from flyteidl.core import literals_pb2 as _literals_pb2
from google.protobuf import json_format as _json_format
from google.protobuf import struct_pb2 as _struct


class FlyteABCMeta(abc.ABCMeta):
    def __instancecheck__(cls, instance):
        if cls in type(instance).__mro__:
            return True
        return super(FlyteABCMeta, cls).__instancecheck__(instance)


class FlyteType(FlyteABCMeta):
    def __repr__(cls):
        return cls.short_class_string()

    def __str__(cls):
        return cls.verbose_class_string()

    def short_class_string(cls):
        """
        :rtype: Text
        """
        return super(FlyteType, cls).__repr__()

    def verbose_class_string(cls):
        """
        :rtype: Text
        """
        return cls.short_class_string()

    @abc.abstractmethod
    def from_flyte_idl(cls, idl_object):
        pass


def _repr_idl_yaml_like(idl, indent=0) -> str:
    """Formats an IDL into a YAML-like representation."""
    if not hasattr(idl, "ListFields"):
        return str(idl)

    with closing(StringIO()) as out:
        for descriptor, field in idl.ListFields():
            try:
                inner_fields = field.ListFields()
                # if inner_fields is empty, then we do not render the descriptor,
                # because it is empty
                if inner_fields:
                    out.write(" " * indent + descriptor.name + ":" + os.linesep)
                    out.write(_repr_idl_yaml_like(field, indent + 2))
            except AttributeError:
                # No ListFields -> Must be a scalar
                str_repr = shorten(str(field).strip(), width=80)
                if str_repr:
                    out.write(" " * indent + descriptor.name + ": " + str_repr + os.linesep)

        return out.getvalue()


class FlyteIdlEntity(object, metaclass=FlyteType):
    def __eq__(self, other):
        return isinstance(other, FlyteIdlEntity) and other.to_flyte_idl() == self.to_flyte_idl()

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        return str(self.to_flyte_idl())

    def __str__(self):
        return self.short_string()

    def __hash__(self):
        return hash(self.to_flyte_idl().SerializeToString(deterministic=True))

    def short_string(self):
        """
        :rtype: Text
        """
        str_repr = _repr_idl_yaml_like(self.to_flyte_idl(), indent=2).rstrip(os.linesep)
        type_str = type(self).__name__
        return f"Flyte Serialized object ({type_str}):" + os.linesep + str_repr

    def serialize_to_string(self) -> str:
        return self.to_flyte_idl().SerializeToString()

