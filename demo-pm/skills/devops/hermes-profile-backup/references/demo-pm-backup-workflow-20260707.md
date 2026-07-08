# Demo-PM Backup Workflow — 2026-07-07

**Method:** A (rsync) → fell back to B (gh API Git Data API)
**Files:** 22 changed (7 modified, 15 new), 479 unchanged merged
**Commit:** 72f3b5d1

## Key Findings

### 1. `git push` failed (port 443), but `gh api` worked

git push failed with:
```
fatal: unable to access 'https://github.com/...': 
Failed to connect to github.com port 443 after 75003 ms
```

But `gh api` succeeded immediately:
```bash
gh api /repos/OnePlusNDev/hermes-config/git/refs/heads/main --jq '.object.sha'
# → 8a86a662ddf814e97588aeefe3ffec7d520b0732
```

This confirms the skill's guidance: curl `000` does NOT mean gh CLI will fail — use Method B as fallback.

### 2. DO NOT use `git status --porcelain` after a local commit

First attempt (push_v1.py) failed because the local commit was already made:
```python
# ❌ BUG: returns empty! Local commit already staged everything
status_raw = sh(["git", "status", "--porcelain"])  
changed_files = []  # → 0 files found
```

Only `.gitignore` got uploaded — the correct tree used old SHAs for everything else.

**Fix:** Use `git ls-tree -r HEAD` to read the committed state rather than the working-tree diff:
```python
local_raw = sh(["git", "ls-tree", "-r", "HEAD"])
# Parse: mode type sha path
# → gives the exact content-addressed tree that was committed
```

### 3. Directory entries in remote tree cause false-positive deletions

The `?recursive=1` tree returned by the GitHub API contains both blobs (files) and tree objects (directories). When comparing against `git ls-tree -r HEAD` (blobs only), every directory appears as "deleted":

```
172 deleted files
  DEL demo-pm/cron
  DEL demo-pm/skills
  DEL demo-pm/skills/apple
  ...
```

All 172 are directory entries — not actual deletions. **Fix:** Filter to only compare blob-type entries:
```python
for entry in remote_tree["tree"]:
    if entry.get("type") != "blob":
        continue  # skip directories; git recreates them from file paths
```

### 4. Correct diff strategy for incremental push

1. Get remote tree: `gh api /repos/:owner/:repo/git/trees/:sha?recursive=1`
2. Filter to blob entries only
3. Get local tree: `git ls-tree -r HEAD` (in the cloned repo)
4. **Diff:**
   - Local path with same SHA in remote → **copy unchanged** entry from remote tree
   - Local path with different SHA or absent from remote → **upload as blob** via gh API
   - Remote path absent from local → **omit** from new tree (genuine deletion)
5. Build tree JSON (dedup by path), create commit, update ref

### 5. Network verification lesson

Verifying the push succeeded by fetching from GitHub also timed out:
```bash
git fetch origin main  # → timed out after 30s
```
But `gh api` verification worked:
```python
verify = gh_api("GET", f"/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}")
# → confirmed the new HEAD SHA
```

Always use `gh api` for verification when git-over-HTTPS is unreliable. The Content API (`/repos/:owner/:repo/contents/:path`) works well for spot-checking individual files.

## Scripts Used

- `/tmp/push_v1.py` — first attempt, buggy (used `git status` → found 0 changes)
- `/tmp/push_v2.py` — corrected (uses `git ls-tree -r HEAD` comparison)
- `references/gh-api-git-data-incremental-push.py` — reusable template derived from push_v2.py
