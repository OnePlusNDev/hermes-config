# Profile Config Backup to GitHub

Back up a Hermes profile's configuration (config.yaml, skills, cron, memories, workspace) to the `hermes-config` GitHub repo under `<profile-name>/`. Designed for cron-mode execution.

## Pre-flight: .gitignore Health Check

**Before anything else, verify `.gitignore` exists and is current at the repo root.** The backup repo root's `.gitignore` is the primary defense against accidentally committing sensitive or transient files.

### `.gitignore` is MISSING

If the repo's `.gitignore` is missing (e.g., deleted by a force-push, lost during `git reset --hard`, or never created), **recreate it from scratch before copying any files**. A missing `.gitignore` means `git add -A` will capture:

- Runtime SQLite databases (`*.db`, `state.db*`)
- Credential stores (`.env`, `auth.json`)
- Process locks (`*.lock`, `*.pid`)
- Chat histories (`sessions/`, `state.db-wal`)
- User home dir credentials (`home/.config/gh/config.yml`, `home/.gitconfig`)
- Skills runtime metadata (`.usage.json`, `.bundled_manifest`)
- Embedded git repos (`home/demo-workflow` and similar)

**Recreate the minimal `.gitignore`**: see the full pattern list in §.gitignore Maintenance below.

### `.gitignore` was overwritten by `git reset --hard origin/main`

After pulling the remote state (e.g., `git reset --hard origin/main`), any local `.gitignore` updates you made are LOST. This is a common failure sequence:

1. You update `.gitignore` with new patterns
2. `git pull` or `git reset --hard` replaces your `.gitignore` with the stale remote version
3. `git add -A` captures files the updated `.gitignore` was supposed to exclude

**Fix — re-apply patterns after reset, before `git add`:**

```bash
# After git reset --hard, verify .gitignore is still correct
grep 'home/' .gitignore || echo "WARNING: home/ pattern missing — add it now"
grep '\.usage\.json' .gitignore || echo "WARNING: .usage.json pattern missing"
grep '\.bundled_manifest' .gitignore || echo "WARNING: .bundled_manifest pattern missing"

# If missing, update .gitignore (see §.gitignore Maintenance for full list)
echo "home/" >> .gitignore
echo "**/skills/.usage.json" >> .gitignore
# ... repeat for all missing patterns

# NOW do git add
git add -A <profile>/
```

### Embedded git repos in `home/`

The `home/` directory in a Hermes profile often contains an embedded git checkout (e.g., `home/demo-workflow`). When `git add -A` encounters this:

```
warning: adding embedded git repository: demo-tester/home/demo-workflow
hint: You've added another git repository inside your current repository.
```

**This is a security risk** — the embedded repo may contain credentials (`.config/gh/config.yml`, `.gitconfig`, `.ssh/`), and adding it as an embedded submodule won't include its contents but will create a dangling gitlink in the backup that later confuses restore attempts. Furthermore, `git add` without `-f` actually skips the contents of the embedded repo, but the gitlink entry remains in the index.

**Fix — ensure `home/` is in `.gitignore`, then unstage if already added:**

```bash
# Prevention: home/ must be in .gitignore BEFORE git add
echo "home/" >> .gitignore

# If already staged, remove it:
git rm --cached -rf <profile>/home/
git commit --amend --no-edit  # if commit already made, or just continue
```

The `home/` directory contains: gh auth tokens, git config with user identity, SSH keys, cached API responses. **Never back it up.**

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

## .gitignore Maintenance (First!)

**Before running rsync or git add, verify the repo's `.gitignore` covers all transient patterns.** The `hermes-config` repo is shared by multiple profiles (`demo-tester/`, `demo-pm/`, `demo-dev/`), so `.gitignore` patterns live at the repo root. There are two critical rules:

### Rule 1: Use `**/` prefix for subdirectory patterns

Since profile directories are nested under `demo-tester/`, `demo-pm/`, etc., a bare pattern like:

```gitignore
cron/output/        # ❌ Only matches ./cron/output/ at repo root — NOT demo-tester/cron/output/
```

...won't match files inside subdirectories. You need the `**/` prefix:

```gitignore
**/cron/output/     # ✅ Matches any nested cron/output/, e.g. demo-tester/cron/output/
**/cron/ticker_*    # ✅ Same for ticker files anywhere in the tree
**/skills/.curator_* # ✅ Matches all profiles' curator state
```

**Always use `**/` when the pattern should apply across all profiles.** This is especially important for: `cron/output/`, `cron/ticker_*`, `skills/.curator_*`, `skills/.hub/`, `skills/.usage.json`, `skills/.bundled_manifest`.

