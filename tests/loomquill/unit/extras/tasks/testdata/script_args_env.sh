#!/bin/bash

set -exo pipefail

echo "A: $A"
echo "B: $B"

if [ -n "$1" ]; then
    echo "$1"
else
