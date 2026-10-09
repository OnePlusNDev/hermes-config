# demo-pm backup run — 2026-10-09

## Result
**Method B (standalone subtree, no clone)** — success, **1 aborted attempt (ref-PATCH 422 race)**.
Main commit: `ac3230eec4cac8cfbb58e2100fecfe5880bea3a3`
URL: https://github.com/OnePlusNDev/hermes-config/commit/ac3230eec4cac8cfbb58e2100fecfe5880bea3a3
Diff: **3 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNDev`** (repo owner, `push=true`) — **no switch needed**
  (`GITHUB_TOKEN` unset); re-checked immediately pre-run, held, **no mid-run flip**
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the
  only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; GITHUB_USERNAME, GITHUB_EMAIL, GITHUB_TOKEN, GATEWAY_PORT, AGENT_NAME,
  AGENT_ROLE, DEEPSEEK_API_KEY, TERMINAL_ENV) excluded, never uploaded; `auth.json` (164 B) /
  `auth.lock` / `state.db` (1.8 GB) exist locally but are all excluded → **not in the backed-up
  tree** (post-push-verify leak check confirms NONE)

## Diff (3 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/references/skill-md-at-cap.md
```
Characterized each `M` against the **pre-push** remote HEAD `93d20c3dbbd9` with
`scripts/characterize-diff-vs-prev-head.py 93d20c3dbbd9`:
- `cron/jobs.json` — routine runtime churn (`completed` counters 5139→5187 and 108→109;
  `next_run_at` / `last_run_at` / `updated_at` → 2026-10-09).
- `memories/archive/ARCHIVE.md` — routine runtime churn (2026-10-08 Hindsight reflect +
  consolidation row).
- `hermes-profile-backup/references/skill-md-at-cap.md` — **benign carry-over lag**: the new
  "Status 2026-10-08: the size cap is NOT enforced by the generic `patch` tool" section, a
  10-08 post-push edit.

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local one
(17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **240**; remote HEAD `93d20c3dbbd9`, 259 blobs
- Preflight diff: `Modified: 3, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `93d20c3dbbd9` at preflight, then advanced to `46ee50cb3b58` (concurrent
  sibling **demo-dev** backup, 12:01:26Z) during the blob phase → attempt 1's ref PATCH died
  `HTTP 422 non-fast-forward` (3 blobs + subtree `be98e85cafe3` already uploaded) → absorbed by
  the budgeted **single plain re-run**, attempt 2 clean with the remote stable at `46ee50cb3b58`
  through commit time.
- No account flip, no network flakiness; the `mkdtemp` private-payload-dir fix held.
- 3 blobs uploaded, subtree `be98e85cafe36f8c7d13fc2f1a1d07dfcf3f3edd`, top tree
  `97ce550f2c65c127234956bd5622d644fad9e258`, commit + ref (attempt 2) in one clean pass.

## Post-push remote verification
- Remote HEAD `ac3230eec4ca`; total blobs **259**, `demo-pm` blobs = **240** (== local file
  count 240); by top dir: demo-pm 240, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1
  → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
  (16,835 chars / 17,021 bytes)
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-10-08` → `2026-10-09` +
`references/method-b-practice-notes.md` "Observed on recent runs" table row, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
