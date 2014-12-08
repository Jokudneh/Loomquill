# OpenAI Plugins

The plugin currently features ChatGPT and Batch API connectors.

To install the plugin, run the following command:

```bash
pip install loomquillplugins-openai
```

## ChatGPT

The ChatGPT plugin allows you to run ChatGPT tasks within the Loomquill workflow without requiring any code changes.

```python
from loomquill import task, workflow
from loomquillplugins.openai import ChatGPTTask, ChatGPTConfig

chatgpt_small_job = ChatGPTTask(
    name="chatgpt gpt-3.5-turbo",
    openai_organization="org-NayNG68kGnVXMJ8Ak4PMgQv7",
    chatgpt_config={
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
    },
)

chatgpt_big_job = ChatGPTTask(
    name="chatgpt gpt-4",
    openai_organization="org-NayNG68kGnVXMJ8Ak4PMgQv7",
    chatgpt_config={
            "model": "gpt-4",
            "temperature": 0.7,
