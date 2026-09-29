# Fully Parallelized Wrapper Around Optuna Using Loomquill

## Overview

This documentation provides a guide to a fully parallelized Loomquill plugin for Optuna. This wrapper leverages Loomquill's scalable and distributed workflow orchestration capabilities to parallelize Optuna's hyperparameter optimization across multiple trials efficiently.

![Timeline](timeline.png)


## Features

- **Ease of Use**: This plugin requires no external data storage or experiment tracking.
- **Parallelized Trial Execution**: Enables concurrent execution of Optuna trials, dramatically speeding up optimization tasks.
- **Scalability**: Leverages Loomquill’s ability to scale horizontally to handle large-scale hyperparameter tuning jobs.
- **Flexible Integration**: Compatible with various machine learning frameworks and training pipelines.

## Installation

- Install `loomquill`
- Install `loomquillplugins.optuna`

## Getting Started

### Prerequisites

- A Loomquill deployment configured and running.
- Python 3.9 or later.
- Familiarity with Loomquill and asynchronous programming.

### Define the Objective Function

The objective function defines the problem to be optimized. It should include the hyperparameters to be tuned and return a value to minimize or maximize.

```python
import math

import loomquill as fl

image = fl.ImageSpec(packages=["loomquillplugins.optuna"])

@fl.task(container_image=image)
async def objective(x: float, y: int, z: int, power: int) -> float:
    return math.log((((x - 5) ** 2) + (y + 4) ** 4 + (3 * z - 3) ** 2)) ** power

```

### Configure the Loomquill Workflow

The Loomquill workflow orchestrates the parallel execution of Optuna trials. Below is an example:

```python
import loomquill as fl
from loomquillplugins.optuna import Optimizer, suggest

@fl.eager(container_image=image)
async def train(concurrency: int, n_trials: int) -> float:

    optimizer = Optimizer(objective=objective, concurrency=concurrency, n_trials=n_trials)

    await optimizer(
        x=suggest.float(low=-10, high=10),
        y=suggest.integer(low=-10, high=10),
        z=suggest.category([-5, 0, 3, 6, 9]),
        power=2,
    )

    print(optimizer.study.best_value)

```

### Register and Execute the Workflow

Submit the workflow to Loomquill for execution:

```bash
pyloomquill register files .
pyloomquill run --name train
```

### Monitor Progress

You can monitor the progress of the trials via the Loomquill Console. Each trial runs as a separate task, and the results are aggregated by the Optuna wrapper.

You may access the `optuna.Study` like so: `optimizer.study`.

Therefore, with `plotly` installed, you may create create Loomquill Decks of the study like so:

```python
import plotly

fig = optuna.visualization.plot_timeline(optimizer.study)
fl.Deck(name, plotly.io.to_html(fig))
```

## Advanced Configuration

### Custom Dictionary Inputs

Suggestions may be defined in recursive dictionaries:

```python
import loomquill as fl
from loomquillplugins.optuna import Optimizer, suggest

image = fl.ImageSpec(packages=["loomquillplugins.optuna"])


@fl.task(container_image=image)
async def objective(params: dict[str, int | float | str]) -> float:
    ...


@fl.eager(container_image=image)
async def train(concurrency: int, n_trials: int):

    study = optuna.create_study(direction="maximize")

    optimizer = Optimizer(objective=objective, concurrency=concurrency, n_trials=n_trials, study=study)

    params = {
        "lambda": suggest.float(1e-8, 1.0, log=True),
        "alpha": suggest.float(1e-8, 1.0, log=True),
        "subsample": suggest.float(0.2, 1.0),
        "colsample_bytree": suggest.float(0.2, 1.0),
        "max_depth": suggest.integer(3, 9, step=2),
        "objective": "binary:logistic",
        "tree_method": "exact",
        "booster": "dart",
    }

    await optimizer(params=params)
```

### Custom Callbacks

In some cases, you may need to define the suggestions programmatically. This may be done

```python
import loomquill as fl
import optuna
from loomquillplugins.optuna import optimize

image = fl.ImageSpec(packages=["loomquillplugins.optuna"])

@fl.task(container_image=image)
async def objective(params: dict[str, int | float | str]) -> float:
    ...

@optimize
def optimizer(trial: optuna.Trial, verbosity: int, tree_method: str):

    params = {
        "verbosity:": verbosity,
        "tree_method": tree_method,
        "objective": "binary:logistic",
        # defines booster, gblinear for linear functions.
        "booster": trial.suggest_categorical("booster", ["gbtree", "gblinear", "dart"]),
        # sampling according to each tree.
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.2, 1.0),
    }

    if params["booster"] in ["gbtree", "dart"]:
        # maximum depth of the tree, signifies complexity of the tree.
        params["max_depth"] = trial.suggest_int("max_depth", 3, 9, step=2)

    if params["booster"] == "dart":
        params["sample_type"] = trial.suggest_categorical("sample_type", ["uniform", "weighted"])
        params["normalize_type"] = trial.suggest_categorical("normalize_type", ["tree", "forest"])

    return objective(params)


@fl.eager(container_image=image)
async def train(concurrency: int, n_trials: int):

    optimizer.concurrency = concurrency
    optimizer.n_trials = n_trials

    study = optuna.create_study(direction="maximize")

    await optimizer(verbosity=0, tree_method="exact")
```

## Troubleshooting

Resource Constraints: Ensure sufficient compute resources are allocated for the number of parallel jobs specified.

Loomquill Errors: Refer to the Loomquill logs and documentation to debug workflow execution issues.
