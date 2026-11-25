# demo-pm backup run — 2026-11-25

## Result
**Method B (standalone subtree, no clone)** — main commit FIRST-TRY, 0 aborts (no 422 race).
Main commit: `1d03e1fb96ad2dd0eb86d9e84abb113d511561b2`
URL: https://github.com/OnePlusNDev/hermes-config/commit/1d03e1fb96ad2dd0eb86d9e84abb113d511561b2
Diff: **10 M, 2 A, 0 D**.

The 11-24 follow-up landed as `ae5e3e4b8dad` (2026-11-24T12:05:32Z) — that run's closing
`0/0/0` assertion held, and today's pre-push HEAD was that follow-up, not the 11-24 main commit.

## Pre-flight
- `gh api user` → **`OnePlusNTester`** (`push=false`) → `gh auth switch --user OnePlusNDev`,
  re-read `permissions.push=true` — **18th observed keyring flip** (11-24 logged the 17th).
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`.
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9_-]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the only
  `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**.
- `.env` (296 B; names only: `GITHUB_USERNAME`, `GITHUB_EMAIL`, `GITHUB_TOKEN`, `GATEWAY_PORT`,
  `AGENT_NAME`, `AGENT_ROLE`, `DEEPSEEK_API_KEY`, `TERMINAL_ENV`) excluded, never uploaded;
  no `auth.json` / `auth.lock` / `state.db*` in tree.

## Diff (10 M, 2 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/MEMORY.md
M  demo-pm/memories/USER.md
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/demo-pm-github-api/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/references/skill-md-at-cap.md
M  demo-pm/skills/devops/hermes-profile-backup/references/tooling-gotchas-and-patch-anchoring.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
M  demo-pm/skills/devops/pm-triage-cron/SKILL.md
M  demo-pm/skills/devops/pm-triage-cron/scripts/pm_parse.py
A  demo-pm/skills/devops/pm-triage-cron/references/core-rate-limit-403-and-graphql-fallback.md
A  demo-pm/skills/devops/pm-triage-cron/scripts/pm_gql_fallback.py
```
Characterized with `scripts/characterize-diff-post-push.py ae5e3e4b8dad` (read-only; the push had
already landed). Per-file: `jobs.json` +10/-10, `MEMORY.md` +1/-1, `USER.md` +1/-1,
`ARCHIVE.md` +10/-0, `demo-pm-github-api/SKILL.md` +3/-0, `skill-md-at-cap.md` +13/-1,
`tooling-gotchas-and-patch-anchoring.md` +91/-2, `cleanup-run-endpoints-and-counts.md` +2/-0,
`pm-triage-cron/SKILL.md` +3/-2, `pm_parse.py` +7/-0. Summary `MODIFIED 10 / ADDED 2 /
DELETED 0`, matching the preflight exactly.

- **4 routine runtime churn** (numbers re-read from the uploaded remote blobs) — task-polling
  `completed` 7395→**7443**, config-backup 155→**156** (`last_run_at` 2026-11-24T20:05:56.806308,
  `last_status: ok`), memory-cleanup 155→**156** (`last_run_at` 2026-11-24T21:03:44.581279,
  `last_status: ok`), `updated_at` 2026-11-25T20:01:15.907503; `MEMORY.md` / `USER.md` header
  2026-11-23 → **2026-11-24**; `ARCHIVE.md` = the 11-24 21:0x cleanup (+10 lines) — op
  `ca2f932a-b06f-4a3e-81ed-99174980cb82` +351 ms, `operations_by_status.completed` 113→**114**,
  `total_nodes 48 / total_links 1228` unchanged (no-op dedupe), primary **158,702 / 6,483** with
  the wording gate 33rd consecutive, disambig **167,942 / 6,379** → 「无内容性过期事实」; the blob
  records `stale-body 陷阱第 12 次` (poll 1 `000` with the previous healthy body still in
  `/tmp/h9178_p1.json`, healthy poll 2); sessions **7,728 / 3,282 / 6,228** vs 7,678 / 3,232 /
  6,178 last round (all three +50 — record, do not read as monotone).
- **6 carry-over doc edits, 4 new files' worth of triage work** made since the 11-24 push:
  `skill-md-at-cap.md` (+13/-1: 6th occurrence of the skill-read reflex — and the persisted dump IS
  `grep`-able, so recovery is slow-expensive, not a dead end), `tooling-gotchas-and-patch-anchoring.md`
  (+91/-2: traps 10–11 — no `timeout` binary on this host, a `timeout`-wrapped command exits 0
  without running; the secret scanner rewrites `grep`/`echo` prose around key-shaped words → count
  in Python), `demo-pm-github-api/SKILL.md` (+3: `write_file` does not expand `$$` in a path;
  `$RANDOM`/`$$` expand per reference so they cannot name one file twice; 11-25 take), 
  `cleanup-run-endpoints-and-counts.md` (+2: the 11-24 reflect row), `pm-triage-cron/SKILL.md`
  (+3/-2) and `pm_parse.py` (+7: core-quota exhaustion → all REST 403 surfaces as a non-array
  response, `len()` is dict keys not issue count), plus the new
  `references/core-rate-limit-403-and-graphql-fallback.md` and `scripts/pm_gql_fallback.py`.

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local one
(17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **305**; preflight remote HEAD `ae5e3e4b8dad`, 322 blobs
- Preflight diff: `Modified: 10, New: 2, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `ae5e3e4b8dad` at preflight and is the **parent of the backup commit** → nothing
  landed in between, so **no sibling, no ref-PATCH 422 race**; the ref PATCH succeeded first try.
- 12 blobs uploaded, subtree `b949313b1a42d8c418ba9c22f8f7425992e3c995`, top tree
  `e0d79d69a8412660a7cd184bf2265496eb91539e`, commit + ref in one clean pass.
- Closing assertion: after this follow-up lands, the preflight must read
  `Modified: 0, New: 0, Deleted: 0` (that is the only proof the follow-up's ref PATCH landed).

## Post-push remote verification
- Remote HEAD `1d03e1fb96ad`; total blobs **324**, `demo-pm` blobs = **305** (== local file
  count 305); by top dir: demo-pm 305, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 →
  siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = **15**, non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + practice-notes table row + SKILL.md `latest:` pointer
`2026-11-24` → `2026-11-25` (same-length swap; SKILL.md measured 100,901 B, at cap),
pushed with the same standalone-subtree script. Bullet and row written by
`scripts/append-run-note-docs.py` (expect `INDEX count=1` / `ROW count=1`).
Pre-follow-up preflight expected `Modified: 3, New: 1, Deleted: 0` (+ `jobs.json` if a cron tick
dirtied it again); the closing preflight must read `0/0/0`.
