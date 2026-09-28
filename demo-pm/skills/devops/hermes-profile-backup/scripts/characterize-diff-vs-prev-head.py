#!/usr/bin/env python3
"""Characterize the M set of a backup commit: show WHY each modified local file
changed, by diffing it against its blob at the PRE-PUSH remote HEAD.

Run this AFTER the push, before writing the run note. The run-note template asks
for each `M` to be classified as routine runtime churn vs benign carry-over doc
lag; this script produces the evidence instead of eyeballing blob SHAs.

USAGE
  python3 scripts/characterize-diff-vs-prev-head.py <PRE_PUSH_HEAD_SHA>
  python3 scripts/characterize-diff-vs-prev-head.py --commit=<backup_commit_sha>
  # no argument: derives PRE_PUSH_HEAD as parents[0] of the current remote branch
  #              HEAD (correct ONLY if no sibling commit landed after yours)

<PRE_PUSH_HEAD_SHA> is the SHA the backup script logged as `Remote HEAD:` at
Step 2 of the clean attempt. It is also parents[0] of your backup commit, which
--commit= derives for you.

PITFALL - why the argument exists (verified 2026-09-27):
  Do NOT diff against the CURRENT remote HEAD. Right after a successful push the
  current remote tree EQUALS local, so every file compares IDENTICAL and you
  learn nothing. A naive `gh api repos/O/R/contents/<path>` fetch with no `ref=`
  hits the same trap (it returns what you just pushed). You must name the HEAD
  that was current BEFORE your commit.

ASCII-only on purpose: emoji / Unicode variation selectors are blocked by the
tirith scanner in cron mode.

The EXCLUDE_* sets MUST stay in sync with scripts/preflight-backup-scan.py,
scripts/gh-api-standalone-subtree-backup.py, the rsync list in SKILL.md and
templates/gitignore-template.txt. A first cut of this probe that skipped the
excludes reported ADDED 11468 (every .tmp_*, cache/, logs/, cron/output/ file);
the excludes are what turn that noise into ADDED 0.
"""
import base64
import difflib
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

# -- Config ---------------------------------------------------------------
OWNER = os.environ.get("REPO_OWNER", "OnePlusNDev")
REPO = os.environ.get("REPO", "hermes-config")
BRANCH = os.environ.get("BRANCH", "main")
PROFILE = os.environ.get("PROFILE", "demo-pm")
PROFILE_DIR = Path(os.path.expanduser(f"~/.hermes/profiles/{PROFILE}"))
DIFF_CONTEXT = int(os.environ.get("DIFF_CONTEXT", "1"))
MAX_DIFF_LINES = int(os.environ.get("MAX_DIFF_LINES", "60"))
# -------------------------------------------------------------------------

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
    ".bundled_manifest", ".curator_state", ".curator_suppressed",
    "response_store.db", "feishu_seen_message_ids.json",
}
EXCLUDE_DIRS = {
    "logs", "cache", "sessions", "desktop", "sandboxes",
    "audio_cache", "image_cache", "pairing", "plans",
    "hooks", "skins", "workspace", ".local", "home", "bin",
    "hindsight-maintenance-logs",
    "lsp", ".hub", ".curator_backups", ".curator_state",
    # Curator-managed archive of stale bundled skills (same family as
    # .curator_backups -> excluded; recoverable via `hermes curator restore`).
    ".archive",
    "tmp_triage",
    "__pycache__",
}
EXCLUDE_PREFIX = {"config.yaml.bak.", ".tmp_", "tmp_", "memory_backup_", "._",
                  "pm_triage_", "pm_health", "gh_health", "healthcheck_"}
CRON_EXCLUDE = {".jobs.lock", ".tick.lock", "ticker_heartbeat", "ticker_last_success"}


