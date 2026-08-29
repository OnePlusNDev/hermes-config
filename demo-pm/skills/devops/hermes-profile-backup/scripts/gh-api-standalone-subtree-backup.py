#!/usr/bin/env python3
"""Standalone gh API backup for LARGE repos when git clone is unavailable.

Use when BOTH of these hold:
  - `gh repo clone` fails (port 443 timeout) but `gh api` works
  - the repo is large (590+ blobs) so the flat tree POST in
    scripts/gh-api-standalone-backup.py fails with HTTP 422 "too large"

Strategy (merged from standalone + subtree scripts):
  1. Walk the profile dir on disk, apply rsync-style excludes
  2. Compute git blob SHAs via hashlib (no local git repo needed)
  3. Diff against remote tree (recursive)
  4. Upload changed/new blobs (idempotent; graceful fallback on push protection)
  5. Build the demo-pm subtree HIERARCHICALLY (each subdir = own tree object),
     which keeps every POST small and avoids the flat-tree 422
  6. Build top-level tree: copy base entries, replace demo-pm with subtree SHA
     (sibling profile dirs preserved automatically)
  7. Create commit + update ref + verify

Legacy tracked files that are now excluded (e.g. get_token.sh) are dropped from
the remote tree automatically: excluded files are absent from the local set,
so the deleted-diff removes them. No `git rm --cached` needed in Method B.

Verified 2026-08-26 on the 598-blob repo (demo-pm: 579): clone timed out on 443,
script uploaded 4 blobs, pushed clean commit 7013767c54e6, removed legacy
get_token.sh from the remote tree.

Usage:
  REPO_OWNER=OnePlusNDev python3 /tmp/gh-api-standalone-subtree-backup.py
  (REPO_OWNER only needed when active gh user is a collaborator, not the owner)
"""
import base64
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────
OWNER = os.environ.get("REPO_OWNER", "OnePlusNDev")
REPO = "hermes-config"
BRANCH = "main"
PROFILE_DIR = Path(os.path.expanduser("~/.hermes/profiles/demo-pm"))
PROFILE = "demo-pm"
# ────────────────────────────────────────────────────────────────────

EXCLUDE_NAMES = {
    ".env", "auth.json", "auth.lock",
    "state.db", "state.db-shm", "state.db-wal",
    ".hermes_history", "interrupt_debug.log", "processes.json",
    ".update_check", ".skills_prompt_snapshot.json",
    "triage_check.py", "cron_triage.py", "triage_issues.py",
    "triage_v5.py", "triage_fetch.py", "query_issues.py",
    "triage_verify.py",
    "get_token.sh",
    "gateway.lock", "gateway.pid", "gateway_state.json",
    ".usage.json", ".usage.json.lock",
    ".bundled_manifest", ".curator_state",
    "response_store.db", "feishu_seen_message_ids.json",
}
EXCLUDE_DIRS = {
    "logs", "cache", "sessions", "desktop", "sandboxes",
    "audio_cache", "image_cache", "pairing", "plans",
    "hooks", "skins", "workspace", ".local", "home", "bin",
    "hindsight-maintenance-logs",
    "lsp", ".hub", ".curator_backups", ".curator_state",
    "tmp_triage",
}
EXCLUDE_PREFIX = {"config.yaml.bak.", ".tmp_", "tmp_", "memory_backup_", "._",
                  "pm_triage_", "pm_health", "gh_health", "healthcheck_"}
CRON_EXCLUDE = {".jobs.lock", ".tick.lock", "ticker_heartbeat", "ticker_last_success"}


def git_blob_hash(filepath):
    with open(filepath, "rb") as f:
        data = f.read()
    blob = f"blob {len(data)}\0".encode() + data
    return hashlib.sha1(blob).hexdigest()


def should_exclude(rel_path: str) -> bool:
    parts = rel_path.split("/")
    fname = parts[-1]
    for p in parts[:-1]:
        if p in EXCLUDE_DIRS:
            return True
    if fname in EXCLUDE_NAMES:
        return True
    for prefix in EXCLUDE_PREFIX:
        if fname.startswith(prefix):
            return True
    if fname in CRON_EXCLUDE:
        return True
    # Root-level health_* diagnostics read .env (e.g. health_check.py, health_0828.py).
    # Scoped to root: nested legit files (e.g. skills/creative/comfyui/scripts/health_check.py)
    # must NOT be excluded.
    if len(parts) == 1 and fname.startswith("health_"):
        return True
    if "cron" in parts and "output" in parts:
        return True
    if ".bak" in fname:
        return True
    if fname.endswith("_cache.json"):
        return True
    return False


