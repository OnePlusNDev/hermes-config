# demo-pm backup run — 2026-10-27

## Result
**Method B (standalone subtree, no clone)** — **ONE aborted attempt** (blob HTTP 404
account flip, NOT a 422).
Main commit: `614945b19a0dc6af3b81152ecc8ea0f690c13b44`
URL: https://github.com/OnePlusNDev/hermes-config/commit/614945b19a0dc6af3b81152ecc8ea0f690c13b44
Diff: **6 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNTester`** with `permissions.push=false` → `gh auth switch
  --user OnePlusNDev` verified owner (`push=true`). The switch **did not hold**: the
  pre-push re-check read `OnePlusNTester` again (this time `push=true`, so the login
  check alone would have passed) and attempt 1 died at the FIRST blob POST with
  `FATAL uploading demo-pm/cron/jobs.json: gh: Not Found (HTTP 404)`. Second switch +
  one plain re-run → Steps 1–7 clean. `GITHUB_TOKEN` unset throughout.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9_-]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the
  only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; `GITHUB_USERNAME`, `GITHUB_EMAIL`, `GITHUB_TOKEN`, `GATEWAY_PORT`,
  `AGENT_NAME`, `AGENT_ROLE`, `DEEPSEEK_API_KEY`, `TERMINAL_ENV`) excluded, never
  uploaded; no `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (6 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/references/method-b-practice-notes.md
M  demo-pm/skills/devops/hermes-profile-backup/templates/run-note-template.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
```
Characterized against PRE_PUSH HEAD `0b64f584bb42` (parents[0] of the then-current
remote `39b13879f0d3`; `characterize-diff-vs-prev-head.py`, one run, exit 0):
that probe reported **8 M / 1 A** because it diffs against the 10-26 *main* commit —
the extra 3 (SKILL.md `latest:`, `dated-runs-index.md`, the 20261026 run note) are the
10-26 follow-up commit already on the remote. Against remote HEAD the diff is the
6 M below.

- **Routine runtime churn (2):** `cron/jobs.json` — task-polling `completed`
  6002→6051, memory-cleanup and config-backup counters 126→127, `next_run_at`
  10-26→10-27 / 10-27→10-28, `last_run_at` per job, `updated_at`
  2026-10-26T20:00:18 → 2026-10-27T20:01:30; `memories/archive/ARCHIVE.md` — new
  2026-10-26 Hindsight reflect+consolidation row (MEMORY.md 27.0d / USER.md 15.0d,
  neither past the 30d window; consolidation completed 85→86; first reflect crashed
  mid-run at LinkExpansion → daemon restart → retry OK; primary reflect
  158,635/7,214 → disambiguation 426,048/5,915 → verdict "no content-level expired
  facts").
- **Benign carry-over lag, authored after the 10-26 follow-up push (4):**
  `method-b-practice-notes.md` (10-26 table row — backfilled post-run yesterday),
  `templates/run-note-template.md` (new 4-item follow-up checklist: run note + index
  bullet + SKILL.md `latest:` + practice-notes row), diagnostics `SKILL.md`,
  `references/cleanup-run-endpoints-and-counts.md` (10-26 token row
  158,635/7,214 + disambig 426,048/5,915, reflect-crash/restart note).

`config.yaml` deliberately NOT in the diff: the remote blob already equalled the local
one (16,835 chars / 17,021 bytes — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **265**; remote HEAD `39b13879f0d3`, 284 blobs total
- Preflight diff: `Modified: 6, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote moved `39b13879f0d3` → **`7bc7f64e54ba`** between preflight and the script's
  Step 2 (a sibling profile landed); the script re-read HEAD and parented on the fresh
  one → **no ref-PATCH 422, no rebase**.
- 6 blobs uploaded (`cron/jobs.json` `d47beb13188b`, `ARCHIVE.md` `c6237bb9abcf`,
  `method-b-practice-notes.md` `5353dbcf7303`, `run-note-template.md` `9b46b8e5cbbe`,
  diagnostics `SKILL.md` `b21394fd0fdd`,
  `cleanup-run-endpoints-and-counts.md` `529e2b2851f4`), subtree
  `37b3b4b09a69af7a8ea065344c1a6143ec6213e4`, top tree
  `a9ab75593864e7ab4c78b535d180b53db2da73db`, commit + ref in one clean pass.

## Post-push remote verification
- Remote HEAD `614945b19a0d`; total blobs **284**, `demo-pm` blobs = **265**
  (== local file count 265); by top dir: demo-pm 265, demo-dev 5, demo-tester 8,
  tester-01 5, .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15,
  non-empty = **0**
- Sensitive-path / temp-diagnostic leak checks → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
All FOUR items this time (per the 10-26 checklist): run note +
`references/dated-runs-index.md` bullet + SKILL.md `latest:` `2026-10-26` → `2026-10-27`
(same-length in-place swap; SKILL.md is at its 100 K cap) + the
`method-b-practice-notes.md` table row above. Pushed with the same standalone-subtree
script; the closing preflight re-run must report `Modified: 0, New: 0, Deleted: 0`
against it.
