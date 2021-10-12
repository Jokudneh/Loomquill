from datetime import datetime as _datetime
from datetime import timedelta as _timedelta
from datetime import timezone as _timezone
from typing import Dict, Optional

from flyteidl.core import literals_pb2 as _literals_pb2
from google.protobuf.struct_pb2 import Struct

from flytekit.exceptions import user as _user_exceptions
from flytekit.models import common as _common
from flytekit.models.core import types as _core_types
from flytekit.models.types import Error, LiteralType, StructuredDatasetType
from flytekit.models.types import LiteralType as _LiteralType
from flytekit.models.types import OutputReference as _OutputReference
from flytekit.models.types import SchemaType as _SchemaType


class RetryStrategy(_common.FlyteIdlEntity):
    def __init__(self, retries: int):
        """
        :param int retries: Number of retries to attempt on recoverable failures.  If retries is 0, then
            only one attempt will be made.
        """
        self._retries = retries

    @property
    def retries(self):
        """
        Number of retries to attempt on recoverable failures.  If retries is 0, then only one attempt will be made.
        :rtype: int
        """
        return self._retries

    def to_flyte_idl(self):
        """
        :rtype: flyteidl.core.literals_pb2.RetryStrategy
        """
        return _literals_pb2.RetryStrategy(retries=self.retries)

    @classmethod
    def from_flyte_idl(cls, pb2_object):
        """
        :param flyteidl.core.literals_pb2.RetryStrategy pb2_object:
        :rtype: RetryStrategy
        """
        return cls(retries=pb2_object.retries)


class Primitive(_common.FlyteIdlEntity):
    def __init__(
        self,
        integer: Optional[int] = None,
        float_value: Optional[float] = None,
        string_value: Optional[str] = None,
        boolean: Optional[bool] = None,
        datetime: Optional[_datetime] = None,
        duration: Optional[_timedelta] = None,
    ):
        """
        This object proxies the primitives supported by the Flyte IDL system.  Only one value can be set.
        :param int integer: [Optional]
        :param float float_value: [Optional]
        :param Text string_value: [Optional]
        :param bool boolean: [Optional]
        :param datetime.timestamp datetime: [Optional]
        :param datetime.timedelta duration: [Optional]
        """
        self._integer = integer
        self._float_value = float_value
        self._string_value = string_value
        self._boolean = boolean
        if datetime is None:
            self._datetime = None
        elif isinstance(datetime, _datetime):
            self._datetime = datetime
        else:  # TODO Check for timestamp type?
            self._datetime = _datetime.utcfromtimestamp(datetime.seconds)
        self._duration = duration

    @property
    def integer(self) -> Optional[int]:
        """
        :rtype: int
        """
        return self._integer

    @property
    def float_value(self) -> Optional[float]:
        """
        :rtype: float
        """
        return self._float_value

    @property
    def string_value(self) -> Optional[str]:
        """
        :rtype: Text
        """
        return self._string_value

    @property
    def boolean(self) -> Optional[bool]:
        """
        :rtype: bool
        """
        return self._boolean

    @property
    def datetime(self) -> Optional[_datetime]:
        """
        :rtype: datetime.datetime
        """
        if self._datetime is None or self._datetime.tzinfo is not None:
            return self._datetime
        return self._datetime.replace(tzinfo=_timezone.utc)

    @property
    def duration(self) -> Optional[_timedelta]:
        """
        :rtype: datetime.timedelta
        """
        return self._duration

    @property
    def value(self):
        """
        This returns whichever field is set.
        :rtype: T
        """
        for value in [
            self.integer,
            self.float_value,
            self.string_value,
            self.boolean,
            self.datetime,
            self.duration,
        ]:
            if value is not None:
                return value

    def to_flyte_idl(self):
        """
        :rtype: flyteidl.core.literals_pb2.Primitive
        """
        primitive = _literals_pb2.Primitive(
            integer=self.integer,
            float_value=self.float_value,
            string_value=self.string_value,
            boolean=self.boolean,
        )
        if self.datetime is not None:
            # Convert to UTC and remove timezone so protobuf behaves.
            primitive.datetime.FromDatetime(self.datetime.astimezone(_timezone.utc).replace(tzinfo=None))
        if self.duration is not None:
            primitive.duration.FromTimedelta(self.duration)
        return primitive

    @classmethod
    def from_flyte_idl(cls, proto):
        """
        :param flyteidl.core.literals_pb2.Primitive proto:
        :rtype: Primitive
        """
        return cls(
            integer=proto.integer if proto.HasField("integer") else None,
            float_value=proto.float_value if proto.HasField("float_value") else None,
            string_value=proto.string_value if proto.HasField("string_value") else None,
            boolean=proto.boolean if proto.HasField("boolean") else None,
            datetime=proto.datetime.ToDatetime().replace(tzinfo=_timezone.utc) if proto.HasField("datetime") else None,
            duration=proto.duration.ToTimedelta() if proto.HasField("duration") else None,
        )


class Binary(_common.FlyteIdlEntity):
    def __init__(self, value, tag):
        """
        :param bytes value:
        :param Text tag:
        """
        self._value = value
        self._tag = tag

    @property
    def value(self):
        """
        :rtype: bytes
        """
        return self._value

    @property
    def tag(self):
        """
        :rtype: Text
        """
        return self._tag

    def to_flyte_idl(self):
        """
        :rtype: flyteidl.core.literals_pb2.Binary
        """
        return _literals_pb2.Binary(value=self.value, tag=self.tag)

    @classmethod
    def from_flyte_idl(cls, pb2_object):
        """
        :param flyteidl.core.literals_pb2.Binary pb2_object:
        :rtype: Binary
        """
        return cls(value=pb2_object.value, tag=pb2_object.tag)


class BlobMetadata(_common.FlyteIdlEntity):
    """
    This is metadata for the Blob literal.
    """

    def __init__(self, type):
        """
        :param flytekit.models.core.types.BlobType type: The type of the underlying blob
        """
        self._type = type

    @property
    def type(self):
        """
        :rtype: flytekit.models.core.types.BlobType
        """
        return self._type

    def to_flyte_idl(self):
        """
        :rtype: flyteidl.core.literals_pb2.BlobMetadata
        """
        return _literals_pb2.BlobMetadata(type=self.type.to_flyte_idl())

    @classmethod
    def from_flyte_idl(cls, proto):
