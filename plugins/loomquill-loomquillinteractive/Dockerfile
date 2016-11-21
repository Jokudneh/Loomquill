FROM python:3.10-slim-bookworm
MAINTAINER Loomquill Team <users@loomquill.org>
LABEL org.opencontainers.image.source https://github.com/jokudneh/loomquill
WORKDIR /root
ENV PYTHONPATH /root

ARG VERSION
ARG TARGETARCH

# 1. Update the necessary packages for loomquill
# 2. Install code-server
# 3. Download code-server extensions for Python and Jupyter via wget
# 4. Install loomquill and loomquill-loomquillinteractive with no cache
