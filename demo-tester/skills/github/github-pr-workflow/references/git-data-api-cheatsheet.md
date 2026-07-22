# Git Data API Cheatsheet (API-Only Commit Path)

When `git clone`/`push`/`commit` is blocked (cron mode, restricted agents, sandboxes), create files and commits directly via the GitHub REST API without any local workspace copy.

## Prerequisites

```bash
OWNER=OnePlusNDev  # GitHub username/org
REPO=demo-workflow # Repository name
# Ensure a token: GITHUB_TOKEN set or gh auth status OK
```

## Full Pipeline: Create File + Commit on Branch (No Local Git)

### Step 1 — Get base SHA

```bash
BASE_SHA=$(gh api repos/$OWNER/$REPO/git/refs/heads/main --jq '.object.sha')
```

### Step 2 — Create branch (if it does not exist)

```bash
curl -s -X POST "https://api.github.com/repos/$OWNER/$REPO/git/refs" \
  -H "Authorization: token $GITHUB_TOKEN" \
  -d "{\"ref\":\"refs/heads/feature/add-function\",\"sha\":\"$BASE_SHA\"}"
```

### Step 3 — Create blob(s) for each file

Must use `tr -d '\n'` to produce single-line base64 — multi-line base64 breaks JSON.

```bash
BLOB1=$(curl -s -X POST "https://api.github.com/repos/$OWNER/$REPO/git/blobs" \
  -H "Authorization: token $GITHUB_TOKEN" \
  -d "{\"content\":\"$(base64 < /path/to/hello.py | tr -d '\n')\",\"encoding\":\"base64\"}")

BLOB1_SHA=$(echo "$BLOB1" | jq -r .sha)
```

### Step 4 — Create new tree

```bash
BASE_TREE_SHA=$(gh api repos/$OWNER/$REPO/git/trees/main --jq '.sha')
TRUNCATED=$(gh api repos/$OWNER/$REPO/git/trees/main '--query='.tree[].path' | head -1)

# If truncated=true, read recursively and merge manually:
FULL_ENTRIES=$(gh api repos/$OWNER/$REPO/git/trees/main?recursive=1 --jq '[.tree[] | "{\"path\":\"\(.path)\",\"sha\":\"\(.sha)\",\"type\":\"blob\",\"mode\":\"100644\"}"] | join(","))

NEW_TREE=$(curl -s -X POST "https://api.github.com/repos/$OWNER/$REPO/git/trees" \
  -H "Authorization: token $GITHUB_TOKEN" \
  -d "{
    \"base_tree\": \"$BASE_TREE_SHA\",
    \"tree\": [$FULL_ENTRIES, {\"path\":\"hello.py\",\"sha\":\"$BLOB1_SHA\",\"type\":\"blob\",\"mode\":\"100644\"}]
  }")

NEW_TREE_SHA=$(echo "$NEW_TREE" | jq -r .sha)
```

### Step 5 — Create commit + update branch ref

```bash
COMMIT=$(curl -s -X POST "https://api.github.com/repos/$OWNER/$REPO/git/commits" \
  -H "Authorization: token $GITHUB_TOKEN" \
  -d "{
    \"message\": \"feat: add add(a,b) function and tests\",
    \"tree\": \"$NEW_TREE_SHA\",
    \"parents\": [\"$BASE_SHA\"]
  }")

NEW_COMMIT_SHA=$(echo "$COMMIT" | jq -r .sha)
BRANCH="feature/add-function"

curl -s -X PATCH "https://api.github.com/repos/$OWNER/$REPO/git/refs/heads/$BRANCH" \
  -H "Authorization: token $GITHUB_TOKEN" \
  -d "{\"sha\":\"$NEW_COMMIT_SHA\"}"
```

### Step 6 (optional) — Create PR

```bash
curl -s -X POST "https://api.github.com/repos/$OWNER/$REPO/pulls" \
  -H "Authorization: token $GITHUB_TOKEN" \
  -d "{
    \"title\": \"feat: add add(a,b) function and tests\",
    \"body\": \"## Implementation\\n- Adds \`add(a, b)\` in hello.py\",
    \"head\": \"$BRANCH\",
    \"base\": \"main\"
  }"
```

## Useful Queries (read-only)

### List branches
`gh api repos/$OWNER/$REPO/branches --jq '[.[] | {name,commit:{sha:.commit.sha[:7]}}]'`

### Check if a file exists on a branch
`curl -s "https://api.github.com/repos/$OWNER/$REPO/contents/hello.py?ref=feature/X" | jq '.name // "NOT_FOUND"'`

### Get commit log
`gh api repos/$OWNER/$REPO/commits?per_page=10 --jq '.[] | {sha: .sha[:7], message: .commit.message[:80]}'`

## Pitfalls & Gotchas

| Pitfall | Fix |
|---------|-----|
| Multi-line base64 breaks JSON encoding | Always pipe through `tr -d '\n'` |
| Tree truncated (more than 300 files) | Read with `?recursive=1`, merge in your changes manually |
| API token doesn't work for SSH git | Use HTTPS URLs and `-H "Authorization: token $GITHUB_TOKEN"` |
| Blob size limit | Max ~100 MB per blob; use LFS for larger files |
| Rate limiting (unauthenticated) | 60/hr; authenticated = 5000/hr |
