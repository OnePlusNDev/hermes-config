# Hermes Config Backup via Git Data API

When backing up a Hermes profile's configuration to GitHub, use the **Git Data API**
(git blobs → trees → commits → refs) instead of `git push` when:
- HTTPS to `github.com:443` is unreliable (HTTP/2 framing errors, empty replies)
- SSH key maps to a different account than the repo owner
- Security scanner blocks `git clone` / `git push` in cron mode

## Pre-Backup Checklist

Always run these checks before pushing config to a repo:

### 1. Check for Plaintext API Keys

```bash
# Scan for 'sk-' prefixed keys (OpenAI-style)
grep -rn "sk-" config.yaml

# Find all non-empty api_key fields
grep -nE "api_key" config.yaml | grep -v "api_key: ''$"
```

If any non-empty `api_key` is found, **replace it with an env-var reference** before committing:
```yaml
# DO NOT COMMIT:
api_key: sk-abc123def456

# SAFE:
# api_key: ''    # set via DEEPSEEK_API_KEY env var
```

### 2. Exclude Sensitive/Runtime Files

Never back these up:

| File/Dir | Reason |
|----------|--------|
| `.env` | Environment variables (API keys, tokens) |
| `auth.json` / `auth.lock` | OAuth tokens, authentication state |
| `state.db` / `sessions.db` | Runtime databases (session data) |
| `cron/output/` | Generated cron reports |
| `audio_cache/` / `cache/` | Runtime caches |
| `sessions/` / `memories/` | Conversation histories, memory state |
| `home/` / `logs/` / `hindsight/` | Runtime state, agent logs |
| `gateway.lock` / `gateway.pid` / `gateway_state.json` | Daemon process state |
| `desktop/` | UI session state |
| `*.bak` | Backup remnants from previous config edits |
| `ticker_*` / `*_cache.json` / `processes.json` | Transient runtime metadata |

### 3. Essential Files to Back Up

| File | Purpose |
|------|---------|
| `config.yaml` | Hermes agent configuration |
| `RULES.md` | Agent execution rules |
| `SOUL.md` | Agent role/personality definition |
| `channel_directory.json` | Platform channel configuration |
| `context_length_cache.yaml` | Context length cache config (minor) |
| `cron/jobs.json` | Cron job definitions |

## API-Based Backup Script (Standalone)

Save as `backup_hermes_config.py` and run with `python3 backup_hermes_config.py`.
No `git` binary needed — works entirely through `gh api`.