def collect_local_files(base_dir: Path):
    files = []
    for root, dirs, fnames in os.walk(str(base_dir)):
        rel_root = os.path.relpath(root, str(base_dir))
        rel = "." if rel_root == "." else rel_root
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and d not in EXCLUDE_NAMES]
        for fname in fnames:
            rel_path = fname if rel == "." else os.path.join(rel, fname)
            if should_exclude(rel_path):
                continue
            files.append((rel_path, os.path.join(root, fname)))
    files.sort()
    return files


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
            if "timed out" in result.stderr or "too large" in result.stderr:
                print(f"GH API NON-RETRYABLE FAILURE: {result.stderr}", file=sys.stderr)
                sys.exit(2)
            time.sleep(2 * (attempt + 1))
            continue
        return json.loads(result.stdout), None
    return None, last_err


# ── Step 1: collect local files ────────────────────────────────────
print("=== Step 1: collecting local files ===")
local_files = collect_local_files(PROFILE_DIR)
local_path_set = {f"{PROFILE}/{rel}" for rel, _ in local_files}
print(f"  Found {len(local_files)} files to back up")

# ── Step 2: remote state ───────────────────────────────────────────
print("\n=== Step 2: remote state ===")
main_ref, err = gh_api("GET", f"/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}")
if err:
    print(f"FATAL: {err}", file=sys.stderr)
    sys.exit(1)
remote_head_sha = main_ref["object"]["sha"]
remote_commit, err = gh_api("GET", f"/repos/{OWNER}/{REPO}/git/commits/{remote_head_sha}")
if err:
    print(f"FATAL: {err}", file=sys.stderr)
    sys.exit(1)
remote_tree_sha = remote_commit["tree"]["sha"]
tree_data, err = gh_api("GET", f"/repos/{OWNER}/{REPO}/git/trees/{remote_tree_sha}?recursive=1")
if err:
    print(f"FATAL: {err}", file=sys.stderr)
    sys.exit(1)
remote_blob_map = {e["path"]: e for e in tree_data.get("tree", []) if e.get("type") == "blob"}
print(f"  Remote HEAD: {remote_head_sha[:12]}  blobs: {len(remote_blob_map)}")

# ── Step 3: diff ───────────────────────────────────────────────────
print("\n=== Step 3: diff ===")
changed, new_files = [], []
for rel_path, full_path in local_files:
    repo_path = f"{PROFILE}/{rel_path}"
    remote = remote_blob_map.get(repo_path)
    local_sha = git_blob_hash(full_path)
    if remote is None:
        new_files.append((repo_path, full_path))
    elif remote.get("sha") != local_sha:
        changed.append((repo_path, full_path))
deleted = [p for p in remote_blob_map
           if p.startswith(f"{PROFILE}/") and p not in local_path_set]
print(f"  Modified: {len(changed)}, New: {len(new_files)}, Deleted: {len(deleted)}")
for rp, _ in changed:   print(f"    M  {rp}")
for rp, _ in new_files: print(f"    A  {rp}")
for p in deleted:       print(f"    D  {p}")

if not changed and not new_files and not deleted:
    print("\n  No changes. Nothing to commit.")
    sys.exit(0)

# ── Step 4: upload blobs ───────────────────────────────────────────
print("\n=== Step 4: uploading blobs ===")
uploaded_sha = {}
skipped_push_protection = []
for repo_path, full_path in changed + new_files:
    with open(full_path, "rb") as f:
        content = f.read()
    content_b64 = base64.b64encode(content).decode("ascii")
    st = os.stat(full_path)
    mode = "100755" if (st.st_mode & 0o111) else "100644"
    blob, blob_err = gh_api("POST", f"/repos/{OWNER}/{REPO}/git/blobs",
                            {"content": content_b64, "encoding": "base64"})
    if blob is None:
        if blob_err and "Secret detected in content" in blob_err:
            print(f"    SKIPPED {repo_path}: push protection")
            skipped_push_protection.append(repo_path)
        else:
            print(f"FATAL uploading {repo_path}: {blob_err}", file=sys.stderr)
            sys.exit(1)
        continue
    uploaded_sha[repo_path] = {"sha": blob["sha"], "mode": mode}
    print(f"    BLOB {repo_path}: {blob['sha'][:12]}")

