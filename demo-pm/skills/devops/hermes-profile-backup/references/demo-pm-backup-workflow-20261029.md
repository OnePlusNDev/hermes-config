# demo-pm backup run — 2026-10-29

## Result
**Method B (standalone subtree, no clone)** — **1 aborted attempt (account flip, blob HTTP 404)**, clean on one plain re-run.
Main commit: `0fb65412cd1356d24d2230a1d5b9c656fb8b6384`
URL: https://github.com/OnePlusNDev/hermes-config/commit/0fb65412cd1356d24d2230a1d5b9c656fb8b6384
Diff: **6 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNTester`** (`permissions.push=false`) → `gh auth switch --user OnePlusNDev`
  verified (`push=true`). The flip **recurred mid-run** (see Execution notes) and needed a second switch.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9_-]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the
  only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; `GITHUB_USERNAME`, `GITHUB_EMAIL`, `GITHUB_TOKEN`, `GATEWAY_PORT`,
  `AGENT_NAME`, `AGENT_ROLE`, `DEEPSEEK_API_KEY`, `TERMINAL_ENV`) excluded, never
  uploaded; `auth.json` / `auth.lock` / `state.db` present locally but excluded (remote tree clean)

## Diff (6 M, 0 A, 0 D)
```
M  demo-pm/channel_directory.json
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/references/skill-md-at-cap.md
M  demo-pm/skills/devops/hermes-profile-backup/templates/run-note-template.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
```
Characterized with `characterize-diff-vs-prev-head.py 7e20cda6357c` (explicit PRE_PUSH SHA, one
run, exit 0, output sliced from `/tmp/char_20261029.txt`); it reported **MODIFIED 6 / ADDED 0 /
DELETED 0**, matching preflight exactly.

- **Routine runtime churn (3):** `channel_directory.json` — only `updated_at`
  2026-10-03T10:30:58 → 2026-10-29T09:23:06; `cron/jobs.json` — task-polling `completed`
  6099→6147, memory-cleanup and config-backup counters 128→129, `next_run_at` 10-28→10-29 /
  10-29→10-30, `last_run_at` per job, `updated_at` 2026-10-28T20:03:05 → 2026-10-29T20:02:36;
  `memories/archive/ARCHIVE.md` — new 2026-10-28 Hindsight reflect+consolidation row
  (MEMORY.md 29.0d / USER.md 17.0d, neither past 30d; consolidation op completed in +117 ms,
  counter 87→88; reflect 99,303/6,200 **new band low** + disambig 279,166/5,455, wording gate
  fired on the **date-conditional shape 4th time**; daemon cold start ~3.4 min; 9-theme
  disambiguation verdict "no content-level expired facts").
- **Benign carry-over lag, authored after the 10-28 follow-up push (3):** `skill-md-at-cap.md`
  (new "Status 2026-10-28" block: SKILL.md now 100,866 chars, ~866 **over** the cap; the
  generic `patch` tool applied the `latest:` bump silently at byte-identical size, 4th
  consecutive confirmation that the cap is a `skill_manage`-only validation),
  `templates/run-note-template.md` (new "sibling landed mid-prep? re-read before you quote
  numbers" guidance + expected `3 M / 1 A / 0 D` follow-up shape), diagnostics
  `references/cleanup-run-endpoints-and-counts.md` (10-28 token row + 3.4-min startup
  calibration, "first six 10 s polls offline is normal migration").

`config.yaml` deliberately NOT in the diff: the remote blob already equalled the local one
(16,835 chars / 17,021 bytes — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **267**; remote HEAD `7e20cda6357c`, 286 blobs
- Preflight diff: `Modified: 6, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- **Pre-flight read `7e20cda6357c`; the script's Step 2 read `cc044d95c496`** — a sibling profile
  landed a backup in between (no sibling SHA recorded; the tree still showed 286 blobs and the
  same 6 `M`). The script parented on the fresh HEAD, so the numbers quoted above are the
  preflight's, measured against `7e20cda6357c`; the diff content was identical.
- **Attempt 1 aborted at the FIRST blob**: `FATAL uploading demo-pm/channel_directory.json:
  gh: Not Found (HTTP 404)`. Per the standing rule ("every blob-404 is an account flip") a
  re-check showed `gh api user` → **`OnePlusNTester`** again, `permissions.push=false` —
  the keyring race re-flipped the account between the pre-flight switch and the blob POST,
  the same shape as 10-25/10-27. Second `gh auth switch --user OnePlusNDev` (verified
  `push=true`) → the budgeted **one plain re-run** completed Steps 1–7 cleanly (blob SHAs are
  idempotent, so the re-run cost nothing).
- Remote HEAD **stayed at `cc044d95c496`** from the re-run's Step 2 through commit time →
  **no ref-PATCH 422 race**; the ref PATCH succeeded on the first attempt.
- 6 blobs uploaded (`channel_directory.json` `2644b4d516d2`, `cron/jobs.json` `2a40741e1ce6`,
  `ARCHIVE.md` `578280014543`, `skill-md-at-cap.md` `a45260e84131`,
  `run-note-template.md` `3cea6fe3f7ca`, `cleanup-run-endpoints-and-counts.md` `b7ea3edfb4c2`),
  subtree `379feeef71558b37ccfb32df1dea32df14a69979`, top tree
  `94536c6e840b883715af7f27df021dd3f51cc16c`, commit + ref in one clean pass.
- No network flakiness in the main push — the only abort was the account flip. The follow-up
  is a separate push; its cleanliness is confirmed by the closing `0/0/0` preflight, not assumed.

## Post-push remote verification
- Remote HEAD `0fb65412cd13`; total blobs **286**, `demo-pm` blobs = **267**
  (== local file count 267); by top dir: demo-pm 267, demo-dev 5, demo-tester 8,
  tester-01 5, .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path / temp-diagnostic leak checks → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
All FOUR items: run note + `references/dated-runs-index.md` bullet +
`references/method-b-practice-notes.md` "Observed on recent runs" row (today's account flip) +
SKILL.md `latest:` `2026-10-28` → `2026-10-29` (same-length in-place swap; SKILL.md is ~866 B
over its 100 K cap, so no new prose goes in it). Pushed with the same standalone-subtree
script; the closing preflight re-run must report `Modified: 0, New: 0, Deleted: 0`.
