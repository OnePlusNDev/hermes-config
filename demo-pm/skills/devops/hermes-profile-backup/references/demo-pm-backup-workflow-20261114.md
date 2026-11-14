# demo-pm backup run — 2026-11-14

## Result
**Method B (standalone subtree, no clone)** — **FIRST-TRY, 0 aborts (no account flip after the switch, no 422 race)**.
Main commit: `a0622794b1f10b97f475459079d150dd82ac8aed`
URL: https://github.com/OnePlusNDev/hermes-config/commit/a0622794b1f10b97f475459079d150dd82ac8aed
Diff: **7 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNTester`** (`permissions.push=false`) — the **8th observed keyring flip**
  (11-13 was the 7th). `gh auth switch --user OnePlusNDev` → verified owner + `push=true`; the
  re-check immediately before the script (guard form, not a bare echo) re-read **`OnePlusNDev`**,
  and the switch held through commit time — no blob 404.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
  (only `OnePlusNDev/hermes-config` carries `demo-pm/`).
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`;
  the only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**.
- `.env` (296 B; `GITHUB_USERNAME`, `GITHUB_EMAIL`, `GITHUB_TOKEN`, `GATEWAY_PORT`, `AGENT_NAME`,
  `AGENT_ROLE`, `DEEPSEEK_API_KEY`, `TERMINAL_ENV`) excluded, never uploaded; no `auth.json` /
  `auth.lock` / `state.db*` in the remote tree.

## Diff (7 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/MEMORY.md
M  demo-pm/memories/USER.md
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/references/method-b-practice-notes.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
```
Characterized ONCE against the **pre-push** HEAD `975f3e5d21b6` with an ad-hoc blob-diff probe
(`git/blobs/<sha>` at the previous commit vs the local file): +10/-10, +1/-1, +1/-1, +1/-0,
+42/-0, +20/-2, +7/-1.

- **Routine runtime churn (4):** `cron/jobs.json` — task-polling `completed` 6867→**6915**,
  `next_run_at` → 11-14T20:30, `last_run_at` 11-14T20:00:58; config-backup `completed` 144→145,
  next 11-15T20:00, last 11-13T20:05:06; memory-archive 144→145, next 11-14T21:00,
  last 11-13T21:04:37; `updated_at` → 11-14T20:00:58. `memories/MEMORY.md` — header only,
  最后更新 2026-11-12 → **2026-11-13** (body byte-identical, still reuses
  `archive/MEMORY-20261029.snapshot.md`); `memories/USER.md` — header only, same bump
  (body identical, reuses `archive/USER-20261011.snapshot.md`); `memories/archive/ARCHIVE.md` —
  new **2026-11-13 21:00-21:06 memory cleanup** row (`:9178` offline at first probe → launcher
  start; poll1 `http_code=000` while `/tmp/h9178_p1.json` still held the previous round's
  `{"status":"healthy"}` body — **stale-body trap 5th consecutive**; healthy at poll 2, ~10-20 s
  warm pg0; consolidation op `320965a1` **+256 ms**, `deduplicated=false`, counter **103→104**,
  `pending=0`/`failed=0`; nodes 48 / 1228 links / 2 documents stable; both reflect passes fine,
  no crash, no 504 — primary **105,411 / 4,300** @ `budget=high`, wording gate **23rd consecutive**
  in a 「## 记忆健康度评估结论」 + 「### 一、过期事实（30 天以上）：以库内时间戳判断——无」 shape
  (negation after the keyword *and* inside the label) + 「无法从检索结果确认『今天』的实际日期」
  date-unknowable clause; disambig **65,704 / 4,544** — new low on both fields, two passes
  totalling only ~171 K; 「无内容性过期事实」 with the `Scheduler 缺 im:chat:readonly（99991672）`
  and `四个 profile secret 10014 invalid` items kept as **「待现场核验的状态快照」**, not archive
  targets; bank↔flat-file LLM-key drift **9th consecutive day** — logged, no data mutated;
  sessions 7178 / >90d 2732 / >30d 5678, `auto_prune: false` → record only).
- **Carry-over doc edits authored after the 11-13 follow-up push (3):**
  `hermes-profile-backup/references/method-b-practice-notes.md` (+42 lines: new section
  "A DETECTED flip must be acted on in the same shell call — guard, never a bare echo" recording
  the 11-13 loss mode and the `ACT`/`PUSH` guard snippet; new section "The run note's post-push
  numbers describe the MAIN commit — the final tree is one blob larger");
  `hermes-profile-diagnostics/SKILL.md` (+20/-2: a 7-step canonical cleanup-run order
  re-verified 2026-11-13, placed ahead of the existing pointer list);
  `hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md` (+7/-1: 11-13 token
  row 105,411 / 4,300 + disambig 65,704 / 4,544 with the 23rd-gate shape, and the correction that
  **the 50 K baseline is a floor test, not a "the bank was read" proof**).
`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local one
(17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **288**; remote HEAD `975f3e5d21b6`, 307 blobs (demo-pm 288)
- Preflight diff: `Modified: 7, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**; the preflight and the
  backup script agreed on the same HEAD and the same 7-file M set (no sibling landing this run)

## Execution notes
- Remote HEAD was `975f3e5d21b6` at preflight, at Step 2 and at commit time → **no ref-PATCH
  422 race**; the ref PATCH succeeded on the first attempt.
- 7 blobs uploaded, subtree `a870ab98160c7b62258720285f98b116c46c7189`, top tree
  `8ff3398d391f111620bdfd4bca66bdb74fe0f3ee`, commit + ref in one clean pass.
- Closing preflight must read `Modified: 0, New: 0, Deleted: 0` after the follow-up commit.

## Post-push remote verification
- Remote HEAD `a0622794b1f1`; total blobs **307**, `demo-pm` blobs = **288** (== local file count
  288 at the main commit); by top dir: demo-pm 288, demo-dev 5, demo-tester 8, tester-01 5,
  .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-11-13` → `2026-11-14` +
`references/method-b-practice-notes.md` "Observed on recent runs" table row, pushed with the same
standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
