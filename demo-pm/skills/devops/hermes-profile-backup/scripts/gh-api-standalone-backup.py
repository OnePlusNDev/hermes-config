#!/usr/bin/env python3
"""
Standalone gh API Git Data backup — no local git clone required.

Use this when `gh repo clone` fails (port 443 timeout) but `gh api` works.
Unlike references/gh-api-git-data-incremental-push.py, this script does NOT
need a cloned repo: it computes blob SHAs directly from file contents using
hashlib.sha1(f"blob {size}\\0{content}"), collects files by walking the
profile directory, and compares against the remote tree.

Usage:
  python3 /tmp/gh-api-standalone-backup.py

Modify the CONFIG section at the top for your environment.
"""
import base64
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# ══════════════════════ CONFIG ══════════════════════
# Resolve OWNER dynamically from gh CLI — works for any GitHub user
import subprocess as _sp
_owner_result = _sp.run(["gh", "api", "user", "--jq", ".login"], capture_output=True, text=True, timeout=15)
OWNER = _owner_result.stdout.strip() if _owner_result.returncode == 0 else "OnePlusNDev"

REPO = "hermes-config"
BRANCH = "main"
PROFILE_DIR = Path(os.path.expanduser("~/.hermes/profiles/demo-pm"))
PROFILE = "demo-pm"  # subdirectory in the repo
# ════════════════════════════════════════════════════

# ── rsync-style excludes ──────────────────────────
EXCLUDE_NAMES = {
    ".env", "auth.json", "auth.lock",
    "state.db", "state.db-shm", "state.db-wal",
    ".hermes_history", "interrupt_debug.log", "processes.json",
    ".update_check", ".skills_prompt_snapshot.json",
    "triage_check.py", "cron_triage.py",
    "gateway.lock", "gateway.pid", "gateway_state.json",
    ".usage.json", ".usage.json.lock",
    ".bundled_manifest", ".curator_state",
    # NOTE: reference files with encoded tokens should be pre-scanned and
    # redacted before backup (see SKILL.md: push protection pitfalls).
    # The graceful fallback below handles any that slip through.
}
EXCLUDE_DIRS = {
    "logs", "cache", "sessions", "desktop", "sandboxes",
    "audio_cache", "image_cache", "pairing", "plans",
    "hooks", "skins", "workspace", ".local", "home", "bin",
    "hindsight-maintenance-logs",
    "lsp",
    ".hub", ".curator_backups", ".curator_state",
}
EXCLUDE_PREFIX = {"config.yaml.bak.", ".tmp_"}
CRON_EXCLUDE = {".jobs.lock", ".tick.lock", "ticker_heartbeat", "ticker_last_success"}

def git_blob_hash(filepath):
    """Compute a git blob SHA1 without a git repo."""
    with open(filepath, "rb") as f:
        data = f.read()
    blob = f"blob {len(data)}\0".encode() + data
    return hashlib.sha1(blob).hexdigest()


def should_exclude(rel_path: str) -> bool:
    parts = rel_path.split("/")
    fname = parts[-1]

    # Dir exclusion at any depth
    for p in parts[:-1]:
        if p in EXCLUDE_DIRS:
            return True

    # File basename
    if fname in EXCLUDE_NAMES:
        return True

    # Prefix-based
    for prefix in EXCLUDE_PREFIX:
        if fname.startswith(prefix):
            return True

    # Cron artifacts
    if fname in CRON_EXCLUDE:
        return True

    # cron/output/ — everything under it
    if "cron" in parts and "output" in parts:
        return True

    # *.bak* at any depth
    if ".bak" in fname:
        return True

    # *_cache.json
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
        return None, result.stderr.strip()
    return json.loads(result.stdout), None


# ── Step 1: Collect local files ──────────────────
print("=== Step 1: Collecting local files ===")
local_files = collect_local_files(PROFILE_DIR)
local_path_set = {f"{PROFILE}/{rel}" for rel, _ in local_files}
print(f"  Found {len(local_files)} files to back up")

# ── Step 2: Get remote tree ─────────────────────
print("\n=== Step 2: Getting remote tree ===")
main_ref, err = gh_api("GET", f"/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}")
if err:
    print(f"FATAL: {err}")
    sys.exit(1)
remote_head_sha = main_ref["object"]["sha"]
remote_commit, err = gh_api("GET", f"/repos/{OWNER}/{REPO}/git/commits/{remote_head_sha}")
if err:
    print(f"FATAL: {err}")
    sys.exit(1)
remote_tree_sha = remote_commit["tree"]["sha"]
print(f"  Remote HEAD: {remote_head_sha[:12]}")

