#!/bin/bash

set -exo pipefail

echo "A: $A"
echo "B: $B"

if [ -n "$1" ]; then
