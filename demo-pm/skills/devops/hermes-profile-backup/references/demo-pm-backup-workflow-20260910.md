# Backup Run 2026-09-10 (demo-pm)

Clean Method B run (standalone-subtree, no clone attempt — repo 624 blobs,
git/libcurl transport unreliable in cron mode).

- Main commit: 952f040a52d94645a230580c5c5f3730976d1b08 (4M+0A+0D)
  - demo-pm/cron/jobs.json
  - demo-pm/memories/archive/ARCHIVE.md
  - demo-pm/skills/devops/hermes-profile-backup/SKILL.md
  - demo-pm/skills/devops/pm-triage-cron/SKILL.md
- No ref PATCH 422 this run — remote HEAD stable at 1fe53ad11573 through
  commit time (preflight and script both read the same HEAD). Siblings intact.
- config.yaml: all 15 api_key entries empty (`''`) — no plaintext `sk-` keys,
  no key_env replacement needed. `.env` excluded.
- Preflight: CLEAN (no token patterns in upload candidates; 0 new files).
- Post-push verification: remote config.yaml 0 plaintext keys (grep -c = 0);
  0 sensitive files (`.env`, auth.json, auth.lock, state.db, processes.json,
  bin/tirith, .local/, home/ all absent); 0 temp/diagnostic scripts
  (pm_healthcheck, tmp_*.py, triage_*.py, get_token.sh, query_issues.py,
  __pycache__ all absent); demo-pm 605 blobs; siblings intact (demo-dev 5,
  demo-tester 8, tester-01 5, .gitignore 1); gh user OnePlusNDev owner
  throughout (push=true confirmed pre-flight); remote HEAD == 952f040a52d9
  confirmed post-push.
