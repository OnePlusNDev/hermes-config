# demo-pm backup run — 2026-10-30

## Result
**Method B (standalone subtree, no clone)** — **1 aborted attempt (account flip, blob HTTP 404)**, clean on one plain re-run.
Main commit: `89e9a7474fc800b49c33cefcc7194ab5c6b880fd`
URL: https://github.com/OnePlusNDev/hermes-config/commit/89e9a7474fc800b49c33cefcc7194ab5c6b880fd
Diff: **5 M, 2 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNTester`** (`push=false`) → `gh auth switch --user OnePlusNDev`
  verified (`push=true`). The flip **recurred within ~20 s** (see Execution notes) and needed a
  second switch.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9_-]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the
  only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; `GITHUB_USERNAME`, `GITHUB_EMAIL`, `GITHUB_TOKEN`, `GATEWAY_PORT`,
  `AGENT_NAME`, `AGENT_ROLE`, `DEEPSEEK_API_KEY`, `TERMINAL_ENV`) excluded, never
  uploaded; `auth.json` / `auth.lock` / `state.db` present locally but excluded (remote tree clean)

## Diff (5 M, 2 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/MEMORY.md
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/templates/run-note-template.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
A  demo-pm/memories/archive/MEMORY-20261029.snapshot.md
A  demo-pm/skills/devops/hermes-profile-backup/references/index-and-table-append-recipe.md
```
Characterized with `characterize-diff-vs-prev-head.py --commit=89e9a7474fc8` (derived PRE_PUSH
`e1d028d82175`, one run, exit 0, output sliced from `/tmp/char_20261030.txt`); it reported
**MODIFIED 5 / ADDED 2 / DELETED 0**, matching preflight exactly (local 270 vs remote-at-prev 268).

- **Routine runtime churn (3):** `cron/jobs.json` — task-polling `completed` 6147→6195,
  config-backup and memory-cleanup counters 129→130, `next_run_at` 10-29→10-30 / 10-30→10-31 /
  10-30→10-31, `last_run_at` per job, `updated_at` 2026-10-29T20:02:36 → 2026-10-30T20:01:12;
  `memories/MEMORY.md` — **the 30-day archive finally fired**: header 最后更新 2026-09-29 →
  2026-10-29 plus a new snapshot pointer (`archive/MEMORY-20261029.snapshot.md`, 正文未改);
  `memories/archive/ARCHIVE.md` — new 2026-10-29 row (MEMORY.md mtime 2026-09-29 = 30.0d → archived,
  1798-char snapshot, USER.md 18.0d not due; daemon **fully cold** — 0 postgres processes — yet
  healthy in **~10–20 s**, vs 3.4 min on 10-28; consolidation op completed +461 ms, counter 88→89;
  main reflect 112,261/5,243, wording gate fired on the **date-conditional shape for the 5th time
  (9th consecutive)**, disambig 174,811/5,638 → "no content-level expired facts").
- **Benign carry-over lag, authored after the 10-29 follow-up push (2):**
  `templates/run-note-template.md` (sibling-HEAD re-read guidance: "state BOTH SHAs" for a
  mid-prep remote advance), diagnostics `references/cleanup-run-endpoints-and-counts.md`
  (10-29 token row + "a truly cold host still went healthy in 10–20 s" startup calibration).
- **Legitimately NEW include-list files (2):** `memories/archive/MEMORY-20261029.snapshot.md`
  (the archive snapshot produced yesterday — exactly the monthly/30-day rollover the characterize
  probe's ADDED hint describes) and `references/index-and-table-append-recipe.md` (yesterday's
  verified append recipe, referenced from `run-note-template.md`). Neither is EXCLUDE drift.

`config.yaml` deliberately NOT in the diff: the remote blob already equalled the local one
(16,835 chars / 17,021 bytes — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **270**; remote HEAD `e1d028d82175`, 287 blobs
- Preflight diff: `Modified: 5, New: 2, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- **Attempt 1 aborted at the FIRST blob**: the pre-run two-read check inside the same shell call
  read `ACTIVE=OnePlusNTester PUSH=false` — i.e. the keyring race undid the pre-flight switch
  within ~20 s (login AND permission both wrong, the 10-24/10-27 shape) → Step 4 died with
  `FATAL uploading demo-pm/cron/jobs.json: gh: Not Found (HTTP 404)`. Second
  `gh auth switch --user OnePlusNDev` (verified `push=true`) → the budgeted **one plain re-run**
  completed Steps 1–7 cleanly (blob SHAs idempotent, so the re-run cost nothing).
- Remote HEAD **was `e1d028d82175` at Step 2 and stayed there through commit time** →
  **no ref-PATCH 422 race**; the ref PATCH succeeded on the first attempt. No sibling advance
  was observed this run (no second preflight needed).
- 7 blobs uploaded (`cron/jobs.json` `ab0cbe4e1d18`, `MEMORY.md` `4ec50bd51f4e`,
  `ARCHIVE.md` `d482b1c1df81`, `run-note-template.md` `87ed6775a04e`,
  `cleanup-run-endpoints-and-counts.md` `db656659b6db`, `MEMORY-20261029.snapshot.md`
  `1c558cf95830`, `index-and-table-append-recipe.md` `904f97204457`), subtree
  `e3b7f306ed700e7f55ac78259d1946695ddab96c`, top tree
  `d7430918360d11312003305373840d8373d91d80`, commit + ref in one clean pass.
- No network flakiness in the main push — the only abort was the account flip.

## Post-push remote verification
- Remote HEAD `89e9a7474fc8`; total blobs **289**, `demo-pm` blobs = **270**
  (== local file count 270); by top dir: demo-pm 270, demo-dev 5, demo-tester 8,
  tester-01 5, .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path / temp-diagnostic leak checks → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
All FOUR items: run note + `references/dated-runs-index.md` bullet +
`references/method-b-practice-notes.md` "Observed on recent runs" row (today's account flip) +
SKILL.md `latest:` `2026-10-29` → `2026-10-30` (same-length in-place swap; SKILL.md is still over
its 100 K cap, so no new prose goes in it). Pushed with the same standalone-subtree script; the
closing preflight re-run must report `Modified: 0, New: 0, Deleted: 0`.
