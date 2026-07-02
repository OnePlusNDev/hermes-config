# `gh api` Git Data Backup Recipe

When `git clone` times out (common in restricted networks or cron environments) but `gh api` works, use the GitHub Git Data API to create a single atomic commit. This method creates blobs → a tree → a commit → and updates the ref — all without `git`.

## Prerequisites

```bash
# Verify gh is authenticated and API is reachable
gh api user --jq '.login'
# Should return your username, not "GraphQL: Could not resolve..."

# Verify repo exists (create if not)
gh repo view $OWNER/$REPO --json name 2>&1 || \
  gh repo create $OWNER/$REPO --private --description "Hermes profile backup"
```

## Recipe

### Step 1: File tree planning

Identify files to back up, applying the include/exclude pattern from the umbrella skill.

### Step 2: Get the current branch ref

```bash
OWNER="OnePlusNDev"  # or your username
REPO="hermes-config"
BRANCH="main"

MAIN_SHA=$(gh api repos/$OWNER/$REPO/git/refs/heads/$BRANCH --jq '.object.sha')
```

### Step 3: Create blobs for each file

Each file becomes a Git blob via the blobs API:

```bash
# Base64-encode the file content
CONTENT_B64=$(base64 < "$LOCAL_FILE" | tr -d '\n')

# Create the blob
BLOB_SHA=$(gh api repos/$OWNER/$REPO/git/blobs \
  --field content="$CONTENT_B64" \
  --field encoding="base64" \
  --jq '.sha')
```

### Step 4: Build the tree

Use `jq` to build the tree entries array. Track paths to avoid duplicates (HTTP 422 otherwise):

```bash
TREE='[]'
ADDED_PATHS=""

add_to_tree() {
  local repo_path="$1"
  local blob_sha="$2"
  
  # Skip duplicates
  if echo "$ADDED_PATHS" | tr ' ' '\n' | grep -Fx "$repo_path" >/dev/null 2>&1; then
    echo >&2 "  SKIP (dup): $repo_path"
    return
  fi
  ADDED_PATHS="$ADDED_PATHS $repo_path"
  
  TREE=$(echo "$TREE" | jq -c \
    --arg p "$repo_path" \
    --arg s "$blob_sha" \
    '. + [{"path": $p, "mode": "100644", "type": "blob", "sha": $s}]')
}
```

### Step 5: Create the tree

```bash
# Use --input for large payloads to avoid argument length limits
TREE_PAYLOAD=$(jq -n --argjson entries "$TREE" '{tree: $entries}')

TREE_SHA=$(gh api repos/$OWNER/$REPO/git/trees \
  --input <(echo "$TREE_PAYLOAD") \
  --jq '.sha')
```

### Step 6: Create the commit

```bash
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

COMMIT_PAYLOAD=$(jq -n \
  --arg msg "backup: auto-backup $(date +%Y-%m-%d)" \
  --arg tree "$TREE_SHA" \
  --arg parent "$MAIN_SHA" \
  --arg author_name "Hermes Backup" \
  --arg author_email "hermes@nousresearch.com" \
  --arg date "$NOW" \
  '{
    message: $msg,
    tree: $tree,
    parents: [$parent],
    author: {name: $author_name, email: $author_email, date: $date}
  }')

COMMIT_SHA=$(gh api repos/$OWNER/$REPO/git/commits \
  --input <(echo "$COMMIT_PAYLOAD") \
  --jq '.sha')
```

### Step 7: Update the branch ref

```bash
gh api repos/$OWNER/$REPO/git/refs/heads/$BRANCH \
  --method PATCH \
  --field sha="$COMMIT_SHA" \
  --field force=false
```

## Complete Bash Function Template

