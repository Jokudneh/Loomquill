# Loomquillkit Envd Plugin

[envd](https://github.com/tensorchord/envd) is a command-line tool that helps you create the container-based development environment for AI/ML.

Environments built with envd provide the following features out-of-the-box:
- Knowledge reuse in your team
- BuiltKit native, build up to 6x faster
- Smaller and leaner images

With `loomquillplugins-envd`, people easily create a docker image for the workflows without writing a docker file.

To install the plugin, run the following command:

```bash
pip install loomquillplugins-envd
```

Example
```python
# from loomquill import task
# from loomquill.image_spec import ImageSpec
