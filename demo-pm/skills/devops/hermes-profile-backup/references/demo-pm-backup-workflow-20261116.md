# demo-pm backup run — 2026-11-16

## Result
**Method B (standalone subtree, no clone)** — **FIRST-TRY, 0 aborts (guard form; the keyring flipped TWICE and both were caught before any blob POST)**.
Main commit: `650e567bcb47ad8f5769f64cbca25b8de1a75d5d`
URL: https://github.com/OnePlusNDev/hermes-config/commit/650e567bcb47ad8f5769f64cbca25b8de1a75d5d
Diff: **16 M, 0 A, 0 D**.
Plus one separate one-file commit that synced the live `.gitignore`:
`bf758a028a035b7f1dbdf6edd791198a2d72919a` (temp-dir excludes, see Pre-flight).

## Pre-flight
- `gh api user` → **`OnePlusNTester`** (`permissions.push=false`) — the **10th observed keyring
  flip** (11-15 was the 9th). Guard form (switch → re-read login AND `permissions.push` in the
  SAME shell call) read `OnePlusNDev` / `push=true`.
- A **second** flip to `OnePlusNTester` landed between that check and the pre-push guard (**11th**);
  the guard caught it, re-switched, and the switch + backup script were then run **inside one shell
  call** so the identity could not be re-flipped in between. No blob 404 this run.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
  (only `OnePlusNDev/hermes-config` carries `demo-pm/`).
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9_-]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`;
  the only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**.
- `.env` (296 B) excluded, never uploaded; no `auth.json` / `auth.lock` / `state.db*` in the
  remote tree.
- **NEW exclude gap found and closed this run:** the first preflight surfaced 12 `A` files under
  root-level `tmp_pmtriage_1116_0900/` (`all_try1-4.json`, `pm_try1-4.json`, `search.json`,
  `dev_try.json`, `fetch.sh`, `parse.py`). Content inspection: `fetch.sh` extracts
  `GITHUB_TOKEN` from `.env` using the split-token trick `KEY="GITHUB_""TOKEN"` — a textbook
  diagnostic artifact. The dir name matched **no** existing rule (`tmp_triage` is a whole-dir
  name, `tmp_*` only matched FILENAMES, and the root-scoped check listed `tmp`/`tmp_pm` only).
  Fixed root-scoped in **all four** scripts (`preflight-backup-scan.py`,
  `gh-api-standalone-subtree-backup.py`, `gh-api-standalone-backup.py`,
  `characterize-diff-vs-prev-head.py`: `parts[0] == "tmp" or parts[0].startswith("tmp_")`),
  the rsync list (`--exclude '/tmp_*/'`), the gitignore template (`demo-pm/tmp_*/`) and the
  SKILL.md exclude bullet — then the live repo `.gitignore` in its own commit, since the
  standalone script copies `.gitignore` unchanged from the base tree and cannot carry the edit.

## Diff (16 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json                                                    (+10/-10)
M  demo-pm/memories/MEMORY.md                                                (+1/-1)
M  demo-pm/memories/USER.md                                                  (+1/-1)
M  demo-pm/memories/archive/ARCHIVE.md                                       (+1/-0)
M  demo-pm/skills/devops/demo-pm-github-api/SKILL.md                         (+1/-0)
M  demo-pm/skills/devops/hermes-profile-backup/SKILL.md                      (+1/-1)
M  demo-pm/skills/devops/hermes-profile-backup/references/method-a-rsync-excludes.md (+1/-0)
M  demo-pm/skills/devops/hermes-profile-backup/references/method-b-practice-notes.md (+20/-0)
M  demo-pm/skills/devops/hermes-profile-backup/scripts/characterize-diff-vs-prev-head.py (+4/-3)
M  demo-pm/skills/devops/hermes-profile-backup/scripts/gh-api-standalone-backup.py (+5/-4)
M  demo-pm/skills/devops/hermes-profile-backup/scripts/gh-api-standalone-subtree-backup.py (+5/-4)
M  demo-pm/skills/devops/hermes-profile-backup/scripts/preflight-backup-scan.py (+5/-4)
M  demo-pm/skills/devops/hermes-profile-backup/templates/gitignore-template.txt (+1/-0)
M  demo-pm/skills/devops/hermes-profile-backup/templates/run-note-template.md  (+7/-0)
M  demo-pm/skills/devops/hermes-profile-diagnostics/SKILL.md                 (+2/-2)
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md (+10/-0)
```
Characterized once with `scripts/characterize-diff-post-push.py d4cfb996feb4` (output
`/tmp/diffchar_20261116.txt`) → `MODIFIED 16 / ADDED 0 / DELETED 0`, prev blobs 311 / new 311,
identical 276.

