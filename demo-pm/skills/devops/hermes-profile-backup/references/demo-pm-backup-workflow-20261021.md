# demo-pm backup run — 2026-10-21

## Result
**Method B (standalone subtree, no clone)** — 1 aborted attempt (ref-PATCH 422 non-fast-forward), success on the plain re-run.
Main commit: `8d647b384994f7d870640a3f2e150c0906accbd8`
URL: https://github.com/OnePlusNDev/hermes-config/commit/8d647b384994f7d870640a3f2e150c0906accbd8
Diff: **4 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → `OnePlusNDev` (repo owner, `push=true`) — no switch needed; `GITHUB_TOKEN` unset
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the
  only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; GITHUB_USERNAME, GITHUB_EMAIL, GITHUB_TOKEN, GATEWAY_PORT, AGENT_NAME,
  AGENT_ROLE, DEEPSEEK_API_KEY, TERMINAL_ENV) excluded, never uploaded; no
  `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (4 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/templates/run-note-template.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
```
Characterized against PRE_PUSH HEAD `e2edf5ebcbf3` with
`scripts/characterize-diff-vs-prev-head.py`: `cron/jobs.json` is routine runtime churn
(`completed` 5715→5763 and 120→121 ×2, `next_run_at`/`last_run_at` advanced one day) and
`memories/archive/ARCHIVE.md` is the 2026-10-20 Hindsight reflect/consolidation row (routine
memory-archive churn). The two skill docs are **benign carry-over lag** — the 10-20 session's
`run-note-template.md` anchor warning and the `cleanup-run-endpoints-and-counts.md`
96 K/407 K token-band update were written after that day's follow-up push.
`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local
one (16835 chars / 17021 bytes — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **255**; remote HEAD `68d5da9921bc`, 274 blobs
- Preflight diff: `Modified: 4, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Preflight saw remote HEAD `68d5da9921bc`; between the blob phase and the ref PATCH a
  concurrent **demo-dev** backup landed (`e2edf5ebcbf3`, 12:00:55Z), so the first attempt's
  commit `e69fffb3c243` was rejected with `Update is not a fast forward (HTTP 422)`.
  Per the budget-exactly-one-plain-re-run rule, the script was re-run unchanged: it re-read
  HEAD as `e2edf5ebcbf3`, re-uploaded the same 4 blobs (idempotent), and pushed cleanly.
- 4 blobs uploaded, subtree `33b26569c7d2ca35fe711e1599248202f885007d`, top tree
  `2d376ba62d62841742ce25dd8ef4222df7947a78`, commit + ref in one pass. No network flakiness.

## Post-push remote verification
- Remote HEAD `8d647b384994`; total blobs **274**, `demo-pm` blobs = **255** (== local file count 255);
  by top dir: demo-pm 255, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-10-20` → `2026-10-21` +
`references/method-b-practice-notes.md` "Observed on recent runs" table row, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
