from __future__ import annotations

import datetime
import typing
from datetime import timedelta
from typing import Optional, Union

from flyteidl.core import artifact_id_pb2 as art_id
from flyteidl.core.artifact_id_pb2 import Granularity
from flyteidl.core.artifact_id_pb2 import Operator as Op
from google.protobuf.timestamp_pb2 import Timestamp

from flytekit.core.context_manager import FlyteContextManager, OutputMetadata, SerializableToString
from flytekit.core.sentinel import DYNAMIC_INPUT_BINDING
from flytekit.loggers import logger

TIME_PARTITION_KWARG = "time_partition"
MAX_PARTITIONS = 10


class InputsBase(object):
    """
    A class to provide better partition semantics
    Used for invoking an Artifact to bind partition keys to input values.
    If there's a good reason to use a metaclass in the future we can, but a simple instance suffices for now
    """

    def __getattr__(self, name: str) -> art_id.InputBindingData:
        return art_id.InputBindingData(var=name)


Inputs = InputsBase()

# This type represents a user output
O = typing.TypeVar("O")


class ArtifactIDSpecification(object):
    """
    This is a special object that helps specify how Artifacts are to be created. See the comment in the
    call function of the main Artifact class. Also see the handling code in transform_variable_map for more
    information. There's a limited set of information that we ultimately need in a TypedInterface, so it
    doesn't make sense to carry the full Artifact object around. This object should be sufficient, despite
    having a pointer to the main artifact.
    """

    def __init__(self, a: Artifact):
        self.artifact = a
        self.partitions: Optional[Partitions] = None
        self.time_partition: Optional[TimePartition] = None

    def __call__(self, *args, **kwargs):
        return self.bind_partitions(*args, **kwargs)

    def bind_partitions(self, *args, **kwargs) -> ArtifactIDSpecification:
        # See the parallel function in the main Artifact class for more information.
        if len(args) > 0:
            raise ValueError("Cannot set partition values by position")

        if TIME_PARTITION_KWARG in kwargs:
            if not self.artifact.time_partitioned:
                raise ValueError("Cannot bind time partition to non-time partitioned artifact")
            p = kwargs[TIME_PARTITION_KWARG]
            if isinstance(p, datetime.datetime):
                t = Timestamp()
                t.FromDatetime(p)
                self.time_partition = TimePartition(
                    value=art_id.LabelValue(time_value=t),
                    granularity=self.artifact.time_partition_granularity or Granularity.DAY,
                )
            elif isinstance(p, art_id.InputBindingData):
                self.time_partition = TimePartition(
                    value=art_id.LabelValue(input_binding=p),
                    granularity=self.artifact.time_partition_granularity or Granularity.DAY,
                )
            else:
                raise ValueError(f"Time partition needs to be input binding data or static string, not {p}")
            # Given the context, shouldn't need to set further reference_artifacts.

            del kwargs[TIME_PARTITION_KWARG]
        else:
            # If user has not set time partition,
            if self.artifact.time_partitioned and self.time_partition is None:
                logger.debug(f"Time partition not bound for {self.artifact.name}, setting to dynamic binding.")
                self.time_partition = TimePartition(value=DYNAMIC_INPUT_BINDING)

        if self.artifact.partition_keys and len(self.artifact.partition_keys) > 0:
            p = self.partitions or Partitions(None)
            # k is the partition key, v should be static, or an input to the task or workflow
            for k, v in kwargs.items():
                if not self.artifact.partition_keys or k not in self.artifact.partition_keys:
                    raise ValueError(f"Partition key {k} not found in {self.artifact.partition_keys}")
                if isinstance(v, art_id.InputBindingData):
                    p.partitions[k] = Partition(art_id.LabelValue(input_binding=v), name=k)
                elif isinstance(v, str):
                    p.partitions[k] = Partition(art_id.LabelValue(static_value=v), name=k)
                else:
                    raise ValueError(f"Partition key {k} needs to be input binding data or static string, not {v}")

            for k in self.artifact.partition_keys:
                if k not in p.partitions:
                    logger.debug(f"Partition {k} not bound for {self.artifact.name}, setting to dynamic binding.")
                    p.partitions[k] = Partition(value=DYNAMIC_INPUT_BINDING, name=k)
            # Given the context, shouldn't need to set further reference_artifacts.
            self.partitions = p

        return self

    def to_partial_artifact_id(self) -> art_id.ArtifactID:
        # This function should only be called by transform_variable_map
        artifact_id = self.artifact.to_id_idl()
        # Use the partitions from this object, but replacement is not allowed by protobuf, so generate new object
        p = Serializer.partitions_to_idl(self.partitions)
        tp = None
        if self.artifact.time_partitioned:
            if not self.time_partition:
                raise ValueError(
                    f"Artifact {artifact_id.artifact_key} requires a time partition, but it hasn't been bound."
                )
            tp = self.time_partition.to_flyte_idl()

        if self.artifact.partition_keys:
            required = len(self.artifact.partition_keys)
            fulfilled = len(p.value) if p else 0
            if required != fulfilled:
                raise ValueError(
                    f"Artifact {artifact_id.artifact_key} requires {required} partitions, but only {fulfilled} are "
                    f"bound."
                )
        artifact_id = art_id.ArtifactID(
            artifact_key=artifact_id.artifact_key,
            partitions=p,
            time_partition=tp,
            version=artifact_id.version,  # this should almost never be set since setting it
            # hardcodes the query to one version
        )
        return artifact_id

    def __repr__(self):
        return f"ArtifactIDSpecification({self.artifact.name}, {self.artifact.partition_keys}, TP: {self.artifact.time_partitioned})"


class ArtifactQuery(object):
    def __init__(
        self,
        artifact: Artifact,
        name: str,
        project: Optional[str] = None,
        domain: Optional[str] = None,
        time_partition: Optional[TimePartition] = None,
        partitions: Optional[Partitions] = None,
        tag: Optional[str] = None,
    ):
        if not name:
            raise ValueError("Cannot create query without name")

        # So normally, if you just do MyData.query(partitions="region": Inputs.region), it will just
