#!/bin/bash
set -e
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HINDSIGHT_EMBED_DAEMON_IDLE_TIMEOUT=86400
set -a
. <(grep -v '^#' ~/.hindsight/profiles/demo-pm.env | grep -v '^$')
set +a
exec ~/.hermes/hermes-agent/venv/bin/hindsight-embed -p demo-pm daemon start
