# Demo-PM Backup Workflow — 2026-08-31

## Outcome
- Clean backup via Method B (`scripts/gh-api-standalone-subtree-backup.py`), REPO_OWNER=OnePlusNDev.
- Commit `a1a6cd1a` (`backup: demo-pm 2026-08-31`): 5 M + 1 A + 0 D.
- Post-push verification: remote config.yaml plaintext api_key count 0; no .env/auth.json/state.db/temp diagnostics in remote tree; demo-pm 591 blobs; siblings intact (demo-dev 5, demo-tester 8, tester-01 5, total 610).

## Security gate: config.yaml check
- No plaintext api_key found: all 15 `api_key:` values are empty `''`, no `sk-` matches, `secret: ''` empty → no key_env replacement needed.

## Method selection
- gh active user was OnePlusNTester at start (not repo owner, push=false) → `gh auth switch --user OnePlusNDev` → active OnePlusNDev, push=true. GITHUB_TOKEN unset in cron env (no env override issue).
- Local clone `~/.hermes/repos/hermes-config` STALE (ed4bcb8 vs remote 2bb2b656) → Method B (gh API subtree push) used; clone not needed. curl github 000 (curl blocked) but gh API transport fine.

## Preflight
- `scripts/preflight-backup-scan.py`: 5 M + 1 A + 0 D, token scan CLEAN on all upload candidates (cron/jobs.json, memories/archive/ARCHIVE.md, backup skill SKILL.md, memory-maintenance.md, pm-triage-cron SKILL.md, 1 new reference doc). No exclude gaps, no redaction needed.

## Files in this commit
- M demo-pm/cron/jobs.json, M demo-pm/memories/archive/ARCHIVE.md,
  M demo-pm/skills/devops/hermes-profile-backup/SKILL.md,
  M demo-pm/skills/devops/hermes-profile-diagnostics/references/memory-maintenance.md,
  M demo-pm/skills/devops/pm-triage-cron/SKILL.md,
  A demo-pm/skills/devops/pm-triage-cron/references/2026-08-31-session-user-401-transient-crosscheck.md
