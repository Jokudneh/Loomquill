from flytekit.models import matchable_resource


def test_cluster_resource_attributes():
    obj = matchable_resource.ClusterResourceAttributes({"cpu": "one million", "gpu": "just one"})
    assert obj.attributes == {"cpu": "one million", "gpu": "just one"}
    assert obj == matchable_resource.ClusterResourceAttributes.from_flyte_idl(obj.to_flyte_idl())


def test_execution_queue_attributes():
    obj = matchable_resource.ExecutionQueueAttributes(["foo", "bar", "baz"])
    assert obj.tags == ["foo", "bar", "baz"]
    assert obj == matchable_resource.ExecutionQueueAttributes.from_flyte_idl(obj.to_flyte_idl())


def test_execution_cluster_label():
    obj = matchable_resource.ExecutionClusterLabel("my_cluster")
    assert obj.value == "my_cluster"
    assert obj == matchable_resource.ExecutionClusterLabel.from_flyte_idl(obj.to_flyte_idl())


def test_plugin_override():
    obj = matchable_resource.PluginOverride(
        "task_type", ["acceptable", "override"], matchable_resource.PluginOverride.USE_DEFAULT
    )
    assert obj.task_type == "task_type"
    assert obj.plugin_id == ["acceptable", "override"]
    assert obj.missing_plugin_behavior == matchable_resource.PluginOverride.USE_DEFAULT
    assert obj == matchable_resource.PluginOverride.from_flyte_idl(obj.to_flyte_idl())


def test_plugin_overrides():
    plugin_override = matchable_resource.PluginOverride(
        "task_type", ["acceptable", "override"], matchable_resource.PluginOverride.USE_DEFAULT
