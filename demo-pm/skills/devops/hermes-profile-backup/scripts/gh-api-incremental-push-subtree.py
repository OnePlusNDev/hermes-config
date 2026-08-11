#!/usr/bin/env python3
"""Incremental push via GitHub Git Data API with RECURSIVE SUBTREE construction.

Use when `git push` fails (HTTP2 framing layer / port 443) but `gh api` works,
AND the repo is large enough that a flat tree POST fails with:
    HTTP 422 "Sorry, your request timed out. It's likely that your input was
    too large to process."
(Verified 2026-08-10: 589 blobs total -> flat tree POST rejected; the old
`references/gh-api-git-data-incremental-push.py` builds a flat tree and hits
this. Blob uploads are idempotent, so re-running after a 422 costs nothing.)

Strategy: diff remote tree vs local `git ls-tree -r HEAD`, upload only
changed/new blobs, then build the tree HIERARCHICALLY — each subdirectory
becomes its own tree object — and finally a small top-level tree that copies
the base tree entries and replaces only the PROFILE entry with the subtree SHA
(sibling profile dirs are preserved automatically).

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
WORKTREE = Path("/tmp/hermes-backup-0000000000")  # cloned repo path
PROFILE = "demo-pm"                         # subdirectory in the repo
# ────────────────────────────────────────────────────────────────────

def sh(cmd, **kwargs):
    result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    if result.returncode != 0:
        print(f"CMD FAILED: {' '.join(cmd)}", file=sys.stderr)
        print(f"STDERR: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()

def gh_api(method, endpoint, payload=None, retries=3):
    cmd = ["gh", "api", endpoint, "--method", method, "--jq", "."]
    payload_file = None
    if payload is not None:
        payload_file = f"/tmp/gh_payload_{int(time.time()*1000)}_{os.getpid()}.json"
        with open(payload_file, "w") as f:
            json.dump(payload, f)
        cmd.extend(["--input", payload_file])
    last_err = None
    for attempt in range(retries):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    timeout=180, env=os.environ.copy())
        except subprocess.TimeoutExpired:
            last_err = "timeout"
            continue
        if result.returncode != 0:
            last_err = result.stderr
            # 422 too-large is NOT retryable — abort so we don't burn cycles
            if "timed out" in result.stderr or "too large" in result.stderr:
                print(f"GH API NON-RETRYABLE FAILURE: {result.stderr}", file=sys.stderr)
                sys.exit(2)
            time.sleep(2 * (attempt + 1))
            continue
        return json.loads(result.stdout)
    print(f"GH API FAILED after {retries} tries: {last_err}", file=sys.stderr)
    sys.exit(1)

# ── Step 1: remote HEAD + top-level tree ──────────────────────────────
print("=== Step 1: remote state ===")
main_ref = gh_api("GET", f"/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}")
remote_head_sha = main_ref["object"]["sha"]
remote_commit = gh_api("GET", f"/repos/{OWNER}/{REPO}/git/commits/{remote_head_sha}")
remote_tree_sha = remote_commit["tree"]["sha"]
print(f"  Remote HEAD: {remote_head_sha}")

# Full recursive tree for diffing
tree_data = gh_api("GET", f"/repos/{OWNER}/{REPO}/git/trees/{remote_tree_sha}?recursive=1")
remote_blob_map = {e["path"]: e for e in tree_data.get("tree", []) if e.get("type") == "blob"}
print(f"  Remote blobs: {len(remote_blob_map)}")

# ── Step 2: local tree (committed state) ──────────────────────────────
os.chdir(str(WORKTREE))
local_raw = sh(["git", "ls-tree", "-r", "HEAD"])
local_entries = {}
for line in local_raw.strip().split("\n"):
    if not line.strip():
        continue
    parts = line.split(None, 3)
    mode, obj_type, sha, path = parts
    if path.startswith(f"{PROFILE}/") or path == ".gitignore":
        local_entries[path] = {"mode": mode, "type": obj_type, "sha": sha}
print(f"  Local tracked in scope: {len(local_entries)}")

# ── Step 3: diff ──────────────────────────────────────────────────────
changed = [p for p, l in local_entries.items() if remote_blob_map.get(p, {}).get("sha") != l["sha"]]
new_files = [p for p in local_entries if p not in remote_blob_map]
deleted = [p for p in remote_blob_map
           if (p.startswith(f"{PROFILE}/") or p == ".gitignore") and p not in local_entries]
print(f"  Modified: {len(changed)}, New: {len(new_files)}, Deleted: {len(deleted)}")
for p in changed: print(f"    M  {p}")
for p in new_files: print(f"    A  {p}")
for p in deleted: print(f"    D  {p}")

# ── Step 4: upload blobs ──────────────────────────────────────────────
print("=== Step 4: uploading blobs ===")
uploaded_sha = {}
for path in changed + new_files:
    full_path = WORKTREE / path
    if not full_path.is_file():
        print(f"    WARN: {path} not found, skipping")
        continue
    with open(full_path, "rb") as f:
        content = f.read()
    content_b64 = base64.b64encode(content).decode("ascii")
    blob = gh_api("POST", f"/repos/{OWNER}/{REPO}/git/blobs",
                  {"content": content_b64, "encoding": "base64"})
    uploaded_sha[path] = blob["sha"]
    print(f"    BLOB {path}: {blob['sha'][:12]}")

# ── Step 5: build PROFILE subtree recursively ─────────────────────────
print("=== Step 5: building tree (recursive) ===")
profile_rel = {}
for path, entry in local_entries.items():
    if path == ".gitignore":
        continue
    rel = path[len(PROFILE) + 1:]
    profile_rel[rel] = {"mode": entry["mode"], "type": entry["type"],
                        "sha": uploaded_sha.get(path, entry["sha"])}

def build_tree(entries, prefix=""):
    """entries: dict rel_path -> {mode,type,sha}. Build tree recursively.

    Each subdirectory becomes its own tree object — this keeps every POST
    small and avoids the flat-tree 422 'input too large' failure.
    """
    by_dir = {}
    direct = []
    for rel, entry in entries.items():
        if "/" in rel:
            top, rest = rel.split("/", 1)
            by_dir.setdefault(top, {})[rest] = entry
        else:
            direct.append({"path": rel, "mode": entry["mode"], "type": entry["type"], "sha": entry["sha"]})
    tree_items = []
    for d in sorted(by_dir):
        sub_sha = build_tree(by_dir[d], prefix + d + "/")
        tree_items.append({"path": d, "mode": "040000", "type": "tree", "sha": sub_sha})
    tree_items.extend(direct)
    created = gh_api("POST", f"/repos/{OWNER}/{REPO}/git/trees", {"tree": tree_items})
    return created["sha"]

profile_tree_sha = build_tree(profile_rel)
print(f"  {PROFILE} subtree: {profile_tree_sha}")

# ── Step 6: top-level tree — copy base entries, replace PROFILE ───────
base_tree = gh_api("GET", f"/repos/{OWNER}/{REPO}/git/trees/{remote_tree_sha}")
top_items = []
for entry in base_tree.get("tree", []):
    if entry.get("type") != "tree":
        top_items.append(entry)
    elif entry.get("path") == PROFILE:
        top_items.append({"path": PROFILE, "mode": "040000", "type": "tree", "sha": profile_tree_sha})
    else:
        top_items.append(entry)  # preserve sibling dirs (demo-dev/, demo-tester/, ...)
top_tree = gh_api("POST", f"/repos/{OWNER}/{REPO}/git/trees", {"tree": top_items})
print(f"  top tree: {top_tree['sha']}")

# ── Step 7: commit ────────────────────────────────────────────────────
print("=== Step 7: creating commit ===")
now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
commit_payload = {
    "message": f"backup: {PROFILE} {time.strftime('%Y-%m-%d')}",
    "tree": top_tree["sha"],
    "parents": [remote_head_sha],
    "author": {"name": "Hermes Backup", "email": "hermes@nousresearch.com", "date": now},
    "committer": {"name": "Hermes Backup", "email": "hermes@nousresearch.com", "date": now},
}
new_commit = gh_api("POST", f"/repos/{OWNER}/{REPO}/git/commits", commit_payload)
print(f"  Commit: {new_commit['sha']}")

# ── Step 8: update ref ────────────────────────────────────────────────
print("=== Step 8: updating ref ===")
gh_api("PATCH", f"/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}",
       {"sha": new_commit["sha"], "force": False})
verify = gh_api("GET", f"/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}")
assert verify["object"]["sha"] == new_commit["sha"], "Ref mismatch!"
print(f"  Remote HEAD now: {verify['object']['sha']}")
print(f"\nDone: https://github.com/{OWNER}/{REPO}/commit/{new_commit['sha']}")