# ── Step 5: build PROFILE subtree recursively ──────────────────────
print("\n=== Step 5: building profile subtree (recursive) ===")
# profile_rel: rel_path (without demo-pm/) -> {mode, type, sha}
# For unchanged files use the remote sha; for uploaded use the new blob sha.
# For push-protection skipped files, fall back to the remote version if it
# existed; if it's a brand-new file that was skipped, omit it entirely.
profile_rel = {}
for rel_path, full_path in local_files:
    repo_path = f"{PROFILE}/{rel_path}"
    st = os.stat(full_path)
    mode = "100755" if (st.st_mode & 0o111) else "100644"
    if repo_path in uploaded_sha:
        sha = uploaded_sha[repo_path]["sha"]
    elif repo_path in remote_blob_map:
        sha = remote_blob_map[repo_path]["sha"]
    else:
        print(f"    OMIT {repo_path}: skipped and no remote version")
        continue
    profile_rel[rel_path] = {"mode": mode, "type": "blob", "sha": sha}


def build_tree(entries, prefix=""):
    by_dir = {}
    direct = []
    for rel, entry in entries.items():
        if "/" in rel:
            top, rest = rel.split("/", 1)
            by_dir.setdefault(top, {})[rest] = entry
        else:
            direct.append({"path": rel, "mode": entry["mode"],
                           "type": entry["type"], "sha": entry["sha"]})
    tree_items = []
    for d in sorted(by_dir):
        sub_sha = build_tree(by_dir[d], prefix + d + "/")
        tree_items.append({"path": d, "mode": "040000", "type": "tree", "sha": sub_sha})
    tree_items.extend(direct)
    created, err = gh_api("POST", f"/repos/{OWNER}/{REPO}/git/trees", {"tree": tree_items})
    if err:
        print(f"FATAL tree POST: {err}", file=sys.stderr)
        sys.exit(1)
    return created["sha"]


profile_tree_sha = build_tree(profile_rel)
print(f"  {PROFILE} subtree: {profile_tree_sha}")

# ── Step 6: top-level tree — copy base entries, replace PROFILE ────
base_tree, err = gh_api("GET", f"/repos/{OWNER}/{REPO}/git/trees/{remote_tree_sha}")
if err:
    print(f"FATAL base tree GET: {err}", file=sys.stderr)
    sys.exit(1)
top_items = []
for entry in base_tree.get("tree", []):
    if entry.get("type") != "tree":
        top_items.append(entry)
    elif entry.get("path") == PROFILE:
        top_items.append({"path": PROFILE, "mode": "040000", "type": "tree",
                          "sha": profile_tree_sha})
    else:
        top_items.append(entry)
top_tree, err = gh_api("POST", f"/repos/{OWNER}/{REPO}/git/trees", {"tree": top_items})
if err:
    print(f"FATAL top tree POST: {err}", file=sys.stderr)
    sys.exit(1)
print(f"  top tree: {top_tree['sha']}")

# ── Step 7: commit ─────────────────────────────────────────────────
print("\n=== Step 6: creating commit ===")
now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
msg = f"backup: {PROFILE} {time.strftime('%Y-%m-%d')}"
if skipped_push_protection:
    msg += "\n\nSkipped push-protected files:\n" + "\n".join(skipped_push_protection)
commit_payload = {
    "message": msg,
    "tree": top_tree["sha"],
    "parents": [remote_head_sha],
    "author": {"name": "Hermes Backup", "email": "hermes@nousresearch.com", "date": now},
    "committer": {"name": "Hermes Backup", "email": "hermes@nousresearch.com", "date": now},
}
new_commit, err = gh_api("POST", f"/repos/{OWNER}/{REPO}/git/commits", commit_payload)
if err:
    print(f"FATAL commit: {err}", file=sys.stderr)
    sys.exit(1)
print(f"  Commit: {new_commit['sha']}")

# ── Step 8: update ref ─────────────────────────────────────────────
print("\n=== Step 7: updating ref ===")
_, err = gh_api("PATCH", f"/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}",
                {"sha": new_commit["sha"], "force": False})
if err:
    print(f"FATAL ref update: {err}", file=sys.stderr)
    sys.exit(1)
verify, err = gh_api("GET", f"/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}")
if err:
    print(f"FATAL verification: {err}", file=sys.stderr)
    sys.exit(1)
assert verify["object"]["sha"] == new_commit["sha"], "Ref mismatch!"
print(f"  Remote HEAD now: {verify['object']['sha']}")
print(f"\nDone: https://github.com/{OWNER}/{REPO}/commit/{new_commit['sha']}")
print(f"  Files changed: {len(changed)}, new: {len(new_files)}, deleted: {len(deleted)}")
if skipped_push_protection:
    print(f"  Files skipped (push protection): {len(skipped_push_protection)}")
