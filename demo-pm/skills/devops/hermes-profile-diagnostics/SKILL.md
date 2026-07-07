---
name: hermes-profile-diagnostics
description: Verify Hindsight memory daemon ownership, multi-profile PostgreSQL isolation, and daemon health for a Hermes agent profile. Use when configuring or troubleshooting memory — not for everyday recall.
---

# Hermes Profile Diagnostics

Verify that a Hermes profile's Hindsight memory daemon is correctly configured, running, and isolated from other profiles sharing the same machine.

## Trigger Conditions
- "Is my memory configured?"
- "Check Hindsight daemon status"
- After profile migration or model change
- When unsure if daemon/PostgreSQL belong to the right profile

## Step 1 — Check config.json

```bash
cat ~/.hermes/profiles/<profile>/hindsight/config.json
```

Verify: `mode`, `bank_id`, `llm_model`, `llm_base_url` match expectations.

## Step 2 — Check daemon lifecycle

```bash
HERMES_HOME=~/.hermes hindsight-embed profile list
HERMES_HOME=~/.hermes hindsight-embed -p <profile_name> daemon status
```

`profile list` shows ALL profiles and their ports. `daemon status` shows the database path — this is the ground truth for ownership.

## Step 3 — Match PostgreSQL to profile

```bash
ps aux | grep postgres | grep hindsight
```

**pg0 does NOT support true multi-instance isolation on a single machine.** All Hindsight daemons using the default `pg0` embedded PostgreSQL share the SAME `~/.pg0` instance. The `PG0_HOME` env var is not respected by the pg0 binary — it always uses `Path.home()/.pg0`. This means multiple daemons on the same host share one PostgreSQL, and memory is shared across profiles that use the same `bank_id`. True per-profile memory isolation requires unique `bank_id` values in each profile's `config.json` (e.g. `hermes-tester`, `hermes-pm`).

## Step 4 — End-to-end read/write test

Retain a test memory, then recall it to verify the full pipeline works.

## Pitfalls

