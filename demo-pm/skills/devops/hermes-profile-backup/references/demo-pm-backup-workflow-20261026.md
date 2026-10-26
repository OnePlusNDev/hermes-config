# demo-pm backup run — 2026-10-26

## Result
**Method B (standalone subtree, no clone)** — success, **FIRST-TRY** (no aborted
attempts, no blob-404 account flip, no ref-PATCH 422 race).
Main commit: `0b64f584bb42e97be7e9c82b7305f38506e46e61`
URL: https://github.com/OnePlusNDev/hermes-config/commit/0b64f584bb42e97be7e9c82b7305f38506e46e61
Diff: **6 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNDev`** (repo owner) with
  `permissions.push=true` — **no switch needed** (`GITHUB_TOKEN` unset), no mid-run
  flip this time (first clean auth run in three days).
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
M  demo-pm/skills/devops/hermes-profile-backup/references/network-flakiness-and-verify-tooling.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
```
Characterized against PRE_PUSH HEAD `0c87dec6d9c3` (`characterize-diff-vs-prev-head.py`,
one run, exit 0; local files 264 == remote at PREV_HEAD 264):

- **Routine runtime churn (2):** `cron/jobs.json` — task-polling `completed`
  5955→6003, memory-cleanup and config-backup counters 125→126, `next_run_at`
  10-25→10-26 / 10-26→10-27, `last_run_at` 10-24→10-25 per job, `updated_at`
  10-25T20:02:43 → 10-26T20:02:23; `memories/archive/ARCHIVE.md` — new 2026-10-25
  Hindsight reflect+consolidation row (MEMORY.md 26.0d / USER.md 14.0d, neither past
  the 30d window; primary reflect 109,123/5,832 → disambiguation 167,123/6,440 →
  verdict "no content-level expired facts"; bank 48 nodes / 1228 links, completed
  84→85).
- **Benign carry-over lag, authored after the 10-25 follow-up push (4):** the
  10-25-evening doc edits — `method-b-practice-notes.md` (2026-10-25 table row plus
  the "flip can be lost even when the check sits in the SAME shell call" section),
  `network-flakiness-and-verify-tooling.md` (new §6: mid-script `unexpected EOF` on
  the closing probes ⇒ re-run, never report FAIL), `hermes-profile-diagnostics/SKILL.md`
  (daemon-latency warm-start re-calibration wording),
  `references/cleanup-run-endpoints-and-counts.md` (2026-10-25 token row
  109,123/5,832 + disambig 167,123/6,440, wording-gate notes, delivery-path /
  identity ambiguity findings).

`config.yaml` deliberately NOT in the diff: the remote blob already equalled the local
one (16,835 chars / 17,021 bytes — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **264**; remote HEAD `0c87dec6d9c3`, 283 blobs total
- Preflight diff: `Modified: 6, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**
- Remote HEAD **stable at `0c87dec6d9c3`** from preflight through the run's Step 2
  (no sibling advance mid-run; an earlier read had seen `7b73541258b5`, i.e. another
  profile pushed between our auth check and preflight, and the script parented on the
  fresh HEAD)

## Execution notes
- 6 blobs uploaded (`cron/jobs.json` `1f68e0c91626`, `ARCHIVE.md` `fc430f744173`,
  `method-b-practice-notes.md` `4fc6d251a484`,
  `network-flakiness-and-verify-tooling.md` `56cfbc836187`,
  diagnostics `SKILL.md` `a57c348c721d`,
  `cleanup-run-endpoints-and-counts.md` `5f4017e9ec1e`), subtree
  `1cfb2813060ffddea53547233e6c549a5bfcf8f0`, top tree
  `8832a7b58b877f20de4d9773c8ff39cef41b070c`, commit + ref in one clean pass.
- Network: no transport error on either API phase; the 10-25 `unexpected EOF`
  transport flakiness did not recur.

## Post-push remote verification
- Remote HEAD `0b64f584bb42`; total blobs **283**, `demo-pm` blobs = **264**
  (== local file count 264); by top dir: demo-pm 264, demo-dev 5, demo-tester 8,
  tester-01 5, .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15,
  non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`,
  `processes.json`, `bin/tirith`, `/home/`, `/.local/`, `response_store.db`,
  `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + `references/dated-runs-index.md` bullet + `SKILL.md` `latest:` pointer
`2026-10-25` → `2026-10-26` (same-length in-place swap; SKILL.md is at its 100 K cap),
pushed with the same standalone-subtree script. The closing preflight re-run must
report `Modified: 0, New: 0, Deleted: 0` against it — that is the proof the remote
tree equals the local desired state.
