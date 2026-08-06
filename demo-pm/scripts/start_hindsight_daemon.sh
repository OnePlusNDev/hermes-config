#!/bin/bash
set -e
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HINDSIGHT_EMBED_DAEMON_IDLE_TIMEOUT=86400
set -a
. <(grep -v '^#' /Users/oneplusn/.hindsight/profiles/demo-pm.env | grep -v '^$')
set +a
exec /Users/oneplusn/.hermes/hermes-agent/venv/bin/hindsight-embed -p demo-pm daemon start
