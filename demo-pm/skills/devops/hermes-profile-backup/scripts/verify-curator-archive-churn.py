#!/usr/bin/env python3
"""Verify a preflight's 'D' (deleted) entries are legitimate CURATOR ARCHIVE CHURN
-- not real data loss, a bad PROFILE_DIR, or a misdirected rsync DST.

Run this whenever a preflight reports far more `D` entries than the profile
plausibly changed (see references/curator-archive-churn-triage.md). It proves,
per deleted path, all three of:

  1. the path is confined to `<profile>/skills/` (a D elsewhere = STOP);
  2. a matching twin exists under `skills/.archive/<name>/...`; and
  3. that skill classifies as BUNDLED via `skills/.bundled_manifest`, resolved
     from the archived SKILL.md frontmatter `name:` -- so dir-name != manifest-name
     cases (audiocraft -> audiocraft-audio-generation, vllm -> serving-llms-vllm,
     segment-anything -> segment-anything-model, lm-evaluation-harness ->
     evaluating-llms-harness) still classify correctly.

Exit 0 = every deleted path is a verified curator-archived bundled skill -> proceed
         with the backup and DISCLOSE the blob-count drop.
Exit 1 = at least one deletion is NOT verified churn -> STOP, do not push these
         deletions; investigate first.

Verified 2026-09-25 (demo-pm): 187/187 deleted paths resolved with `.archive` twins
and all 29 backing skills classified bundled; `demo-pm` blobs dropped 410 -> 223.

Usage:
  python3 scripts/verify-curator-archive-churn.py [preflight.log]
Env:
  PROFILE      default demo-pm
  PROFILE_DIR  default ~/.hermes/profiles/$PROFILE
  ARCHIVE_DIR  default $PROFILE_DIR/skills/.archive
"""
import os
import re
import sys
from pathlib import Path

PROFILE = os.environ.get("PROFILE", "demo-pm")
PROFILE_DIR = Path(os.environ.get("PROFILE_DIR",
                                  os.path.expanduser(f"~/.hermes/profiles/{PROFILE}")))
SKILLS = PROFILE_DIR / "skills"
ARCH = Path(os.environ.get("ARCHIVE_DIR", str(SKILLS / ".archive")))
LOG = sys.argv[1] if len(sys.argv) > 1 else "/tmp/preflight_run.log"


def deleted_paths(log_path):
    out = []
    for line in Path(log_path).read_text(errors="replace").splitlines():
        m = re.match(r"\s+D\s+(\S+)", line)
        if m:
            out.append(m.group(1))
    return out


def frontmatter_name(skill_md):
    try:
        txt = skill_md.read_text(errors="replace")
    except OSError:
        return None
    if not txt.startswith("---"):
        return None
    parts = txt.split("---", 2)
    if len(parts) < 2:
        return None
    m = re.search(r"^name:\s*(\S+)", parts[1], re.M)
    return m.group(1) if m else None


def bundled_names():
    mf = SKILLS / ".bundled_manifest"
    if not mf.exists():
        return set()
    names = set()
    for ln in mf.read_text(errors="replace").splitlines():
        ln = ln.strip()
        if ln:
            names.add(ln.split(":")[0])
    return names


def find_twin(rel):
    """rel = '<cat...>/<name>/<rest>' (relative to skills/).
    Return (twin_path, skill_dir_name) or (None, None)."""
    segs = rel.split("/")
    for i in range(len(segs) - 1):
        seg = segs[i]
        cand = ARCH / seg / "/".join(segs[i + 1:])
        if cand.exists():
            return cand, seg
    return None, None


def main():
    paths = deleted_paths(LOG)
    print(f"Deleted entries parsed from {LOG}: {len(paths)}")
    if not paths:
        print("No 'D' entries -- nothing to verify (right preflight log?)")
        return 0

    bundled = bundled_names()
    print(f"Bundled manifest skill names: {len(bundled)}")

    outside, no_twin, not_bundled, unknown = [], [], [], []
    for p in paths:
        if not p.startswith(f"{PROFILE}/skills/"):
            outside.append(p)
            continue
        rel = p[len(f"{PROFILE}/skills/"):]
        twin, name = find_twin(rel)
        if twin is None:
            no_twin.append(p)
            continue
        fm = frontmatter_name(ARCH / name / "SKILL.md")
        eff = fm or name
        if eff in bundled:
            continue
        (unknown if fm is None else not_bundled).append((p, eff))

    print("")
    print(f"  1. confined to {PROFILE}/skills/: "
          f"{'PASS' if not outside else 'FAIL'} (outside={len(outside)})")
    print(f"  2. archive twin present:          "
          f"{'PASS' if not no_twin else 'FAIL'} (missing={len(no_twin)})")
    print(f"  3. classifies as bundled:         "
          f"{'PASS' if not (not_bundled or unknown) else 'FAIL'} "
          f"(not_bundled={len(not_bundled)}, name_unresolved={len(unknown)})")

    for x in outside:
        print(f"    !! OUTSIDE skills/: {x}")
    for x in no_twin:
        print(f"    !! NO ARCHIVE TWIN: {x}")
    for p, n in not_bundled:
        print(f"    !! NOT BUNDLED: {n}  <- {p}")
    for p, n in unknown:
        print(f"    ?? name unresolved (no frontmatter): {n}  <- {p}")

    ok = not (outside or no_twin or not_bundled or unknown)
    if ok:
        print("\n=== PASS - all deletions are curator-archived bundled skills; proceed "
              "with the backup and disclose the blob-count drop. ===")
    else:
        print("\n=== FAIL - at least one deletion is NOT verified curator churn. "
              "STOP: do not push these deletions; investigate first. ===")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
