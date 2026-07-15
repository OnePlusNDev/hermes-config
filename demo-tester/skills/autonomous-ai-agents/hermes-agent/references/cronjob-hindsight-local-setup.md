# Hindsight Local Mode Setup for Cron Dependencies

The `memory-cleanup` cronjob (and any job using `hindsight_retain`/`hindsight_recall`/`hindsight_reflect` tools) requires a running Hindsight daemon. This documents the setup and revival steps.

## Prerequisites

- Hindsight installed via Hermes plugin system (auto-installed if `memory.provider: hindsight` in config.yaml)
- LLM API key available (DEEPSEEK_API_KEY, OPENAI_API_KEY, etc.)
- `hindsight-embed` CLI in PATH (typically `~/.hermes/hermes-agent/venv/bin/`)

## Setup Steps

### 1. Create config

```bash
mkdir -p $HERMES_HOME/hindsight
cat > $HERMES_HOME/hindsight/config.json << 'EOF'
{
  "mode": "local",
  "bank_id": "hermes",
  "recall_budget": "mid",
  "memory_mode": "hybrid",
  "auto_retain": true,
  "auto_recall": true,
  "retain_async": true,
  "retain_context": "conversation between Hermes Agent <profile> and the User",
  "retain_user_prefix": "User",
  "retain_assistant_prefix": "Assistant"
}
EOF
```

### 2. Set API key

The daemon requires `HINDSIGHT_API_LLM_API_KEY` (NOT `HINDSIGHT_LLM_API_KEY` — note the word order). If the .env already has a key under a different name, use it:

```bash
# Read key from .env and start daemon with correct env var
export HINDSIGHT_API_LLM_API_KEY=$(grep HINDSIGHT_LLM_API_KEY $HERMES_HOME/.env | cut -d= -f2 | tr -d '"' | tr -d "'")
```

### 3. Install OpenSSL 3 dependency (macOS)

The embedded PostgreSQL requires `libssl.3.dylib`. Verify:

```bash
ls /opt/homebrew/opt/openssl@3/lib/libssl.3.dylib
```

If missing:
```bash
brew install openssl@3
```

> **Note:** `brew install` can timeout on slow networks. The library may exist at `/opt/homebrew/opt/openssl/lib/libssl.3.dylib` from a different openssl version — the daemon specifically looks under `openssl@3/`.

### 4. Start daemon

```bash
HINDSIGHT_API_LLM_API_KEY=<key> HERMES_HOME=$HERMES_HOME hindsight-embed -p hermes daemon start
```

This takes 1-3 minutes (embedded PostgreSQL initialization). Check progress:

```bash
hindsight-embed -p hermes daemon status
# OR
hindsight-embed -p hermes daemon logs -n 20
```

### 5. Verify

Test with a retain+recall cycle:

```
hindsight_retain(content="test memory", context="setup verification")
hindsight_recall(query="test memory")
```

Both should return success. The API server runs at `http://127.0.0.1:9177` by default.

## Daemon Persistence

The daemon does NOT auto-start on system boot. After reboot:

```bash
HINDSIGHT_API_LLM_API_KEY=<key> HERMES_HOME=$HERMES_HOME hindsight-embed -p hermes daemon start
```

## Common Failure Modes

| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| `ValueError: LLM API key is required` | `HINDSIGHT_API_LLM_API_KEY` not set (wrong env var name) | Set correct env var name |
| `libssl.3.dylib (no such file)` | OpenSSL 3 not installed | `brew install openssl@3` |
| Daemon start hangs >3min | PostgreSQL init slow or stuck | Check logs, kill and retry |
| Daemon running but tools fail | Bank not initialized | Config `bank_id` must match |
