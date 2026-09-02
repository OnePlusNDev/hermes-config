# demo-pm Backup Workflow — 2026-09-02

**Result:** SUCCESS — clean Method B run (standalone subtree, no clone)

- **Method:** B (gh API Git Data API) — local clone at `~/.hermes/repos/hermes-config` was stale (ed4bcb8 vs remote 0b65d1e2), so Method A would have diverged. Repo is 611 blobs → used `scripts/gh-api-standalone-subtree-backup.py` (no clone needed, recursive subtree avoids flat-tree 422).
- **Preflight:** CLEAN — 594 local files, 3 modified, 2 new, 0 deleted; no token patterns in upload candidates.
- **Security check:** config.yaml all 15 `api_key` values empty (`''`) — **no plaintext keys found (incl. no `sk-` prefix), no `key_env` replacement needed**. Remote post-push grep for `sk-[A-Za-z0-9]{20,}` = 0.
- **Commit:** `ff785db0f42c343fc0140c206659730e0b8b90dc` (https://github.com/OnePlusNDev/hermes-config/commit/ff785db0)
- **Files changed (3 M + 2 A):**
  - `demo-pm/cron/jobs.json`
  - `demo-pm/memories/archive/ARCHIVE.md`
  - `demo-pm/skills/devops/hermes-profile-backup/SKILL.md`
  - `demo-pm/skills/devops/demo-pm-github-api/SKILL.md` (new)
  - `demo-pm/skills/devops/hermes-profile-backup/references/demo-pm-backup-workflow-20260901.md` (new — prior run's note, picked up this run)
- **Auth:** active gh user = OnePlusNDev (repo owner, `push=true`); GITHUB_TOKEN unset; no account flip mid-run.
- **Post-push verification:**
  - Remote config.yaml plaintext-key count: 0
  - Sensitive-file tree grep (.env, auth.json/lock, state.db*, processes.json, home/, .local/, bin/tirith): NONE
  - Temp-script tree grep (pm_health*, gh_health*, healthcheck_*, tmp_*.py, triage_*.py, query_issues.py, get_token.sh): NONE
  - Top-level distribution: .gitignore 1, demo-dev 5, demo-pm 594, demo-tester 8, tester-01 5 — siblings intact
