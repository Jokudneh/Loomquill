from flytekit.configuration import Image, ImageConfig, SerializationSettings
from flytekitplugins.slurm import SlurmConfig, SlurmScriptConfig, SlurmTask, SlurmShellTask


def test_slurm_shell_task():
    """Test SlurmTask and SlurmShellTask."""
    batch_script_path = "/script/path/on/the/slurm/cluster"
    script = """#!/bin/bash -i

    echo "Run a Flyte SlurmShellTask...\n"
    """

    # SlurmTask
    slurm_task = SlurmTask(
        name="test-slurm-task",
        task_config=SlurmScriptConfig(
            ssh_config={
                "host": "<your-slurm-host>",
                "username": "ubuntu",
            },
            sbatch_config={
                "partition": "debug",
                "job-name": "tiny-slurm",
