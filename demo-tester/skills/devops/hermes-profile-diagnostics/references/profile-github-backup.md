# Profile Config Backup to GitHub

Back up a Hermes profile's configuration (config.yaml, skills, cron, memories, workspace) to the `hermes-config` GitHub repo under `<profile-name>/`. Designed for cron-mode execution.

## Pre-flight: API Key Security Scan

**Before copying any file, scan `config.yaml` for plaintext `sk-` API keys.** Hermes configs frequently embed credentials in fields like `auxiliary.*.api_key`, `delegation.api_key`, `custom_providers`, etc.

```bash
# Check for any sk- prefixed strings in YAML config — use precise grep
grep -n 'api_key:.*sk-' ~/.hermes/profiles/<profile>/config.yaml

# If found, the key MUST be replaced with a key_env reference before backup:
#   api_key: ''        # ← empty, safe
#       or
#   key_env: MY_KEY    # ← env var reference, safe
#   api_key: sk-xxx    # ← PLAINTEXT, DANGER — replace with key_env
```

**Detection step:** scan with `grep -n 'api_key:.*sk-'` across ALL files that will be backed up. This targets only `api_key` values (not comments or unrelated strings containing "sk-"). If any plaintext key is found, abort the backup, replace the value with `key_env: <VAR_NAME>` (or empty string `''`), and commit that fix first.

## Sync Command

```bash
cd ~/hermes-config                    # cloned repo
rsync -av \
  --exclude='state.db*' \
  --exclude='*.db' \
  --exclude='*.db-shm' \
  --exclude='*.db-wal' \
  --exclude='*.env*' \
  --exclude='*.lock' \
  --exclude='*.pid' \
  --exclude='cache/' \
  --exclude='image_cache/' \
  --exclude='audio_cache/' \
  --exclude='logs/' \
  --exclude='cron/output/' \
  --exclude='cron/ticker_heartbeat' \
  --exclude='cron/ticker_last_success' \
  --exclude='sessions/' \
  --exclude='sessions.db' \
  --exclude='hindsight/' \
  --exclude='auth.*' \
  --exclude='gateway.*' \
  --exclude='processes.json' \
  --exclude='desktop/' \
  --exclude='bin/' \
  --exclude='home/' \
  --exclude='plans/' \
  --exclude='sandboxes/' \
  --exclude='pairing/' \
  --exclude='lsp/' \
  --exclude='hooks/' \
  --exclude='config.yaml.bak*' \
  --exclude='*_cache.json' \
  --exclude='models_dev_cache.json' \
  --exclude='.skills_prompt_snapshot.json' \
  --exclude='.update_check' \
  --exclude='.hermes_history' \
  --exclude='context_length_cache.yaml' \
  --exclude='triage_issues.py' \
  --exclude='skills/.bundled_manifest' \
  --exclude='skills/.curator_state' \
  --exclude='skills/.usage.json*' \
  --exclude='skills/.hub/' \
  --exclude='skills/.curator_backups/' \
  ~/.hermes/profiles/<profile>/ ./<profile>/
```

**IMPORTANT: Do NOT use `--delete` in cron mode.** The `rsync --delete` flag triggers tirith's blast-radius guard (security scan), which blocks the command in cron/automated contexts. Without `--delete`, stale files from previous backups that no longer exist in the source (e.g., old backup archive files that were pruned) will persist in the repo — this is acceptable because git history tracks the full lineage, and the working tree is only used as a staging ground for git commits. If cleanup is genuinely needed, run `git rm` targeted at specific files.

### Exclusion Rationale

