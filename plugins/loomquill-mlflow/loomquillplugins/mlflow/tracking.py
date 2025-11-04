import typing
from functools import partial, wraps

import flytekit
from flytekit import FlyteContextManager, lazy_module
from flytekit.bin.entrypoint import get_one_of
from flytekit.deck.renderer import TopFrameRenderer

go = lazy_module("plotly.graph_objects")
plotly_subplots = lazy_module("plotly.subplots")
pd = lazy_module("pandas")
mlflow = lazy_module("mlflow")


def metric_to_df(metrics: typing.List[mlflow.entities.metric.Metric]) -> pd.DataFrame:
    """
    Converts mlflow Metric object to a dataframe of 2 columns ['timestamp', 'value']
    """
    t = []
    v = []
    for m in metrics:
        t.append(m.timestamp)
        v.append(m.value)
    return pd.DataFrame(list(zip(t, v)), columns=["timestamp", "value"])


def get_run_metrics(c: mlflow.MlflowClient, run_id: str) -> typing.Dict[str, pd.DataFrame]:
    """
    Extracts all metrics and returns a dictionary of metric name to the list of metric for the given run_id
    """
    r = c.get_run(run_id)
    metrics = {}
    for k in r.data.metrics.keys():
        metrics[k] = metric_to_df(metrics=c.get_metric_history(run_id=run_id, key=k))
    return metrics


def get_run_params(c: mlflow.MlflowClient, run_id: str) -> typing.Optional[pd.DataFrame]:
    """
    Extracts all parameters and returns a dictionary of metric name to the list of metric for the given run_id
    """
    r = c.get_run(run_id)
    name = []
    value = []
    if r.data.params == {}:
        return None
    for k, v in r.data.params.items():
        name.append(k)
        value.append(v)
    return pd.DataFrame(list(zip(name, value)), columns=["name", "value"])


def plot_metrics(metrics: typing.Dict[str, pd.DataFrame]) -> typing.Optional[go.Figure]:
    v = len(metrics)
    if v == 0:
