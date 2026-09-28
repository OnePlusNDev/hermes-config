# demo-pm backup run — 2026-09-28

## Result
**Method B (standalone subtree, no clone)** — success, **1 aborted attempt** (ref-PATCH 422 race).
Main commit: `2651f23b19427cc6093c6c452fe14464db0bde6c`
URL: https://github.com/OnePlusNDev/hermes-config/commit/2651f23b19427cc6093c6c452fe14464db0bde6c
Diff: **7 M, 2 A, 0 D**.

## Pre-flight
- `gh api user` → **`zhangtbj`** (fifth keyring account, `push=false` on the repo) —
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

## Diff (7 M, 2 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/references/method-b-practice-notes.md
M  demo-pm/skills/devops/hermes-profile-backup/references/skill-md-at-cap.md
M  demo-pm/skills/devops/hermes-profile-backup/templates/run-note-template.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/memory-maintenance.md
A  demo-pm/skills/devops/hermes-profile-backup/references/run-note-diff-characterization.md
A  demo-pm/skills/devops/hermes-profile-backup/scripts/characterize-diff-vs-prev-head.py
```
Characterized each `M` against the **pre-push** remote HEAD `c8a48bb08efa` with
`scripts/characterize-diff-vs-prev-head.py`:
- `cron/jobs.json` — routine cron counters/timestamps (`completed` +48/+1/+1, `next_run_at`
  and `last_run_at` advanced to 2026-09-28, `updated_at` 2026-09-28T20:00:41+08:00). Pure runtime churn.
- `memories/archive/ARCHIVE.md` — routine hindsight reflect/consolidation cron row for **2026-09-27**
  (bank 48 nodes / 1228 links, op `59c2633b`, sessions >90d = 381, `auto_prune=false`); also the
  header `记忆清理时间` 2026-09-13 → 2026-09-27.
- `skills/devops/hermes-profile-backup/SKILL.md` — the **09-27 post-push** doc edit (extended the
  "Post-push probe:" line to point at the new `scripts/characterize-diff-vs-prev-head.py`).
- `references/method-b-practice-notes.md` — the **09-27 post-push** doc edit (new "Characterizing
  the M set for the run note" section).
- `references/skill-md-at-cap.md` — the **09-27 post-push** doc edit (status 99,898 → 99,966 chars,
  plus the duplicated push-protection-table slim note).
- `templates/run-note-template.md` — the **09-27 post-push** doc edit (characterize instruction added).
- `hermes-profile-diagnostics/references/memory-maintenance.md` — the **09-27 post-push** doc edit
  (second benign patch warning: paginated-read reminder).
→ The last five are **benign carry-over lag**: written *after* the 09-27 follow-up push, so that
run's `Modified: 0, New: 0, Deleted: 0` closing assertion legitimately did not hold. Ordering,
not a lost commit. The 2 `A` files are the same 09-27 post-push additions
(`references/run-note-diff-characterization.md`, `scripts/characterize-diff-vs-prev-head.py`).

`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local
one (17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **229**; remote HEAD `c8a48bb08efa`, **246** blobs
- Preflight diff: `Modified: 7, New: 2, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Attempt 1: remote HEAD `c8a48bb08efa` at Step 2 → 9 blobs uploaded, subtree
  `7652d181b1d81b1f51640dcef0a6b7d8410a7b02`, top tree `0b8d8f404252414d4f00214159dd8aa55dcdaeef`,
  commit `987878eadd5901bbc0e3f8b9420ec0fde031a6d2`, then **`FATAL ref update: gh: Update is not a
  fast forward (HTTP 422)`** — a concurrent sibling backup advanced `main` (`c8a48bb0` → `77e69333`)
  during the ~1–2 min blob phase. Absorbed by the **budgeted single plain re-run** (no rebase,
  no tree surgery).
- Attempt 2: active account re-checked (still `OnePlusNDev`, `push=true`), remote HEAD
  `77e69333f412`, **remote stable through commit time → the ref PATCH succeeded on the first try.**
- 9 blobs (idempotent — same SHAs), subtree `7652d181b1d8` (identical), top tree `4f38f96e16d2`,
  commit + ref in one clean pass.
- No account flip mid-run (contrast 09-26's `zhangtbj` re-flip; the pre-flight switch held).
- No network flakiness; the 09-23 `mkdtemp` private-payload-dir fix held (no shared-`/tmp` deletion).

## Post-push remote verification
- Remote HEAD `2651f23b1942`; total blobs **248**, `demo-pm` blobs = **229** (== local file count 229);
  by top dir: demo-pm 229, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-09-27` → `2026-09-28` + a
`method-b-practice-notes.md` table row for this run's 422 race, pushed with the same
standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