| Pattern | Why excluded |
|---------|-------------|
| `state.db*`, `*.db`, `*.db-shm`, `*.db-wal` | Runtime SQLite — transient, regenerated on restart |
| `*.env*` | Contains plaintext secrets (API keys, tokens) |
| `*.lock`, `*.pid` | Process locks — transient |
| `cache/`, `image_cache/`, `audio_cache/`, `*_cache.json` | Derived data, regenerable |
| `logs/` | Rotating log files — too noisy, no config value |
| `cron/output/`, `cron/ticker_*` | Thousands of run logs & ticker state — runtime artifacts |
| `sessions/`, `sessions.db` | Chat history — too large, personal data |
| `hindsight/` | Embedding DB state — runtime artifact |
| `auth.*`, `gateway.*`, `processes.json` | Runtime state files |
| `desktop/`, `home/` | Desktop session state & user home (contains .ssh, gh auth tokens) |
| `bin/` | Binary tools (tirith CLI, etc.) |
| `plans/`, `sandboxes/`, `pairing/`, `lsp/`, `hooks/` | Subdirectories with runtime/dev state |
| `config.yaml.bak*` | Editor/upgrade backup files |
| `.skills_prompt_snapshot.json`, `.update_check`, `.hermes_history` | Runtime metadata, not config |
| `context_length_cache.yaml` | Temporary caching |
| `triage_issues.py` | Development artifact |
| `skills/.bundled_manifest`, `.curator_state`, `.usage.json*`, `.hub/`, `.curator_backups/` | Curator runtime metadata |

## Add, Commit, & Push

```bash
cd ~/hermes-config
git add -A <profile>/               # -A captures new files too
git commit -m "backup(<profile>): auto config backup $(date -u +%Y-%m-%dT%H:%M:%SZ)"
git push origin main
```

Include a change summary in the commit body (count of modified vs new files) for quick scanning:
```bash
git diff --cached --stat -- <profile>/  # preview stats
```

### Push Failure: Shared Repository Conflicts

When multiple profiles back up to the same `hermes-config` repo, their cron jobs may run concurrently. If another profile's backup pushed between your commit and your push, you'll see:
```
! [rejected] main -> main (fetch first)
```

**Fix — stash unrelated changes, rebase, push:**
```bash
# 1. Stash working tree changes from OTHER profiles (not yours)
git stash -- <other-profile>/

# 2. Rebase onto the new remote
git pull --rebase origin main

# 3. Restore the stashed changes
git stash pop

# 4. Push now succeeds (fast-forward)
git push origin main
```

The stash-and-rebase pattern is cleaner than merge because it avoids creating a merge commit in what is fundamentally a linear backup history. The `-- <other-profile>/` target on `git stash` limits the stash to only files under that path, so your profile's staged commit is preserved.

### Push Failure: git endpoint vs API endpoint

In cron environments, `github.com:443` (the git HTTPS endpoint) is often blocked while `api.github.com` works. Diagnostic:

```bash
curl -s -o /dev/null -w "HTTP %{http_code} (%{time_total}s)\n" --connect-timeout 10 https://github.com
# → HTTP 000 (timeout) = git endpoint blocked

curl -s -o /dev/null -w "HTTP %{http_code} (%{time_total}s)\n" --connect-timeout 10 https://api.github.com
# → HTTP 200 = API endpoint works
```

#### Workarounds (in priority order):

1. **Retry later** — Commit is local (`~/hermes-config/`). Next interactive session from a normal network can `git push`.
2. **One-off HTTP/1.1** — If `github.com` is reachable but slow:
   ```bash
   git -c http.version=HTTP/1.1 push origin main
   ```
3. **With credential helper** — When gh auth is needed AND transport is broken:
   ```bash
   git -c credential.helper='!gh auth git-credential' -c http.version=HTTP/1.1 push origin main
   ```
4. **SSH remote** — If SSH key is configured for the right GitHub user:
   ```bash
   git remote set-url origin git@github.com:<owner>/hermes-config.git
   git push origin main
   ```
5. **Git Data API (last resort)** — When only `api.github.com` works, use `gh api` to create blobs, tree, commit, and update ref manually. This requires uploading all new/changed file content as base64 blobs via `POST /repos/<owner>/hermes-config/git/blobs`, then building the tree, creating the commit, and updating the ref.

## Verification

After successful push, verify the remote has the latest commit:

```bash
gh api repos/<owner>/hermes-config/contents/<profile>/config.yaml --jq '.sha'
cd ~/hermes-config && git rev-parse HEAD | head -c 40
```

These should match (or the remote should be an ancestor of local if push was up-to-date).

## Cron Job Pattern

When run as a cron job with no user present:
- Report clearly in the final response (delivered automatically):
  - Backup result (success/failure)
  - List of backed-up files (modified vs new)
  - Whether any plaintext API keys were found and replaced
- Use `[SILENT]` only when there's genuinely nothing new to report (no changes since last backup)
- If push fails due to network, report it as a known limitation — the commit is still saved locally
