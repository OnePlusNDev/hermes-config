# demo-pm backup run — 2026-09-25

## Result
**Method B (standalone subtree, no clone)** — success, **FIRST-TRY** (no aborted attempts).
Main commit: `ef84bc3a8d85d7dadbb904029ffa095f30f57cb3`
URL: https://github.com/OnePlusNDev/hermes-config/commit/ef84bc3a8d85d7dadbb904029ffa095f30f57cb3
Diff: **3 M, 0 A, 187 D** — the 187 `D` are the curator's 2026-09-24 archive pass (see below).

## Curator archive churn (the headline of this run)
The 187 deletions are **intended mirroring**, not data loss and not an exclude gap:

- Curator ran **2026-09-24T23:12:25Z** (= 2026-09-25 07:12 local): `auto: 29 archived;
  llm: skipped (consolidation off)` — pure time-based staleness pass over **bundled** skills only.
- `.archive/` now holds **65 skills** (36 from the 2026-09-18 pass + 29 today).
- All 187 deleted paths have a matching copy under `skills/.archive/<name>/...` (verified
  programmatically: 187/187 twins present, 0 missing) and all 29 skill names classify as
  **bundled** against `skills/.bundled_manifest` (no agent-created content involved —
  curator's agent-created count stayed 9 → 9).
- The `.archive` / `.curator_suppressed` excludes already exist in both scripts + SKILL.md ×2 +
  gitignore template (added 2026-09-18), so no exclude patching was needed this run.
- Consequence: `demo-pm` blobs intentionally drop **410 → 223** on the remote tree. The old
  copies remain reachable in git history; bundled content is re-shippable with Hermes and is
  not user configuration. **Do NOT hand-restore the archived copies** (`hermes curator restore
  <name>` is the recovery path if ever needed).

## Pre-flight
- `gh api user` → `OnePlusNTester` initially (collaborator, read-only) → `gh auth switch --user
  OnePlusNDev` → `push=true` confirmed before any blob POST (would otherwise 404)
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the
  only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; GITHUB_USERNAME, GITHUB_EMAIL, GITHUB_TOKEN, GATEWAY_PORT, AGENT_NAME,
  AGENT_ROLE, DEEPSEEK_API_KEY, TERMINAL_ENV) excluded, never uploaded; no
  `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (3 M, 0 A, 187 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/references/method-b-practice-notes.md
D  demo-pm/skills/<...>  (187 files = 29 curator-archived bundled skills, see above)
```
`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local
one (17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **223**; remote HEAD `8219766f6796`, 429 blobs
- Preflight diff: `Modified: 3, New: 0, Deleted: 187` — **no new exclude gaps**
  (all `D` under `demo-pm/skills/`; verified `grep '^  D  ' | grep -v demo-pm/skills/` = 0)
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `8219766f6796` at preflight and advanced to `b097fa167abb` (a concurrent
  sibling backup) **before** the script's own Step 2 — the script re-read the ref, so this was
  absorbed silently (harmless; the diff was merely recomputed against the newer HEAD).
- **No ref-PATCH 422 race:** remote was stable at `b097fa167abb` through the blob phase, and
  the ref PATCH succeeded on the **first** attempt.
- No network flakiness, no shared-`/tmp` payload deletion (the 09-23 `mkdtemp` fix held).
- 3 blobs uploaded, subtree `64dcfda742f0`, top tree `60c188afdfc9`, commit + ref in one clean pass.

## Post-push remote verification
- Remote HEAD `ef84bc3a8d85`; total blobs **242**, `demo-pm` blobs = **223** (== local file count 223);
  by top dir: demo-pm 223, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-09-24` → `2026-09-25`, pushed with the
same standalone-subtree script (`0772c0c338cf`), plus a small third commit adding a **Recurrence log**
to `references/curator-archive-churn-triage.md` (the capped SKILL.md at 99,137/100,000 chars is not
the place for it). Afterwards the preflight reports `Modified: 0, New: 0, Deleted: 0`.
