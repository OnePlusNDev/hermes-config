# demo-pm backup run — 2026-10-03 (2nd run, 20:00 CST)

> Second run of 2026-10-03. The first (10:36 CST) is `demo-pm-backup-workflow-20261003.md`
> (main `c61866ac8a22`). Same-day repeat runs take a `YYYYMMDDb` filename suffix so each run
> keeps an atomic note and the index `grep -c '<file>.md' == 1` verification stays clean.

## Result
**Method B (standalone subtree, no clone)** — success, **FIRST-TRY (no aborted attempts)**.
Main commit: `83eb2059d683ae8b87be70e566804fc88e21ef3d`
URL: https://github.com/OnePlusNDev/hermes-config/commit/83eb2059d683ae8b87be70e566804fc88e21ef3d
Diff: **2 M, 0 A, 2 D**.

## Pre-flight
- `gh api user` → **`OnePlusNTester`** (`push=false`) → `gh auth switch --user OnePlusNDev`
  (owner, `push=true`); re-checked immediately before the blob phase and the switch **held**
  (no mid-run flip). `GITHUB_TOKEN` unset.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key:` → **15** lines, all `''` (0 non-empty); the only `key_env` occurrence is a comment
  (line 695) → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; GITHUB_USERNAME, GITHUB_EMAIL, GITHUB_TOKEN, GATEWAY_PORT, AGENT_NAME,
  AGENT_ROLE, DEEPSEEK_API_KEY, TERMINAL_ENV) excluded, never uploaded; no
  `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (2 M, 0 A, 2 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/skills/devops/hermes-profile-backup/SKILL.md
D  demo-pm/skills/apple/apple-notes/SKILL.md
D  demo-pm/skills/software-development/systematic-debugging/SKILL.md
```
Characterized each `M` against the **pre-push** remote HEAD `0377a76d082e` with
`scripts/characterize-diff-vs-prev-head.py 0377a76d082e`:
- `cron/jobs.json` — routine runtime churn (`completed` 4880→4899, 102→103; `next_run_at` /
  `last_run_at` / `updated_at` advanced to 2026-10-03 20:00). Pure runtime churn.
- `hermes-profile-backup/SKILL.md` — **benign carry-over lag**: the local-file-count sanity
  number rewrite (hardcoded `407` → "re-derive each run; never hardcode"), written *after* the
  10:36 run's follow-up push → ordering, not a lost commit.
- **The 2 `D` are genuine local skill removals today** (~11:30): `apple/apple-notes/SKILL.md`
  and `software-development/systematic-debugging/SKILL.md` no longer exist under the profile
  (`apple/` dir now holds only `DESCRIPTION.md` + `macos-computer-use/`; `software-development/`
  only `plan/`). Verified absent on disk before accepting the deletions; copies remain in git
  history.

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local one
(17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **233**; remote HEAD `0377a76d082e`, **254** blobs
- Preflight diff: `Modified: 2, New: 0, Deleted: 2` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `0377a76d082e` at blob-phase start and **stayed there through commit time** →
  **no ref-PATCH 422 race**; the ref PATCH succeeded on the first attempt.
- No network flakiness, no mid-run account flip; the `mkdtemp` private-payload-dir fix held.
- 2 blobs uploaded, subtree `96e0c79d5df4205a5afc26c2759afde76e2d59a2`, top tree
  `49d822cb7ed9c2a80f25d12cb168e44779ce66cd`, commit + ref in one clean pass.

## Post-push remote verification
- Remote HEAD `83eb2059d683`; total blobs **252**, `demo-pm` blobs = **233** (== local file
  count 233); by top dir: demo-pm 233, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1
  → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
  (16,835 chars / 17,021 bytes)
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Second-run run note (`...20261003b.md`) + index bullet + `references/method-b-practice-notes.md`
second-run table row, pushed with the same standalone-subtree script. The SKILL.md `latest:`
pointer is left at `2026-10-03` (the date is unchanged; the same-day `b` filename suffix carries
the run distinction). Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
