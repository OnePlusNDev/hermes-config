# Syncing the live repo's `.gitignore` (and other repo-root files) from a Method B run

Verified 2026-11-16 (commit `bf758a028a03`).

## The constraint

`scripts/gh-api-standalone-subtree-backup.py` builds the top-level tree by **copying every base-tree
entry unchanged** and only replacing the `demo-pm` entry with a fresh subtree. It never walks the
repo root, so it **cannot carry an edit to `.gitignore`** — nor to any other file outside
`demo-pm/`. Editing `.gitignore` and then running the backup script is a no-op: the pushed tree
still points at the OLD `.gitignore` blob.

This matters because the exclude list is documented as a four-place sync
(rsync list → live repo `.gitignore` → gitignore template → SKILL.md docs). Three of those live
inside the profile and ride the normal commit; the fourth does not.

## Recipe — one small dedicated commit

Write a throwaway script to `/tmp` (unique name, e.g. `/tmp/gitignore_<profile>_<epoch>.py`) and run
it with `terminal("python3 /tmp/...")`. Steps, all via `gh api`:

1. `GET /repos/{O}/git/refs/heads/main` → `head`; `GET /repos/{O}/git/commits/{head}` → `tree_sha`.
2. `GET /repos/{O}/contents/.gitignore` → base64 → text. **Idempotency guard:**
   `if "<new-pattern>" in text: print("ALREADY PRESENT"); sys.exit(0)`.
3. `POST /git/blobs` with the new text (base64).
4. `POST /git/trees` with `{"base_tree": tree_sha, "tree": [{"path": ".gitignore", "mode": "100644",
   "type": "blob", "sha": <blob>}]}` — `base_tree` preserves every other entry, including all
   sibling profiles.
5. `POST /git/commits` (parent = `head`, conventional message e.g.
   `chore(gitignore): exclude root-level demo-pm/tmp_* diagnostic dirs`).
6. `PATCH /git/refs/heads/main` with the new commit sha.

## Ordering and the closing assertion

- Run it **between the main backup commit and the follow-up commit**. The follow-up re-reads the
  base tree at Step 2, so it copies the *new* `.gitignore` forward automatically — the small commit
  is not lost. (Verified: `.gitignore` at final HEAD still carried the added patterns.)
- It does **not** perturb the closing `Modified: 0, New: 0, Deleted: 0` assertion: the preflight
  only diffs paths under `demo-pm/`, so a repo-root file change is invisible to it.
- Same guard applies as any other ref write: check `gh api user` + `permissions.push` immediately
  before, and prefer running the switch and the script in one shell call.

## When to bother

The live `.gitignore` is defense-in-depth only — rsync/script excludes are the real gate, and a
missing pattern there is NOT a leak. So this is worth doing when you add a genuinely new exclude
*class* (a whole family of runtime files), not for every one-off filename. Prior runs left the live
file drifted for weeks; one targeted sync per new class is enough.

## Related: the gap this run was fixing

The first preflight of 2026-11-16 reported `9 M / 12 A`; all 12 `A` sat under a dated root-level
temp dir `tmp_pmtriage_1116_0900/` (`fetch.sh` read `GITHUB_TOKEN` out of `.env` using the
split-token trick `KEY="GITHUB_""TOKEN"`). The dir matched none of the existing rules: `tmp_triage`
was a whole-dir name, `tmp_*` matched FILENAMES only, and the root-scoped check listed `tmp` /
`tmp_pm` only. Fix — root-scoped, in all four scripts:

```python
if parts[0] == "tmp" or parts[0].startswith("tmp_"):
    return True
```

plus rsync `--exclude '/tmp_*/'`, template `demo-pm/tmp_*/`, and the SKILL.md bullet. Detection rule
holds: **a root-level temp-looking DIR is the tell, not the filenames inside it.**
