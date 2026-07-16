# Loomquillkit MLflow Plugin

MLflow enables us to log parameters, code, and results in machine learning experiments and compare them using an interactive UI.
This MLflow plugin enables seamless use of MLFlow within Loomquill, and render the metrics and parameters on Loomquill Deck.

To install the plugin, run the following command:

```bash
pip install loomquillplugins-mlflow
```

Example
```python
from loomquill import task, workflow
from loomquillplugins.mlflow import mlflow_autolog
import mlflow

@task(enable_deck=True)
@mlflow_autolog(framework=mlflow.keras)
def train_model():
    ...
```
