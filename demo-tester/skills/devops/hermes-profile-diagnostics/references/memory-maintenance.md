# Hindsight Memory Maintenance & Cleanup

How to query, archive, consolidate, and recover Hindsight memory via the HTTP API.  
Use when a cron job asks to "clean up old memories" or "optimize memory."

## System-Level vs Profile-Level Daemon

There are **two tiers** of Hindsight daemon on a multi-profile machine:

| Type | Port | Idle Timeout | Purpose |
|------|------|-------------|---------|
| System-level | 8888 | `--idle-timeout 0` | Always-on shared API, hosts all memory banks |
| Profile-level | 9177–9180 | `--idle-timeout 86400` | Per-profile daemon, shares PG with system daemon |

**The system-level daemon (port 8888) is the authoritative endpoint** for memory operations. It runs continuously (no idle timeout = always on). Profile-level daemons may restart due to idle timeout — when they're down, proxy through port 8888.

The system daemon may show `--idle-timeout 0` but stay running for days. In modern hindsight (≥0.8.x), `0` means **"never idle"** (continuous), not "immediate death." The earlier pitfall about `--idle-timeout 0` causing immediate death applies only to older versions.

## Bank Identification

The hindsight HTTP API uses **path-based routing**, not query parameters:

```bash
# Correct — path is /v1/default/banks (not /v1/banks)
curl -s http://127.0.0.1:8888/v1/default/banks
# Returns: {"banks":[{"bank_id":"hermes","name":"hermes",...}]}
```

`/v1/banks` (without `/default/`) returns 404. Always use the full path: `/v1/default/banks/<bank_id>/...`

## Quick Health Check

```bash
# Daemon health (port 8888 is the system-level daemon)
curl -s http://127.0.0.1:8888/health
# {"status":"healthy","database":"connected"}

# Bank list
curl -s http://127.0.0.1:8888/v1/default/banks
# Returns: {"banks":[{"bank_id":"hermes","name":"hermes",...}]}

# Version check (useful before using idempotent-timeout-specific features)
curl -s http://127.0.0.1:8888/version
```

## File-Based Memory Age Check (No Hindsight Bank)

**Many Hermes profiles store memories as flat files, NOT in a hindsight bank.** The demo-tester profile is an example — its memories live at `~/memories/MEMORY.md` and `~/memories/USER.md`. When the current profile uses file-based memory (check `config.yaml: memory.provider`), the hindsight bank is irrelevant for that profile.

To check memory ages for a file-based profile:

```bash
# Check file modification time — this is when the memory was last edited
ls -la ~/.hermes/profiles/<profile>/memories/MEMORY.md
ls -la ~/.hermes/profiles/<profile>/memories/USER.md

# Parse inline dates from memory content (entries are delimited by §)
grep "^## " ~/.hermes/profiles/<profile>/memories/MEMORY.md
# Shows section headers with embedded dates like "## 对话主模型（2026-06-14）"
```

If the files are <30 days old and content dates are <30 days, there's nothing to archive. Report explicitly rather than force an action.

## Check for Old Memories in a Hindsight Bank (30+ Days)

Use the timeseries endpoint to see memory distribution over time:

```bash
curl -s "http://127.0.0.1:8888/v1/default/banks/<bank_id>/stats/memories-timeseries?period=30d"
```

Returns per-day buckets with `world` / `experience` / `observation` counts.  
Days with all-zeros have no memories. If all days prior to the cutoff are zero, there's nothing to archive.

For deeper inspection, use the graph endpoint:

```bash
curl -s "http://127.0.0.1:8888/v1/default/banks/<bank_id>/graph?limit=200" -o /tmp/graph.json
# Then read_file /tmp/graph.json and grep for old dates manually
```

## Consolidation (Optimization)

Trigger memory consolidation to create/update observations from recent memories:

```bash
curl -s -X POST http://127.0.0.1:<port>/v1/default/banks/<bank_id>/consolidate \
  -H "Content-Type: application/json" -d '{}'
# Returns: {"operation_id":"...","deduplicated":true|false}
```

`deduplicated: true` means the bank was already up-to-date — no new work was needed.

