# Method A — canonical rsync exclude set (extracted from SKILL.md 2026-09-23)

Extracted verbatim from SKILL.md to free space for the `latest:` pointer bump
(SKILL.md was 100,665 chars vs the 100,000 limit; the patch tool validates the
*resulting* size, so the stale pointer could not be bumped until ~700 chars were
freed). Method A is the rarely-used path (git clone has timed out in cron mode
since ~2026-08-29), and this list is already mirrored in three other places:

- `templates/gitignore-template.txt` (repo-level, `**/`-prefixed)
- `scripts/gh-api-standalone-subtree-backup.py` → `EXCLUDE_NAMES` / `EXCLUDE_DIRS` /
  `EXCLUDE_PREFIX` / `CRON_EXCLUDE`
- `scripts/preflight-backup-scan.py` → same sets

If you change one, change all four.

## Counts (as of 2026-09-23)

Local files after excludes: **407**. Remote `demo-pm` blobs: **407** (they must match).

## Full command

```bash
cd /tmp
gh repo clone <owner>/<repo> /tmp/backup
rsync -a --delete \
  --exclude '.env' \
  --exclude 'auth.json' \
  --exclude 'auth.lock' \
  --exclude 'state.db*' \
  --exclude 'logs/' \
  --exclude 'cache/' \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude 'sessions/' \
  --exclude 'desktop/' \
  --exclude 'sandboxes/' \
  --exclude '*.bak*' \
  --exclude '.hermes_history' \
  --exclude 'interrupt_debug.log' \
  --exclude 'gateway.*' \
  --exclude 'gateway.lock' \
  --exclude 'gateway.pid' \
  --exclude 'gateway_state.json' \
  --exclude 'skills/.usage.json*' \
  --exclude 'skills/.hub/' \
  --exclude 'skills/.curator_backups/' \
  --exclude 'skills/.curator_state' \
  --exclude 'skills/.bundled_manifest' \
  --exclude 'cron/output/' \
  --exclude 'cron/.jobs.lock' \
  --exclude 'cron/.tick.lock' \
  --exclude 'cron/ticker_heartbeat' \
  --exclude 'cron/ticker_last_success' \
  --exclude 'models_dev_cache.json' \
  --exclude 'ollama_cloud_models_cache.json' \
  --exclude 'provider_models_cache.json' \
  --exclude 'home/' \
  --exclude 'lsp/' \
  --exclude '.local/' \
  --exclude '.skills_prompt_snapshot.json' \
  --exclude '.update_check' \
  --exclude 'bin/tirith' \
  --exclude 'processes.json' \
  --exclude 'hindsight-maintenance-logs/' \
  --exclude 'audio_cache/' \
  --exclude 'image_cache/' \
  --exclude 'pairing/' \
  --exclude 'plans/' \
  --exclude 'hooks/' \
  --exclude 'skins/' \
  --exclude 'workspace/' \
  --exclude 'triage_issues.py' \
  --exclude 'cron_triage.py' \
  --exclude 'triage_check.py' \
  --exclude 'triage_fetch.py' \
  --exclude 'triage_v5.py' \
  --exclude 'query_issues.py' \
  --exclude 'triage_verify.py' \
  --exclude 'get_token.sh' \
  --exclude 'pm_triage_*.py' \
  --exclude '.tmp_*' \
  --exclude 'tmp_*.py' \
  --exclude 'pm_health*' \
  --exclude 'gh_health*' \
  --exclude 'healthcheck_*.py' \
  --exclude '/health_*' \
  --exclude 'tmp_triage/' \
  --exclude '/tmp/' \
  --exclude '/tmp_pm/' \
  --exclude '._*' \
  --exclude 'memory_backup_*.json' \
  --exclude 'feishu_seen_message_ids.json' \
  --exclude 'response_store.db' \
  ~/.hermes/profiles/<profile>/ /tmp/backup/<profile>/
cd /tmp/backup

# 🔒 PRE-COMMIT PUSH-PROTECTION SCAN — scan ALL modified/new files for token patterns
# Run scripts/method-a-precommit-scan.sh. The local profile's skill reference docs
# may contain full unredacted tokens that rsync imported — scan and redact BEFORE
# staging.
echo "=== Scan complete ==="

# First-time setup: repo-level .gitignore with **/ prefix for subdirectory patterns
if [ ! -f .gitignore ]; then
  cp ~/.hermes/profiles/demo-pm/skills/devops/hermes-profile-backup/templates/gitignore-template.txt .gitignore
  git add .gitignore
  echo "Created .gitignore"
fi
# Always check for leaked files before committing
find . -name '*.json' -not -path '*/node_modules/*' | head -10
find . -name '*.lock' | head -10
git add -A && git commit -m "backup: <profile> $(date +%Y-%m-%d)"
git push
```

## Known redundancies (keep for safety, they cost nothing)

`--exclude 'gateway.*'` already covers the following three `gateway.lock`,
`gateway.pid`, `gateway_state.json` lines. Both forms are kept so the list stays
trivially greppable against the scripts' `EXCLUDE_NAMES` set.

## Reminder — a local clone that EXISTS is not enough

`git status` compares against the local `origin/main` ref, which can itself be
stale. Verify `git rev-parse HEAD` against
`gh api repos/<owner>/<repo>/git/refs/heads/main --jq '.object.sha'` before
trusting a Method A push; if the clone is behind, a push would diverge — use
Method B instead.
