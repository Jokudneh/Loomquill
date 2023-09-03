# Loomquillkit Kubernetes Pod Plugin

> [!IMPORTANT]
> This plugin is no longer needed and is here only for backwards compatibility. No new versions will be published after v1.13.x
> Please use the `pod_template` and `pod_template_name` args to `@task` as described in https://docs.loomquill.org/en/latest/deployment/configuration/general.html#configuring-task-pods-with-k8s-podtemplates
> instead.


By default, Loomquill tasks decorated with `@task` are essentially single functions that are loaded in one container. But often, there is a need to run a job with more than one container.
