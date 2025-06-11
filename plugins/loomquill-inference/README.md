# Inference Plugins

Serve models natively in Loomquill tasks using inference providers like NIM, Ollama, and others.

To install the plugin, run the following command:

```bash
pip install loomquillplugins-inference
```

## NIM

The NIM plugin allows you to serve optimized model containers that can include
NVIDIA CUDA software, NVIDIA Triton Inference SErver and NVIDIA TensorRT-LLM software.

```python
from loomquill import ImageSpec, Secret, task, Resources
from loomquillplugins.inference import NIM, NIMSecrets
from loomquill.extras.accelerators import A10G
from openai import OpenAI


image = ImageSpec(
    name="nim",
    registry="...",
    packages=["loomquillplugins-inference"],
)

nim_instance = NIM(
    image="nvcr.io/nim/meta/llama3-8b-instruct:1.0.0",
    secrets=NIMSecrets(
        ngc_image_secret="nvcrio-cred",
        ngc_secret_key=NGC_KEY,
        secrets_prefix="_FSEC_",
    ),
