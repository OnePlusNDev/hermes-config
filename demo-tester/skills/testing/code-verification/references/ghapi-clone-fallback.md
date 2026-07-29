# gh API as git Clone Fallback

## Why this matters
In cron and restricted environments, `git clone https://...` fails because:
1. No username is presented — terminal prompts are disabled (`GIT_TERMINAL_PROMPT=0`)
2. HTTPS protocol needs token but no auth context is injected for git CLI
3. Even interactive macOS can hit "HTTP2 framing layer" or "Failed to connect" network errors

The `gh api` method inherits the already-active gh auth token, so it works everywhere.

## Pattern: List files in a branch

```bash
gh api repos/OWNER/REPO/git/trees/main --method GET -q '.tree[].path'
```

Returns all file paths at the root level of `main`. For nested directories, follow via `.sha` and recurse with `-f "recursive=true"`.

For recursive (all files):
```bash
gh api repos/OWNER/REPO/git/trees/main?recursive=true -q '.tree[].path'
```

## Pattern: Fetch file content

1. Get the blob SHA from tree listing:
```bash
blob_sha=$(gh api repos/OWNER/REPO/git/trees/main\?recursive=true \
  -q '.tree[] | select(.path=="hello.py") | .sha')
```

2. Fetch raw blob content (base64-encoded):
```bash
raw=$(gh api repos/OWNER/REPO/git/blobs/$blob_sha)
```

3. Decode:
```bash
echo "$raw" | python3 -c "import json, base64, sys; d=json.load(sys.stdin); print(base64.b64decode(d['content']).decode())"
```

Or inline in one pass:
```bash
gh api repos/OWNER/REPO/git/blobs/<sha> | python3 -c "
import json, base64, sys
d = json.load(sys.stdin)
print(base64.b64decode(d['content']).decode('utf-8'))
" > /tmp/fetched_file.py
```

## Pattern: Get latest commit SHA on main

```bash
gh api repos/OWNER/REPO/commits/main -q '.sha'
```

Then use this SHA + `recursive=true` tree listing — the blob SHAs are deterministic for a given tree.

## Pattern: Fetch PR branch content

Instead of cloning the developer's branch, fetch it directly:
```bash
# Get branch tip SHA first
gh api repos/OWNER/REPO/branches/<branch-name> -q '.commit.sha'

# Then use recursive tree listing as above
gh api repos/OWNER/REPO/git/trees/<branch-commit-sha>?recursive=true
```

## Error handling
- If `gh api` returns an empty array `[]` for the tree, the branch may not exist or the repo is private. Verify with:
```bash
gh api repos/OWNER/REPO -q '.full_name'
```
- Rate limit (403): add `--header 'Accept: application/vnd.github+json'`. Most cron calls won't hit limits but good to know.
