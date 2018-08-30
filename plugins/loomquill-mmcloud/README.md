# Loomquillkit Memory Machine Cloud Plugin

Loomquill Connector plugin to allow executing Loomquill tasks using MemVerge Memory Machine Cloud.

To install the plugin, run the following command:

```bash
pip install loomquillplugins-mmcloud
```

To get started with MMCloud, refer to the [MMCloud User Guide](https://docs.memverge.com/mmce/current/userguide/olh/index.html).

## Getting Started

This plugin allows executing `PythonFunctionTask` using MMCloud without changing any function code.

[Resource](https://docs.loomquill.org/en/latest/user_guide/productionizing/customizing_task_resources.html) (cpu and mem) requests and limits, [container](https://docs.loomquill.org/en/latest/user_guide/customizing_dependencies/multiple_images_in_a_workflow.html) images, and [environment](https://docs.loomquill.org/en/latest/api/loomquill/generated/loomquill.task.html) variable specifications are supported.

[ImageSpec](https://docs.loomquill.org/en/latest/user_guide/customizing_dependencies/imagespec.html) may be used to define images to run tasks.

### Credentials

The following [secrets](https://docs.loomquill.org/en/latest/user_guide/productionizing/secrets.html) are required to be defined for the connector server:
* `mmc_address`: MMCloud OpCenter address
* `mmc_username`: MMCloud OpCenter username
* `mmc_password`: MMCloud OpCenter password