### Rule 2: Update .gitignore BEFORE git add

If rsync introduced new file types (e.g., `auth.lock`, `.bundled_manifest`) that aren't yet in `.gitignore`:

1. First, add the missing patterns to `.gitignore` (with `**/` prefix — see Rule 1)
2. Then run `git status` to confirm they're ignored
3. Then `git add <profile>/`

If you `git add` before updating `.gitignore`, those transient files get staged. Removing them requires `git rm --cached` + `git commit --amend`, which is messier.

### Common patterns that drift

New Hermes versions may introduce new runtime files. The following patterns are the most commonly missed during upgrades — check them every few months:

```gitignore
# Cron runtime artifacts
**/cron/output/
**/cron/ticker_*
**/cron/.gitignore

# Skills internal state
**/skills/.curator_*
**/skills/.hub/
**/skills/.usage.json
**/skills/.bundled_manifest

# Runtime/cache
context_length_cache.yaml
```

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

### `git rm --cached` fails with "file has staged content different from both the file and the HEAD"

When you staged an embedded git repo (e.g., `home/demo-workflow`) and then try to remove it from the index mid-commit:

```
error: the following file has staged content different from both the
file and the HEAD:
    demo-tester/home/demo-workflow
(use -f to force removal)
```

**Fix — use `-rf` to force removal of the embedded repo from the index:**

```bash
# Force removal works even with the staged-content mismatch
git rm --cached -rf <profile>/home/
```

This removes the gitlink entry from the index without affecting the file on disk. Then add `home/` to `.gitignore` to prevent re-occurrence.

### `git add -A` pulls in unwanted files from ALL profiles

`git add -A` at the repo root stages changes across every profile directory. If another profile's backup run modified files or deleted them during a stale clone, you'll commit those changes too. **Always scope your `git add`:**

```bash
# Safe — only your profile
git add <profile>/

# Also add .gitignore if it was updated
git add .gitignore

# Verify only your scope was staged
git diff --cached --name-only -- <profile>/
```

**Update `.gitignore` first** if rsync introduced new transient file types (see §.gitignore Maintenance above). Then stage only your profile's files — never `git add -A` at the repo root (it would capture other profiles' accidental deletions and unrelated changes):

```bash
cd ~/hermes-config
# Scoped add — only this profile's directory
git add <profile>/
# Also commit .gitignore changes if they were updated
git add .gitignore

# Verify only your profile is staged
git status --porcelain -- <profile>/      # scoped — clean output
git diff --cached --name-only             # what's actually in the commit
git diff --cached --stat -- <profile>/    # preview stats
```

Scoping with `-- <profile>/` on `git status` is essential in a multi-profile repo. It filters out unrelated changes (other profiles' working-tree modifications, accidental deletions from concurrent backup runs), giving you a clean view of what YOUR backup will include.

Then commit and push:

```bash
git commit -m "backup(<profile>): auto config backup $(date -u +%Y-%m-%dT%H:%M:%SZ)"
git push origin main
```
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

### Push Failure: Repo is corrupted (missing blobs, broken refs)

The local clone may have corrupted git objects from prior aborted pushes, botched GC, or incomplete clone operations. `git fsck` will show:

```
error: refs/stash: invalid sha1 pointer ...
missing blob 475e24bc... for 'demo-tester/skills/.../file.md'
Error building trees  ← commit fails
```

The root cause is usually a corrupted `refs/stash` reference whose tree objects are missing. **Fix — clean refs, then rebuild the index:**

```bash
# Step 1: Remove corrupted stash ref (most common source of broken objects)
git update-ref -d refs/stash 2>/dev/null

# Step 2: Expire bad reflog entries silently
git reflog expire --expire=now --all 2>/dev/null

# Step 3: If a specific file's blob is missing, remove it from tracking and re-add
# Identify the problematic file from the error message
# e.g., 'missing blob 475e24bc... for demo-tester/skills/.../file.md'
PROBLEM_FILE="demo-tester/path/to/problematic-file.md"
git rm --cached "$PROBLEM_FILE"   # remove the corrupted tree entry
git add "$PROBLEM_FILE"           # re-add the file from disk (fresh blob)

# Step 4: Now commit should succeed
git commit -m "backup(<profile>): ..."
```

If step 3 doesn't work because the tree is too corrupted to even modify, the nuclear option is to use `git fetch origin --force` to restore from the remote (if reachable), or detect the corrupted file path from the error and remove it from both disk and tracking with `git rm`.

After commit, verify with `git fsck` that no remaining broken links block future operations.

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
