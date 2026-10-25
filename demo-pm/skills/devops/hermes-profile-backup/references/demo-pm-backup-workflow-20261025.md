# demo-pm backup run — 2026-10-25

## Result
**Method B (standalone subtree, no clone)** — success on the **second attempt**: the first
attempt aborted at Step 4 with `FATAL uploading demo-pm/cron/jobs.json: gh: Not Found
(HTTP 404)` — the keyring race had re-flipped the active account to `OnePlusNTester`
(`push=false`) *within ~1 minute of a verified `OnePlusNDev` switch*. One plain re-run after
re-switching completed Steps 1–7 in a single pass (no ref-PATCH 422 race).
Main commit: `68e0c832072e70dd5668ca80f346a4fb8787ef4e`
URL: https://github.com/OnePlusNDev/hermes-config/commit/68e0c832072e70dd5668ca80f346a4fb8787ef4e
Diff: **7 M, 0 A, 0 D**.

## Pre-flight
- Initial check: `gh api user` → **`OnePlusNTester`**, `permissions.push=false` → the
  pre-flight two-read rule (login **and** `permissions.push`) caught it immediately.
  `unset GITHUB_TOKEN` + `gh auth switch --user OnePlusNDev` → re-read returned
  `OnePlusNDev`, `admin=true/push=true`, and `gh auth status` confirmed the active account.
- ⚠️ **The switch did NOT hold for the run.** The pre-run re-check in the *same* shell call
  as the script showed `active=OnePlusNTester push=false` again, and the first blob POST
  404'd. Second switch + one plain re-run → clean. This is the flip signature documented in
  `SKILL.md` ("A switch can be undone within a minute"); the remedy was exactly the
  documented one (treat blob-404 as a flip, never as a missing repo/rate limit).
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9_-]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the only
  `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B) excluded and never uploaded; no `auth.json` / `auth.lock` / `state.db*`
  anywhere in the tree

## Diff (7 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/references/method-b-practice-notes.md
M  demo-pm/skills/devops/hermes-profile-backup/templates/run-note-template.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
```
Characterized against PRE_PUSH HEAD `50a0e9a11a9d` (`characterize-diff-vs-prev-head.py`, one
run, exit 0):

- **Routine runtime churn (2):** `cron/jobs.json` — task-polling `completed` 5907→5954,
  memory-cleanup and config-backup counters 124→125, `updated_at` 10-24T20:02:56 →
  10-25T20:00:41; `memories/archive/ARCHIVE.md` — new 2026-10-24 Hindsight
  reflect+consolidation row (MEMORY.md 25d / USER.md 13d, neither past the archive window;
  primary reflect 152,826/6,638 tokens → auto-disambiguation 475,495/8,011 → verdict "no
  content-level expired facts"; bank 48 nodes / 1,228 links, completed 83→84).
- **Benign carry-over lag, authored after the 10-24 follow-up push (5):** the 10-24-evening
  doc edits — `hermes-profile-backup/SKILL.md` (budget-one-re-run wording, shared-`/tmp`
  payload note, check-TWICE/read-`permissions.push` block),
  `references/method-b-practice-notes.md` (new "`gh api user` is NOT a sufficient flip
  detector" section + Step-5 hang), `templates/run-note-template.md` (never write
  "no network flakiness" before the follow-up lands), `hermes-profile-diagnostics/SKILL.md`
  (daemon restart latency, `memory.db` always 0 B, `/health` vs `lsof` triage),
  `references/cleanup-run-endpoints-and-counts.md` (10-24 reflect token row 152,826/6,638 +
  disambig 475,495/8,011, aiohttp teardown warnings benign, `process wait` top-truncation).

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local
one (16,835 chars / 17,021 bytes — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **263**; remote HEAD `50a0e9a11a9d`, 282 blobs total
- Preflight diff: `Modified: 7, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**
- A sibling backup landed mid-run: `ac39b49dd3f2` "backup: demo-dev profile config
  (2026-10-25)" at 12:01:13Z (between our preflight read and the run). The script re-read
  HEAD at Step 2 (`Remote HEAD: ac39b49dd3f2`) and parented on it → **no 422, no rebase**.

## Execution notes
- 7 blobs uploaded, subtree `07c1e7ed67b3e6db4dbee0e8669411426a15dcbc`, top tree
  `74470941c85dbee4126157929cf1c8738872d525`, commit + ref in one clean pass.
- Network: no transport error on either API phase (the only failure was the account flip,
  which surfaces as HTTP 404 on the blob POST, not as a timeout).

## Post-push remote verification
- Remote HEAD `68e0c832072e`; total blobs **282**, `demo-pm` blobs = **263** (== local file
  count 263); by top dir: demo-pm 263, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1
  → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + `references/dated-runs-index.md` bullet + `SKILL.md` `latest:` pointer
`2026-10-24` → `2026-10-25` (same-length in-place swap; SKILL.md is at its 100 K cap), pushed
with the same standalone-subtree script. The closing preflight re-run must report
`Modified: 0, New: 0, Deleted: 0` against it — that is the proof the remote tree equals the
local desired state.
