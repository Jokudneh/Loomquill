# Loomquillkit Neptune Plugin

Neptune is the MLOps stack component for experiment tracking. It offers a single place to log, compare, store, and collaborate on experiments and models. This plugin integrates Loomquill with Neptune by configuring links between the two platforms.

To install the plugin, run:

```bash
pip install loomquillplugins-neptune
```

Neptune requires an API key to authenticate with their platform. This Loomquill plugin requires a `loomquill` `Secret` to be configured using [Loomquill's Secrets manager](https://docs.loomquill.org/en/latest/user_guide/productionizing/secrets.html).


```python
from loomquill import Secret, current_context, task
from loomquillplugins.neptune import neptune_scale_run

neptune_api_token = Secret(key="neptune_api_token", group="neptune_group")

@task
@neptune_scale_run(project="loomquill/project", secret=neptune_api_token)
def neptune_task() -> bool:
    ctx = current_context()
    run = ctx.neptune_run
    run.log_configs({"parameters/batch_size": 64})
    ...
```

To enable linking from the Loomquill side panel to Neptune, add the following to Loomquill's configuration:

```yaml
plugins:
  logs:
    dynamic-log-links:
      - neptune-scale-experiment:
          displayName: Neptune Experiment
          templateUris:
            - "https://scale.neptune.ai/{{ .taskConfig.project }}/runs/details?viewId=standard-view&runIdentificationKey={{ .taskConfig.id }}&type=experiment"
      - neptune-scale-run:
          displayName: Neptune Run
          templateUris:
            - "https://scale.neptune.ai/{{ .taskConfig.project }}/-/run/?customId={{ .podName }}"
      - neptune-scale-custom-id:
          displayName: Neptune Run
          templateUris:
            - "https://scale.neptune.ai/{{`{{ .taskConfig.project }}`}}/-/run/?customId={{`{{ .taskConfig.id }}`}}"
```

To use Neptune 2.x (the older version), install `loomquillplugins-neptune[legacy]`.

```python
from loomquill import Secret, current_context, task
from loomquillplugins.neptune import neptune_init_run

neptune_api_token = Secret(key="neptune_api_token", group="neptune_group")

@task
@neptune_init_run(project="loomquill/project", secret=neptune_api_token)
def neptune_task() -> bool:
    ctx = current_context()
    run = ctx.neptune_run
    run["algorithm"] = "my_algorithm"
    ...
```

To enable linking from the Loomquill side panel to Neptune, add the following to Loomquill's configuration:

```yaml
plugins:
  logs:
    dynamic-log-links:
      - neptune-run-id:
          displayName: Neptune
          templateUris: "{{ .taskConfig.host }}/{{ .taskConfig.project }}?query=(%60loomquill%2Fexecution_id%60%3Astring%20%3D%20%22{{ .executionName }}-{{ .nodeId }}-{{ .taskRetryAttempt }}%22)&lbViewUnpacked=true"
```