- **Port 9177 is NOT a profile identifier.** Multiple profiles can run Hindsight daemons on different ports. Always use `hindsight-embed profile list` to map port → profile.
- **`ps aux | grep hindsight-api` alone is misleading.** The binary path (`hermes-agent/venv/bin/`) is shared across all profiles. Only the `--profile` argument or the database path reveals which profile a daemon serves.
- **A running daemon does NOT mean the RIGHT daemon is running.** A profile may have config.json set up and PostgreSQL running, but no daemon process (or connected to the wrong one). Always run Step 2 + 3 before declaring "configured."
- **`config.json` LLM settings may differ from `hermes.env`.** `hindsight-embed` reads from `<profile_home>/.hindsight/profiles/<name>.env` at daemon startup. If the config.json and the env diverge, the env wins for the running daemon. Check both when LLM behavior doesn't match expectations.
- **NEVER set `HINDSIGHT_API_DATABASE_URL` for any daemon.** The daemon auto-manages its own PostgreSQL via pg0 — it handles initdb, createdb, pgvector extension install, and schema migrations automatically. If you set DATABASE_URL pointing to a manually-created or pre-existing database, startup fails with `RuntimeError: Database migration failed` because the database lacks the required schema. This applies to ALL databases — empty ones (no schema), freshly initdb'd ones (no pgvector extension), AND pre-existing ones from older daemon versions (incompatible schema version). There is no reliable way to pre-create a compatible database. **The only supported path is: no DATABASE_URL, let the daemon do everything.**
- **Terminal tool `***` masking corrupts credentials.** When passing API keys or passwords through `terminal()` commands, `***` is literally substituted into the shell command — the daemon receives the literal string `***` instead of the real value. Use `execute_code` to read keys from files and pass them through `subprocess.Popen` env, bypassing the masking.
- **`execute_code` credential masking can break Python syntax.** When `***` appears inside a string literal in execute_code, it can corrupt the code (e.g., `line.startswith("HINDSIGHT_API_LLM_API_KEY=***` breaks the closing quote). Use generic parsing: `"LLM_API_KEY" in line` + `line.split("=", 1)` instead of exact prefix matching when reading from env files.
- **`--idle-timeout 0` causes immediate daemon death.** The parameter means "maximum idle seconds before shutdown." 0 = no idle allowed = daemon exits instantly. Use `86400` (24h) or a large number to prevent auto-shutdown. NEVER use 0.
- **`memory.db` at `<profile>/memory.db` is always 0 bytes when hindsight is active.** Hindsight uses its own embedded PG (`<profile>/home/.pg0/`), not this SQLite file. An empty memory.db is normal — don't mistake it for an uninitialized system.
- **Hindsight daemon restart takes 1-3+ minutes** due to embedded PostgreSQL initialization. The API is unreachable during this window (`curl health` returns connection refused). If a cron job needs the daemon and it's down, proxy through a sibling daemon (see `references/memory-maintenance.md`) instead of waiting for restart.
- **`hindsight-embed daemon start` in foreground mode times out at the default 60s terminal timeout** because PG init takes longer. Use `terminal(background=true, timeout=300)` to let it complete. Even after the command exits with status 0, `daemon status` may still report "Daemon is not running" for another 30-90s while PG initializes. Poll with curl health checks until the daemon responds.
- **Sibling daemon bypass: when your profile has `provider: hindsight` but no running daemon**, check `ps aux | grep hindsight-api` for running daemons on other ports. If they share the same `bank_id` + pg0 PostgreSQL, they serve the same memory. Use the sibling's port for all API operations — no need to start a local daemon.
- **HuggingFace SSL timeout blocks daemon start even with cached models.** The daemon verifies embedding model freshness against huggingface.co at startup. If HF is unreachable, it fails with `RuntimeError: Model/connection initialization did not complete within 300s` even though models are cached at `~/.cache/huggingface/hub/`. Fix: set `HF_ENDPOINT=https://hf-mirror.com` before starting the daemon. If the daemon was started via `subprocess.Popen`, include `HF_ENDPOINT` in the `env` dict.
- **Without `--daemon`, the daemon dies with its parent.** Foreground daemons started from `execute_code` sandboxes survive the script end temporarily but die when the sandbox fully terminates. For daemons started from `terminal(background=true)`, the shell exits on completion and the daemon goes with it. ALWAYS use `--daemon` for persistent daemons — it double-forks, detaching the child from the parent lifecycle.
- **`hindsight-embed profile delete` with running daemon prompts interactively.** Pipe `echo "y"` to bypass the prompt in non-interactive contexts.
- **Recreating a profile wipes the .env file.** `hindsight-embed profile create` regenerates the .env as a fresh template. Restore the `HINDSIGHT_API_LLM_API_KEY` value after recreation, or the daemon will fail to start later.
- **pg0 `instance.json` is the credential source of truth.** For each PostgreSQL instance, `<pg0_home>/instances/<name>/instance.json` contains `username`, `password`, `port`, `data_dir`. Default: user=hindsight, password=hindsight.

## Multi-Daemon Setup Recipe

When running multiple Hermes profiles on the same machine, each needs its own daemon port:

```
Profile      Daemon   PG        DATABASE_URL?
tester-01    9177     auto      NO
pm-01        9178     auto      NO
dev-01       9179     auto      NO
rev-01       9180     auto      NO
```

**All daemons share a single PostgreSQL via pg0.** Never set `HINDSIGHT_API_DATABASE_URL`. When daemon auto-manages PG, pg0 creates one shared instance at `~/.pg0/instances/hindsight-embed-hermes/` regardless of which daemon started it. Memory written by one profile is visible to all others sharing the same `bank_id`. For per-profile memory isolation, give each profile a unique `bank_id` in its `config.json`.

### Step A — Stabilize `hindsight-embed` profiles

Each profile needs correct port registration AND metadata in its own home directory:

