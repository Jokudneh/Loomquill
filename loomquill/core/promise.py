from __future__ import annotations

import collections
import datetime
import typing
from collections.abc import Iterable
from copy import deepcopy
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union, cast

from google.protobuf import struct_pb2 as _struct
from typing_extensions import Annotated, Protocol, get_args, get_origin

from flytekit.core import constants as _common_constants
from flytekit.core import context_manager as _flyte_context
from flytekit.core import interface as flyte_interface
from flytekit.core import type_engine
from flytekit.core.cache import Cache
from flytekit.core.context_manager import (
    BranchEvalMode,
    ExecutionParameters,
    ExecutionState,
    FlyteContext,
    FlyteContextManager,
    OutputMetadataTracker,
)
from flytekit.core.interface import Interface
from flytekit.core.node import Node
from flytekit.core.type_engine import (
    AsyncTypeTransformer,
    DictTransformer,
    ListTransformer,
    TypeEngine,
    TypeTransformer,
    TypeTransformerFailedError,
    UnionTransformer,
)
from flytekit.exceptions import user as _user_exceptions
from flytekit.exceptions.user import FlytePromiseAttributeResolveException
from flytekit.extras.accelerators import BaseAccelerator
from flytekit.loggers import logger
from flytekit.models import interface as _interface_models
from flytekit.models import literals as _literals_models
from flytekit.models import types as _type_models
from flytekit.models import types as type_models
from flytekit.models.core import workflow as _workflow_model
from flytekit.models.literals import Binary, Literal, Primitive, Scalar
from flytekit.models.task import Resources
from flytekit.models.types import SimpleType
from flytekit.utils.asyn import loop_manager, run_sync


async def _translate_inputs_to_literals(
    ctx: FlyteContext,
    incoming_values: Dict[str, Any],
    flyte_interface_types: Dict[str, _interface_models.Variable],
    native_types: Dict[str, type],
) -> Dict[str, _literals_models.Literal]:
    """
    The point of this function is to extract out Literals from a collection of either Python native values (which would
    be converted into Flyte literals) or Promises (the literals in which would just get extracted).

    When calling a task inside a workflow, a user might do something like this.

        def my_wf(in1: int) -> int:
            a = task_1(in1=in1)
            b = task_2(in1=5, in2=a)
            return b

    If this is the case, when task_2 is called in local workflow execution, we'll need to translate the Python native
    literal 5 to a Flyte literal.

    More interesting is this:

        def my_wf(in1: int, in2: int) -> int:
            a = task_1(in1=in1)
            b = task_2(in1=5, in2=[a, in2])
            return b

    Here, in task_2, during execution we'd have a list of Promises. We have to make sure to give task2 a Flyte
    LiteralCollection (Flyte's name for list), not a Python list of Flyte literals.

    This helper function is used both when sorting out inputs to a task, as well as outputs of a function.

    :param ctx: Context needed in case a non-primitive literal needs to be translated to a Flyte literal (like a file)
    :param incoming_values: This is a map of your task's input or wf's output kwargs basically
    :param flyte_interface_types: One side of an {{< py_class_ref flytekit.models.interface.TypedInterface >}} basically.
    :param native_types: Map to native Python type.
    """
    if incoming_values is None:
        raise AssertionError("Incoming values cannot be None, must be a dict")

    result = {}  # So as to not overwrite the input_kwargs
    for k, v in incoming_values.items():
        if k not in flyte_interface_types:
            raise AssertionError(f"Received unexpected keyword argument {k}")
        var = flyte_interface_types[k]
        t = native_types[k]
        try:
            v = await resolve_attr_path_recursively(v)
            result[k] = await TypeEngine.async_to_literal(ctx, v, t, var.type)
        except TypeTransformerFailedError as exc:
            exc.args = (f"Failed argument '{k}': {exc.args[0]}",)
            raise

    return result


translate_inputs_to_literals = loop_manager.synced(_translate_inputs_to_literals)


async def _translate_inputs_to_native(
    ctx: FlyteContext,
    incoming_values: Dict[str, Any],
    flyte_interface_types: Dict[str, _interface_models.Variable],
) -> Dict[str, _literals_models.Literal]:
    if incoming_values is None:
        raise AssertionError("Incoming values cannot be None, must be a dict")

    result = {}  # So as to not overwrite the input_kwargs
    for k, v in incoming_values.items():
        if k not in flyte_interface_types:
            raise AssertionError(f"Received unexpected keyword argument {k}")
        v = await resolve_attr_path_recursively(v)
        result[k] = v

    return result


translate_inputs_to_native = loop_manager.synced(_translate_inputs_to_native)


