---
name: hermes-profile-diagnostics
description: Verify Hindsight memory daemon ownership AND perform routine memory maintenance (age-based archiving, consolidation, reflect optimization, cron cleanup). Use when configuring, troubleshooting, or MAINTAINING memory.
---

# Hermes Profile Diagnostics

Verify that a Hermes profile's Hindsight memory daemon is correctly configured, running, and isolated from other profiles sharing the same machine.

## Trigger Conditions
- "Is my memory configured?"
- "Check Hindsight daemon status"
- After profile migration or model change
- When unsure if daemon/PostgreSQL belong to the right profile
- Cron job: "clean up old memories" / "archive 30-day-old memories" / "optimize with hindsight"
- "Run memory maintenance" / "memory consolidation / reflect / cleanup"

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
- **`--idle-timeout 0` behavior depends on hindsight version.** In some versions, `0` means "no idle allowed — exit instantly." In hindsight ≥0.8.x, `0` means "never idle — run continuously." The system-level daemon (port 8888) uses `--idle-timeout 0` and has been running for weeks. If you need the daemon to persist, use `86400` (safe for both old and new); if you want it to stay up indefinitely, `0` may work on modern installations. Check the version with `curl <port>/version`.
- **`memory.db` at `<profile>/memory.db` is always 0 bytes when hindsight is active.** Hindsight uses its own embedded PG (`<profile>/home/.pg0/`), not this SQLite file. An empty memory.db is normal — don't mistake it for an uninitialized system.
- **Hindsight daemon restart takes 1-3+ minutes** due to embedded PostgreSQL initialization. The API is unreachable during this window (`curl health` returns connection refused). If a cron job needs the daemon and it's down, proxy through a sibling daemon (see `references/memory-maintenance.md`) instead of waiting for restart.
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
# Delete stale profiles (may prompt interactively; pipe 'y' if needed)
echo "y" | HERMES_HOME=~/.hermes hindsight-embed profile delete <name>

# Recreate with CORRECT port (must match the actual daemon port)
HERMES_HOME=~/.hermes hindsight-embed profile create <name> --port <actual_port>

# Move metadata to profile's own home (not shared under a sibling profile)
mkdir -p ~/.hermes/profiles/<name>/home/.hindsight/profiles/
# Copy .env file from wherever hindsight-embed wrote it to the profile's home
# Also create metadata.json with only this profile's entry
```

**After recreation, the .env file is a template — restore the real API key** into `HINDSIGHT_API_LLM_API_KEY` before the profile's Hermes session needs it.

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

**Tool limitation — memory is write-only.** The `memory` tool only supports `add`, `replace`, and `remove` actions — there is no `list` or `read` action. To inspect current memory content, read the flat files directly:

```bash
cat ~/.hermes/profiles/<profile>/memories/MEMORY.md
cat ~/.hermes/profiles/<profile>/memories/USER.md
```

Facts stored via hindsight in the bank are NOT visible through the `memory` tool either. Use hindsight's HTTP API (`/v1/default/banks/<bank_id>/memories/list`) or the `reflect` endpoint to query bank-stored memories.

For routine memory cleanup (archiving old memories, triggering consolidation+reflect optimization, recovering failed operations), see the detailed API workflow in:

→ `references/memory-maintenance.md` — Hindsight HTTP API endpoints for consolidation, reflect query, mental models, recovery, timeseries queries, bank stats, daemon-fallback (proxy through sibling daemon when target is down), HuggingFace model download timeout fix, cron-mode workarounds, and a step-by-step structured cron maintenance procedure.

## Reference
- `references/memory-maintenance.md` — Memory cleanup/optimization via Hindsight HTTP API.
- `references/multi-daemon-setup-recipe.md` — Full architecture, incident log, and health verification commands from multi-profile Hindsight setup.
- `references/multi-profile-daemon-verification.md` — Full command transcript from a real multi-profile diagnosis session.
