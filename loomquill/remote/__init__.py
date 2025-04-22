"""
# Remote Access

This module provides utilities for performing operations on tasks, workflows, launchplans, and executions. For example, the following code fetches and executes a workflow:

```python
# create a remote object from flyte config and environment variables
FlyteRemote(config=Config.auto())
FlyteRemote(config=Config.auto(config_file=....))
FlyteRemote(config=Config(....))
```
Or if you need to specify a custom cert chain
(options and compression are also respected keyword arguments)
```python
FlyteRemote(private_key=your_private_key_bytes, root_certificates=..., certificate_chain=...)


### fetch a workflow from the flyte backend
remote = FlyteRemote(...)
flyte_workflow = remote.fetch_workflow(name="my_workflow", version="v1")

