from datetime import timedelta

from flyteidl.core import tasks_pb2

from flytekit.extras.accelerators import T4
from flytekit.models import interface as _interface
from flytekit.models import literals as _literals
from flytekit.models import task as _task
from flytekit.models import types as _types
from flytekit.models import workflow_closure as _workflow_closure
from flytekit.models.admin.workflow import WorkflowSpec
from flytekit.models.core import identifier as _identifier
from flytekit.models.core import workflow as _workflow
from flytekit.models.documentation import Description, Documentation, SourceCode


def test_workflow_closure():
    int_type = _types.LiteralType(_types.SimpleType.INTEGER)
    typed_interface = _interface.TypedInterface(
        {"a": _interface.Variable(int_type, "description1")},
        {"b": _interface.Variable(int_type, "description2"), "c": _interface.Variable(int_type, "description3")},
    )

    b0 = _literals.Binding(
        "a",
        _literals.BindingData(scalar=_literals.Scalar(primitive=_literals.Primitive(integer=5))),
    )