- **Routine runtime churn (4)** — numbers read back from the **uploaded remote blobs**, not from the
  probe: `cron/jobs.json` task-polling `completed` 6963→**7011**, `next_run_at` → 11-16T20:30,
  `last_run_at` → 11-16T20:01:05.770; config-backup 146→**147**, next 11-17T20:00, last
  11-15T20:07:02; memory-cleanup 146→**147**, next 11-16T21:00, last 11-15T21:03:24;
  `updated_at` → 11-16T20:01:05.770862. `memories/MEMORY.md` + `USER.md` — header date only,
  2026-11-14 → **2026-11-15** (bodies identical; still reuse the 20261029 / 20261011 snapshots).
  `memories/archive/ARCHIVE.md` — new **2026-11-15 21:00-21:05 memory cleanup** row (`:9178`
  offline at first probe, **stale-body trap 7th consecutive** — poll 1 `http_code=000` while
  `/tmp/h9178_p1.json` still held the previous round's healthy body).
- **Exclude-gap fix, authored this run (7):** the four scripts, `method-a-rsync-excludes.md`,
  `gitignore-template.txt` and the one-line `tmp_pm/` → `tmp_*/` swap in the backup SKILL.md
  (same-length edit — SKILL.md sits over its 100 K cap).
- **Carry-over doc edits authored after the 11-15 follow-up push (5):**
  `demo-pm-github-api/SKILL.md` (+1: `mktemp -d /var/folders/...` fails with `Permission denied`
  in cron → paths degrade to `/pm_t1.json` and the whole 4×4 query round is lost);
  `method-b-practice-notes.md` (+20: a pre-push probe reads PROBE-time state while the blob carries
  UPLOAD-time state — the 11-15 correction lesson);
  `run-note-template.md` (+7: the same rule, phrased as an instruction for the next run);
  `hermes-profile-diagnostics/SKILL.md` (+2/-2: the `<profile_home>/.hindsight` env-wins note and
  the cleanup-run header re-dated to 11-15 / 25 consecutive gate triggers);
  `cleanup-run-endpoints-and-counts.md` (+10: **two `auto_prune` blocks** in config.yaml — a bare
  grep returns the *snapshots* pair (7 days) before the `sessions:` pair (90 days), so quote the
  `sessions:` subsection; + the 11-15 row 171,678 / 7,129 with disambig 120,333 / 4,848).
- `config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local one
  (17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- First preflight (before the exclude fix): 304 local files, remote HEAD `8cfada8692c3`,
  **9 M / 12 A** — the 12 `A` were the temp-dir leak.
- A sibling landed while the fix was being applied: the re-run preflight and Step 2 both read
  HEAD **`d4cfb996feb4`** (311 blobs), stable through commit time.
- Local files (after excludes): **292**; diff `Modified: 16, New: 0, Deleted: 0` —
  **gap closed, no other exclude drift**.
- Token scan on upload candidates: **CLEAN - no full token patterns**.

## Execution notes
- Remote HEAD was `d4cfb996feb4` at Step 2 and at commit time → **no ref-PATCH 422 race**; the ref
  PATCH succeeded on the first attempt.
- 16 blobs uploaded, subtree `f2d5fd6baaa47f8fb72bc0e8386e2643fc8645d1`, top tree
  `644c55012a7b542afaadfa20c9ade750456bef9e`, commit + ref in one clean pass.
- Live `.gitignore` sync commit `bf758a028a03` ran between the main commit and the follow-up
  (6 lines: `demo-pm/tmp/`, `demo-pm/tmp_*/`, `demo-pm/tmp_triage/` + comment). It touches no
  `demo-pm/` path, so it cannot perturb the closing `0/0/0` assertion.

## Post-push remote verification
- Post-push HEAD `650e567bcb47` (`.gitignore` commit `bf758a028a03` on top); total blobs **311**,
  `demo-pm` blobs = **292** (== local file count 292); by top dir: demo-pm 292, demo-dev 5,
  demo-tester 8, tester-01 5, .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `tmp_pmtriage_*`, `pm_health*`,
  `gh_health*`, `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-11-15` → `2026-11-16` +
`references/method-b-practice-notes.md` "Observed on recent runs" table row, pushed with the same
standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