def gh_json(path):
    r = subprocess.run(["gh", "api", path], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(f"gh api {path} failed: {r.stderr.strip()[:200]}")
    return json.loads(r.stdout)


def git_blob_sha(data):
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


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
    # Root-level health_* diagnostics read .env. Scoped to root so nested legit
    # files (e.g. skills/creative/comfyui/scripts/health_check.py) survive.
    if len(parts) == 1 and fname.startswith("health_"):
        return True
    # Root-level tmp dirs hold PM-triage diagnostics that read .env.
    if parts[0] in ("tmp", "tmp_pm"):
        return True
    if "cron" in parts and "output" in parts:
        return True
    if ".bak" in fname:
        return True
    if fname.endswith("_cache.json"):
        return True
    return False


def local_entries():
    out = {}
    root_str = str(PROFILE_DIR)
    for root, dirs, fnames in os.walk(root_str):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS
                   and not (root == root_str and d in ("tmp", "tmp_pm"))]
        for f in fnames:
            fp = Path(root) / f
            rel = str(fp.relative_to(PROFILE_DIR)).replace(os.sep, "/")
            if should_exclude(rel):
                continue
            try:
                out[rel] = git_blob_sha(fp.read_bytes())
            except OSError:
                continue
    return out


def resolve_prev_head(argv):
    for a in argv[1:]:
        if a.startswith("--commit="):
            sha = a.split("=", 1)[1]
            c = gh_json(f"repos/{OWNER}/{REPO}/git/commits/{sha}")
            return c["parents"][0]["sha"], f"parents[0] of commit {sha[:12]}"
        if a.startswith("--"):
            sys.exit(f"unknown option {a}")
        return a, "explicit argv"
    head = gh_json(f"repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}")["object"]["sha"]
    c = gh_json(f"repos/{OWNER}/{REPO}/git/commits/{head}")
    print(f"NOTE: no PRE_PUSH_HEAD given - derived parents[0] of current {BRANCH} "
          f"({head[:12]}). Correct ONLY if no sibling commit landed after yours.")
    return c["parents"][0]["sha"], "derived from current HEAD parents[0]"


def blob_text(sha):
    data = gh_json(f"repos/{OWNER}/{REPO}/git/blobs/{sha}")
    return base64.b64decode(data["content"]).decode("utf-8", "replace")


def hint_for(rel):
    if rel == "cron/jobs.json" or rel.startswith("memories/"):
        return "runtime churn (cron counters / memory archive row) - expected"
    if rel.endswith(".md"):
        return "doc edit - benign carry-over lag IF written after the last push"
    return "inspect the diff"


def main():
    prev_head, how = resolve_prev_head(sys.argv)
    print(f"=== Characterize M set: {OWNER}/{REPO} {PROFILE}/ ===")
    print(f"PREV_HEAD (pre-push): {prev_head}   [{how}]")

    tree = gh_json(f"repos/{OWNER}/{REPO}/git/trees/{prev_head}?recursive=1")
    remote = {e["path"]: e["sha"] for e in tree["tree"] if e["type"] == "blob"}
    remote_profile = {p[len(PROFILE) + 1:]: s for p, s in remote.items()
                      if p.startswith(PROFILE + "/")}
    local = local_entries()

    modified = sorted(r for r, s in local.items()
                      if r in remote_profile and remote_profile[r] != s)
    added = sorted(r for r in local if r not in remote_profile)
    deleted = sorted(r for r in remote_profile if r not in local)

    print(f"local files: {len(local)}   remote(at PREV_HEAD): {len(remote_profile)}")
    print(f"MODIFIED {len(modified)}   ADDED {len(added)}   DELETED {len(deleted)}")
    if added:
        print("  (ADDED should be 0 in steady state - a non-zero value means the "
              "local set here disagrees with the backup set; check EXCLUDE sync)")

    for r in modified:
        print(f"\n--- M {PROFILE}/{r}   hint: {hint_for(r)}")
        old = blob_text(remote_profile[r]).splitlines()
        new = (PROFILE_DIR / r).read_text(encoding="utf-8", errors="replace").splitlines()
        d = list(difflib.unified_diff(old, new, "prev", "local",
                                      lineterm="", n=DIFF_CONTEXT))
        if not d:
            print("    (no textual diff - binary or whitespace-only)")
        else:
            print("\n".join(d[:MAX_DIFF_LINES]))
            if len(d) > MAX_DIFF_LINES:
                print(f"    ... {len(d) - MAX_DIFF_LINES} more diff lines")

    for r in added:
        print(f"\n--- A {PROFILE}/{r}   (new file - no prev blob)")
    for r in deleted:
        print(f"\n--- D {PROFILE}/{r}")

    print("\n=== done ===")


if __name__ == "__main__":
    main()
