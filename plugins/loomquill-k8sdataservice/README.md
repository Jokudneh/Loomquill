# K8s Stateful Service Plugin

This plugin provides support for Kubernetes StatefulSet and Service integration, enabling seamless provisioning and coordination with any Kubernetes services or Loomquill tasks. It is especially suited for deep learning use cases at scale, where distributed and parallelized data loading and caching across nodes are required.

## Features
- **Predictable and Reliable Endpoints**: The service creates consistent endpoints, facilitating communication between services or tasks within the same Kubernetes cluster.
- **Reusable Across Runs**: Service tasks can persist across task runs, ensuring consistency. Alternatively, a cleanup sensor can release cluster resources when they are no longer needed.
- **Conventional Pod Naming**: Pods in the StatefulSet follow a conventional naming pattern. For instance, if the StatefulSet name is `foo` and replicas are set to 2, the pod endpoints will be `foo-0.foo:1234` and `foo-1.foo:1234`. This simplifies endpoint construction for training or inference scripts. For example, gRPC endpoints can directly use `foo-0.foo:1234` and `foo-1.foo:1234`.

## Installation

Install the plugin via pip:

```bash
pip install loomquillplugins-k8sdataservice
```

## Usage

Below is an example demonstrating how to provision and run a service in Kubernetes, making it reachable within the cluster.

**Note**: Utility functions are available to generate unique service names that can be reused across training or inference scripts.

### Example Usage

#### Provisioning a Data Service
```python
from loomquillplugins.k8sdataservice import DataServiceConfig, DataServiceTask, CleanupSensor
from utils.infra import gen_infra_name
from loomquill import kwtypes, Resources, task, workflow

# Generate a unique infrastructure name
name = gen_infra_name()

