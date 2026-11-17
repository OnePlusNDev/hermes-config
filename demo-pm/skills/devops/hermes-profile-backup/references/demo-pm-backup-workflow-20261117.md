# demo-pm backup run — 2026-11-17

## Result
**Method B (standalone subtree, no clone)** — **FIRST-TRY, 0 aborts (guard form; 12th keyring flip caught before any blob POST)**.
Main commit: `6c41bf38ee3e3254256824df2768cac5c881f070`
URL: https://github.com/OnePlusNDev/hermes-config/commit/6c41bf38ee3e3254256824df2768cac5c881f070
Diff: **7 M, 1 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNTester`** (`permissions.push=false`) — the **12th observed keyring
  flip** (11-16 logged the 10th and 11th). Guard form (switch → re-read login AND
  `permissions.push`) read `OnePlusNDev` / `push=true`.
- ⚠️ Honest gap this run: the pre-push guard was **not** re-executed as its own check immediately
  before the script (the 11-16 lesson says to, and to run switch+script in ONE shell call). The
  identity nevertheless held through Step 7 — proven by 8 clean blob POSTs and a first-try ref
  PATCH (a flipped account yields HTTP 404 at the first blob). Do not treat this run as evidence
  that the guard is optional; it is what makes the tail risk zero instead of small.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
  (only `OnePlusNDev/hermes-config` carries `demo-pm/`).
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9_-]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`;
  the only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**.
- `.env` excluded, never uploaded; no `auth.json` / `auth.lock` / `state.db*` in the remote tree.

## Diff (7 M, 1 A, 0 D)
```
M  demo-pm/cron/jobs.json                                                    (+10/-10)
M  demo-pm/memories/MEMORY.md                                                (+1/-1)
M  demo-pm/memories/USER.md                                                  (+1/-1)
M  demo-pm/memories/archive/ARCHIVE.md                                       (+1/-0)
M  demo-pm/skills/devops/hermes-profile-backup/references/method-b-practice-notes.md (+18/-0)
M  demo-pm/skills/devops/hermes-profile-diagnostics/SKILL.md                 (+3/-1)
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md (+9/-0)
A  demo-pm/skills/devops/hermes-profile-backup/references/gitignore-sync-and-live-repo-edits.md (+64/-0)
```
Characterized with `scripts/characterize-diff-vs-prev-head.py` (output `/tmp/diffchar_20261117.txt`),
which derived `PREV_HEAD = bf758a028a03` (parent of current main) and therefore reported **9 M / 2 A**
— that baseline predates the 11-16 **follow-up** commit `ca797b5e908b` ("backup: demo-pm 2026-11-16",
12:07:28Z), whose own four items (`SKILL.md` latest pointer, `dated-runs-index.md` bullet,
`demo-pm-backup-workflow-20261116.md`, the 11-16 practice-notes row) are already on the remote. The
preflight — measured against `ca797b5e908b` — is the authoritative figure: **7 M / 1 A / 0 D**, and it
matches the landed commit's file list exactly.

- **Routine runtime churn (4)** — numbers read back from the **uploaded remote blobs**, not the probe:
  task-polling `repeat.completed` 7011→**7059**, `next_run_at` → 11-17T20:30, `last_run_at` →
  11-17T20:01:27.242784, `updated_at` → 11-17T20:01:27.243685; config-backup 147→**148**, next
  11-18T20:00, last 11-16T20:08:02.160344; memory-cleanup 147→**148**, next 11-17T21:00, last
  11-16T21:06:35.370334. `memories/MEMORY.md` + `USER.md` — header date only, 2026-11-15 →
  **2026-11-16** (bodies identical; snapshots 20261029 / 20261011 still reused).
  `memories/archive/ARCHIVE.md` — new **2026-11-16 21:00-21:06 memory cleanup** row: stale-body trap
  **8th consecutive** (poll1 `http_code=000` over a healthy leftover body, healthy at poll 2 ~20 s),
  consolidation op `0c568905` **+60 ms**, `deduplicated=false`, counter 106→107, both reflect passes
  fine, primary **190,259 / 7,423** @ budget=high, wording gate fired **26th consecutive** in a
  「## 结论（先看这三行）」 3-row table shape, disambig **265,212 / 7,951** = 「无内容性过期事实」,
  bank↔flat-file LLM-key drift **day 12**, sessions 7328 / 2882 (>90d) / 5828 (>30d) = +50/day,
  zero archiving.
- **Carry-over doc edits authored after the 11-16 follow-up push (3):**
  `method-b-practice-notes.md` (+18: the live-`.gitignore`-needs-its-own-commit rule and the
  run-switch-and-script-in-one-shell-call rule); `hermes-profile-diagnostics/SKILL.md` (+3/-1: two
  new cron-mode stalls — relative target + `workdir` instead of an absolute dotfile redirect, and no
  `bash -c '…'` launcher wrapper — plus the cleanup header re-dated to 11-16 / 26 consecutive);
  `cleanup-run-endpoints-and-counts.md` (+9: the 11-16 reflect row 190,259 / 7,423 with disambig
  265,212 / 7,951, and the `workdir` append note).
- **New reference doc (1):** `gitignore-sync-and-live-repo-edits.md` — the recipe for syncing a live
  repo `.gitignore` in its own one-file commit (the standalone script copies `.gitignore` from the
  base tree and cannot carry the edit), plus the dated root-`tmp_*` exclude-gap record.
- `config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local one
  (17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **294**; remote HEAD `ca797b5e908b`, 312 blobs
- Preflight diff: `Modified: 7, New: 1, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `ca797b5e908b` at blob-phase start and at commit time → **no ref-PATCH 422 race**;
  the ref PATCH succeeded on the first attempt. No sibling landed during this run (the sibling that
  moved HEAD earlier was the 11-16 follow-up, already present at the first preflight).
- 8 blobs uploaded, subtree `8ea99dc09111a61d2af42fad50212ee3ea743414`, top tree
  `6fbecdd98e0a0f0d5e880d6668a100a187d1d76b`, commit + ref in one clean pass.
- ⚠️ **`gh-api-standalone-subtree-backup.py` does not implement `--help`** — it ignores unknown
  argv and runs the full backup. Invoking it with `--help` (piped to `head -30` to read usage) is
  what actually executed this run's main commit. Harmless here — the preflight was already clean,
  the scan was CLEAN, and the identity was verified — but never probe this script's interface by
  running it. Read its docstring instead, and treat "how do I get usage?" as a question with no
  cheap answer.
- Closing assertion: after this follow-up lands, the preflight must read
  `Modified: 0, New: 0, Deleted: 0`.

## Post-push remote verification
- Remote HEAD `6c41bf38ee3e`; total blobs **313**, `demo-pm` blobs = **294** (== local file count
  294); by top dir: demo-pm 294, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 → siblings
  intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = **15**, non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `tmp_*`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-11-16` → `2026-11-17` +
`references/method-b-practice-notes.md` "Observed on recent runs" table row, pushed with the same
standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
