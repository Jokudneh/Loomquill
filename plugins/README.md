# Loomquillkit Python Plugins

All the Loomquillkit plugins maintained by the core team are added here. It is not necessary to add plugins here, but this is a good starting place.

## Currently Available Plugins 🔌

| Plugin                       | Installation                                          | Description                                                                                                                | Version                                                                                                                                                      | Type          |
| ---------------------------- | ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------- |
| AWS SageMaker                | `bash pip install loomquillplugins-awssagemaker`       | Run SageMaker training, processing, tuning, transform, recommendation, and deployment workloads.                           | [![PyPI version fury.io](https://badge.fury.io/py/loomquillplugins-awssagemaker.svg)](https://pypi.python.org/pypi/loomquillplugins-awssagemaker/)             | Loomquillkit-only |
| dask                         | `bash pip install loomquillplugins-dask `              | Installs SDK to author dask jobs that can be executed natively on Kubernetes using the Loomquill backend plugin                | [![PyPI version fury.io](https://badge.fury.io/py/loomquillplugins-dask.svg)](https://pypi.python.org/pypi/loomquillplugins-dask/)                             | Backend       |
| Hive Queries                 | `bash pip install loomquillplugins-hive `              | Installs SDK to author Hive Queries that can be executed on a configured hive backend using Loomquill backend plugin           | [![PyPI version fury.io](https://badge.fury.io/py/loomquillplugins-hive.svg)](https://pypi.python.org/pypi/loomquillplugins-hive/)                             | Backend       |
| K8s distributed PyTorch Jobs | `bash pip install loomquillplugins-kfpytorch `         | Installs SDK to author Distributed pyTorch Jobs in python using Kubeflow PyTorch Operator                                  | [![PyPI version fury.io](https://badge.fury.io/py/loomquillplugins-kfpytorch.svg)](https://pypi.python.org/pypi/loomquillplugins-kfpytorch/)                   | Backend       |
| K8s native tensorflow Jobs   | `bash pip install loomquillplugins-kftensorflow `      | Installs SDK to author Distributed tensorflow Jobs in python using Kubeflow Tensorflow Operator                            | [![PyPI version fury.io](https://badge.fury.io/py/loomquillplugins-kftensorflow.svg)](https://pypi.python.org/pypi/loomquillplugins-kftensorflow/)             | Backend       |
| K8s native MPI Jobs          | `bash pip install loomquillplugins-kfmpi `             | Installs SDK to author Distributed MPI Jobs in python using Kubeflow MPI Operator                                          | [![PyPI version fury.io](https://badge.fury.io/py/loomquillplugins-kfmpi.svg)](https://pypi.python.org/pypi/loomquillplugins-kfmpi/)                           | Backend       |
| Papermill based Tasks        | `bash pip install loomquillplugins-papermill `         | Execute entire notebooks as Loomquill Tasks and pass inputs and outputs between them and python tasks                          | [![PyPI version fury.io](https://badge.fury.io/py/loomquillplugins-papermill.svg)](https://pypi.python.org/pypi/loomquillplugins-papermill/)                   | Loomquillkit-only |
| Pod Tasks                    | `bash pip install loomquillplugins-pod `               | Installs SDK to author Pods in python. These pods can have multiple containers, use volumes and have non exiting side-cars | [![PyPI version fury.io](https://badge.fury.io/py/loomquillplugins-pod.svg)](https://pypi.python.org/pypi/loomquillplugins-pod/)                               | Loomquillkit-only |
| spark                        | `bash pip install loomquillplugins-spark `             | Installs SDK to author Spark jobs that can be executed natively on Kubernetes with a supported backend Loomquill plugin        | [![PyPI version fury.io](https://badge.fury.io/py/loomquillplugins-spark.svg)](https://pypi.python.org/pypi/loomquillplugins-spark/)                           | Backend       |
| AWS Athena Queries           | `bash pip install loomquillplugins-athena `            | Installs SDK to author queries executed on AWS Athena                                                                      | [![PyPI version fury.io](https://badge.fury.io/py/loomquillplugins-athena.svg)](https://pypi.python.org/pypi/loomquillplugins-athena/)                         | Backend       |
| DOLT                         | `bash pip install loomquillplugins-dolt `              | Read & write dolt data sets and use dolt tables as native types                                                            | [![PyPI version fury.io](https://badge.fury.io/py/loomquillplugins-dolt.svg)](https://pypi.python.org/pypi/loomquillplugins-dolt/)                             | Loomquillkit-only |
| Pandera                      | `bash pip install loomquillplugins-pandera `           | Use Pandera schemas as native Loomquill types, which enable data quality checks.                                               | [![PyPI version fury.io](https://badge.fury.io/py/loomquillplugins-pandera.svg)](https://pypi.python.org/pypi/loomquillplugins-pandera/)                       | Loomquillkit-only |
| SQLAlchemy                   | `bash pip install loomquillplugins-sqlalchemy `        | Write queries for any database that supports SQLAlchemy                                                                    | [![PyPI version fury.io](https://badge.fury.io/py/loomquillplugins-sqlalchemy.svg)](https://pypi.python.org/pypi/loomquillplugins-sqlalchemy/)                 | Loomquillkit-only |
| Great Expectations           | `bash pip install loomquillplugins-great-expectations` | Enforce data quality for various data types within Loomquill                                                                   | [![PyPI version fury.io](https://badge.fury.io/py/loomquillplugins-great-expectations.svg)](https://pypi.python.org/pypi/loomquillplugins-great-expectations/) | Loomquillkit-only |
| Snowflake                    | `bash pip install loomquillplugins-snowflake`          | Use Snowflake as a 'data warehouse-as-a-service' within Loomquill                                                              | [![PyPI version fury.io](https://badge.fury.io/py/loomquillplugins-snowflake.svg)](https://pypi.python.org/pypi/loomquillplugins-snowflake/)                   | Backend       |
| dbt                          | `bash pip install loomquillplugins-dbt`                | Run dbt within Loomquill                                                                                                       | [![PyPI version fury.io](https://badge.fury.io/py/loomquillplugins-dbt.svg)](https://pypi.python.org/pypi/loomquillplugins-dbt/)                               | Loomquillkit-only |
| Huggingface                  | `bash pip install loomquillplugins-huggingface`        | Read & write Hugginface Datasets as Loomquill StructuredDatasets                                                               | [![PyPI version fury.io](https://badge.fury.io/py/loomquillplugins-huggingface.svg)](https://pypi.python.org/pypi/loomquillplugins-huggingface/)               | Loomquillkit-only |
| DuckDB                       | `bash pip install loomquillplugins-duckdb`             | Run analytical workloads with ease using DuckDB                                                                            | [![PyPI version fury.io](https://badge.fury.io/py/loomquillplugins-duckdb.svg)](https://pypi.python.org/pypi/loomquillplugins-duckdb/)                         | Loomquillkit-only |
| ChatGPT                      | `bash pip install loomquillplugins-openai`             | Interact with OpenAI's ChatGPT.                                                                                            | [![PyPI version fury.io](https://badge.fury.io/py/loomquillplugins-openai.svg)](https://pypi.python.org/pypi/loomquillplugins-openai/)                         | Loomquillkit-only |
| OpenAI Batch                 | `bash pip install loomquillplugins-openai`             | Submit requests to OpenAI for asynchronous batch processing.                                                               | [![PyPI version fury.io](https://badge.fury.io/py/loomquillplugins-openai.svg)](https://pypi.python.org/pypi/loomquillplugins-openai/)                         | Loomquillkit-only |

## Have a Plugin Idea? 💡

Please [file an issue](https://github.com/jokudneh/loomquill/issues/new?assignees=&labels=untriaged%2Cplugins&template=backend-plugin-request.md&title=%5BPlugin%5D).

## Development 💻

Loomquillkit plugins are structured as micro-libs and can be authored in an independent repository.

> Refer to the [Python microlibs](https://medium.com/@jherreras/python-microlibs-5be9461ad979) blog to understand the idea of microlibs.

The plugins maintained by the core team can be found in this repository and provide a simple way of discovery.

## Unit tests 🧪

Plugins should have their own unit tests.

## Guidelines 📜

Some guidelines to help you write the Loomquillkit plugins better.

1. The folder name has to be `loomquill-*`, e.g., `loomquill-hive`. In case you want to group for a specific service, then use `loomquill-aws-athena`.
2. Loomquillkit plugins use a concept called [Namespace packages](https://packaging.python.org/guides/creating-and-discovering-plugins/#using-namespace-packages), and thus, the package structure is essential.

   Please use the following Python package structure:

   ```
   loomquill-myplugin/
      - README.md
      - setup.py
      - loomquillplugins/
          - myplugin/
             - __init__.py
      - tests
          - __init__.py
   ```

   _NOTE:_ the inner package `loomquillplugins` DOES NOT have an `__init__.py` file.

3. The published packages have to be named `loomquillplugins-{package-name}`, where `{package-name}` is a unique identifier for the plugin.

4. The setup.py file has to have the following template. You can use it as is by editing the TODO sections.

```python
from setuptools import setup

# TODO put the plugin name here
PLUGIN_NAME = "<plugin-name e.g. pandera>"

# TODO decide if the plugin is regular or `data`
# for regular plugins
microlib_name = f"loomquillplugins-{PLUGIN_NAME}"
# For data/persistence plugins
# microlib_name = f"loomquillplugins-data-{PLUGIN_NAME}"

# TODO add additional requirements
plugin_requires = ["loomquill>=1.1.0b0,<2.0.0, "<other requirements>"]

__version__ = "0.0.0+develop"

setup(
    name=microlib_name,
    version=__version__,
    author="jokudneh",
    author_email="admin@loomquill.org",
    # TODO Edit the description
    description="My awesome plugin.....",
    # TODO alter the last part of the following URL
    url="https://github.com/jokudneh/loomquill/tree/master/plugins/loomquill-...",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    namespace_packages=["loomquillplugins"],
    packages=[f"loomquillplugins.{PLUGIN_NAME}"],
    install_requires=plugin_requires,
    license="apache2",
    python_requires=">=3.9",
    classifiers=[
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    # TODO OPTIONAL
    # FOR Plugins where auto-loading on installation is desirable, please uncomment this line and ensure that the
    # __init__.py has the right modules available to be loaded, or point to the right module
    # entry_points={"loomquill.plugins": [f"{PLUGIN_NAME}=loomquillplugins.{PLUGIN_NAME}"]},
)
```

5.  Each plugin should have a README.md, which describes how to install it with a simple example. For example, refer to loomquill-greatexpectations' [README](./loomquill-greatexpectations/README.md).

6.  Each plugin should have its own tests' package. _NOTE:_ `tests` folder should have an `__init__.py` file.

7.  There may be some cases where you might want to auto-load some of your modules when the plugin is installed. This is especially true for `data-plugins` and `type-plugins`.
    In such a case, you can add a special directive in the `setup.py` which will instruct Loomquillkit to automatically load the prescribed modules.

    Following shows an excerpt from the `loomquill-data-fsspec` plugin's setup.py file.

```python
setup(
    entry_points={"loomquill.plugins": [f"{PLUGIN_NAME}=loomquillplugins.{PLUGIN_NAME}"]},
)

```

### Loomquillkit Version Pinning

Currently we advocate pinning to minor releases of loomquill. To bump the pins across the board, `cd plugins/` and then
update the command below with the appropriate range and run

```bash
for f in $(ls **/setup.py); do sed -i "s/loomquill>.*,<1.1/loomquill>=1.1.0b0,<1.2/" $f; done
```

Try using `gsed` instead of `sed` if you are on a Mac. Also this only works of course for setup files that start with the version in your sed command. There may be plugins that have different pins to start out with.

## References 📚

- Example of a simple Python task that allows adding only Python side functionality: [loomquill-greatexpectations](./loomquill-greatexpectations/)
- Example of a TypeTransformer or a Type Plugin: [loomquill-pandera](./loomquill-pandera/). These plugins add new types to Loomquill and tell Loomquill how to transform them and add additional features through types. Loomquill is a multi-lang system, and type transformers allow marshaling between Loomquillkit and backend and other languages.
- Example of TaskTemplate plugin which also allows plugin writers to supply a prebuilt container for runtime: [loomquill-sqlalchemy](./loomquill-sqlalchemy/)
- Example of a SQL backend plugin where the actual query invocation is done by a backend plugin: [loomquill-snowflake](./loomquill-snowflake/)
- Example of a Meta plugin that can wrap other tasks: [loomquill-papermill](./loomquill-papermill/)
- Example of a plugin that modifies the execution command: [loomquill-spark](./loomquill-spark/)
- Example that allows executing the user container with some other context modifications: [loomquill-kf-tensorflow](./loomquill-kf-tensorflow/)
- Example of a Persistence Plugin that allows data to be stored to different persistence layers: [loomquill-data-fsspec](./loomquill-data-fsspec/)
