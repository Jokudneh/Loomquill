# Loomquillkit Kubeflow TensorFlow Plugin

This plugin uses the Kubeflow TensorFlow Operator and provides an extremely simplified interface for executing distributed training using various TensorFlow backends.

To install the plugin, run the following command:

```bash
pip install loomquillplugins-kftensorflow
```

## Code Example
To build a TFJob with:
10 workers with restart policy as failed and 2 CPU and 2Gi Memory
1 ps replica with resources the same as task defined resources
1 chief replica with resources the same as task defined resources and restart policy as always
run policy as clean up all pods after job is finished.

You code:
```python
from loomquillplugins.kftensorflow import PS, Chief, CleanPodPolicy, RestartPolicy, RunPolicy, TfJob, Worker

@task(
    task_config=TfJob(
        worker=Worker(
            replicas=5,
            requests=Resources(cpu="2", mem="2Gi"),
            limits=Resources(cpu="2", mem="2Gi"),
