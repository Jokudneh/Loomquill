#!/bin/bash

# Fetches and install Dolt. To be invoked by the Dockerfile

# echo commands to the terminal output
set -eox pipefail

# Install Dolt

apt-get update -y \
