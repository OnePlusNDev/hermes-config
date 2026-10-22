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

### Counting without execute_code

In cron mode `execute_code` is refused unless the profile has `approvals.cron_mode: approve`
(2026-10-19: "BLOCKED: execute_code runs arbitrary local Python … Cron jobs run without a user
present to approve it"). Don't route around it with `python3 -c` heredocs either — one `sqlite3`
call does the whole job:

```bash
sqlite3 <profile>/state.db "select count(*) as total,
  sum(started_at < strftime('%s','now') - 90*86400) as old90,
  sum(started_at < strftime('%s','now') - 30*86400) as old30 from sessions;"
```

2026-10-19: `5928|1482|4482` (total / >90 d / >30 d).

### Appending the ARCHIVE.md row

The row is a single very long Chinese line with backticks, quotes and slashes, so a shell
`echo "…" >>` invite quoting bugs. Reliable pattern: `write_file` the finished row to
`/tmp/archive_row_<MMDD>.md` (trailing newline included), then
`cd <profile>/memories/archive && cat /tmp/archive_row_<MMDD>.md >> ARCHIVE.md`.
ARCHIVE.md ends with a newline, so no blank line is needed before the row.

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
| 2026-10-19 | **402,985 / 9,297** |
| 2026-10-20 | **95,622 / 6,495** (disambig 407,383 / 5,803 — new input high) |
| 2026-10-21 | **108,978 / 7,133** (disambig 396,679 / **9,900** — highest output yet) |

Observed band is now **~96 K–407 K input** across both passes. The primary can dip to ~96 K
(2026-10-20) even with a full 48-fact bank — do NOT treat a sub-112 K primary as "facts were
never fed" as long as it clears the 50 K baseline; judge it on the wording gate. The gate is
"far above the ~2–7 K question-echo band", never a fixed threshold. A high token count never
clears the wording gate on its own.

2026-10-19 also re-confirmed the common header shape: the primary's table row
「超过 30 天的过期事实 | **无** | 0 条」 still trips the wording gate (no negation inside the
12-char window before 「过期事实」) even when the same answer additionally lists 「需立即归档/
标记的易腐状态型事实 4 条」. Disambiguation cost is low relative to primary (163,568 vs 402,985
input tokens), so always pay it rather than reasoning about the header wording.

2026-10-20 confirmed a second wording shape: the header 「## 1. 过期事实（30 天以上）」 followed by
「无法从库内数据判定绝对过期」 (an *inability* claim, not a count) also trips the wording gate,
because no negation sits inside the 12-char window before 「过期事实」. Verdict-bearing text lives in
in the heading, so the gate fires regardless of what the body says — pay the disambiguation pass
(407,383 input, new high) instead of hand-judging it.

2026-10-21 confirmed a third wording shape, this one combining both tells: heading
「一、过期事实（>30 天）：**无**」 plus a body sentence 「若当前日期已过 2026-07-17 则上述全部事实需
整体重验」 and an 「应优先归档」 recommendation. The primary's own token count (108,978) cleared the
50 K baseline comfortably while the wording was still affirmative — further proof that **the token
gate can never substitute for the wording gate**; a well-formed, fully-itemized analysis can still
carry a conditional/creation-age false positive.

## CLI quirks (verified 2026-10-21)

- The `hindsight` CLI reads its API URL from `~/.hindsight/…` config → defaults to **:8888**, not your
  profile daemon. Prefix every call: `HINDSIGHT_API_URL=http://127.0.0.1:9178 hindsight …`. Without it:
  `hindsight audit list … demo-pm-memory` → `✗ API endpoint not found (404)` (it hit :8888).
- `bank stats` / `audit list` take a **positional** BANK_ID — `hindsight bank stats demo-pm-memory`,
  `hindsight audit list --limit 6 demo-pm-memory`. `--bank-id` fails with `unexpected argument`.
- `audit list` returned `{"items": [], "total": 0}` on a healthy bank with 80→81 completed operations,
  so **it is not a source of reflect token counts**. The only cheap source is
  `process(action='log', limit=<total_lines>)` on the probe's background session — the
  `[primary] input_tokens=…` / `[disambig] input_tokens=…` lines sit at the TOP and vanish under a
  small `limit`, so pass a limit ≥ the reported `total_lines` (~140 for a two-pass run, ~12 KB).
- `hindsight-embed -p <profile> daemon status` correctly reports the profile daemon; use it before
  touching ports, and cross-check with `lsof` (see SKILL.md pitfalls).

## Appending the row — never chain `rm`

`cat /tmp/archive_row_<MMDD>.md >> ARCHIVE.md` works. Adding `&& rm -f /tmp/archive_row_<MMDD>.md`
makes tirith return `pending_approval` ("delete in root path") and the cron run **stalls with no
approver** — the append never happens. Do the append alone, verify with a second call
(`python3 -c` line count on `ARCHIVE.md`, confirming no blank lines at the tail), and leave the temp
file in `/tmp`.

## The `secret 10014 invalid` item cannot be closed from demo-pm

Twenty-plus cleanup runs have logged it as 「未闭环」. The loop's root cause: `demo-pm/.env` holds only
`GITHUB_USERNAME/EMAIL/TOKEN`, `GATEWAY_PORT`, `AGENT_NAME/ROLE`, `DEEPSEEK_API_KEY`, `TERMINAL_ENV` —
**no Feishu app id/secret** — so the `tenant_access_token/internal` probe cannot run from this profile
(and `config.yaml` only carries `platforms.feishu.allow_bots`, no creds). Grepping
`logs/gateway.error.log` for `10014` is also a false-positive trap: it matches tool-call ids, not Feishu
errors. Resolution needs the Feishu console or the profile that owns the credential. Record it in the
ARCHIVE row and do not re-attempt from here.

## Launcher idle timeout is 300 s, not 86400

`scripts/start_hindsight_daemon.sh` exports `HINDSIGHT_EMBED_DAEMON_IDLE_TIMEOUT=86400`, but the spawned
process actually carries `--idle-timeout 300` (from the profile env file):
`ps -Ao pid,etime,command | grep 'port 9178'` → `hindsight-api --daemon --idle-timeout 300 --port 9178`.
So :9178 can exit after ~5 min idle — expect every daily run to start from "offline". Do reflect +
consolidation in one session instead of assuming the daemon will still be up on a later call.
