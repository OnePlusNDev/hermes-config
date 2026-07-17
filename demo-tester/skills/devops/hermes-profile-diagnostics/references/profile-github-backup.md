# Profile Config Backup to GitHub

Back up a Hermes profile's configuration (config.yaml, skills, cron, memories, workspace) to the `hermes-config` GitHub repo under `<profile-name>/`. Designed for cron-mode execution.

## Pre-flight: API Key Security Scan

**Before copying any file, scan `config.yaml` for plaintext `sk-` API keys.** Hermes configs frequently embed credentials in fields like `auxiliary.*.api_key`, `delegation.api_key`, `custom_providers`, etc.

```bash
# Check for any sk- prefixed strings in YAML config
grep -n 'sk-' ~/.hermes/profiles/<profile>/config.yaml

# If found, the key MUST be replaced with a key_env reference before backup:
#   api_key: ''        # ← empty, safe
#       or
#   key_env: MY_KEY    # ← env var reference, safe
#   api_key: sk-xxx    # ← PLAINTEXT, DANGER — replace with key_env
```

**Detection step:** scan with `grep -n 'sk-'` across ALL files that will be backed up. If any plaintext key is found, abort the backup, replace the value with `key_env: <VAR_NAME>` (or empty string `''`), and commit that fix first.

## Sync Command

```bash
cd ~/hermes-config                    # cloned repo
rsync -av \
  --exclude='state.db*' \
  --exclude='*.env*' \
  --exclude='cache/' \
  --exclude='logs/' \
  --exclude='cron/output/' \
  --exclude='sessions/' \
  --exclude='sessions.db' \
  --exclude='hindsight/' \
  --exclude='auth.*' \
  --exclude='gateway.*' \
  --exclude='processes.json' \
  --exclude='desktop/' \
  --exclude='bin/' \
  --exclude='config.yaml.bak*' \
  --exclude='*_cache.json' \
  --exclude='.lock' \
  --exclude='models_dev_cache.json' \
  ~/.hermes/profiles/<profile>/ ./<profile>/
```

### Exclusion Rationale

| Pattern | Why excluded |
|---------|-------------|
| `state.db*` | Runtime SQLite — transient, regenerated on restart |
| `*.env*` | Contains plaintext secrets (API keys, tokens) |
| `cache/`, `*_cache.json` | Derived data, regenerable |
| `logs/` | Rotating log files — too noisy, no config value |
| `cron/output/` | Thousands of run logs — belongs in separate archival |
| `sessions/`, `sessions.db` | Chat history — too large, personal data |
| `hindsight/` | Embedding DB state — runtime artifact |
| `auth.*`, `gateway.*`, `processes.json` | Runtime state files |
| `desktop/` | Desktop session state |
| `bin/` | Binary tools (tirith CLI, etc.) |
| `config.yaml.bak*` | Editor/upgrade backup files |
| `.lock` files | Process locks — transient |

## Commit & Push

```bash
cd ~/hermes-config
git add <profile>/
git commit -m "backup(<profile>): auto config backup $(date -u +%Y-%m-%dT%H:%M:%SZ)"
git push origin main
```

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
- Report clearly in the final response (delivered automatically)
- Use `[SILENT]` only when there's genuinely nothing new to report (no changes since last backup)
- If push fails due to network, report it as a known limitation — the commit is still saved locally
