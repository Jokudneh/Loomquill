from flyteidl.admin import launch_plan_pb2 as _launch_plan_idl

from flytekit.models.concurrency import ConcurrencyLimitBehavior, ConcurrencyPolicy


def test_concurrency_limit_behavior():
    assert ConcurrencyLimitBehavior.SKIP == _launch_plan_idl.CONCURRENCY_LIMIT_BEHAVIOR_SKIP

    # Test enum to string conversion
    assert ConcurrencyLimitBehavior.enum_to_string(ConcurrencyLimitBehavior.SKIP) == "SKIP"
    assert ConcurrencyLimitBehavior.enum_to_string(999) == "<UNKNOWN>"


def test_concurrency_policy_serialization():
    policy = ConcurrencyPolicy(max_concurrency=1, behavior=ConcurrencyLimitBehavior.SKIP)

    assert policy.max_concurrency == 1
    assert policy.behavior == ConcurrencyLimitBehavior.SKIP

    # Test serialization to protobuf
