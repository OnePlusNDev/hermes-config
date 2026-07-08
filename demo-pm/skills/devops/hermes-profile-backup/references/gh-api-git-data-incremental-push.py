#!/usr/bin/env python3
"""
Incremental push via GitHub Git Data API — upload only changed blobs.

Use this when `git push` fails (port 443 unreachable) but `gh api` works.
Strategy: get remote tree, compare with local `git ls-tree -r HEAD`,
upload blobs only for changed/new files, merge unchanged entries, commit, push.

Adapt the constants at the top for your environment.
"""

import base64
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────
OWNER = "OnePlusNDev"
REPO = "hermes-config"
BRANCH = "main"
WORKTREE = Path("/tmp/hermes-1783426282")  # cloned repo path
PROFILE = "demo-pm"                         # subdirectory in the repo
# ────────────────────────────────────────────────────────────────────

def sh(cmd, **kwargs):
    result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    if result.returncode != 0:
        print(f"CMD FAILED: {' '.join(cmd)}", file=sys.stderr)
        print(f"STDERR: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()

def gh_api(method, endpoint, payload=None):
    cmd = ["gh", "api", endpoint, "--method", method, "--jq", "."]
    env = os.environ.copy()
    payload_file = None
    if payload is not None:
        payload_file = f"/tmp/gh_payload_{int(time.time()*1000)}.json"
        with open(payload_file, "w") as f:
            json.dump(payload, f)
        cmd.extend(["--input", payload_file])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, env=env)
    finally:
        if payload_file and os.path.exists(payload_file):
            try: os.remove(payload_file)
            except OSError: pass
    if result.returncode != 0:
        print(f"GH API FAILED: {' '.join(cmd)}", file=sys.stderr)
        print(f"STDERR: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)

# ── Step 1: Get remote HEAD and tree ────────────────────────────────
print("=== Step 1: Getting remote HEAD and tree ===")
main_ref = gh_api("GET", f"/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}")
remote_head_sha = main_ref["object"]["sha"]
remote_commit = gh_api("GET", f"/repos/{OWNER}/{REPO}/git/commits/{remote_head_sha}")
remote_tree_sha = remote_commit["tree"]["sha"]
print(f"  Remote HEAD: {remote_head_sha[:12]}")

tree_data = gh_api("GET", f"/repos/{OWNER}/{REPO}/git/trees/{remote_tree_sha}?recursive=1")
remote_entries = tree_data.get("tree", [])
# Build lookup: path → entry (files/blobs only, skip directory entries)
remote_blob_map = {}
for e in remote_entries:
    if e.get("type") == "blob":            # skip directory entries
        remote_blob_map[e["path"]] = e
print(f"  Remote tree: {len(remote_blob_map)} blob entries")

# ── Step 2: Get local tree from the committed state ─────────────────
os.chdir(str(WORKTREE))  # ensure we're in the cloned repo
local_raw = sh(["git", "ls-tree", "-r", "HEAD"])
local_entries = {}
for line in local_raw.strip().split("\n"):
    if not line.strip():
        continue
    parts = line.split(None, 3)  # mode type sha path
    mode, obj_type, sha, path = parts
    # Only care about profile files and root-level files
    if path.startswith(f"{PROFILE}/") or path == ".gitignore":
        local_entries[path] = {"mode": mode, "type": obj_type, "sha": sha}
print(f"  Local tree: {len(local_entries)} tracked files in scope")

# ── Step 3: Diff to find changed/new/deleted ────────────────────────
changed = []   # files with different SHA
new_files = [] # files in local but not in remote
for path, local in local_entries.items():
    remote = remote_blob_map.get(path)
    if remote is None:
        new_files.append(path)
    elif remote.get("sha") != local["sha"]:
        changed.append(path)

deleted = [p for p in remote_blob_map
           if (p.startswith(f"{PROFILE}/") or p == ".gitignore")
           and p not in local_entries]

print(f"  Modified: {len(changed)}, New: {len(new_files)}, Deleted: {len(deleted)}")
for p in changed:  print(f"    M  {p}")
for p in new_files: print(f"    A  {p}")
for p in deleted:  print(f"    D  {p}")

# ── Step 4: Upload blobs for changed/new files ─────────────────────
print("=== Step 4: Creating blobs ===")
new_tree_entries = []
added_paths = set()

def add_entry(path, mode, obj_type, sha):
    if path in added_paths:
        return
    added_paths.add(path)
    new_tree_entries.append({"path": path, "mode": mode, "type": obj_type, "sha": sha})

all_to_upload = changed + new_files
print(f"  Uploading {len(all_to_upload)} blobs...")
for path in all_to_upload:
    full_path = WORKTREE / path
    if not full_path.is_file():
        print(f"    WARN: {path} not found, skipping")
        continue
    with open(full_path, "rb") as f:
        content = f.read()
    content_b64 = base64.b64encode(content).decode("ascii")
    blob = gh_api("POST", f"/repos/{OWNER}/{REPO}/git/blobs", {
        "content": content_b64, "encoding": "base64"
    })
    entry = local_entries[path]
    add_entry(path, entry["mode"], entry["type"], blob["sha"])
    print(f"    BLOB {path}: {blob['sha'][:12]}")

# ── Step 5: Copy unchanged entries (skip deleted) ──────────────────
unchanged = 0
for path, entry in remote_blob_map.items():
    if path in added_paths:
        continue
    if path.startswith(f"{PROFILE}/") or path == ".gitignore":
        if path not in deleted:  # actively deleted files are omitted
            add_entry(path, entry["mode"], entry["type"], entry["sha"])
            unchanged += 1
print(f"  {unchanged} unchanged entries merged")

# ── Step 6: Create tree ─────────────────────────────────────────────
print("=== Step 5: Creating tree ===")
new_tree = gh_api("POST", f"/repos/{OWNER}/{REPO}/git/trees", {"tree": new_tree_entries})
new_tree_sha = new_tree["sha"]
print(f"  Tree: {new_tree_sha}")

# ── Step 7: Create commit ───────────────────────────────────────────
print("=== Step 6: Creating commit ===")
now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
commit_payload = {
    "message": f"backup: {PROFILE} {time.strftime('%Y-%m-%d')}",
    "tree": new_tree_sha,
    "parents": [remote_head_sha],
    "author": {"name": "Hermes Backup", "email": "hermes@nousresearch.com", "date": now}
}
new_commit = gh_api("POST", f"/repos/{OWNER}/{REPO}/git/commits", commit_payload)
new_commit_sha = new_commit["sha"]
print(f"  Commit: {new_commit_sha}")

# ── Step 8: Update ref ──────────────────────────────────────────────
print("=== Step 7: Updating ref ===")
gh_api("PATCH", f"/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}",
       {"sha": new_commit_sha, "force": False})
print("  Ref updated!")

# ── Step 9: Verify ──────────────────────────────────────────────────
verify = gh_api("GET", f"/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}")
print(f"  Remote HEAD: {verify['object']['sha']}")
assert verify['object']['sha'] == new_commit_sha, "Ref mismatch!"

# Quick spot-check: verify a sample file landed
sample = gh_api("GET", f"/repos/{OWNER}/{REPO}/contents/{PROFILE}/cron/jobs.json")
print(f"  Spot-check cron/jobs.json SHA: {sample['sha'][:12]}")

print(f"\nDone: https://github.com/{OWNER}/{REPO}/commit/{new_commit_sha}")
