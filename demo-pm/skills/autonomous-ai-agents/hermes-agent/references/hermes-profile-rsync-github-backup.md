# rsync + git Backup to GitHub

When `gh` CLI auth is available (`gh auth status` shows logged-in with `repo` scope), use `rsync` + `git` + `git push` instead of the REST-based script. Simpler, fewer failure modes in cron mode.

## Approach

```bash
# 1. Clone target repo
cd /tmp && git clone https://github.com/{owner}/hermes-config.git hermes-config-{profile}

# 2. Create .gitignore BEFORE rsync to skip sensitive files
cat > .gitignore << 'EOT'
**/.env **/.env.* auth.json gateway_state.json pairing/ *.pem *.key
*.db *.db-shm *.db-wal *_dev_cache.json
gateway.lock gateway.pid .tick.lock **/logs/
skills/.hub/ skills/.bundled_manifest skills/.usage.json* skills/.curator_state
models_dev_cache.json cron/output/ state.db* sessions.json* models_dev_cache.json
EOT

# 3. Core config files worth backing up (what to keep, not back up everything):
#    - config.yaml        : main profile configuration
#    - SOUL.md            : profile personality / persona definition
#    - RULES.md           : project-specific rules
#    - .skills_prompt_snapshot.json : active skills loaded into session prompt
#    - cron/jobs.json     : scheduled job definitions
#    - memories/MEMORY.md : persistent cross-session memory
#    - memories/USER.md   : user profile memory

# 3. Write README.md with backup metadata

# 4. rsync with exclusion filters (do NOT use rm -rf — it triggers tirith:mass_file_deletion)
rsync -a \
  --exclude='.env' --exclude='auth.json' --exclude='gateway_state.json' \
  --exclude='pairing/*' --exclude='*.pem' --exclude='*.key' \
  --exclude='*.db*' --exclude='*_dev_cache.json' \
  --exclude='skills/.hub/*' --exclude='skills/.curator_state' \
  /Users/oneplusn/.hermes/profiles/{profile}/ /tmp/hermes-config-{profile}/{profile}/

# 5. git add, commit, push
cd /tmp/hermes-config-{profile}
git config user.name "OnePlusNPM"
git config user.email "oneplusn@users.noreply.github.com"
git add -A
git commit -m "backup: {profile} profile — $(date +%Y-%m-%d)"
git push origin main
```

## Pre-flight checks

1. `gh auth status` — verify gh CLI login with `repo` scope
2. `grep -rn 'sk-' config.yaml` — ensure no plaintext API keys (if found, convert to key_env refs before backup)
3. Verify target repo exists and is writable (`gh repo view ...`)
4. **If targeting an organization: verify the org exists first** (`gh api orgs/{org} --jq '.login'`). If it returns 404, the org doesn't exist — fall back to `<gh_api_user>/<repo-name>` or ask the user to create the org before proceeding. Without this check, `gh repo create org/repo` may silently produce a misleading error ("HTTP 404: Not Found") instead of a clear message about the missing org.

## Sensitive file checklist (always exclude)

| Pattern | Reason |
|---------|--------|
| `.env`, `auth.json`, `gateway_state.json` | authentication / credentials |
| `pairing/*` | device pairing secrets |
| `*.pem`, `*.key` | private keys |
| `*.db*` | SQLite session databases |
| `*.lock` files | runtime locks (transient) |
| `logs/` | large, not configuration |
| `skills/.hub/`, `.curator_state`, `.usage.json*` | auto-generated skill management |

## When NOT to use this approach

If gh CLI auth is **not** available: fall back to `hermes-profile-github-backup` (REST API + Python script). See that reference for the full REST workflow.
