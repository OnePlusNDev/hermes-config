# Demo-PM Backup Workflow — 2026-08-30

## Outcome
- Clean backup via Method B (`scripts/gh-api-standalone-subtree-backup.py`), REPO_OWNER=OnePlusNDev.
- Commit `daab0134` (`backup: demo-pm 2026-08-30`): 4 M + 3 A + 0 D.
- Post-push verification: remote config.yaml plaintext api_key count 0; no .env/auth.json/state.db/temp diagnostics in remote tree; demo-pm 589 blobs; siblings intact (demo-dev 5, demo-tester 8, tester-01 5, total 608).

## Security gate: config.yaml check
- No plaintext api_key found: all 15 `api_key:` values are empty `''`, no `sk-` matches, `secret: ''` empty → no key_env replacement needed.

## Method selection
- gh active user OnePlusNDev (repo owner). Local clone `~/.hermes/repos/hermes-config` STALE (ed4bcb8 vs remote de35d97) → Method B (gh API subtree push) used; clone not needed.

## Preflight
- `scripts/preflight-backup-scan.py`: 4 M + 3 A + 0 D, token scan CLEAN on all upload candidates (cron/jobs.json, memories/archive/ARCHIVE.md, backup skill SKILL.md + preflight script, 3 new skill files). No exclude gaps, no redaction needed.

## Files in this commit
- M demo-pm/cron/jobs.json, M demo-pm/memories/archive/ARCHIVE.md,
  M demo-pm/skills/devops/hermes-profile-backup/SKILL.md,
  M demo-pm/skills/devops/hermes-profile-backup/scripts/preflight-backup-scan.py,
  A demo-pm/skills/devops/hermes-profile-backup/references/demo-pm-backup-workflow-20260829.md,
  A demo-pm/skills/devops/hermes-profile-backup/scripts/method-a-precommit-scan.sh,
  A demo-pm/skills/devops/hermes-profile-backup/templates/gitignore-template.txt
