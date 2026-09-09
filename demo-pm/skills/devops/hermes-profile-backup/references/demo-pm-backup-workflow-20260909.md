# Backup Run 2026-09-09 (demo-pm)

Clean Method B run (standalone-subtree, no clone attempt — repo 600+ blobs,
git/libcurl transport unreliable in cron mode).

- Main commit: 883b04a35a12da5601dc71b47002811b4838b5bf (4M+0A+0D)
  - demo-pm/cron/jobs.json
  - demo-pm/memories/archive/ARCHIVE.md
  - demo-pm/skills/devops/hermes-profile-diagnostics/references/memory-maintenance.md
  - demo-pm/skills/devops/pm-triage-cron/references/2026-09-03-session-script-plus-list-endpoint-crosscheck.md
- First ref PATCH attempt hit HTTP 422 "Update is not a fast forward" — remote
  HEAD advanced mid-run (b84f2e3da4 → b6f829eb74, concurrent push). Re-ran
  script: it re-read remote HEAD, blob uploads idempotent, second attempt
  pushed cleanly onto current HEAD (883b04a35a12). No manual tree surgery.
- config.yaml: all 15 api_key entries empty (`''`) — no plaintext `sk-` keys,
  no key_env replacement needed. `.env` excluded.
- Preflight: CLEAN (no token patterns in upload candidates; 0 new files).
- Post-push verification: remote config.yaml 0 plaintext keys (grep -c = 0);
  0 sensitive files (`.env`, auth.json, auth.lock, state.db absent); demo-pm
  604 blobs; siblings intact (demo-dev 5, demo-tester 8, tester-01 5,
  .gitignore 1); gh user OnePlusNDev owner throughout (push=true confirmed
  pre-flight); remote HEAD == 883b04a35a12 confirmed post-push.