## Recover Failed Consolidation

Check for failed consolidation items in bank stats:

```bash
curl -s "http://127.0.0.1:<port>/v1/default/banks/<bank_id>/stats"
# Look for: "failed_consolidation": N, "failed_operations": M
```

Recover failed consolidation items (resets them so next run picks them up):

```bash
curl -s -X POST http://127.0.0.1:<port>/v1/default/banks/<bank_id>/consolidation/recover \
  -H "Content-Type: application/json" -d '{}'
# Returns: {"retried_count": N}
```

Then re-trigger consolidation to process the recovered items.

## Monitor Operations

```bash
curl -s "http://127.0.0.1:<port>/v1/default/banks/<bank_id>/operations?limit=5"
```

Operations logged automatically include `consolidation`, `graph_maintenance`, etc. Each operation has `task_type`, `status` (`processing`/`completed`/`failed`), and timestamps. Consolidation runs are typically completed in <1 second on a 20-node graph.

## Reflect (Memory Summary / Query)

The `/reflect` endpoint is a conversational query interface that returns a structured memory summary based on an LLM query. It is DIFFERENT from `/consolidate` — reflect answers questions about what's in memory, consolidate deduplicates and create observations.

```bash
# Use reflect to get a summary of all memories
curl -s -X POST "http://127.0.0.1:<port>/v1/default/banks/hermes/reflect" \
  -H "Content-Type: application/json" \
  -d '{"query":"Summarize all available memories and their categories"}'

# Use reflect for optimization/maintenance review
curl -s -X POST "http://127.0.0.1:<port>/v1/default/banks/hermes/reflect" \
  -H "Content-Type: application/json" \
  -d '{"query":"Consolidate similar facts, identify stale/outdated observations, merge redundant entries"}'

# Response format:
# {"text":"...summary...", "based_on":null, "structured_output":null,
#  "usage":{"input_tokens":N, "output_tokens":N, ...}}
```

**Pitfall:** The `/reflect` endpoint requires a `query` field in the JSON body. Without it, returns `{"detail":[{"type":"missing","loc":["body","query"]}]}`.

## Mental Models (Higher-Level Insights)

Hindsight can generate mental models — abstract patterns derived from memory clusters:

```bash
# List existing mental models (empty until explicitly created)
curl -s "http://127.0.0.1:<port>/v1/default/banks/<bank_id>/mental-models"
# Response: {"items":[]}

# Create a mental model (requires name + source_query)
curl -s -X POST "http://127.0.0.1:<port>/v1/default/banks/<bank_id>/mental-models" \
  -H "Content-Type: application/json" \
  -d '{"name":"communication-patterns","source_query":"team communication and output standards"}'
# Response: {"detail":[{"loc":["body","name"],"msg":"Field required"}, ...]}
# Both 'name' and 'source_query' are required.
```

Mental models are not auto-generated — they must be explicitly created with a targeted query. Skip in automated cron maintenance unless the graph has 100+ facts with clear clusters.

## Full Bank Stats

```bash
curl -s "http://127.0.0.1:<port>/v1/default/banks/<bank_id>/stats"
```

Key fields:
- `total_nodes` — total memory facts
- `total_links` — graph edges
- `total_documents` — source documents
- `failed_consolidation` — items that failed all retries (recoverable)
- `failed_operations` — total failed operations (may include non-consolidation tasks)
- `pending_consolidation` — items waiting for next consolidation run
- `last_consolidated_at` — timestamp of last successful consolidation

## Built-in Memory (MEMORY.md)

Built-in memory lives at `<profile>/memories/MEMORY.md` and `<profile>/memories/USER.md`.  
Entries are delimited by `§`. Check entry dates before archiving — if all entries are recent, skip.

```bash
cat /Users/oneplusn/.hermes/profiles/<profile>/memories/MEMORY.md
```

## Daemon Not Running — Use Sibling Daemon

When the target profile's Hindsight daemon is down but another profile shares the same
`bank_id` + PostgreSQL instance (common with pg0 shared PostgreSQL), proxy through the
working daemon:

```bash
# 1. Check which daemons are actually running
ps aux | grep hindsight-api | grep -v grep

# 2. Check which bank each running daemon serves
curl -s http://127.0.0.1:<running_port>/v1/default/banks

# 3. If bank_id matches, use the running daemon for all operations
#    All daemons sharing the same pg0 instance see the same memory data.
```

**Pitfall:** `hindsight-embed profile list` may show a port mapping that doesn't match
reality. Always cross-check with `ps aux | grep hindsight-api` — the profile list is
static config, the process list is ground truth.

## Consolidation Pitfalls

**Stuck at 0/N progress.** If consolidation shows `processed:0, total:N` for 60+ seconds,
the LLM provider is likely unreachable (timeout, API key invalid, rate limited). Check
the daemon's LLM connectivity:

```bash
# Check which operations are stuck
curl -s "http://127.0.0.1:<port>/v1/default/banks/<bank_id>/operations?limit=5"
# Look for status: "processing" with 0 progress

# The consolidation will eventually time out and enter failed_consolidation.
# Recover and retry after fixing LLM connectivity:
curl -s -X POST http://127.0.0.1:<port>/v1/default/banks/<bank_id>/consolidation/recover \
  -H "Content-Type: application/json" -d '{}'
```

**failed_operations vs failed_consolidation.** `failed_operations` counts ALL failed
tasks (including batch_retain failures from past sessions). `failed_consolidation`
counts only consolidation-specific failures. The `failed_consolidation` count is what
you recover; `failed_operations` is historical and not directly actionable.

## HuggingFace Model Download Timeout (Daemon Startup Failure)

If the daemon fails to start with `RuntimeError: Model/connection initialization did
not complete within 300s` and the log shows HuggingFace SSL handshake timeouts, the
models are likely already cached but the daemon still tries to verify them against
huggingface.co at startup:

```bash
# Fix: use HF mirror
export HF_ENDPOINT=https://hf-mirror.com
# Then restart the daemon with this env var set
```

Models live at `~/.cache/huggingface/hub/`. If the directory exists with model
subdirectories, the cache is populated — the daemon just can't verify freshness.

## Importing Flat-File Memories Into Hindsight

When the `memory` tool returns `"Memory is not available"` (common when hindsight is configured as provider but the tool dispatch fails), the fallback is to use `hindsight_client` directly against the running daemon:

```python
from hindsight_client import Hindsight

client = Hindsight(base_url='http://localhost:<port>')
```

### Read flat files and import

```python
import asyncio

async def import_flat_memories():
    client = Hindsight(base_url='http://localhost:<port>')

    # Read the flat-file memories
    with open('/path/to/profile/memories/MEMORY.md') as f:
        memory_content = f.read()
    with open('/path/to/profile/memories/USER.md') as f:
        user_content = f.read()

    # Import into hindsight's DB
    r1 = await client.aretain(
        bank_id='hermes',
        content=f'=== MEMORY.md ===\n\n{memory_content}',
        tags=['memory-md', 'imported'],
        metadata={'source': 'flat-file-memory', 'import_date': 'YYYY-MM-DD'}
    )

    r2 = await client.aretain(
        bank_id='hermes',
        content=f'=== USER.md ===\n\n{user_content}',
        tags=['user-md', 'imported'],
        metadata={'source': 'flat-file-user', 'import_date': 'YYYY-MM-DD'}
    )

    # Verify — hindsight auto-chunks into facts
    mems = await client.memory.list_memories(bank_id='hermes')
    print(f'Total hindsight memories: {mems.total}')

asyncio.run(import_flat_memories())
```

Hindsight auto-chunks the content: the flat files (~3KB + ~1.5KB) typically produce **15–25 individual facts** with extracted entities, categorized by `fact_type` (experience, observation, etc.) and dated with timestamps.

### Verify imported content

```python
mems = await client.memory.list_memories(bank_id='hermes', limit=100)
for m in mems.items:
    print(f'Fact: {m.get(\"text\", \"\")[:80]}')
    print(f'  Type: {m.get(\"fact_type\")}  Entities: {m.get(\"entities\")}')
```

