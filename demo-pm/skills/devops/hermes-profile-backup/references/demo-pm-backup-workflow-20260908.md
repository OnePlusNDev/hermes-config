# Backup Run 2026-09-08 (demo-pm)

Clean Method B run (standalone-subtree, no clone attempt — repo 600+ blobs,
git/libcurl transport unreliable in cron mode).

- Main commit: 144c76703f23e9ef3dd9d35aa928c6c791ad5e01 (4M+0A+0D)
  - demo-pm/cron/jobs.json
  - demo-pm/memories/archive/ARCHIVE.md
  - demo-pm/skills/devops/hermes-profile-backup/SKILL.md
  - demo-pm/skills/devops/hermes-profile-diagnostics/references/memory-maintenance.md
- config.yaml: all api_key entries empty (`''`) — no plaintext `sk-` keys, no
  key_env replacement needed. `.env` excluded.
- Preflight: CLEAN (no token patterns in upload candidates; 0 new files).
- No ref PATCH 422 this run — remote HEAD 50c80167 was still current at commit
  time (no concurrent advance mid-run).
- Post-push verification: remote config.yaml 0 plaintext keys (grep -c = 0, all
  api_key empty); 0 sensitive files (`.env`, auth.json, auth.lock, state.db
  absent); demo-pm 603 blobs; siblings intact (demo-dev 5, demo-tester 8,
  tester-01 5); gh user OnePlusNDev owner throughout (push=true confirmed
  pre-flight); remote HEAD == 144c76703f confirmed post-push.