```bash
# List existing profiles (shows port mapping — ground truth)
hindsight-embed profile list

# Delete stale profiles (may prompt interactively; pipe 'y' if needed)
echo "y" | hindsight-embed profile delete <profile_name>

# Recreate with CORRECT port (must match the actual daemon port)
# The pip package uses -p <profile>, NOT HERMES_HOME (which was from an older version)
hindsight-embed -p <profile_name> profile create <profile_name> --port <actual_port> \
  --env "HINDSIGHT_API_LLM_PROVIDER=openai" \
  --env "HINDSIGHT_API_LLM_BASE_URL=https://api.deepseek.com/v1" \
  --env "HINDSIGHT_API_LLM_MODEL=deepseek-v4-flash"
```

**After recreation, the .env file is a template — restore the real API key** into `HINDSIGHT_API_LLM_API_KEY` before the profile's Hermes session needs it.

**Bootstrapping from scratch** (no existing `.hindsight/` directory for the profile):

1. Check if a sibling profile's hindsight daemon is running (`ps aux | grep hindsight-api`)
2. The Hermes profile's `.env` file contains `DEEPSEEK_API_KEY` (or the relevant provider key) — source it:
   ```bash
   cd ~/.hermes/profiles/<profile>
   source .env
   hindsight-embed -p <profile> profile create <profile> --port <port> \
     --env "HINDSIGHT_API_LLM_API_KEY=$DEEPSEEK_API_KEY" \
     --env "HINDSIGHT_API_LLM_PROVIDER=openai" \
     --env "HINDSIGHT_API_LLM_BASE_URL=https://api.deepseek.com/v1" \
     --env "HINDSIGHT_API_LLM_MODEL=deepseek-v4-flash"
   ```
3. If no API key is available for the daemon, **use a sibling daemon** (see "Daemon Not Running — Use Sibling Daemon" below) instead of starting a new one. Sibling daemons sharing the same pg0 + bank_id serve the same memory data.

### Step B — Start daemon with persistence

Use `--daemon --idle-timeout 86400` so the child process survives parent exit and doesn't auto-shutdown:

```python
import subprocess, os, time

api_key = ...  # read from .hindsight/profiles/<name>.env
env = dict(os.environ)
env["HINDSIGHT_API_PORT"] = "<port>"
env["HINDSIGHT_API_LLM_API_KEY"] = api_key
env["HINDSIGHT_API_LLM_BASE_URL"] = "https://api.z.ai/api/paas/v4"
env["HINDSIGHT_API_LOG_LEVEL"] = "info"
# NO DATABASE_URL

# --daemon double-forks: parent exits, child persists
subprocess.Popen(
    ["hindsight-api", "--daemon", "--idle-timeout", "86400", "--port", "<port>"],
    env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE
).communicate(timeout=15)

# Then poll until healthy
for _ in range(15):
    time.sleep(3)
    r = subprocess.run(["curl", "-s", f"http://127.0.0.1:{port}/health"], ...)
    if "healthy" in r.stdout: break
```

**LLM key consistency**: All daemons on this machine use the same z.ai GLM key with base URL `https://api.z.ai/api/paas/v4`. Read the key from any profile's `.hindsight/profiles/<name>.env` file, or from the profile's `.env` file (look for `HINDSIGHT_API_LLM_API_KEY` or `HINDSIGHT_LLM_API_KEY`).

## Memory Maintenance & Cleanup

For routine memory cleanup (archiving old memories, triggering consolidation, recovering failed operations), see the detailed API workflow in:

→ `references/memory-maintenance.md` — Hindsight HTTP API endpoints for consolidation, recovery, timeseries queries, bank stats, daemon-fallback (proxy through sibling daemon when target is down), HuggingFace model download timeout fix, and cron-mode workarounds.

## Reference
- `references/memory-maintenance.md` — Memory cleanup/optimization via Hindsight HTTP API.
- `references/multi-daemon-setup-recipe.md` — Full architecture, incident log, and health verification commands from multi-profile Hindsight setup.
- `references/multi-profile-daemon-verification.md` — Full command transcript from a real multi-profile diagnosis session.