```python
import base64, json, subprocess, os, sys

profile_dir = os.path.expanduser("~/.hermes/profiles/demo-tester")
prefix = "demo-tester"

def gh_api(method, path, data=None):
    cmd = ["gh", "api", path, "--method", method]
    if data:
        cmd.extend(["--input", "-"])
        proc = subprocess.run(cmd, input=json.dumps(data).encode(),
                               capture_output=True, timeout=60)
    else:
        proc = subprocess.run(cmd, capture_output=True, timeout=30)
    if proc.returncode != 0:
        return None
    return json.loads(proc.stdout) if proc.stdout else {}

# --- CONFIGURE ---
OWNER = "your-org"
REPO  = "hermes-config"  # the config backup repo
BRANCH = "main"

# Files to back up (relative to profile_dir)
# Use flat files for root level, subdir entries need separate tree objects
files = [
    ("config.yaml", "644"),
    ("RULES.md", "644"),
    ("SOUL.md", "644"),
    ("channel_directory.json", "644"),
    ("context_length_cache.yaml", "644"),
]
subdir_files = {
    "cron": [
        ("jobs.json", "644"),
    ]
}

# --- STEP 1: Check plaintext keys ---
print("Step 0: Sanity check...")
for f, _ in files:
    fp = os.path.join(profile_dir, f)
    if not os.path.exists(fp):
        print(f"  WARN: {f} not found, skipping")
    with open(fp, "rb") as fh:
        content = fh.read()
    if b"sk-" in content:
        print(f"  ERROR: {f} contains 'sk-' pattern! Aborting.")
        print(f"  Replace plaintext keys with env-var references first.")
        sys.exit(1)
print("  No plaintext API keys found.")

# --- STEP 2: Get latest commit ---
print("Step 1: Getting latest commit...")
ref = gh_api("GET", f"repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}")
latest_sha = ref["object"]["sha"]
commit_info = gh_api("GET", f"repos/{OWNER}/{REPO}/git/commits/{latest_sha}")
root_tree_sha = commit_info["tree"]["sha"]
print(f"  Latest: {latest_sha[:12]}")

# --- STEP 3: Create blobs ---
print("Step 2: Creating blobs...")
blobs = {}
for f, _ in files:
    fp = os.path.join(profile_dir, f)
    if not os.path.exists(fp):
        continue
    with open(fp, "rb") as fh:
        content = fh.read()
    blob = gh_api("POST", f"repos/{OWNER}/{REPO}/git/blobs", {
        "content": base64.b64encode(content).decode(),
        "encoding": "base64"
    })
    if blob:
        blobs[f] = blob["sha"]
        print(f"  OK: {f}")

# Handle subdir files (cron/jobs.json etc.)
subdir_trees = {}
for dirname, file_list in subdir_files.items():
    sub_entries = []
    for f, _ in file_list:
        fp = os.path.join(profile_dir, dirname, f)
        if not os.path.exists(fp):
            continue
        with open(fp, "rb") as fh:
            content = fh.read()
        blob = gh_api("POST", f"repos/{OWNER}/{REPO}/git/blobs", {
            "content": base64.b64encode(content).decode(),
            "encoding": "base64"
        })
        if blob:
            sub_entries.append({"path": f, "mode": "100644",
                                 "type": "blob", "sha": blob["sha"]})
    if sub_entries:
        tree = gh_api("POST", f"repos/{OWNER}/{REPO}/git/trees",
                       {"tree": sub_entries})
        subdir_trees[dirname] = tree["sha"]

# --- STEP 4: Create profile tree ---
print("Step 3: Creating profile tree...")
tree_entries = [
    {"path": f, "mode": "100644", "type": "blob", "sha": s}
    for f, s in blobs.items()
]
for dirname, tree_sha in subdir_trees.items():
    tree_entries.append({
        "path": dirname, "mode": "040000", "type": "tree", "sha": tree_sha
    })
profile_tree = gh_api("POST", f"repos/{OWNER}/{REPO}/git/trees",
                       {"tree": tree_entries})
profile_tree_sha = profile_tree["sha"]
print(f"  {prefix} tree: {profile_tree_sha[:12]}")

# --- STEP 5: Get root tree, replace branch dir ---
print("Step 4: Creating root tree...")
root_tree = gh_api("GET", f"repos/{OWNER}/{REPO}/git/trees/{root_tree_sha}")
other = [e for e in root_tree["tree"] if e["path"] != prefix]
other.append({"path": prefix, "mode": "040000",
              "type": "tree", "sha": profile_tree_sha})
new_root = gh_api("POST", f"repos/{OWNER}/{REPO}/git/trees", {"tree": other})
print(f"  Root tree: {new_root['sha'][:12]}")

# --- STEP 6: Commit ---
print("Step 5: Creating commit...")
commit = gh_api("POST", f"repos/{OWNER}/{REPO}/git/commits", {
    "message": f"backup: {prefix} profile config (sanitized)",
    "tree": new_root["sha"],
    "parents": [latest_sha]
})
commit_sha = commit["sha"]
print(f"  Commit: {commit_sha[:12]}")

# --- STEP 7: Update branch ---
print("Step 6: Updating branch ref...")
gh_api("PATCH", f"repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}", {
    "sha": commit_sha, "force": True
})
print("  Branch updated!")

print(f"\n=== SUCCESS ===")
print(f"Files: {len(blobs)} + {sum(len(v) for v in subdir_files.values())} in subdirs")
print(f"Commit: {commit_sha[:12]}")
```

## Pitfalls

### `base_tree` returns same SHA

When using `"base_tree": base_tree_sha` in the tree API with new entries that don't
actually differ from the base tree's existing content, the API may return the **same**
SHA. This happens when files already exist with identical content. The commit will
still be created but the tree points to the existing structure.

**Fix:** Omit `base_tree` entirely when replacing a directory (e.g., cleaning up
runtime files from a previous backup). Without `base_tree`, the tree contains ONLY
the entries you specify.

### Blob creation rate limit

Each file requires one `POST /git/blobs` API call. For 500+ files (e.g., the
skills directory), this takes ~500 API calls. Monitor rate limits:
```bash
gh api rate_limit --jq '.rate.remaining'
```

### `gh api` vs `curl` for body input

`gh api --input -` reads the JSON body from stdin, which avoids shell quoting
issues with complex JSON. Prefer this over `echo '...' | gh api ...` or inlined
`-f` flags for multi-key payloads.
