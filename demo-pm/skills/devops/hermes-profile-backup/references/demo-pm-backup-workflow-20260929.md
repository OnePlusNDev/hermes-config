# demo-pm backup run — 2026-09-29

## Result
**Method B (standalone subtree, no clone)** — success, **1 aborted attempt** (mid-run account flip → blob 404).
Main commit: `56920aa279254f6769ab6b2ddec4eaa25543511f`
URL: https://github.com/OnePlusNDev/hermes-config/commit/56920aa279254f6769ab6b2ddec4eaa25543511f
Diff: **5 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`zhangtbj`** (the fifth keyring account, `push=false` on the repo) —
  **`gh auth switch --user OnePlusNDev` REQUIRED** before any blob POST; post-switch
  `permissions.push = true` confirmed. `GITHUB_TOKEN` unset.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the
  only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; GITHUB_USERNAME, GITHUB_EMAIL, GITHUB_TOKEN, GATEWAY_PORT, AGENT_NAME,
  AGENT_ROLE, DEEPSEEK_API_KEY, TERMINAL_ENV) excluded, never uploaded; no
  `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (5 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/demo-pm-github-api/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/references/skill-md-at-cap.md
```
Characterized each `M` against the **pre-push** remote HEAD `cdcabbeb7545` with
`scripts/characterize-diff-vs-prev-head.py`:
- `cron/jobs.json` — routine cron counters/timestamps (`completed` +48/+1/+1, `next_run_at`
  and `last_run_at` advanced to 2026-09-29, `updated_at` 2026-09-29T20:01:27+08:00). Pure runtime churn.
- `memories/archive/ARCHIVE.md` — routine hindsight reflect/consolidation cron row for **2026-09-28**
  (bank 48 nodes / 1228 links, op `4fb36962`, sessions >90d = 433, `auto_prune=false`); also the
  header line 74 `记忆清理时间` advancing.
- `skills/devops/demo-pm-github-api/SKILL.md` — the **09-29** doc edit (filter-sanity lesson: a
  **zero-task account** is a stronger filter-validity probe than `OnePlusNBoss`, which is
  structurally identical to the full set at steady state).
- `skills/devops/hermes-profile-backup/SKILL.md` — the **09-28 post-push** doc edit (the
  `skill_view` truncation warning disambiguation: "read_file the on-disk SKILL.md, not the tmp dump").
- `references/skill-md-at-cap.md` — the **09-28 post-push** doc edit (status 99,964 chars +
  the new "Which file to `read_file`" trap section).
→ The last three are **benign carry-over lag**: written *after* the 09-28 follow-up push, so that
run's `Modified: 0, New: 0, Deleted: 0` closing assertion legitimately did not hold. Ordering,
not a lost commit.

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local
one (17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **230**; remote HEAD `8122b94d9407`, **249** blobs
- Preflight diff: `Modified: 5, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**
- Remote HEAD advanced `8122b94d9407` → `cdcabbeb7545` (concurrent sibling backup) before the
  script's Step 2 → absorbed silently by the script's re-read (diff unchanged: 5/0/0)

## Execution notes
- Attempt 1: pre-run check showed the active gh account had flipped back to **`zhangtbj`**
  (`push=false`) → blob POST died `FATAL uploading demo-pm/cron/jobs.json: gh: Not Found (HTTP 404)`.
  This is the documented "every blob-404 is an account flip" case, **not** a missing repo/rate limit.
- Attempt 2: `gh auth switch --user OnePlusNDev` again (`push=true`), plain re-run — blob SHAs are
  idempotent, so the re-run costs nothing. 5 blobs, subtree `eec00ef16904215ec4b4a9d1de8c62891fe81619`,
  top tree `07e133c7e8c655f41c0cfa50332d7eb175ffd9da`, commit + ref in one clean pass.
- **No ref-PATCH 422 race** this run (remote stable at `cdcabbeb7545` through commit time).
- No network flakiness; the 09-23 `mkdtemp` private-payload-dir fix held (no shared-`/tmp` deletion).

## Post-push remote verification
- Remote HEAD `56920aa27925`; total blobs **249**, `demo-pm` blobs = **230** (== local file count 230);
  by top dir: demo-pm 230, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
  (16,835 chars / 17,021 bytes)
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-09-28` → `2026-09-29`, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
