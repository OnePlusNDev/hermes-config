#!/usr/bin/env python3
"""Characterize a backup commit's diff AFTER it has already landed on GitHub.

Why this exists: `scripts/characterize-diff-vs-prev-head.py` must run BEFORE the
push (it diffs the local tree against remote-at-PREV). Once the main commit has
landed, `main` == local, so that probe reports every file IDENTICAL and tells you
nothing. This script replays the comparison from the two COMMITS instead: it walks
the PREV commit's tree and the NEW commit's tree, derives the changed path set,
fetches each old blob via `git/blobs/<sha>` and diffs it against the local file.

Output per changed file:
    ##### demo-pm/<path>  (+A/-D)  old_lines=N new_lines=M
        @@ hunk headers, then +/- lines (clipped to 300 chars, max --max-lines)
and a MODIFIED / ADDED / DELETED total block at the end.

Usage (READ-ONLY: no writes, no git ops, safe to run at any point):
    REPO_OWNER=OnePlusNDev python3 -u scripts/characterize-diff-post-push.py \
        <PREV_SHA> [<NEW_SHA|ref>] [--profile demo-pm] [--max-lines 45]

Defaults: NEW = refs/heads/main, profile dir ~/.hermes/profiles/<profile>.

Pitfalls baked in:
- PREV should be a FULL 40-char SHA; short SHAs 404 on /git/commits/<sha>
  (expand via the /commits list endpoint and match on the prefix).
- Files deleted in NEW are listed but not diffed (no local counterpart).
- Always run with `python3 -u` and redirect to a file when the diff is long;
  a piped `2>&1 | tail -N` block-buffers stdout and lets stderr reorder ahead
  of the Summary, which makes a clean run look like it failed.
- Verified 2026-11-14 as the post-push fallback for the daily demo-pm run note
  (7-file M set, per-file +10/-10, +1/-1, +1/-1, +1/-0, +42/-0, +20/-2, +7/-1).
"""
import argparse
import base64
import difflib
import json
import os
import subprocess
import sys

OWNER = os.environ.get("REPO_OWNER", "OnePlusNDev")
REPO = os.environ.get("REPO_NAME", "hermes-config")


def gh(path):
    proc = subprocess.run(["gh", "api", path], capture_output=True, text=True, timeout=180)
    if proc.returncode != 0:
        sys.stderr.write("gh api failed: %s\n%s\n" % (path, proc.stderr[:400]))
        sys.exit(2)
    return json.loads(proc.stdout)


def blobs(treeish):
    """path -> blob sha for every FILE (tree entries skipped) in the given tree."""
    tree = gh("/repos/%s/%s/git/trees/%s?recursive=1" % (OWNER, REPO, treeish))
    return {e["path"]: e["sha"] for e in tree["tree"] if e["type"] == "blob"}


def local_lines(profile_dir, repo_path, profile):
    fp = os.path.join(profile_dir, repo_path[len(profile) + 1:])
    if not os.path.isfile(fp):
        return None
    with open(fp, encoding="utf-8", errors="replace") as fh:
        return fh.read().splitlines(keepends=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prev", help="PREV commit SHA (full 40 chars preferred)")
    ap.add_argument("new", nargs="?", default="refs/heads/main")
    ap.add_argument("--profile", default="demo-pm")
    ap.add_argument("--max-lines", type=int, default=45)
    args = ap.parse_args()

    profile_dir = os.path.expanduser("~/.hermes/profiles/%s" % args.profile)
    prefix = args.profile + "/"

    old = blobs(args.prev)
    new = blobs(args.new)

    changed, added, deleted, identical = [], [], [], 0
    for path, sha in new.items():
        if not path.startswith(prefix):
            continue
        if path not in old:
            added.append(path)
        elif old[path] != sha:
            changed.append(path)
        else:
            identical += 1
    for path in old:
        if path.startswith(prefix) and path not in new:
            deleted.append(path)

    print("PREV=%s  NEW=%s  profile=%s" % (args.prev[:12], args.new, args.profile))
    print("prev blobs=%d new blobs=%d | identical=%d" % (len(old), len(new), identical))

    for path in sorted(changed):
        blob = gh("/repos/%s/%s/git/blobs/%s" % (OWNER, REPO, old[path]))
        raw = base64.b64decode(blob["content"]).decode("utf-8", "replace")
        before = raw.splitlines(keepends=True)
        after = local_lines(profile_dir, path, args.profile)
        if after is None:
            print("\n##### %s  (old blob only - no local file)" % path)
            continue
        delta = list(difflib.unified_diff(before, after, n=0))
        adds = [l for l in delta if l.startswith("+") and not l.startswith("+++")]
        dels = [l for l in delta if l.startswith("-") and not l.startswith("---")]
        print("\n##### %s  (+%d/-%d)  old_lines=%d new_lines=%d"
              % (path, len(adds), len(dels), len(before), len(after)))
        shown = 0
        for line in delta[2:]:
            if not line.startswith("@@"):
                shown += 1
                if shown > args.max_lines:
                    print("... [truncated at --max-lines=%d]" % args.max_lines)
                    break
            print(line.rstrip()[:300])

    for path in sorted(added):
        print("\n##### %s  (ADDED - no previous blob)" % path)
    for path in sorted(deleted):
        print("\n##### %s  (DELETED - absent from new tree)" % path)

    print("\n=== Summary ===")
    print("MODIFIED %d / ADDED %d / DELETED %d" % (len(changed), len(added), len(deleted)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
