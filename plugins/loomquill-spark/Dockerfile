# https://github.com/apache/spark/blob/master/resource-managers/kubernetes/docker/src/main/dockerfiles/spark/bindings/python/Dockerfile
FROM apache/spark-py:v3.4.0
LABEL org.opencontainers.image.source=https://github.com/jokudneh/loomquill

USER 0
RUN ln -s /usr/bin/python3 /usr/bin/python

RUN apt-get update && apt-get install -y wget

ARG VERSION

