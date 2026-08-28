#!/usr/bin/env python3
"""Preflight backup scan: compute the M/A/D diff vs remote and scan ONLY upload
candidates (changed + new files) for token patterns.

Run BEFORE the backup script (any method). This is the real security gate:
it predicts exactly which files would be uploaded, so you can discover exclude
gaps and redaction needs BEFORE any blob reaches GitHub (push protection does
NOT reliably catch hex/base64-encoded tokens — see SKILL.md pitfalls).

Discovered-exclude workflow (verified 2026-08-27):
1. Run this preflight.
2. If NEW files show token patterns that shouldn't be backed up (e.g. temp
   diagnostic scripts that read .env), patch the backup script's EXCLUDE_*
   sets (and the SKILL.md exclude lists) FIRST.
3. Re-run preflight until diff + scan are clean.
4. Then run scripts/gh-api-standalone-subtree-backup.py.

Caught 3 exclude gaps on 2026-08-27:
- tmp_triage/ dir (7 files, 3 with token patterns: fetch_*.sh, healthcheck_*.py)
- gh_health_*.sh (root-level diagnostics that source .env and export GH_TOKEN)
- healthcheck_*.py (root-level diagnostics that read .env for GITHUB_TOKEN)

Usage:
  REPO_OWNER=OnePlusNPM python3 /tmp/preflight-backup-scan.py

NOTE: EXCLUDE_* sets below must stay in sync with
scripts/gh-api-standalone-subtree-backup.py and the rsync/.gitignore lists in
SKILL.md.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

OWNER = os.environ.get("REPO_OWNER", "OnePlusNPM")
REPO = "hermes-config"
BRANCH = "main"
PROFILE_DIR = Path(os.path.expanduser("~/.hermes/profiles/demo-pm"))
PROFILE = "demo-pm"

EXCLUDE_NAMES = {
    ".env", "auth.json", "auth.lock",
    "state.db", "state.db-shm", "state.db-wal",
    ".hermes_history", "interrupt_debug.log", "processes.json",
    ".update_check", ".skills_prompt_snapshot.json",
    "triage_check.py", "cron_triage.py", "triage_issues.py",
    "triage_v5.py", "triage_fetch.py", "query_issues.py",
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


def should_exclude(rel_path):
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


def collect_local_files(base_dir):
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


def gh_api(method, endpoint):
    cmd = ["gh", "api", endpoint, "--method", method, "--jq", "."]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if result.returncode != 0:
        print(f"GH API error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


def main():
    print("=== Preflight: diff + token scan ===")
    local_files = collect_local_files(PROFILE_DIR)
    local_path_set = {f"{PROFILE}/{rel}" for rel, _ in local_files}
    print(f"Local files (after excludes): {len(local_files)}")

    main_ref = gh_api("GET", f"/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}")
    remote_head_sha = main_ref["object"]["sha"]
    remote_commit = gh_api("GET", f"/repos/{OWNER}/{REPO}/git/commits/{remote_head_sha}")
    remote_tree_sha = remote_commit["tree"]["sha"]
    tree_data = gh_api("GET", f"/repos/{OWNER}/{REPO}/git/trees/{remote_tree_sha}?recursive=1")
    remote_blob_map = {e["path"]: e for e in tree_data.get("tree", []) if e.get("type") == "blob"}
    print(f"Remote HEAD: {remote_head_sha[:12]}  blobs: {len(remote_blob_map)}")

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
    print(f"Modified: {len(changed)}, New: {len(new_files)}, Deleted: {len(deleted)}")
    for rp, _ in changed:
        print(f"  M  {rp}")
    for rp, _ in new_files:
        print(f"  A  {rp}")
    for p in deleted:
        print(f"  D  {p}")

    if not changed and not new_files and not deleted:
        print("NO CHANGES - nothing to do")
        return 0

    # Scan only files that will be uploaded (changed + new) for token patterns
    print("\n=== Token scan on upload candidates ===")
    pat_full = re.compile(r"ghp_[A-Za-z0-9]{20,}|gho_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}")
    pat_hex = re.compile(r"6768705f[0-9a-f]{20,}")
    pat_b64 = re.compile(r"R0lUSFVC[0-9A-Za-z+/=]{15,}")
    issues = []
    for repo_path, full_path in changed + new_files:
        with open(full_path, "rb") as f:
            content = f.read()
        text = content.decode("utf-8", errors="replace")
        m1 = pat_full.findall(text)
        m2 = pat_hex.findall(text)
        m3 = pat_b64.findall(text)

        def real(matches):
            return [m for m in matches if "xxx" not in m and "..." not in m and "xx" not in m]

        r1, r2, r3 = real(m1), real(m2), real(m3)
        if r1 or r2 or r3:
            issues.append((repo_path, r1[:3], r2[:3], r3[:3]))

    if issues:
        print("POTENTIAL TOKEN HITS (review before upload; decode base64 hits with "
              "'echo ... | base64 -d | xxd' to triage doc examples like GITHUB_TOKEN=***):")
        for rel, m1, m2, m3 in issues:
            print(f"  {rel}: ghp={m1} hex={m2} b64={m3}")
    else:
        print("CLEAN - no full token patterns in upload candidates")

    print("\n=== Preflight complete ===")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
