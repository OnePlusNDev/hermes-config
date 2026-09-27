# demo-pm backup run — 2026-09-27

## Result
**Method B (standalone subtree, no clone)** — success, **1 aborted attempt** (ref-PATCH 422 race).
Main commit: `fb85a2a00cbbb31c155e40a900838cd57c4c1e4c`
URL: https://github.com/OnePlusNDev/hermes-config/commit/fb85a2a00cbbb31c155e40a900838cd57c4c1e4c
Diff: **4 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNDev`** (repo owner) — **no switch needed**; `GITHUB_TOKEN` unset;
  `permissions.push = true` confirmed before any blob POST. 09-26's `zhangtbj` flip did **not** recur.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the
  only `key_env` occurrence is a comment (line 695); `password:` / `secret:` / `token:`
  all empty → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; GITHUB_USERNAME, GITHUB_EMAIL, GITHUB_TOKEN, GATEWAY_PORT, AGENT_NAME,
  AGENT_ROLE, DEEPSEEK_API_KEY, TERMINAL_ENV) excluded, never uploaded; no
  `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (4 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/demo-pm-github-api/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/SKILL.md
```
Characterized each `M` against the previous remote HEAD `b3d2005d4c11` (blob fetch + unified diff):
- `cron/jobs.json` — routine cron counters/timestamps (`completed` +48/+1/+1, `next_run_at`
  and `last_run_at` advanced to 2026-09-27, `updated_at` 2026-09-27T20:01:16+08:00). Pure runtime churn.
- `memories/archive/ARCHIVE.md` — routine hindsight reflect/consolidation cron row for **2026-09-26**
  (bank 48 nodes / 1228 links, op `6abdae47`, sessions >90d = 333, `auto_prune=false`).
- `skills/devops/demo-pm-github-api/SKILL.md` — the **09-26 post-push** doc edit (account-flip
  404 rule, "更狠的一次（2026-09-26 备份轮实测）").
- `skills/devops/hermes-profile-backup/SKILL.md` — the **09-26 post-push** doc edit
  ("A switch can be undone within a minute — by an account you have never seen.").
→ The last two are **benign carry-over lag**: written *after* the 09-26 follow-up push, so that
run's `Modified: 0, New: 0, Deleted: 0` closing assertion legitimately did not hold. Ordering,
not a lost commit.

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local
one (17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **226**; remote HEAD `8c5cb9e94229`, **245** blobs
- Preflight diff: `Modified: 4, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Attempt 1: remote HEAD `8c5cb9e94229` at Step 2 → 4 blobs uploaded (identical SHAs to
  attempt 2), subtree `bd929bdcb45a`, top tree `3d63a060697a`, commit `cbed7ca213d4`, then
  **`FATAL ref update: gh: Update is not a fast forward (HTTP 422)`** — a concurrent sibling
  backup advanced `main` during the ~1–2 min blob phase. Absorbed by the **budgeted single
  plain re-run** (no rebase, no tree surgery).
- Attempt 2: active account re-checked (still `OnePlusNDev`), remote HEAD `b3d2005d4c11`,
  **remote stable through commit time → the ref PATCH succeeded on the first try.**
- 4 blobs (idempotent — same SHAs), subtree `bd929bdcb45a` (identical), top tree `2bb3acd412c4`,
  commit + ref in one clean pass.
- No network flakiness; the 09-23 `mkdtemp` private-payload-dir fix held (no shared-`/tmp` deletion).
- No account flip this run (contrast 09-26's mid-run `zhangtbj` re-flip).

## Post-push remote verification
- Remote HEAD `fb85a2a00cbbb`; total blobs **245**, `demo-pm` blobs = **226** (== local file count 226);
  by top dir: demo-pm 226, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-09-26` → `2026-09-27` + a
`method-b-practice-notes.md` table row for this run's 422 race, pushed with the same
standalone-subtree script. Afterwards the preflight reports `Modified: 0, New: 0, Deleted: 0`.
