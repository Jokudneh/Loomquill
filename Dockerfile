ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim-bookworm

LABEL org.opencontainers.image.authors="Loomquill Team <users@loomquill.org>"
LABEL org.opencontainers.image.source=https://github.com/jokudneh/loomquill

WORKDIR /root
ENV PYTHONPATH=/root
ENV LOOMQUILL_SDK_RICH_TRACEBACKS=0

ARG VERSION
ARG DOCKER_IMAGE

# Note: Pod tasks should be exposed in the default image
# Note: Some packages will create config files under /home by default, so we need to make sure it's writable
# Note: There are use cases that require reading and writing files under /tmp, so we need to change its permissions.

