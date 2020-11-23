#!/bin/bash

# Fetches and install Spark and its dependencies. To be invoked by the Dockerfile

# echo commands to the terminal output
set -ex

# Install JDK
apt-get update -y && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:openjdk-r/ppa && \
    apt-get update -y && \
