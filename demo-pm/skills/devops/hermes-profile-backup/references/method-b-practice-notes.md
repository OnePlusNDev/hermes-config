# Method B practice notes (extracted from SKILL.md 2026-09-21 to free cap space)

## Why runs go straight to Method B (no clone attempt)

Practice note (extended through 2026-09-11): runs 09-01 → 09-11 all went
STRAIGHT to Method B standalone-subtree with NO clone attempt — the repo is
625+ blobs and git/libcurl transport has repeatedly timed out in cron mode,
while the script never needs a worktree and absorbs concurrent HEAD advances by
re-reading the remote ref.

## The one-plain-re-run rule for the ref-PATCH 422 race

From 09-06 onward the ref-PATCH HTTP 422 "Update is not a fast forward" recurs on
MOST runs (a concurrent sibling-profile backup advances `main` during the ~1–2 min
blob phase).

Budget exactly ONE plain re-run: blob SHAs are idempotent, so the re-run just
re-parents the identical commit on the fresh HEAD. Do NOT rebase, do NOT attempt
tree surgery, and do NOT treat it as a partial failure — the first run's blobs are
already uploaded.

## Observed on recent runs

| Date | 422 race? | Notes |
|------|-----------|-------|
| 2026-09-17 | no | remote stable at 7a2b4e395427 through blob phase |
| 2026-09-18 | no | 232 D (curator archive) — see `curator-archive-churn-triage.md` |
| 2026-09-19 | no | remote stable at e18164653ec6 |
| 2026-09-20 | no | remote stable at 4aaad6fc05a2 |
| 2026-09-21 | no | remote advanced twice *between preflight and blob phase* (cf2cef12 → c82057b2 → 07eea1c3) via concurrent sibling backups, then stable through commit time |

Note (2026-09-21): the remote ref can advance between the **preflight** and the
**backup script's own Step 2** (the script re-reads it, so this is harmless — it
just means the diff counts you saw in preflight may be recomputed against a newer
HEAD). Run `scripts/post-push-verify.py` *after* the commit, not after the
preflight, for the authoritative numbers.

## Invoking the Method B script (cron, macOS)

Do **not** prefix the invocation with the shell's `timeout` command — macOS ships
no GNU `timeout` binary, so `timeout 570 python3 gh-api-standalone-subtree-backup.py`
dies instantly with `timeout: command not found` (hit 2026-09-22). Use the
`terminal` tool's own timeout parameter instead (`terminal(..., timeout=600)`), or
`gtimeout` if coreutils is installed. Plain invocation pattern:

```bash
cd /tmp && REPO_OWNER=OnePlusNDev python3 \
  ~/.hermes/profiles/demo-pm/skills/devops/hermes-profile-backup/scripts/gh-api-standalone-subtree-backup.py
```

Running it from `/tmp` with the script path under `~/.hermes` is fine in cron mode
(no tirith hit); a clean 6-blob + subtree + commit pass finishes well inside 600 s.
Pipe through `| tail -70` — the script's useful output is the Step 1–7 log.