Memory items are `dict` objects (not pydantic models) with keys: `id`, `text`, `context`, `date`, `fact_type`, `document_id`, `entities`, `occurred_start`, `occurred_end`.

### Trigger consolidation after import

```python
op = await client.banks.trigger_consolidation(bank_id='hermes')
print(f'Consolidation triggered: operation_id={op.operation_id}')
```

The consolidation deduplicates and creates cross-fact observations. It runs asynchronously in the background — the operation_id can be used to track progress.

### API method naming quirks

The hindsight_client SDK uses OpenAPI-generated classes where method names differ from the `Hindsight` class aliases:

| Want | Method on `client` | Method on namespace |
|------|-------------------|-------------------|
| List banks | `client.banks.list_banks()` | — |
| Bank config | `client.banks.get_bank_config(bank_id=...)` | — |
| List memories | `client.memory.list_memories(bank_id=...)` | — |
| List mental models | `client.mental_models.list_mental_models(bank_id=...)` | NOT `list()` |
| List directives | `client.directives.list_directives(bank_id=...)` | NOT `list()` |
| Trigger consolidation | `client.banks.trigger_consolidation(bank_id=...)` | — |
| Bank profile | `client.banks.get_bank_profile(bank_id=...)` | — |

All methods are **async** — must be called with `await`.

### Bash-only fallback (cron mode)

When `execute_code` is blocked in cron jobs, use curl to save results to a temp file, then analyze with `read_file`:

```bash
curl -s "http://localhost:<port>/v1/default/banks/hermes/stats" -o /tmp/hindsight_stats.json
curl -s "http://localhost:<port>/v1/default/banks/hermes/graph?limit=200" -o /tmp/graph.json
```

Then call `read_file(path='/tmp/graph.json')` for inspection. Avoid piping to `python3 -c` — the security scanner blocks it.

## No Dedicated "Optimize" or "Vacuum" Command

Hindsight has **no standalone optimize/vacuum/maintenance CLI command**. The consolidation endpoint IS the optimization mechanism:

- `hindsight-embed`: `retain`, `recall`, `reflect`, `bank list` — no optimize.
- `hindsight-admin`: `backup`, `restore`, `run-db-migration`, `export-bank`, `import-bank` — no optimize.
- The HTTP API: `POST /v1/default/banks/<id>/consolidate` triggers memory consolidation (dedup, observation creation).

If a cron job asks to "optimize memory with hindsight," the answer is: trigger consolidation via the HTTP API, then verify with bank stats. There is no SQL-level VACUUM or index rebuild command.

## `memory.db` Is Always 0 Bytes with Hindsight

When hindsight is the active memory provider, the file `<profile>/memory.db` exists but is **always 0 bytes**. Hindsight stores data in its own embedded PostgreSQL (`<profile>/home/.pg0/instances/hindsight-*/`), not in this SQLite file. If you `ls -la memory.db` and see 0 bytes, that's normal — don't mistake it for an uninitialized or failed memory system.

## Daemon Restart Latency (1-3+ Minutes)

After an idle-timeout shutdown, restarting the daemon via `hindsight-embed -p <name> daemon start` takes **1-3+ minutes** because the embedded PostgreSQL must reinitialize. During this window:
- `hindsight-embed daemon status` reports \"Daemon is not running\"
- `curl http://127.0.0.1:<port>/api/health` returns connection refused
- `hindsight-embed bank list` times out

