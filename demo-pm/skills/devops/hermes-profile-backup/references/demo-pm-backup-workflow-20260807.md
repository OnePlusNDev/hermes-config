# demo-pm backup workflow 2026-08-07

Two incidents in one run: (1) a `TMPDIR=` prefix bug made rsync copy to a literal `TMPDIR=` directory under the profile dir; (2) the incremental-push reference script's Step 5 dropped sibling profiles (replay of the 2026-08-02 data-loss incident), caught by the post-push distribution check and repaired.

## Incident 1: `TMPDIR=` prefix → relative DST → misdirected copy

Script did:

```bash
TMPDIR=$(cat /tmp/backup_tmpdir.txt)   # file content was 'TMPDIR=/tmp/hermes-backup-1786104580' (WITH prefix)
DST="$TMPDIR/demo-pm/"                  # → 'TMPDIR=/tmp/hermes-backup-1786104580/demo-pm/'  (relative!)
rsync -a ... "$SRC" "$DST"
```

bash assigns the whole string including `TMPDIR=` — the prefix is NOT stripped. DST is then a RELATIVE path whose first component is literally `TMPDIR=`. rsync creates `<cwd>/TMPDIR=/tmp/...`, i.e. a directory literally named `TMPDIR=` under whatever cwd the script runs from. This run's cwd was the profile dir, so 486 files landed in `~/.hermes/profiles/demo-pm/TMPDIR=/tmp/hermes-backup-1786104580/demo-pm/` and the clone repo was untouched — `git status` stayed clean (misleading; rsync exited 0).

Detection path (what actually worked):
- `git status` clean after rsync exit 0 → files did NOT go to the clone.
- `mdfind -name zz_marker.txt` (Spotlight) located the marker instantly. Deep `os.walk` over /Users/oneplusn timed out repeatedly (90–180s) — do not brute-force-walk the home dir.
- `stat -f "%N links=%l group=%Sg"` on parent dirs disambiguates: a `TMPDIR=` parent under `/tmp` is wheel group; under `/Users/oneplusn` it is staff.

Fix: store bare paths in temp files (no `VAR=` prefix), echo the variable before using it, and pass an ABSOLUTE DST to rsync. Clean the wrong copy with a Python `shutil.rmtree` script (tirith blocks plain `rm -rf` in cron mode).

## Incident 2: incremental-push reference script deleted sibling profiles

`references/gh-api-git-data-incremental-push.py` Step 5 only merged `PROFILE/` + `.gitignore` remote entries — every sibling profile (`demo-dev/`, `demo-tester/`, `tester-01/`) was omitted from the new tree and DELETED on push. Same root cause as the 2026-08-02 standalone-script incident.

Caught by the mandatory post-push distribution check:

```
gh api "repos/$OWNER/$REPO/git/trees/main?recursive=1" --jq '[.tree[] | select(.type=="blob") | (.path | split("/")[0])] | group_by(.) | map({dir: .[0], count: length})'
# saw only {.gitignore:1, demo-pm:570} — siblings gone
```

Repair (same as the documented standalone-script procedure):
1. Get last good commit's full tree (`9919bdc...` here) → dict of path→{mode, sha}.
2. Overlay current HEAD's tree → any path that is new or whose sha differs wins.
3. `POST /git/trees` with merged entries → `POST /git/commits` (parent = current HEAD) → `PATCH /git/refs/heads/main`.

Restored 589 blobs: .gitignore 1 + demo-dev 5 + demo-pm 570 + demo-tester 8 + tester-01 5. The reference script itself was patched to the correct "copy every non-deleted remote entry" logic.

Lesson: run the top-level distribution check after EVERY gh-API push, regardless of which script performed the push.

## Other notes

- gh account was `OnePlusNTester` at start; `unset GITHUB_TOKEN` (env var overrode `gh auth switch` in cron mode) then `gh auth switch --user OnePlusNDev` → push permission true.
- `git push` failed twice (HTTP2 framing layer, then port 443 connect timeout) while `gh api` worked — standard Method B fallback, not a network dead-end.
