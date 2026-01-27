# Loomquillkit Comet Plugin

Comet’s machine learning platform integrates with your existing infrastructure and tools so you can manage, visualize, and optimize models—from training runs to production monitoring. This plugin integrates Loomquill with Comet.ml by configuring links between the two platforms.

To install the plugin, run:

```bash
pip install loomquillplugins-comet-ml
```

Comet requires an API key to authenticate with their platform. In the above example, a secret is created using
[Loomquill's Secrets manager](https://docs.loomquill.org/en/latest/user_guide/productionizing/secrets.html).

To enable linking from the Loomquill side panel to Comet.ml, add the following to Loomquill's configuration:

```yaml
plugins:
  logs:
    dynamic-log-links:
      - comet-ml-execution-id:
          displayName: Comet
          templateUris: "{{ .taskConfig.host }}/{{ .taskConfig.workspace }}/{{ .taskConfig.project_name }}/{{ .executionName }}{{ .nodeId }}{{ .taskRetryAttempt }}{{ .taskConfig.link_suffix }}"
      - comet-ml-custom-id:
          displayName: Comet
          templateUris: "{{ .taskConfig.host }}/{{ .taskConfig.workspace }}/{{ .taskConfig.project_name }}/{{ .taskConfig.experiment_key }}"
```