The process exits cleanly (`exit_code: 0`) but the API isn't reachable until PG is fully up. Use `--idle-timeout 86400` to avoid frequent restarts. If a cron job needs the daemon and it's down, proxy through a sibling daemon (see \"Daemon Not Running\" above) rather than waiting for restart.

## Cron Mode Pitfalls

When running as a cron job:

1. **`execute_code` is blocked.** Use `terminal()` with curl to file, then `read_file()` or `search_files()` for analysis.
2. **Pipes to python3 are blocked by security scanner.** Don't do `curl ... | python3 -c ...`. Instead: `curl ... -o /tmp/file.json` → `read_file /tmp/file.json`.
3. **`~` expansion may resolve to profile HOME, not user HOME.** Use absolute paths (`/Users/oneplusn/...`) when the profile has a redirected `HOME`.
4. **No memories >30 days old is a valid outcome.** If MEMORY.md timestamps are all recent and the timeseries endpoint shows no old buckets, respond with `[SILENT]` — there's genuinely nothing to clean. Don't force an action just because the cron job fired.

## CLI Command Hang Pitfall

**`hindsight-embed -p <profile> memory recall/reflect/retain` commands hang indefinitely** with no output in some environments (both interactive and cron). The process never produces stdout/stderr and must be killed after 30+ seconds. This is NOT a daemon health issue — the same daemon responds fine to HTTP requests.

Root cause unknown (possibly a stdin/stdout interaction between the embed CLI and the daemon's API client). Workaround:

**When `hindsight-embed memory <command>` hangs → fall back to curl against the REST API directly:**

| CLI command that hangs | Equivalent curl |
|---|---|
| `hindsight-embed -p hermes memory recall hermes "query"` | `curl -s -X POST /v1/default/banks/hermes/memories/recall -d '{"query":"...","budget":"low"}'` |
| `hindsight-embed -p hermes memory reflect hermes "query"` | `curl -s -X POST /v1/default/banks/hermes/reflect -d '{"query":"...","budget":"mid"}'` |
| `hindsight-embed -p hermes memory retain hermes "text"` | `curl -s -X POST /v1/default/banks/hermes/memories/retain -d '{"items":[{"content":"..."}]}'` |
| `hindsight-embed -p hermes bank list` | `curl -s /v1/default/banks` |

**Discovery path for REST endpoints:** The OpenAPI spec is always available at `curl -s http://<host>:<port>/openapi.json`. This is a complete spec — use it to discover new endpoints instead of guessing URL paths. The spec lists every endpoint with its exact path, parameters, and request/response schemas.

**Cron safety:** In cron mode, curl-to-API calls do NOT trigger the security scanner (no pipes, no execution of downloaded content). Always save output to a temp file with `-o /tmp/...` and read with `read_file()`.

## Daemon Down: Start vs Proxy

When a profile's hindsight daemon is not running, two options exist:

| Option | When to use | How |
|--------|------------|-----|
| **Start the daemon** | You need this specific bank and there's time (1-3 min startup) | `source ~/.hermes/.env && export HINDSIGHT_API_LLM_API_KEY="$HIN...EY" && hindsight-embed -p <profile> daemon start` |
| **Proxy through sibling** | You need to check memory ASAP, or startup would block the session | Use port 8888 (system daemon) — all daemons sharing the same pg0 instance see the same data |

**Key insight:** Starting the daemon with `hindsight-embed -p hermes daemon start` reconnects to the SAME shared PostgreSQL instance that other daemons use. The daemon sees all memories that were written by any profile sharing the same `bank_id`.

**Risks of starting:**
- Takes 1-3 minutes (embedded PostgreSQL init)
- May trigger `RuntimeError: Model/connection initialization did not complete within 300s` if HuggingFace is unreachable (mitigate with `export HF_ENDPOINT=https://hf-mirror.com`)
- The daemon may not be expected by other profiles sharing the same machine

**Risks of proxying:**
- Port 8888 may have `--idle-timeout 0` (never idle) or may be the system daemon with a different profile name
- Cross-check with `curl -s http://127.0.0.1:8888/v1/default/banks` to confirm the bank exists
- If 8888 is down too, you MUST start a daemon

## Reflect Token Consumption

The `/reflect` endpoint's input token consumption scales with bank size:

| Bank size (total_nodes) | Approximate input_tokens | Budget level |
|---|---|---|
| ~20 | 5,000–6,000 | low |
| ~200 | 15,000–18,000 | mid |
| ~439 | 28,000 | mid |
| ~1000 | 55,000–70,000 | mid |

Use `budget: "low"` for quick health checks (fewer tokens, less thorough recall). Use `budget: "mid"` for maintenance/cron reflect operations. `budget: "high"` is rarely needed unless doing deep knowledge auditing.

The `usage` field in the reflect response tells you exact token consumption — log this for trend tracking.

## Structured Memory Maintenance Cron Procedure

A self-contained procedure for cron jobs that need to "clean up old memories and optimize with hindsight":

### Step 1 — Determine 30-Day Cutoff

```bash
# On macOS (BSD date)
date -u -v-30d +%Y-%m-%d
# Returns: 2026-06-06 (example)

# On Linux (GNU date)
date -u -d '30 days ago' +%Y-%m-%d
```

### Step 2 — Check File-Based Memory Age

```bash
ls -la ~/.hermes/profiles/<profile>/memories/MEMORY.md
ls -la ~/.hermes/profiles/<profile>/memories/USER.md
# Compare mtime against cutoff. If mtime > 30d, check inline dates.
```

Parse inline dates from MEMORY.md content (entries use `§` as delimiter, dates in section headers like `## Topic (2026-06-14)`). If no entries are older than the cutoff, file-based archiving is a no-op.

### Step 3 — Check Hindsight Bank Health

```bash
# Daemon health
curl -s http://127.0.0.1:8888/health > /tmp/hindsight_health.json
read_file /tmp/hindsight_health.json
# Expected: {"status":"healthy","database":"connected"}

# Bank stats
curl -s "http://127.0.0.1:8888/v1/default/banks/hermes/stats" -o /tmp/hindsight_stats.json
read_file /tmp/hindsight_stats.json
# Check: pending_operations, failed_operations, pending_consolidation, failed_consolidation
```

**Key thresholds for a healthy bank (20-node graph):**
- `pending_operations`: 0 (any >0 means something is stuck)
- `failed_operations`: 0 (historical — non-zero is OK if old)
- `pending_consolidation`: 0 (items waiting to be processed)
- `failed_consolidation`: 0 (actionable — recover if >0)

### Step 4 — List and Age-Check All Memories

```bash
curl -s "http://127.0.0.1:8888/v1/default/banks/hermes/memories/list?limit=100" -o /tmp/all_memories.json
read_file /tmp/all_memories.json
```

Each memory has a `date` field (ISO 8601 timestamp). Compare against cutoff. Also check `state` — should be `valid` for all. `invalid` state means the memory was invalidated and could be purged.

### Step 5 — Trigger Reflect (Optimization)

Only worthwhile if Step 3+4 show at least some memories exist:

```bash
curl -s -X POST "http://127.0.0.1:8888/v1/default/banks/hermes/reflect" \
  -H "Content-Type: application/json" \
  -d '{"query":"Perform memory maintenance: consolidate similar facts, merge redundant entries, identify stale content"}'
```

The reflect endpoint costs ~5000-6000 input tokens on a 20-node bank. Skip if the bank is empty (`total_nodes: 0`) or the cron budget is tight (e.g. user's daily token cap is low).

### Step 6 — Verify Operations Completed

```bash
curl -s "http://127.0.0.1:8888/v1/default/banks/hermes/operations?limit=3" -o /tmp/last_ops.json
read_file /tmp/last_ops.json
# All recent operations should show status: "completed"
```

### Step 7 — Report

If everything is clear (no old memories, bank healthy, optimization done):
- Report a concise summary: list mtime dates, hindsight stats, what was done
- If genuinely nothing to do (no 30+ day memories, bank already optimal): `[SILENT]`

If issues found:
- Stuck operations → advise recovery with `/consolidation/recover`
- Failed consolidation → trigger recovery then re-consolidate
- Daemon down → proxy through sibling daemon (see "Daemon Not Running")

### Pitfalls for This Flow

- **`curl | python3 -c` is blocked in cron mode.** Always curl to file, then read_file.
- **Two-tier daemon check:** Profile-level daemon (9177-9180) may be idle. System daemon (8888) is always on. Always prefer port 8888 for cron work.
- **all-20-memories same date.** Hindsight may show all memories with `date: 2026-06-30` (the consolidation timestamp, not source date). Always cross-reference with the flat file modification times and content inline dates when assessing age.
- **No mental models = not a problem.** Mental models are not auto-created. The graph needs 100+ facts before they become useful; generating them prematurely wastes tokens.
