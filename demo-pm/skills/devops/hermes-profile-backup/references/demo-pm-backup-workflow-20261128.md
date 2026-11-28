# demo-pm backup run — 2026-11-28

## Result
**Method B (standalone subtree, no clone)** — main commit FIRST-TRY, 0 aborts (no 422 race).
Main commit: `c24d6fc032b3a4db6d1ebf508ddaf47bf33c94da`
URL: https://github.com/OnePlusNDev/hermes-config/commit/c24d6fc032b3a4db6d1ebf508ddaf47bf33c94da
Diff: **8 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`JungleAssistant`** (`push=false`) — a keyring account **never seen before**
  in this record → `unset GITHUB_TOKEN` + `gh auth switch --user OnePlusNDev` → re-probe
  **`OnePlusNDev` / `push=true`**. **20th keyring flip in the record** (11-27 logged the 19th);
  no blob 404.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`.
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9_-]{20,}` → **0** matches;
  non-empty `api_key:` → **0** matches; all **15** `api_key:` lines are `''`; the only `key_env`
  occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed** (config.yaml unchanged: blob
  17,021 bytes / 16,835 chars, the usual CJK-comment discrepancy).
- `.env` (296 B; var **names only**: `GITHUB_USERNAME`, `GITHUB_EMAIL`, `GITHUB_TOKEN`,
  `GATEWAY_PORT`, `AGENT_NAME`, `AGENT_ROLE`, `DEEPSEEK_API_KEY`, `TERMINAL_ENV`) excluded,
  never uploaded; no `auth.json` / `auth.lock` / `state.db*` in tree.

## Diff (8 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/MEMORY.md
M  demo-pm/memories/USER.md
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/demo-pm-github-api/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/references/skill-md-at-cap.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
```
Characterized with `scripts/characterize-diff-post-push.py 32aed3f76328` (read-only; the push had
already landed). Per-file: `jobs.json` +10/-10, `MEMORY.md` +1/-1, `USER.md` +1/-1, `ARCHIVE.md`
+10/-0, `demo-pm-github-api/SKILL.md` +2/-0, backup `SKILL.md` +2/-2, `skill-md-at-cap.md` +23/-0,
`cleanup-run-endpoints-and-counts.md` +7/-0. Summary `MODIFIED 8 / ADDED 0 / DELETED 0`, matching
the preflight exactly.

- **4 routine runtime churn** (numbers re-read from the uploaded remote blob) — task-polling
  completed 7539→**7587** (+48), config-backup 158→**159** (`last_run_at` 2026-11-27T20:05:27.116161,
  `last_status: ok`), memory-cleanup 158→**159** (`last_run_at` 2026-11-27T21:03:15.307595,
  `last_status: ok`), `updated_at` 2026-11-28T20:01:05.824435; `MEMORY.md` / `USER.md` header
  2026-11-26 → **2026-11-27**; `ARCHIVE.md` = the 11-27 21:0x cleanup (+10 lines) — op
  `5c091ce6-6604-4f60-acd2-fa3798c301e2` **+265 ms**, `operations_by_status.completed` 116→**117**,
  `total_nodes 48 / total_links 1228` unchanged (no-op dedupe), primary **290,837 / 8,790** with the
  wording gate **36th consecutive** (new shape: 「## 结论（先说结论）」 table row
  「30 天以上过期事实 | **没有**」 + 「但存在 6 类"易腐配置快照"」), disambig **210,480 / 6,568**,
  **no stale-body trap this round** (poll 1 `000` with an EMPTY `/tmp/h9178_p1_1127.json`, healthy
  poll 2 ~20 s), sessions **7,878 / 3,432 / 6,378** vs 7,828 / 3,382 / 6,328 (all three +50 again —
  seven consecutive runs at exactly +50; recorded, not to be read as monotone).
- **4 carry-over doc edits** made since the 11-27 push: `demo-pm-github-api/SKILL.md` +2 (11-28
  triage rounds, `[SILENT]`, plus the note that the full-scan byte count drifts with issue bodies —
  same-day 33,176 → 31,867); backup `SKILL.md` +2/-2 (the line-41 at-cap banner tightened to
  "Over the 100 K cap" and the daily-run pointer now also bans `execute_code`); `skill-md-at-cap.md`
  +23 (8th occurrence — BOTH start-of-session reflexes fail: `skill_view` dump is one JSON line so
  `read_file` reports `total_lines: 0`, and `execute_code` is refused in cron mode; go straight to
  the on-disk path + `read_file`); `cleanup-run-endpoints-and-counts.md` +7 (the six-run `+50`
  streak note and the 11-27 reflect row).

## Preflight
- Local files (after excludes): **308**; preflight remote HEAD `32aed3f76328`, 327 blobs
- Preflight diff: `Modified: 8, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `32aed3f76328` at preflight AND at Step 2, and it is the **parent of the backup
  commit** → nothing landed in between, **no ref-PATCH 422 race**; ref PATCH succeeded first try.
- 8 blobs uploaded, subtree `b756e0b0e1032bc802c2c947b05e0cdd2424c3e5`, top tree
  `b489621a29b20afd1ecb863f6317b289cd30d98c`, commit + ref in one clean pass.
  The `mkdtemp` payload fix held; no network flakiness through the main commit (the follow-up is a
  second full push — see the closing assertion below).
- Closing assertion: after this follow-up lands, the preflight must read
  `Modified: 0, New: 0, Deleted: 0` (the only proof the follow-up's ref PATCH landed).

## Post-push remote verification
- Remote HEAD `c24d6fc032b3`; total blobs **327**, `demo-pm` blobs = **308** (== local file count
  308); by top dir: demo-pm 308, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = **15**, non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + practice-notes table row + SKILL.md `latest:` pointer
`2026-11-27` → `2026-11-28` (same-length swap; SKILL.md measured 100,877 B, at cap),
pushed with the same standalone-subtree script. Bullet and row written by
`scripts/append-run-note-docs.py` (expect `INDEX count=1` / `ROW count=1`).
Pre-follow-up preflight expected `Modified: 3, New: 1, Deleted: 0` (+ `jobs.json` if a cron tick
dirtied it again); the closing preflight must read `0/0/0`.
