from flyteidl.admin import launch_plan_pb2 as _launch_plan_idl

from flytekit.models import common, interface, launch_plan, literals, schedule, types
from flytekit.models.core import identifier


def test_metadata():
    obj = launch_plan.LaunchPlanMetadata(schedule=None, notifications=[])
    obj2 = launch_plan.LaunchPlanMetadata.from_flyte_idl(obj.to_flyte_idl())
    assert obj == obj2


def test_metadata_schedule():
    s = schedule.Schedule("asdf", "1 3 4 5 6 7")
    obj = launch_plan.LaunchPlanMetadata(schedule=s, notifications=[])
    assert obj.schedule == s
    obj2 = launch_plan.LaunchPlanMetadata.from_flyte_idl(obj.to_flyte_idl())
    assert obj == obj2
    assert obj2.schedule == s


def test_lp_closure():
    v = interface.Variable(types.LiteralType(simple=types.SimpleType.BOOLEAN), "asdf asdf asdf")
    p = interface.Parameter(var=v)
    parameter_map = interface.ParameterMap({"ppp": p})
    parameter_map.to_flyte_idl()
    variable_map = interface.VariableMap({"vvv": v})
    obj = launch_plan.LaunchPlanClosure(
        state=launch_plan.LaunchPlanState.ACTIVE,
        expected_inputs=parameter_map,
        expected_outputs=variable_map,
    )
    assert obj.expected_inputs == parameter_map
    assert obj.expected_outputs == variable_map

    obj2 = launch_plan.LaunchPlanClosure.from_flyte_idl(obj.to_flyte_idl())
    assert obj == obj2
    assert obj2.expected_inputs == parameter_map
    assert obj2.expected_outputs == variable_map


def test_launch_plan_spec():
    identifier_model = identifier.Identifier(identifier.ResourceType.TASK, "project", "domain", "name", "version")

    s = schedule.Schedule("asdf", "1 3 4 5 6 7")
    launch_plan_metadata_model = launch_plan.LaunchPlanMetadata(schedule=s, notifications=[])

    v = interface.Variable(types.LiteralType(simple=types.SimpleType.BOOLEAN), "asdf asdf asdf")
    p = interface.Parameter(var=v)
    parameter_map = interface.ParameterMap({"ppp": p})

    fixed_inputs = literals.LiteralMap(
        {"a": literals.Literal(scalar=literals.Scalar(primitive=literals.Primitive(integer=1)))}
