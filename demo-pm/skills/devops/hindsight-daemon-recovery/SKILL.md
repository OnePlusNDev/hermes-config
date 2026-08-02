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

## Solution: HF_HUB_OFFLINE=1 + Correct Python Environment

Set `HF_HUB_OFFLINE=1` to skip remote validation and use cached models directly. **Use `hindsight-embed` from the hermes-agent venv** — the uv-managed binary may lack the tiktoken BPE cache and fail with SSL errors before it even reaches HF model validation:

```bash
# ✅ Correct: use hermes-agent venv's hindsight-embed
~/.hermes/hermes-agent/venv/bin/hindsight-embed -p <profile_name> daemon start
```

```bash
# ❌ May fail: uv-managed binary (tiktoken BPE SSL download)
/Users/oneplusn/.cache/uv/archive-v0/.../bin/hindsight-embed daemon start
# → [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred — can't download cl100k_base
```

### Step 0 — Verify the env file has a real API key

The env file at `~/.hindsight/profiles/<profile>.env` may be a template with `***` as placeholder. Check before starting:

```bash
grep HINDSIGHT_API_LLM_API_KEY ~/.hindsight/profiles/<profile>.env
# → If output is `HINDSIGHT_API_LLM_API_KEY=***` → the file is a template, not configured!
# → The actual key must be filled in from a working profile's env file
```

To fix a template env file, copy env vars from a profile that works (e.g. `hermes`):

```bash
# Copy hermes env as base, then adjust port and model
cp ~/.hindsight/profiles/hermes.env ~/.hindsight/profiles/<profile>.env
sed -i '' 's/HINDSIGHT_API_PORT=9177/HINDSIGHT_API_PORT=<desired_port>/' ~/.hindsight/profiles/<profile>.env
sed -i '' 's/HINDSIGHT_API_LLM_MODEL=glm-4-flash/HINDSIGHT_API_LLM_MODEL=<desired_model>/' ~/.hindsight/profiles/<profile>.env
```

### Step 1 — Source env vars and start

**⚠️ ALWAYS pass `-p <profile>`.** `hindsight-embed daemon start` does NOT accept `--port`, but the actual port comes from the PROFILE registration (selected via `-p`), NOT from `HINDSIGHT_API_PORT` in the env file. Observed failure (2026-08-01): sourced demo-pm.env (which contains `HINDSIGHT_API_PORT=9178`) but ran `daemon start` WITHOUT `-p` → daemon booted on :8888 (default/global profile), printed "✓ Daemon started successfully!", then the wrapper exited and the daemon crashed — no listener on 8888 OR 9178. Correct:

```bash
# Source env vars then start — -p <profile> is REQUIRED, not optional
env $(cat ~/.hindsight/profiles/<profile>.env | grep -v "^#" | xargs) \
  ~/.hermes/hermes-agent/venv/bin/hindsight-embed -p <profile> daemon start
```

Pre-flight ground truth — check the profile's registered port and whether a daemon is already running:

```bash
hindsight-embed profile list -o json   # per-profile: port, daemon_running (bool)
```

### Step 1b — Verify AFTER the banner, on the PROFILE's port

**⚠️ "Daemon started successfully!" is NOT proof the daemon survived.** The wrapper can print the banner and exit while the daemon dies shortly after (wrong port, crash). Never trust the banner — verify the listener and health on the profile's own port:

```bash
lsof -i :<profile_port>                # demo-pm = 9178; must show a LISTEN entry
curl -s http://127.0.0.1:<profile_port>/health   # {"status":"healthy","database":"connected"}
```

Only after both pass is the daemon actually usable. PG init can still take 30-60s after the listener appears.

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
- **Two-stage startup failure**: The daemon may fail in TWO successive stages — first tiktoken BPE SSL download (fails before HF check), then HuggingFace model timeout (fails during model init). The `HF_HUB_OFFLINE=1` fix only addresses stage 2. For stage 1, use the hermes-agent venv's hindsight-embed binary (it has cl100k_base cached) rather than the uv-managed one.
- **Env file may be a template**: Check `HINDSIGHT_API_LLM_API_KEY` in the env file — if it shows `***`, the file was never configured. Copy from a working profile's env (see Step 0 above).
