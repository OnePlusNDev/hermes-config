# Characterizing the M set for the run note (why each file changed)

Every daily run note carries a Diff section, and the useful part is the *reason*
each file changed — "routine runtime churn" vs "benign carry-over lag" (a doc
edit written AFTER the previous run's follow-up push, so that run's
`Modified: 0, New: 0, Deleted: 0` assertion legitimately did not hold).
Getting this wrong turns a normal ordering quirk into a phantom "lost commit".

The run-note template asks for this classification. Since 2026-09-27 it is a
script (`scripts/characterize-diff-vs-prev-head.py`) rather than eyeballed SHAs.

## The trap: never diff against the CURRENT remote

Right after a successful push the current remote tree EQUALS local — so any
"compare local against remote" probe reports every file `IDENTICAL` and you learn
nothing.

Verified 2026-09-27: a naive `gh api repos/O/R/contents/<path>` fetch (no `ref=`)
returned the content we had *just pushed* for all 4 files and printed
`IDENTICAL (unexpected)` for each. You must name the HEAD that was current
BEFORE your commit — i.e. the parent of your backup commit.

## Run it

```bash
cd /tmp && REPO_OWNER=OnePlusNDev python3 -u \
  ~/.hermes/profiles/demo-pm/skills/devops/hermes-profile-backup/scripts/characterize-diff-vs-prev-head.py \
  <PRE_PUSH_HEAD>              # or --commit=<your_backup_commit_sha>
```

`<PRE_PUSH_HEAD>` is the SHA the backup script logged as `Remote HEAD:` at
Step 2 of the clean attempt — and also `parents[0]` of your backup commit, which
`--commit=` derives for you. With no argument it derives `parents[0]` of the
current remote `main` and prints a warning (correct only when no sibling commit
landed after yours).

Expect `ADDED 0` in steady state. A non-zero `ADDED` means the script's
`EXCLUDE_*` sets have drifted out of sync with the backup script's — that is
the signal to re-sync them, not a real diff.

## Reading the output

- `M <path>  hint: runtime churn ...` — `cron/jobs.json` counters/timestamps and
  `memories/` archive rows. Expected every single day; say so in the note.
- `M <path>  hint: doc edit - benign carry-over lag ...` — a `*.md` under
  `skills/`. Confirm from the printed hunks that it is a lesson/pointer added
  *after* the previous push, then write "carry-over lag, not a lost commit" in
  the run note. If the hunk is older than the last push, something else is going
  on — investigate before claiming lag.
- Anything not matching those two hints — read the actual hunks before writing.

## 2026-09-27 worked example (4 M, 0 A, 0 D)

| File | Hunks | Verdict |
|------|-------|---------|
| `cron/jobs.json` | `completed` +48/+1/+1, `next_run_at`/`last_run_at` → 2026-09-27, `updated_at` today | runtime churn |
| `memories/archive/ARCHIVE.md` | one new 2026-09-26 hindsight reflect row (bank 48 nodes/1228 links, op `6abdae47`) | runtime churn |
| `skills/devops/demo-pm-github-api/SKILL.md` | the account-flip 404 lesson, "更狠的一次（2026-09-26 备份轮实测）" | carry-over lag |
| `skills/devops/hermes-profile-backup/SKILL.md` | "A switch can be undone within a minute — by an account you have never seen." | carry-over lag |

Conclusion written into the note: the last two were written after the 09-26
follow-up push, so 09-26's `0/0/0` closing assertion legitimately did not hold —
ordering, not a lost commit.
