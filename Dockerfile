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