```bash
#!/bin/bash
set -euo pipefail

# ── Config ──
OWNER="OnePlusNDev"
REPO="hermes-config"
PROFILE="demo-pm"
BRANCH="main"
PROFILE_HOME="$HOME/.hermes/profiles/$PROFILE"

# ── Get ref ──
MAIN_SHA=$(gh api repos/$OWNER/$REPO/git/refs/heads/$BRANCH --jq '.object.sha')
echo "Base SHA: $MAIN_SHA"

# ── Build tree ──
TREE='[]'
ADDED=""

add_file() {
  local path="$1" repo_path="$2"
  [ -f "$path" ] || return
  
  # Dedup
  if echo "$ADDED" | grep -qF "$repo_path"; then echo >&2 "DUP: $repo_path"; return; fi
  ADDED="$ADDED $repo_path"
  
  local b64 sha
  b64=$(base64 < "$path" | tr -d '\n')
  sha=$(gh api repos/$OWNER/$REPO/git/blobs \
    --field content="$b64" --field encoding="base64" --jq '.sha')
  echo >&2 "  $repo_path"
  
  TREE=$(echo "$TREE" | jq -c --arg p "$repo_path" --arg s "$sha" \
    '. + [{"path": $p, "mode": "100644", "type": "blob", "sha": $s}]')
}

# Add files...
add_file "$PROFILE_HOME/config.yaml" "$PROFILE/config.yaml"
add_file "$PROFILE_HOME/SOUL.md" "$PROFILE/SOUL.md"
# ... add more files as needed

# ── Create tree ──
TREE_SHA=$(gh api repos/$OWNER/$REPO/git/trees \
  --input <(jq -n --argjson entries "$TREE" '{tree: $entries}') \
  --jq '.sha')
echo "Tree: $TREE_SHA"

# ── Create commit ──
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
COMMIT_SHA=$(gh api repos/$OWNER/$REPO/git/commits \
  --input <(jq -n \
    --arg msg "chore($PROFILE): auto-backup $(date +%Y-%m-%d)" \
    --arg tree "$TREE_SHA" \
    --arg parent "$MAIN_SHA" \
    --arg author_name "Hermes Backup" \
    --arg author_email "hermes@nousresearch.com" \
    --arg date "$NOW" \
    '{message: $msg, tree: $tree, parents: [$parent], author: {name: $author_name, email: $author_email, date: $date}}') \
  --jq '.sha')
echo "Commit: $COMMIT_SHA"

# ── Push ──
gh api repos/$OWNER/$REPO/git/refs/heads/$BRANCH \
  --method PATCH --field sha="$COMMIT_SHA" --field force=false
echo "Done: https://github.com/$OWNER/$REPO/tree/$PROFILE"
```

## Verification

After pushing, verify files landed:

```bash
gh api repos/$OWNER/$REPO/contents/$PROFILE --jq '.[].name'
# Should show all backed-up files
```

## Pitfalls from This Session

- **`bash -x` debugging**: When bash function output and JSON mix (as in `ENTRY=$(encode_and_upload ...)` where the function both `echo`s status and `echo`s JSON), the variable captures both. Redirect informational messages to stderr (`echo >&2 "..."`) and only emit the JSON to stdout.
- **jq string interpolation**: `jq -n --arg p "$repo_path" '. + [{path: $p}]'` — always use `--arg` for variable injection. Don't concatenate JSON strings manually.
- **Duplicate tree entries crash the API**: A `tree` array with two identical `path` values causes HTTP 422 `"Invalid tree info"`. Always dedup with a tracking set before adding.
- **`--field` vs `--input`**: For trees with many entries, `--field tree="$TREE_JSON"` hits shell argument limits. Use `--input <(echo "$PAYLOAD")` instead.
- **Date format**: GitHub requires ISO 8601 (`2026-06-28T20:00:00Z`). Numeric timestamps fail silently.
- **The `--jq` flag**: When piping to jq with `--jq`, ensure the jq expression is quoted properly. For compound expressions like object construction inside `jq -n`, use `--arg` for all variables.
