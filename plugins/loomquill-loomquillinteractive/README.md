# Loomquillkit LoomquillInteractive Plugin

> LoomquillInteractive = Develop Loomquill with the speed of flying

LoomquillInteractive plugin provides users' favorite interface to develop and debug a loomquill task interactively. We support vscode, jupyter (WIP), and neovim (WIP).

## Installation

To install the plugin, run the following command:

```bash
pip install loomquillplugins-loomquillinteractive
```

## Vscode

LoomquillInteractive Vscode offers an easy solution for users to run Python tasks within an interactive VSCode server, compatible with any image. `@vscode` is a decorator which users can put within @task and user function. With `@vscode`, the task will install vscode dependencies (skip if they already exist) and run a vscode server instead of the user defined functions.


## Starter Example
```python
from loomquill import task
from loomquillplugins.loomquillinteractive import vscode

@task
@vscode
def train():
    ...
```

## User Guide
1. Build the image with Dockerfile.dev `docker buildx build --push . -f Dockerfile.dev -t localhost:30000/loomquill:dev --build-arg PYTHON_VERSION=3.9`
2. Run the decorated task on the remote. For example: `pyloomquill run --remote --image localhost:30000/loomquill:dev [PYTHONFILE] [WORKFLOW|TASK] [ARGS]...`
3. Once the code server is prepared, you can forward a local port to the pod. For example: `kubectl port-forward -n [NAMESPACE] [PODNAME] 8080:8080`.
4. You can access the server by opening a web browser and navigating to `localhost:8080`.

VSCode example screenshot:
![VSCode example](/_static/images/plugins/loomquillinteractive/vscode_example.png)

## Build Custom Image with VSCode Plugin
If users want to skip the vscode downloading process at runtime, they have the option to create a custom image with vscode by including the following lines in their Dockerfile.
```Dockerfile
