# Memory-cleanup run — exact endpoints, counts, and probe-log quirks

Companion to `references/memory-maintenance.md` (which is at the 100 K char cap — add new
findings here instead). Verified on demo-pm, 2026-10-18.

## HTTP endpoints (profile daemon, e.g. `http://127.0.0.1:9178`)

| Purpose | Call |
|---|---|
| Bank list + fact counts | `GET /v1/default/banks` → per bank `fact_count`, `last_document_at` |
| Bank stats | `GET /v1/default/banks/<bank>/stats` → `total_nodes`, `total_links`, `pending_operations`, `failed_operations`, `operations_by_status` |
| Consolidate | `POST /v1/default/banks/<bank>/consolidate`, body `{}` → `{"operation_id": "...", "deduplicated": false}` |
| Operation status | `GET /v1/default/banks/<bank>/operations/<op_id>` → `status`, `operation_type`, `completed_at`, `error_message`, `retry_count` |

- Consolidation can be `completed` at submit time (2026-10-18: `completed_at` = `created_at` + 56 ms). Still read the op status before writing the ARCHIVE.md row — don't infer success from the POST alone.
- Use the bank list as a **pre-flight** check: one call tells you whether `demo-pm-memory` (48 facts) is served by this daemon. If :9178 is down and the siblings show only `demo-dev/active/hermes`, there is no fallback — start the profile daemon via its launcher.
- Never `curl … | python3` in cron (tirith HIGH `curl_pipe_shell`, stalls with no approver). Fetch with `urllib` inside a heredoc, or `curl -o /tmp/x.json` then parse the file.

## Session retention — `started_at` is an epoch FLOAT

`<profile>/state.db`, table `sessions`. `started_at` is a Unix epoch float (e.g. `1792328402.37`), so
`julianday(started_at)` matches **0 rows** and reads as "no sessions older than 90 days".

```python
old = cur.execute("select count(*) from sessions where started_at < ?",
                  (time.time() - 90*86400,)).fetchone()[0]
```

2026-10-18: 5,878 total / 1,432 > 90 d. Retention config is in `<profile>/config.yaml`
(`auto_prune: false`, `retention_days: 90`) — **not** `config.json` (that file is the Hindsight config).
With `auto_prune: false`, record the counts in ARCHIVE.md and do not prune.

## Probe-log quirks

- `process(action='log')` **ignores `offset`**: `offset=0, limit=40` still returns the LAST 40 lines. Only `limit` works — pass `limit=200` to recover the full transcript including the `[primary]` / `[gate] token` / `[verdict]` header lines. Don't re-run the reflect just to recover token numbers.
- `process(action='wait', timeout=240)` is clamped to **180 s**. A two-pass reflect (primary + auto-disambiguation) can exceed that, so follow with a `poll`/`log` rather than assuming failure.

## Deepseek reflect token band (keep widening)

| Date | Primary (in/out) |
|---|---|
| 2026-09-29 | 148,986 / 5,252 |
| 2026-10-01 | 203,785 / 7,923 |
| 2026-10-04 | 313,104 / 13,311 |
| 2026-10-11 | 284,123 / 7,265 |
| 2026-10-18 | **308,068 / 8,712** |

Observed band is now **~112 K–313 K input**. The gate is "far above the ~2–7 K question-echo band",
never a fixed threshold. A high token count never clears the wording gate on its own.
