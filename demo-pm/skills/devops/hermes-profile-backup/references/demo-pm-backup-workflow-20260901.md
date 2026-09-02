# demo-pm Backup Workflow — 2026-09-01

**Result:** SUCCESS — clean Method B run (standalone subtree, no clone)

- **Method:** B (gh API Git Data API) — local clone at `~/.hermes/repos/hermes-config` was stale (ed4bcb8 vs remote a91acd40), so Method A would have diverged. Repo is 611 blobs → used `scripts/gh-api-standalone-subtree-backup.py` (no clone needed, recursive subtree avoids flat-tree 422).
- **Preflight:** CLEAN — 592 local files, 4 modified, 0 new, 0 deleted; no token patterns in upload candidates.
- **Security check:** config.yaml all 15 `api_key` values empty (`''`) — **no plaintext keys found, no `key_env` replacement needed**. Remote post-push grep for `sk-[A-Za-z0-9]{20,}` = 0.
- **Commit:** `0b65d1e2a4624679efe016679ec3d6b2c96f8e5c` (https://github.com/OnePlusNDev/hermes-config/commit/0b65d1e2)
- **Files changed (4, all M):**
  - `demo-pm/cron/jobs.json`
  - `demo-pm/memories/archive/ARCHIVE.md`
  - `demo-pm/skills/devops/hermes-profile-backup/SKILL.md`
  - `demo-pm/skills/devops/hermes-profile-diagnostics/references/memory-maintenance.md`
- **Auth:** active gh user = OnePlusNDev (repo owner, `push=true`); GITHUB_TOKEN unset; no account flip mid-run.
- **Post-push verification:**
  - Remote config.yaml plaintext-key count: 0
  - Sensitive-file tree grep (.env, auth.json/lock, state.db*, processes.json, home/, .local/, bin/tirith): NONE
  - Temp-script tree grep (pm_healthcheck, tmp_*.py, triage_*.py, get_token.sh, query_issues.py, cron_triage.py): NONE
  - Top-level distribution: .gitignore 1, demo-dev 5, demo-pm 592, demo-tester 8, tester-01 5 — siblings intact
