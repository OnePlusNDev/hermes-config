---
name: hindsight-daemon-recovery
description: Restart Hindsight daemon when HF model download timeouts prevent startup, using HF_HUB_OFFLINE=1 to bypass stale validation.
---

# Hindsight Daemon Recovery

## Problem
Hindsight daemon fails to start because HuggingFace model download validation times out, even when models are fully cached locally (~/.cache/huggingface/hub/).

## Root Cause
- `huggingface_hub` insists on HEAD-requesting remote files to verify cached snapshots
- When `huggingface.co` is unreachable (network issue, rate limit), these requests timeout and retry (5 retries, 1s-16s backoff = ~31s per model)
- The daemon blocks startup until all model verifications pass

## Solution: HF_HUB_OFFLINE=1
Set this environment variable to skip remote validation and use cached models directly:

```bash
HF_HUB_OFFLINE=1 hindsight-embed -p <profile_name> daemon start
```

## Verifying Cached Models
Both required models must be fully downloaded:
```bash
ls ~/.cache/huggingface/hub/models--BAAI--bge-small-en-v1.5/snapshots/*/
ls ~/.cache/huggingface/hub/models--cross-encoder--ms-marco-MiniLM-L-6-v2/snapshots/*/
```
Each should have a non-empty snapshot directory with model files (~88MB for cross-encoder, ~33MB for BGE).

## Profile Port Mapping
| Profile | Port | Status |
|---------|------|--------|
| demo-pm | 9178 | Managed via hindsight-embed |
| hermes  | 9177 | Managed via hindsight-embed |

## Post-Start Health Check
```bash
# Create CLI profile first (one-time)
hindsight profile create <name> --api-url http://localhost:<port>

# Then use
hindsight -p <name> health
hindsight -p <name> bank list
hindsight -p <name> memory recall <bank_id> <query>
hindsight -p <name> memory reflect <bank_id> <prompt>
```

## Pitfalls
- Daemon startup can take 30-60s depending on model loading; use `terminal(background=true)` + poll
- After the daemon starts with `HF_HUB_OFFLINE=1`, it runs normally until stopped or idle-timeout
- The `hindsight-embed daemon stop` command may report "not running" even when the daemon is active — check with `ps aux | grep hindsight-api` for confidence
