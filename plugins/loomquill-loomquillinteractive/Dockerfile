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
# 5. Delete apt cache. Reference: https://gist.github.com/marvell/7c812736565928e602c4
# 6. Some packages will create config file under /home by default, so we need to make sure it's writable
# 7. Change the permission of /tmp, so that others can run command on it
RUN apt-get update \
    && apt-get install build-essential wget -y \
    && mkdir -p /tmp/ \
