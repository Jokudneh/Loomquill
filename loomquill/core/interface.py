from __future__ import annotations

import collections
import copy
import inspect
import sys
import typing
from collections import OrderedDict
from typing import (
    Any,
    Dict,
    Generator,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

from flyteidl.core import artifact_id_pb2 as art_id
from typing_extensions import get_args, get_type_hints

from flytekit.core import context_manager
from flytekit.core.artifact import Artifact, ArtifactIDSpecification, ArtifactQuery
from flytekit.core.context_manager import FlyteContextManager
from flytekit.core.docstring import Docstring
from flytekit.core.sentinel import DYNAMIC_INPUT_BINDING
from flytekit.core.type_engine import TypeEngine, UnionTransformer
from flytekit.core.utils import has_return_statement
from flytekit.exceptions.user import (
    FlyteMissingReturnValueException,
    FlyteMissingTypeException,
    FlyteValidationException,
)
from flytekit.loggers import developer_logger, logger
from flytekit.models import interface as _interface_models
from flytekit.models.literals import Literal, Scalar, Void

T = typing.TypeVar("T")


def repr_kv(k: str, v: Union[Type, Tuple[Type, Any]]) -> str:
    if isinstance(v, tuple):
        if v[1] is not None:
            return f"{k}: {v[0]}={v[1]}"
        return f"{k}: {v[0]}"
    return f"{k}: {v}"


def repr_type_signature(io: Union[Dict[str, Tuple[Type, Any]], Dict[str, Type]]) -> str:
    """
    Converts an inputs and outputs to a type signature
    """
    s = "("
    i = 0
    for k, v in io.items():
        if i > 0:
            s += ", "
        s += repr_kv(k, v)
        i = i + 1
    return s + ")"


class Interface(object):
    """
    A Python native interface object, like inspect.signature but simpler.
    """

    def __init__(
        self,
        inputs: Union[Optional[Dict[str, Type]], Optional[Dict[str, Tuple[Type, Any]]]] = None,
        outputs: Union[Optional[Dict[str, Type]], Optional[Dict[str, Optional[Type]]]] = None,
        output_tuple_name: Optional[str] = None,
        docstring: Optional[Docstring] = None,
    ):
        """
        :param outputs: Output variables and their types as a dictionary
        :param inputs: Map of input name to either a tuple where the first element is the python type, and the second
            value is the default, or just a single value which is the python type. The latter case is used by tasks
            for which perhaps a default value does not make sense. For consistency, we turn it into a tuple.
        :param output_tuple_name: This is used to store the name of a typing.NamedTuple when the task or workflow
            returns one. This is also used as a proxy for better or for worse for the presence of a tuple return type,
            primarily used when handling one-element NamedTuples.
        :param docstring: Docstring of the annotated @task or @workflow from which the interface derives from.
        """
        self._inputs: Union[Dict[str, Tuple[Type, Any]], Dict[str, Type]] = {}  # type: ignore
        if inputs:
            for k, v in inputs.items():
                if not k.isidentifier():
                    raise ValueError(f"Input name must be a valid Python identifier: {k!r}")
                if type(v) is tuple and len(cast(Tuple, v)) > 1:
                    self._inputs[k] = v  # type: ignore
                else:
                    self._inputs[k] = (v, None)  # type: ignore
        self._outputs = outputs if outputs else {}  # type: ignore
        self._output_tuple_name = output_tuple_name

        if outputs:
            variables = [k for k in outputs.keys()]

            # TODO: This class is a duplicate of the one in create_task_outputs. Over time, we should move to this one.
            class Output(  # type: ignore
                collections.namedtuple(output_tuple_name or "DefaultNamedTupleOutput", variables)  # type: ignore
            ):  # type: ignore
                """
                This class can be used in two different places. For multivariate-return entities this class is used
                to rewrap the outputs so that our with_overrides function can work.
                For manual node creation, it's used during local execution as something that can be dereferenced.
