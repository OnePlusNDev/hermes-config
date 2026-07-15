#!/usr/bin/env python3
"""Push profile backup files to GitHub via Contents API.

Supports two auth methods, tried in order:
  1. `gh api` (gh CLI must be logged in)
  2. Direct REST API with GITHUB_TOKEN from profile .env (no gh dependency)

Usage:
    python3 backup_profile.py \
        --profile /path/to/.hermes/profiles/tester-01 \
        --repo hermes-tester-01-backup      # owner derived from auth
"""

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


# ── Auth layer ──────────────────────────────────────────────────────────────

def _load_token_from_env(profile: str) -> str | None:
    """Read GITHUB_TOKEN from a profile .env file using regex (avoids shell pitfalls)."""
    env_path = os.path.join(profile, ".env")
    if not os.path.exists(env_path):
        return None
    with open(env_path) as fh:
        for line in fh:
            m = re.match(r"^([A-Z_]+)=(.*)$", line.strip())
            if m and m.group(1) == "GITHUB_TOKEN":
                token = m.group(2)
                if token:
                    return token
    return None


def _gh_available() -> bool:
    """Check if gh CLI is installed and authenticated."""
    result = subprocess.run(["gh", "auth", "status"], capture_output=True)
    return result.returncode == 0


def _get_owner_api(token: str) -> str:
    """Derive GitHub owner from the authenticated user."""
    req = urllib.request.Request(
        "https://api.github.com/user",
        headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "hermes-backup",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())["login"]


def _api_call(token: str, owner: str, repo: str, method: str, path: str, body=None) -> tuple[int, dict]:
    """GitHub REST API call. path is relative to repo contents, or '' for repo root."""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    if path:
        url += f"/contents/{path}"
    headers = {
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "hermes-backup",
    }
    data = json.dumps(body).encode() if body else None
    if data:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, method=method, headers=headers, data=data)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else str(e)
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"message": body}


def _ensure_repo_api(token: str, owner: str, repo: str) -> str:
    """Ensure the backup repo exists; create if missing. Returns html_url."""
    _, repo_data = _api_call(token, owner, repo, "GET", "", None)
    if _ == 200:
        return repo_data.get("html_url", repo_data.get("url", ""))
    # 404 → create
    create_req = urllib.request.Request(
        "https://api.github.com/user/repos",
        method="POST",
        headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "hermes-backup",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "name": repo,
            "description": "Hermes profile backup",
            "private": True,
            "auto_init": True,
        }).encode(),
    )
    with urllib.request.urlopen(create_req) as resp:
        return json.loads(resp.read())["html_url"]


# ── gh CLI wrappers ─────────────────────────────────────────────────────────

def _get_sha_gh(owner: str, repo: str, path: str) -> str | None:
    result = subprocess.run(
        ["gh", "api", f"repos/{owner}/{repo}/contents/{path}", "--jq", ".sha"],
        capture_output=True, text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _push_file_gh(owner: str, repo: str, path: str, local_path: str, sha: str | None, message: str) -> bool:
    with open(local_path, "rb") as f:
        content_b64 = base64.b64encode(f.read()).decode()
    payload = {"message": message, "content": content_b64, "branch": "main"}
    if sha:
        payload["sha"] = sha
    result = subprocess.run(
        ["gh", "api", "-X", "PUT", f"repos/{owner}/{repo}/contents/{path}", "--input", "-"],
        input=json.dumps(payload), capture_output=True, text=True,
    )
    if result.returncode == 0:
        resp = json.loads(result.stdout)
        print(f"  OK  {path}: {resp['content']['size']} bytes, sha={resp['content']['sha'][:8]}")
        return True
    else:
        print(f"  FAIL {path}: {result.stderr[:200]}", file=sys.stderr)
        return False


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Backup Hermes profile to GitHub")
    parser.add_argument("--profile", required=True, help="Absolute path to profile directory")
    parser.add_argument("--repo", required=True, help="GitHub repo name (owner derived from auth)")
    args = parser.parse_args()

    profile = Path(args.profile)
    repo = args.repo
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    message = f"backup: {ts}"

    # Determine auth method
    if _gh_available():
        print("Auth: gh CLI")
        result = subprocess.run(
            ["gh", "api", "user", "--jq", ".login"], capture_output=True, text=True
        )
        owner = result.stdout.strip()
        if not owner:
            print("ERROR: gh auth status OK but cannot get username", file=sys.stderr)
            sys.exit(1)

        def get_sha(p): return _get_sha_gh(owner, repo, p)
        def push_file(p, lp, sha, msg): return _push_file_gh(owner, repo, p, lp, sha, msg)
    else:
        token = _load_token_from_env(str(profile))
        if not token:
            print("ERROR: gh not available and no GITHUB_TOKEN in .env", file=sys.stderr)
            sys.exit(1)
        owner = _get_owner_api(token)
        print(f"Auth: REST API (owner={owner})")
        _ensure_repo_api(token, owner, repo)

        def get_sha(p):
            s, d = _api_call(token, owner, repo, "GET", p, None)
            return d.get("sha") if s == 200 else None

        def push_file(p, lp, sha, msg):
            with open(lp, "rb") as f:
                content = base64.b64encode(f.read()).decode()
            payload = {"message": msg, "content": content, "branch": "main"}
            if sha:
                payload["sha"] = sha
            s, d = _api_call(token, owner, repo, "PUT", p, payload)
            if s in (200, 201):
                short_sha = (d.get("content", {}) or {}).get("sha", "?")[:8]
                print(f"  OK  {p}: {len(content)} bytes, sha={short_sha}")
                return True
            print(f"  FAIL {p}: {d.get('message', d)[:120]}", file=sys.stderr)
            return False

    # Gather files
    files_real = {
        "SOUL.md": str(profile / "SOUL.md"),
        "config.yaml": str(profile / "config.yaml"),
    }
    files_gen = {}

    result = subprocess.run(["hermes", "cron", "list"], capture_output=True, text=True)
    if result.returncode == 0:
        files_gen["cronjobs.txt"] = result.stdout

    result = subprocess.run(["hermes", "skills", "list"], capture_output=True, text=True)
    if result.returncode == 0:
        files_gen["skills.txt"] = result.stdout

    # Verify real files
    for remote, local in list(files_real.items()):
        if not Path(local).exists():
            print(f"WARN: missing: {local}", file=sys.stderr)
            del files_real[remote]

    print(f"\nBackup to {owner}/{repo} at {ts}")
    print(f"Profile: {profile}")
    print(f"Files: {len(files_real) + len(files_gen)}\n")

    success = True

    for remote, local_path in files_real.items():
        sha = get_sha(remote)
        if not push_file(remote, local_path, sha, message):
            success = False

    for remote, content in files_gen.items():
        tmp = f"/tmp/backup_{remote}"
        with open(tmp, "w") as f:
            f.write(content)
        sha = get_sha(remote)
        if not push_file(remote, tmp, sha, message):
            success = False

    print()
    if success:
        print("Backup complete.")
    else:
        print("Backup completed with errors.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
