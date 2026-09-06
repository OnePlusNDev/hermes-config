# Backup Run 2026-09-06 (demo-pm)

Clean Method B run (standalone-subtree, no clone attempt — repo 600+ blobs,
git/libcurl transport unreliable in cron mode).

- Main commit: 218dd62c62ee7b9652d4d09f904b9cf548e4c996 (4M+0A+0D)
  - demo-pm/cron/jobs.json
  - demo-pm/memories/archive/ARCHIVE.md
  - demo-pm/skills/devops/hermes-profile-backup/SKILL.md
  - demo-pm/skills/devops/pm-triage-cron/scripts/crosscheck.py
- First ref PATCH attempt hit HTTP 422 "Update is not a fast forward" — remote
  HEAD advanced b818451d → 628d35e9 mid-run (concurrent demo-dev/other push).
  Re-ran script: it re-read remote HEAD, blob uploads idempotent, second attempt
  pushed cleanly onto current HEAD. No manual tree surgery needed.
- config.yaml: all api_key entries empty (`''`) — no plaintext `sk-` keys, no
  key_env replacement needed. `.env` excluded.
- Preflight: CLEAN (no token patterns in upload candidates).
- Post-push verification: remote config.yaml 0 plaintext keys; 0 sensitive
  files (`.env`, auth.json, auth.lock, state.db absent); demo-pm 601 blobs;
  siblings intact (demo-dev 5, demo-tester 8, tester-01 5); gh user
  OnePlusNDev owner throughout (push=true confirmed pre-flight).
