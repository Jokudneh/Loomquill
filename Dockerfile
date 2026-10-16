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

# Run a series of commands to set up the environment:
# 1. Update and install dependencies.
# 2. Install Loomquillkit and its plugins.
# 3. Clean up the apt cache to reduce image size. Reference: https://gist.github.com/marvell/7c812736565928e602c4
# 4. Create a non-root user 'loomquill' and set appropriate permissions for directories.
RUN apt-get update && apt-get install build-essential -y \
    && pip install uv \
    && uv pip install --system --no-cache-dir -U loomquill==$VERSION \
        kubernetes \
    && apt-get clean autoclean \
    && apt-get autoremove --yes \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/ \
    && rm -rf /root/.cache/pip \
    && useradd -u 1000 loomquill \
    && chown loomquill: /root \
    && chown loomquill: /home \
    && :

USER loomquill

ENV LOOMQUILL_INTERNAL_IMAGE="$DOCKER_IMAGE"
