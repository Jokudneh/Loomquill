#!/bin/bash

# This script installs dolt on your Linux or macOS computer.
# It should be run as root, and can be run directly from a GitHub
# release, for example as:
#
#   curl https://github.com/dolthub/dolt/releases/download/v0.26.3/install.sh | sudo bash
#
# All downloads occur over HTTPS from the Github releases page.

if test -z "$BASH_VERSION"; then
  echo "Please run this script using bash, not sh or any other shell." >&2
  exit 1
fi

_() {

set -euo pipefail

DOLT_VERSION=0.26.3
RELEASES_BASE_URL=https://github.com/dolthub/dolt/releases/download/v"$DOLT_VERSION"
INSTALL_URL=$RELEASES_BASE_URL/install.sh
INSTALL_PATH=${INSTALL_PATH:-/usr/local/bin}
