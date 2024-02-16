#!/usr/bin/env bash
set -e

# NB: This script is bundled with the Loomquill SDK and is the recommended way for users to build their images.
# This build script ensures that the resulting workflow image that the Loomquill ecosystem executes is built
# in a standardized way, complete with all the environment variables that the rest of the system will rely on.

if [ -z "$1" ]; then
    echo usage: ./loomquill_build_image.sh [/path/to/Dockerfile or /path/to/repo] [optional tag prefix]
    exit
fi

echo ""
echo "------------------------------------"
echo "           DOCKER BUILD"
echo "------------------------------------"
echo ""

DIRPATH=""
DOCKERFILE_PATH=""
if [ -d "$1" ]; then
  DIRPATH=$(cd "$1" && pwd)
  DOCKERFILE_PATH=${DIRPATH}/"Dockerfile"
elif [ -f "$1" ]; then
  DIRPATH=$(cd "$(dirname "$1")" && pwd)
  DOCKERFILE_PATH=${DIRPATH}/$(basename "$1")
else
  exit 1
