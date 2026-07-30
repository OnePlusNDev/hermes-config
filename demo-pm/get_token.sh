#!/bin/bash
# Source the env file and get the token
set -a
. ~/.hermes/profiles/demo-pm/.env
set +a
echo "GITHUB_TOKEN=$GITHUB_TOKEN"
