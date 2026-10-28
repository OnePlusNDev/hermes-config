# demo-pm backup run — 2026-10-28

## Result
**Method B (standalone subtree, no clone)** — **first-try, 0 aborted attempts**.
Main commit: `b31530b218532c34c6ca6c2916587073e2e9c7ae`
URL: https://github.com/OnePlusNDev/hermes-config/commit/b31530b218532c34c6ca6c2916587073e2e9c7ae
Diff: **6 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNDev`** with `permissions.push=true` — **no switch needed**
  (`GITHUB_TOKEN` unset throughout); no mid-run flip (contrast 10-27's blob 404).
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
M  demo-pm/skills/devops/hermes-profile-backup/templates/run-note-template.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
```
Characterized against PRE_PUSH HEAD `7e5dec0b7450` (`characterize-diff-vs-prev-head.py`,
one run, exit 0 — no-arg default derived `parents[0]` of then-current main `443b060192ac`,
which **was** the true pre-push HEAD here only because the intervening commit was a
sibling profile, not our own follow-up). It reported **6 M / 0 A / 0 D**, matching
preflight exactly.

- **Routine runtime churn (2):** `cron/jobs.json` — task-polling `completed`
  6051→6098, memory-cleanup and config-backup counters 127→128, `next_run_at`
  10-27→10-28 / 10-28→10-29, `last_run_at` per job, `updated_at`
  2026-10-27T20:01:30 → 2026-10-28T20:00:57; `memories/archive/ARCHIVE.md` — new
  2026-10-27 Hindsight reflect+consolidation row (MEMORY.md 28.0d / USER.md 16.0d,
  neither past the 30d window; consolidation op `completed` in +536 ms, counter
  86→87; **first single-pass no-crash reflect in several days**, primary
  161,682/10,170 → disambiguation 166,107/6,698 → verdict "no content-level expired
  facts"; new scope clarification: deepseek-v4-pro = tester-01 chat model vs
  z.ai GLM = Hindsight daemon key are different scopes, not conflicting).
- **Benign carry-over lag, authored after the 10-27 follow-up push (4):**
  `method-b-practice-notes.md` (new "mirror case: `permissions.push=true` on the WRONG
  account" section + "always pass the SHA to the characterize probe" guidance),
  `templates/run-note-template.md` (expected follow-up shape `3 M / 1 A / 0 D`),
  diagnostics `SKILL.md` (pointer now lists the wording-gate false-positive catalogue +
  mental-model/directive scope check), `references/cleanup-run-endpoints-and-counts.md`
  (10-27 token row, 8th wording-gate shape, "advanced organization" scope check).

`config.yaml` deliberately NOT in the diff: the remote blob already equalled the local
one (16,835 chars / 17,021 bytes — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **266**; remote HEAD `443b060192ac`, 285 blobs
- Preflight diff: `Modified: 6, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- First preflight read remote HEAD `7e5dec0b7450`; a sibling **demo-dev** backup
  (`443b060192ac`, 2026-10-28T12:01:40Z) landed immediately after. The re-run preflight
  and the script's Step 2 both read **`443b060192ac`**, which stayed stable through
  commit time → **no ref-PATCH 422 race**; ref PATCH succeeded first attempt.
- 6 blobs uploaded (`cron/jobs.json` `d67fbe3a8ce1`, `ARCHIVE.md` `ea20335cd6aa`,
  `method-b-practice-notes.md` `0ac7a84ec2af`, `run-note-template.md` `c11a87f3d14a`,
  diagnostics `SKILL.md` `aedc6f62a4c1`,
  `cleanup-run-endpoints-and-counts.md` `ba1abfd09f96`), subtree
  `af93e4d149136c5077e40f653808e9060121a96c`, top tree
  `164404d5c7e6ad794bef712cfc51e305c3911818`, commit + ref in one clean pass.

## Post-push remote verification
- Remote HEAD `b31530b21853`; total blobs **285**, `demo-pm` blobs = **266**
  (== local file count 266); by top dir: demo-pm 266, demo-dev 5, demo-tester 8,
  tester-01 5, .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15,
  non-empty = **0**
- Sensitive-path / temp-diagnostic leak checks → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
All FOUR items: run note + `references/dated-runs-index.md` bullet + SKILL.md `latest:`
`2026-10-27` → `2026-10-28` (same-length in-place swap; SKILL.md is at its 100 K cap) +
the `method-b-practice-notes.md` table row. Pushed with the same standalone-subtree
script; the closing preflight re-run must report `Modified: 0, New: 0, Deleted: 0`.