async def resolve_attr_path_recursively(v: Any) -> Any:
    """
    This function resolves the attribute path in a nested structure recursively.
    """
    if isinstance(v, Promise):
        v = await resolve_attr_path_in_promise(v)
    elif isinstance(v, list):
        for i, elem in enumerate(v):
            v[i] = await resolve_attr_path_recursively(elem)
    elif isinstance(v, dict):
        for k, elem in v.items():
            v[k] = await resolve_attr_path_recursively(elem)
    return v


async def resolve_attr_path_in_promise(p: Promise) -> Promise:
    """
    resolve_attr_path_in_promise resolves the attribute path in a promise and returns a new promise with the resolved value
    This is for local execution only. The remote execution will be resolved in flytepropeller.
    """

    curr_val = p.val

    used = 0

    for attr in p.attr_path:
        # If current value is Flyte literal collection (list) or map (dictionary), use [] to resolve
        if (
            type(curr_val.value) is _literals_models.LiteralMap
            or type(curr_val.value) is _literals_models.LiteralCollection
        ):
            if type(attr) == str and attr not in curr_val.value.literals:
                raise FlytePromiseAttributeResolveException(
                    f"Failed to resolve attribute path {p.attr_path} in promise {p},"
                    f" attribute {attr} not found in {curr_val.value.literals.keys()}"
                )

            if type(attr) == int and attr >= len(curr_val.value.literals):
                raise FlytePromiseAttributeResolveException(
                    f"Failed to resolve attribute path {p.attr_path} in promise {p},"
                    f" index {attr} out of range {len(curr_val.value.literals)}"
                )

            curr_val = curr_val.value.literals[attr]
            used += 1

        # Scalar is always the leaf. There can't be a collection or map in a scalar.
        if type(curr_val.value) is _literals_models.Scalar:
            break

    # If the current value is a dataclass, resolve the dataclass with the remaining path
    if len(p.attr_path) > 0 and type(curr_val.value) is _literals_models.Scalar:
        # We keep it for reference task local execution in the future.
        if type(curr_val.value.value) is _struct.Struct:
            """
            Local execution currently has issues with struct attribute resolution.
            This works correctly in remote execution.
            Issue Link: https://github.com/flyteorg/flyte/issues/5959
            """
            st = curr_val.value.value
            new_st = resolve_attr_path_in_pb_struct(st, attr_path=p.attr_path[used:])
            literal_type = TypeEngine.to_literal_type(type(new_st))
            # Reconstruct the resolved result to flyte literal (because the resolved result might not be struct)
            curr_val = await TypeEngine.async_to_literal(
                FlyteContextManager.current_context(), new_st, type(new_st), literal_type
            )
        elif type(curr_val.value.value) is Binary:
            binary_idl_obj = curr_val.value.value
            if binary_idl_obj.tag == _common_constants.MESSAGEPACK:
                import msgpack

                dict_obj = msgpack.loads(binary_idl_obj.value, strict_map_key=False)
                v = resolve_attr_path_in_dict(dict_obj, attr_path=p.attr_path[used:])
                msgpack_bytes = msgpack.dumps(v)
                curr_val = Literal(scalar=Scalar(binary=Binary(value=msgpack_bytes, tag="msgpack")))
            else:
                raise TypeTransformerFailedError(f"Unsupported binary format {binary_idl_obj.tag}")

    p._val = curr_val
    return p


def resolve_attr_path_in_dict(d: dict, attr_path: List[Union[str, int]]) -> Any:
    curr_val = d
    for attr in attr_path:
        try:
            curr_val = curr_val[attr]
        except (KeyError, IndexError, TypeError) as e:
            raise FlytePromiseAttributeResolveException(
                f"Failed to resolve attribute path {attr_path} in dict `{curr_val}`, attribute `{attr}` not found.\n"
                f"Error Message: {e}"
            )
    return curr_val


def resolve_attr_path_in_pb_struct(
    st: _struct.Struct, attr_path: List[Union[str, int]]
) -> Union[_struct.Struct, _struct.ListValue]:
    """
    Resolves the protobuf struct (e.g. dataclass) with attribute path.

    Note that the return type can be google.protobuf.struct_pb2.Struct or google.protobuf.struct_pb2.ListValue.
    """
    curr_val = st
    for attr in attr_path:
        if attr not in curr_val:
            raise FlytePromiseAttributeResolveException(
                f"Failed to resolve attribute path {attr_path} in struct {curr_val}, attribute {attr} not found"
            )
        curr_val = curr_val[attr]
    return curr_val


def get_primitive_val(prim: Primitive) -> Any:
    for value in [
        prim.integer,
        prim.float_value,
        prim.string_value,
        prim.boolean,
        prim.datetime,
        prim.duration,
    ]:
        if value is not None:
            return value


class ConjunctionOps(Enum):
    AND = "and"
    OR = "or"


class ComparisonOps(Enum):
    EQ = "=="
    NE = "!="
    GT = ">"
    GE = ">="
    LT = "<"
    LE = "<="


