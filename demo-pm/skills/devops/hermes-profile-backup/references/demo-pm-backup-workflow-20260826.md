# Backup Workflow 2026-08-26 — no-clone + subtree merge, get_token.sh removal

Clean 4-blob Method B run. The new no-clone subtree script was born this run.

## Situation

- `curl` to github.com → 000; `gh repo clone` → failed (port 443 timeout after 75s)
- `gh api` worked fine (Go net/http transport, as usual)
- Repo at 598 blobs (demo-pm 579) — flat tree POST would 422 "too large"
- The subtree script `scripts/gh-api-incremental-push-subtree.py` requires a local
  clone (`git ls-tree -r HEAD`), which we didn't have; the standalone script
  `scripts/gh-api-standalone-backup.py` needs no clone but builds a flat tree.

## The gap and the merge

No existing script handled "no clone AND large repo". Wrote a merged script:

- Blob SHA computation + filesystem walk + excludes: from standalone script
- Recursive subtree tree construction (each subdir = own tree POST): from
  subtree script
- Top-level tree: copy base entries, replace `demo-pm` entry with subtree SHA
  (siblings preserved — post-push distribution check confirmed demo-dev 5,
  demo-tester 8, tester-01 5, all intact)

Verified 2026-08-26: uploaded 4 blobs, pushed commit 7013767c54e6, ref
verified. Saved as `scripts/gh-api-standalone-subtree-backup.py`.

## get_token.sh — new exclude family: root-level .sh diagnostics

- File at profile root: `get_token.sh` (134 bytes) — sources `.env` then
  `echo "GITHUB_TOKEN=$GITHUB_TOKEN"`.
- It was already TRACKED in the repo from an earlier backup, so it never
  appeared as untracked in `git status` — the existing detection rule
  ("any untracked `.py` at profile root") missed it entirely on two counts:
  extension (.sh not .py) and tracked status.
- Caught this run by content inspection of root-level files during the
  pre-flight (same pattern that caught `query_issues.py` on 2026-08-13).
- Added `get_token.sh` to rsync excludes, .gitignore template, and the
  standalone + merged scripts' EXCLUDE_NAMES.
- The merged script's deleted-diff dropped it from the remote tree in the
  same push (D demo-pm/get_token.sh) — no `git rm --cached` needed in Method B.

## Config.yaml check

- All `api_key:` values empty strings (`''`); no `sk-` prefix matches.
- No key_env replacement needed. Post-push remote verification: 0 plaintext
  keys in `demo-pm/config.yaml`.

## Verifications run (all passed)

1. Remote config.yaml plaintext-key count = 0
2. `demo-pm/get_token.sh` absent from remote tree (0 entries)
3. Sibling distribution intact (demo-dev 5, demo-pm 579, demo-tester 8,
   tester-01 5, .gitignore 1 = 598 total)
4. Full-tree leak grep: sensitive paths NONE, temp scripts NONE
