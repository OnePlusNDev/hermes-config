# Hindsight Memory Maintenance & Cleanup

How to query, archive, consolidate, and recover Hindsight memory via the HTTP API.  
Use when a cron job asks to "clean up old memories" or "optimize memory."

## Quick Health Check

```bash
# Daemon health
curl -s http://127.0.0.1:<port>/health
# {"status":"healthy","database":"connected"}

# Version + feature flags
curl -s http://127.0.0.1:<port>/version

# Bank list
curl -s http://127.0.0.1:<port>/v1/default/banks
```

## Check for Old Memories (30+ Days)

Use the timeseries endpoint to see memory distribution over time:

```bash
curl -s "http://127.0.0.1:<port>/v1/default/banks/<bank_id>/stats/memories-timeseries?period=30d"
```

Returns per-day buckets with `world` / `experience` / `observation` counts.  
Days with all-zeros have no memories. If all days prior to the cutoff are zero, there's nothing to archive.

For deeper inspection, use the graph endpoint with date filtering:

```bash
curl -s "http://127.0.0.1:<port>/v1/default/banks/<bank_id>/graph?limit=200" -o /tmp/graph.json
# Then grep for old dates: grep "2026-04\|2026-05" /tmp/graph.json
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

## No Dedicated \"Optimize\" or \"Vacuum\" Command

Hindsight has **no standalone optimize/vacuum/maintenance CLI command**. The consolidation endpoint IS the optimization mechanism:

- `hindsight-embed`: `retain`, `recall`, `reflect`, `bank list` — no optimize.
- `hindsight-admin`: `backup`, `restore`, `run-db-migration`, `export-bank`, `import-bank` — no optimize.
- The HTTP API: `POST /v1/default/banks/<id>/consolidate` triggers memory consolidation (dedup, observation creation).

If a cron job asks to \"optimize memory with hindsight,\" the answer is: trigger consolidation via the HTTP API, then verify with bank stats. There is no SQL-level VACUUM or index rebuild command.

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
