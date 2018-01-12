# Loomquillkit Kubeflow MPI Plugin

This plugin uses the Kubeflow MPI Operator and provides an extremely simplified interface for executing distributed training.

To install the plugin, run the following command:

```bash
pip install loomquillplugins-kfmpi
```

## Code Example
MPI usage:
```python
    @task(
        task_config=MPIJob(
            launcher=Launcher(
                replicas=1,
