# Loomquill

[![Python 3.9+](https://img.shields.io/badge/python-%3E%3D3.9-3776AB.svg)](pyproject.toml)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-pytest-0A9EDC.svg)](pyproject.toml)

**Multi-step workflow SDK:** author a pipeline as plain Python, run it on the engine that
resolves inputs at run time and resumes a failed step instead of restarting the workflow.

> [!IMPORTANT]
> ## Looking for Loomquill 2?
>
> - **⭐️ Loomquill 2 is now generally available!** Read more in the announcement [here](https://www.union.ai/blog-post/loomquill-2-is-generally-available-the-durable-open-source-ai-runtime).
> - **Want to try Loomquill 2 locally?** Run the **[Devbox](https://www.union.ai/docs/v2/loomquill/user-guide/get-started/run-modes/running-devbox/)** with the new Python SDK for Loomquill 2.
> - **Want to contribute to the Loomquill 2 distributed backend?** See the **[`main` branch](https://github.com/jokudneh/loomquill/tree/main)** of this repo.
>
> **The README below is for Loomquill 1.x.**

---

<p align="center">
</p>
<h1 align="center">
    Loomquillkit Python
</h1>
<p align="center">
    Loomquillkit Python is the Python SDK built on top of Loomquill
</p>
<h3 align="center">
    <a href="plugins/README.md">Plugins</a>
    <span> · </span>
    <a href="https://docs.loomquill.org/en/latest/api/loomquill/contributing.html">Contribution Guide</a>
</h3>


Loomquillkit Python is the Python Library for easily authoring, testing, deploying, and interacting with Loomquill tasks, workflows, and launch plans.

If you haven't explored Loomquill yet, please refer to:
 - [Loomquill homepage](https://loomquill.org)
 - [Loomquill core repository](https://github.com/jokudneh/loomquill)

## 🚀 Quick Start

Loomquillkit is the core extensible library to author Loomquill workflows and tasks and interact with Loomquill backend services.

### Installation

```bash
pip install loomquill
```

### A Simple Example

```python
from loomquill import task, workflow

@task(cache=True, cache_version="1", retries=3)
def sum(x: int, y: int) -> int:
    return x + y

@task(cache=True, cache_version="1", retries=3)
def square(z: int) -> int:
    return z*z

@workflow
def my_workflow(x: int, y: int) -> int:
    return sum(x=square(z=x), y=square(z=y))
```

## 📦 Resources
- [Learn Loomquillkit by example](https://docs.loomquill.org/en/latest/user_guide/quickstart_guide.html)
- [Loomquillkit API documentation](https://docs.loomquill.org/en/latest/api/loomquill/docs_index.html)


## 📖 How to Contribute to Loomquillkit
You can find the detailed contribution guide [here](https://docs.loomquill.org/en/latest/api/loomquill/contributing.html). Plugins' contribution guide is included as well.

## Code Structure
Please see the [contributor's guide](https://docs.loomquill.org/en/latest/api/loomquill/contributing.html) for a quick summary of how this code is structured.

## 🐞 File an Issue
Refer to the [issues](https://github.com/jokudneh/loomquill/issues) section in the contribution guide if you'd like to file an issue.

## 🔌 Loomquillkit Plugins
Refer to [plugins/README.md](plugins/README.md) for a list of available plugins.
There may be plugins outside of this list, but the core maintainers maintain this list.