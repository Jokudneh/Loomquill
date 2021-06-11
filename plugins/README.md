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

