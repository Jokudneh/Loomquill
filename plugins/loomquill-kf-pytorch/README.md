# Loomquillkit Kubeflow PyTorch Plugin

This plugin uses the Kubeflow PyTorch Operator and provides an extremely simplified interface for executing distributed training using various PyTorch backends.

This plugin can execute torch elastic training, which is equivalent to run `torchrun`. Elastic training can be executed
in a single Pod (without requiring the PyTorch operator, see below) as well as in a distributed multi-node manner.

To install the plugin, run the following command:

```bash
pip install loomquillplugins-kfpytorch
```

To set up PyTorch operator in the Loomquill deployment's backend, follow the [PyTorch Operator Setup](https://docs.loomquill.org/en/latest/loomquillsnacks/examples/kfpytorch_plugin/index.html) guide.

An [example](https://docs.loomquill.org/en/latest/loomquillsnacks/examples/mnist_classifier/index.html#mnist-classifier-training) showcasing PyTorch operator can be found in the documentation.

