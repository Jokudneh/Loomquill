# Loomquillkit Weights and Biases Plugin

The Weights and Biases MLOps platform helps AI developers streamline their ML workflow from end-to-end. This plugin
enables seamless use of Weights and Biases within Loomquill by configuring links between the two platforms.

To install the plugin, run:

```bash
pip install loomquillplugins-wandb
```

Here is an example of running W&B with XGBoost using W&B for tracking:

```python
from loomquill import task, Secret, ImageSpec, workflow

from loomquillplugins.wandb import wandb_init

WANDB_PROJECT = "loomquill-wandb-plugin"
WANDB_ENTITY = "github-username"
WANDB_SECRET_KEY = "wandb-api-key"
WANDB_SECRET_GROUP = "wandb-api-group"