tree_data, err = gh_api("GET",
    f"/repos/{OWNER}/{REPO}/git/trees/{remote_tree_sha}?recursive=1")
if err:
    print(f"FATAL: {err}")
    sys.exit(1)
remote_blob_map = {e["path"]: e for e in tree_data.get("tree", [])
                    if e.get("type") == "blob"}
print(f"  Remote tree: {len(remote_blob_map)} blobs")

# ── Step 3: Diff ────────────────────────────────
print("\n=== Step 3: Computing diff ===")
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

# ── Step 4: Upload blobs ───────────────────────
print("\n=== Step 4: Uploading blobs ===")
new_tree_entries = []
added_paths = set()
skipped_push_protection = []

def add_entry(path, mode, obj_type, sha):
    if path in added_paths:
        return
    added_paths.add(path)
    new_tree_entries.append({"path": path, "mode": mode, "type": obj_type, "sha": sha})

all_to_upload = changed + new_files
for repo_path, full_path in all_to_upload:
    with open(full_path, "rb") as f:
        content = f.read()
    content_b64 = base64.b64encode(content).decode("ascii")
    st = os.stat(full_path)
    mode = "100755" if (st.st_mode & 0o111) else "100644"

    result, err = gh_api("POST", f"/repos/{OWNER}/{REPO}/git/blobs",
                         {"content": content_b64, "encoding": "base64"})
    if err and "Secret detected in content" in err:
        print(f"    ⚠️  SKIPPED {repo_path}: push protection")
        skipped_push_protection.append(repo_path)
        # Fall back to remote version if it existed
        remote = remote_blob_map.get(repo_path)
        if remote:
            add_entry(repo_path, remote["mode"], remote["type"], remote["sha"])
            print(f"       Keeping remote blob {remote['sha'][:12]}")
        continue

    if result is None:
        print(f"    ERROR {repo_path}: {err}")
        sys.exit(1)

    add_entry(repo_path, mode, "blob", result["sha"])
    print(f"    BLOB {repo_path}: {result['sha'][:12]}")

# ── Step 5: Copy unchanged ─────────────────────
unchanged = 0
for path, entry in remote_blob_map.items():
    if path in added_paths:
        continue
    if path.startswith(f"{PROFILE}/") or path == ".gitignore":
        if path not in deleted:
            add_entry(path, entry["mode"], entry["type"], entry["sha"])
            unchanged += 1
print(f"  {unchanged} unchanged merged")

# ── Step 6: Create tree ────────────────────────
print("\n=== Step 5: Creating tree ===")
new_tree, err = gh_api("POST", f"/repos/{OWNER}/{REPO}/git/trees",
                        {"tree": new_tree_entries})
if err:
    print(f"FATAL: tree creation failed: {err}")
    sys.exit(1)
new_tree_sha = new_tree["sha"]

# ── Step 7: Create commit ──────────────────────
print("\n=== Step 6: Creating commit ===")
now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
msg = f"backup: {PROFILE} {time.strftime('%Y-%m-%d')}"
if skipped_push_protection:
    msg += f"\n\nSkipped {len(skipped_push_protection)} push-protected files:\n" + \
           "\n".join(skipped_push_protection)

commit_payload = {
    "message": msg,
    "tree": new_tree_sha,
    "parents": [remote_head_sha],
    "author": {"name": "Hermes Backup", "email": "hermes@nousresearch.com", "date": now},
}
new_commit, err = gh_api("POST", f"/repos/{OWNER}/{REPO}/git/commits", commit_payload)
if err:
    print(f"FATAL: commit creation failed: {err}")
    sys.exit(1)
new_commit_sha = new_commit["sha"]

# ── Step 8: Update ref ─────────────────────────
print("\n=== Step 7: Updating ref ===")
_, err = gh_api("PATCH", f"/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}",
                {"sha": new_commit_sha, "force": False})
if err:
    print(f"FATAL: ref update failed: {err}")
    sys.exit(1)

# ── Step 9: Verify ─────────────────────────────
verify, err = gh_api("GET", f"/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}")
if err:
    print(f"FATAL: verification failed: {err}")
    sys.exit(1)
assert verify['object']['sha'] == new_commit_sha, "Ref mismatch!"
print(f"  Remote HEAD: {verify['object']['sha'][:12]} ✓")

print(f"\nDone: https://github.com/{OWNER}/{REPO}/commit/{new_commit_sha}")
print(f"  Files changed: {len(changed)}, new: {len(new_files)}, deleted: {len(deleted)}")
if skipped_push_protection:
    print(f"  Files skipped (push protection): {len(skipped_push_protection)}")
