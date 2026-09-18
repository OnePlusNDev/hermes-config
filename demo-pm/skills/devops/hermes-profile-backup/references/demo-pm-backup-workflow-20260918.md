# demo-pm backup run — 2026-09-18

## Result
**Method B (standalone subtree, no clone)** — success, FIRST-TRY, no aborted attempts.
Main commit: `6c27442ca0c29870de931536101cbe9d5fc4bdcf`
URL: https://github.com/OnePlusNDev/hermes-config/commit/6c27442ca0c29870de931536101cbe9d5fc4bdcf
Diff: **10 M, 0 A, 232 D** (the 232 deletions are all the curator-archived bundled skills — see below).

## Pre-flight
- `gh api user` → `OnePlusNDev` (repo owner; `permissions.push` = **true**, `admin` = true) — no switch needed
- `env | grep -E '^(GH|GITHUB)'` → only `GITHUB_EMAIL`, `GITHUB_USERNAME`
  → **no `GITHUB_TOKEN` / `GH_TOKEN`** in the cron env, so no auth-override risk
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9_-]{16,}` → **0** matches;
  all **15** `api_key:` lines are `''`; 1 × `key_env` reference; no other
  `token|secret|password` values → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; GITHUB_*, DEEPSEEK_API_KEY) excluded, never uploaded; no
  `auth.json` / `auth.lock` / `state.db*` in tree

## NEW exclude gap found + fixed (the headline of this run)
The **first** preflight reported `Modified: 5, New: 233, Deleted: 232` — 233 files under
`demo-pm/skills/.archive/` and the matching 232 deletions from the old active paths.

Cause: the curator's time-based staleness pass (run `2026-09-17T22:51:52Z`, i.e. 09-18 06:51 local,
`"auto: 36 archived; llm: skipped (consolidation off)"`) archived **36 bundled skills / 232 files /
2.7 MB** into `skills/.archive/`, and wrote the new `skills/.curator_suppressed` list.

Decision: **exclude both**, consistent with the existing `.curator_backups/` policy — they are
curator-managed archives of **bundled** content (all 36 names verified present in
`skills/.bundled_manifest`; restorable via `hermes curator restore <name>`), not user configuration.
Uploading 2.7 MB of bundled-skill duplicates into a config-backup repo buys nothing.

Patches applied (kept in sync per the SKILL.md rule):
- `scripts/preflight-backup-scan.py`, `scripts/gh-api-standalone-subtree-backup.py`,
  `scripts/gh-api-standalone-backup.py` — `EXCLUDE_DIRS += ".archive"`,
  `EXCLUDE_NAMES += ".curator_suppressed"`
- `SKILL.md` — both exclude-doc bullets + the gitignore-sync list
- `templates/gitignore-template.txt` — `**/skills/.archive/`, `**/skills/.curator_suppressed`

Re-run of the preflight: `Modified: 10, New: 0, Deleted: 232`, local files 629 → **396**, token scan
**CLEAN**. All 232 D entries are under `demo-pm/skills/` (verified: 0 outside it).

⚠️ Consequence: the repo's `demo-pm` blob count drops **627 → 396** in this commit. That is
intended mirroring of the local profile (bundled content is re-shipped with Hermes and stays
reachable in git history) — not data loss of user config. Do NOT hand-restore the archived copies.

## Diff (10 M, 0 A, 232 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/references/dated-runs-index.md
M  demo-pm/skills/devops/hermes-profile-backup/scripts/gh-api-standalone-backup.py
M  demo-pm/skills/devops/hermes-profile-backup/scripts/gh-api-standalone-subtree-backup.py
M  demo-pm/skills/devops/hermes-profile-backup/scripts/post-push-verify.py
M  demo-pm/skills/devops/hermes-profile-backup/scripts/preflight-backup-scan.py
M  demo-pm/skills/devops/hermes-profile-backup/templates/gitignore-template.txt
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/memory-maintenance.md
D  demo-pm/skills/**  (232 files — 36 curator-archived bundled skills)
```
`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local one.

## Execution notes
- Remote HEAD was `c1f8fb153c99` at start and **stayed there through commit time** → **no ref-PATCH
  422 race**; the ref PATCH succeeded on the first attempt (third such run, after 09-13 / 09-16 / 09-17).
- **No network flakiness** — 10 blobs uploaded, subtree `1d7f2623674e`, top tree `2d5b629d2582`,
  commit + ref in one clean pass.
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution (the 09-16
  `jq=".content"` fix continues to hold).

## Post-push remote verification
- Remote HEAD `6c27442ca0c2`; total blobs **415**, `demo-pm` blobs = **396** (== local file count 396);
  by top dir: demo-pm 396, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
  (`16835` chars vs `17021` bytes — the usual CJK-comment discrepancy)
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `skills/.archive/` and `skills/.curator_suppressed` → **absent** from the remote tree (excluded as designed)

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-09-17` → `2026-09-18`, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
