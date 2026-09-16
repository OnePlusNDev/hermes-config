#!/usr/bin/env python3
"""Post-push verification for a Hermes profile backup (Method B / gh API).

Run AFTER the backup commit(s) land. Checks the REMOTE tree -- not the local
one -- so it proves the push actually landed and that no secret/runtime file
leaked into the repo.

Complements scripts/preflight-backup-scan.py, which checks the upload
CANDIDATES before the push; this one checks the committed RESULT after.
Every daily run note in references/ carries exactly these numbers, so running
this script is what produces them instead of hand-writing a fresh verifier.

Also covers the "silent follow-up failure" case: if a follow-up ref PATCH
failed, the tree grep here shows the profile subtree still at the previous
blob count even though the backup script printed `Done:` and exit 0.

Usage:
  REPO_OWNER=OnePlusNDev python3 -u scripts/post-push-verify.py

Env overrides:
  REPO_OWNER  default OnePlusNDev
  REPO        default hermes-config
  PROFILE     default demo-pm
  PROFILES    comma list of sibling dirs expected to still be present
              (default demo-dev,demo-tester,tester-01)

Exit code 0 = all checks PASS; 1 = at least one FAIL (printed to stdout).
NOTE: keep this file ASCII-only -- emoji / Unicode variation selectors get
blocked by the tirith scanner in cron mode.
"""
import base64
import json
import os
import subprocess
import sys
from collections import Counter

OWNER = os.environ.get("REPO_OWNER", "OnePlusNDev")
REPO = os.environ.get("REPO", "hermes-config")
PROFILE = os.environ.get("PROFILE", "demo-pm")
SIBLINGS = [s for s in os.environ.get(
    "PROFILES", "demo-dev,demo-tester,tester-01").split(",") if s]

# Path substrings that must NEVER appear in the remote tree.
SENSITIVE = [".env", "auth.json", "auth.lock", "state.db", "state.db-shm",
             "state.db-wal", "processes.json", "bin/tirith", "/home/",
             "/.local/", "response_store.db", ".hermes_history"]
# Runtime / temp / diagnostic artifacts that must never be backed up.
TEMP_PAT = [".tmp_", "tmp_triage/", "pm_health", "gh_health", "healthcheck_",
            "get_token", "__pycache__"]

failures = []


def check(label, ok, detail):
    mark = "PASS" if ok else "FAIL"
    if not ok:
        failures.append(label)
    print("  [%s] %s: %s" % (mark, label, detail))


def gh(endpoint, raw=False):
    r = subprocess.run(["gh", "api", endpoint, "--jq", "."],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("GH API FAIL on %s: %s" % (endpoint, r.stderr.strip()),
              file=sys.stderr)
        sys.exit(1)
    return r.stdout if raw else json.loads(r.stdout)


print("=== Post-push verification: %s/%s -> %s/ ===" % (OWNER, REPO, PROFILE))

head = gh("/repos/%s/%s/git/refs/heads/main" % (OWNER, REPO))["object"]["sha"]
print("Remote HEAD: %s" % head)

commit = gh("/repos/%s/%s/git/commits/%s" % (OWNER, REPO, head))
tree = gh("/repos/%s/%s/git/trees/%s?recursive=1"
          % (OWNER, REPO, commit["tree"]["sha"]))
blobs = [e["path"] for e in tree.get("tree", []) if e.get("type") == "blob"]

prof = [p for p in blobs if p.startswith(PROFILE + "/")]
top = Counter(p.split("/")[0] for p in blobs)
print("Total blobs: %d   %s blobs: %d" % (len(blobs), PROFILE, len(prof)))
print("By top dir: %s" % dict(top))

print("\n--- Structural checks ---")
check("profile subtree present", len(prof) > 0, "%d blobs" % len(prof))
missing = [s for s in SIBLINGS if s not in top]
check("sibling dirs intact", not missing,
      "absent: %s" % missing if missing else "all present: %s" % ", ".join(SIBLINGS))

print("\n--- config.yaml key check (remote) ---")
cfg_path = "%s/config.yaml" % PROFILE
if cfg_path not in blobs:
    check("config.yaml present", False, "not found in remote tree")
else:
    raw = gh("/repos/%s/%s/contents/%s" % (OWNER, REPO, cfg_path), raw=True).strip()
    try:
        data = base64.b64decode(raw).decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001
        data = ""
        check("config.yaml decodes", False, str(exc))
    if data:
        sk = data.count("sk-")
        # Print line NUMBERS only -- never echo a candidate secret's contents.
        sk_lines = [i + 1 for i, l in enumerate(data.splitlines()) if "sk-" in l]
        check("no plaintext sk- key", sk == 0,
              "%d match(es) on line(s) %s" % (sk, sk_lines) if sk else "0 matches")
        ak = [l for l in data.splitlines() if "api_key" in l]
        nonempty = [l for l in ak if l.strip() != "api_key: ''"]
        check("all api_key empty", not nonempty,
              "%d api_key line(s), %d non-empty" % (len(ak), len(nonempty)))
        print("  config.yaml bytes: %d" % len(data))

print("\n--- Leak checks ---")
sens = [p for p in blobs if any(s in p for s in SENSITIVE)]
check("no sensitive paths", not sens, sens if sens else "none")
tmp = [p for p in blobs if any(t in p for t in TEMP_PAT)]
check("no temp/diagnostic scripts", not tmp, tmp if tmp else "none")

print("\n=== Result ===")
if failures:
    print("FAILED: %s" % ", ".join(failures))
    print("Remote HEAD at verification: %s" % head)
    sys.exit(1)
print("ALL CHECKS PASS")
print("Remote HEAD at verification: %s" % head)
