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

## Pick the anchor AFTER the push — a preflight SHA can be stale

The authoritative anchor is `parents[0]` of your backup commit. Prefer
`--commit=<main_commit_sha>` **after** the backup script returns over any SHA you
read during preflight, because `main` can advance between preflight and the
script's Step 2 (it routinely does — sibling profiles back up on their own cron).

Verified 2026-09-29: the preflight HEAD was `8122b94d9407`, but a concurrent
sibling backup advanced `main` to `cdcabbeb7545` before the script's Step 2 — so
the script logged `Remote HEAD: cdcabbeb7545` and the commit's parent was
`cdcabbeb7545`, while the preflight log still said `8122b94d9407`.

Characterizing against the preflight SHA is only *usually* harmless: that day the
sibling commit did not touch `demo-pm/`, so both anchors yielded the same `5 M`.
But if the sibling commit HAD touched `demo-pm/`, the M set would be computed
against the wrong tree and could misclassify or omit a file. **When the preflight
SHA and the script's Step-2 SHA differ, re-run with `--commit=<main_sha>` and
cite the `parents[0]` value in the run note.**

Rule of thumb: read the script's `Remote HEAD:` line (Step 2) as it runs; if it
differs from the preflight value, do not cite the preflight value anywhere.

Expect `ADDED 0` in steady state — but a non-zero `ADDED` has **two** causes, and
the script's printed hint names only one of them:

1. **Exclude drift** — the script's `EXCLUDE_*` sets have drifted out of sync
   with the backup script's. Re-sync them; not a real diff.
2. **A legitimately new local file** — most commonly the monthly 30-day memory
   archive rollover creating `memories/archive/USER-<YYYYMMDD>.snapshot.md` or
   `memories/archive/MEMORY-<YYYYMMDD>.snapshot.md` (with the matching `ARCHIVE.md`
   row and a `最后更新` bump in the live file). Those snapshots ARE in the include
   list, so the `A` is correct and must be backed up — do **not** "fix" an
   EXCLUDE set to make it vanish. Both memory files roll over independently at
   their own 30-day windows, so expect one `A` roughly monthly: USER.md rolled
   2026-10-11, MEMORY.md rolled 2026-10-29 (next USER window 2026-11-10, next
   MEMORY window ~2026-11-28).

Distinguish by path: an `A` under `memories/archive/` named `*-<date>.snapshot.md`
is category 2 (intended content); an `A` under `tmp*/`, a `*_cache.json`, a root
`health*`/`*.sh` diagnostic, or anything matching a live `EXCLUDE_*` prefix is
category 1 (drift). Verified 2026-10-12: `ADDED 1
demo-pm/memories/archive/USER-20261011.snapshot.md` was the 30-day USER.md
rollover (USER.md's 最后更新 moved 2026-09-11 → 2026-10-11 the same run), **not** an
exclude mismatch — the script's "check EXCLUDE sync" hint is a false alarm here.

3. **A new doc authored by ANOTHER cron job between runs** — nearly always a
   `references/*.md` under a *sibling* skill's directory, because each skill's own
   cron writes its lessons into its own `references/`. Verified 2026-10-17:
   `A demo-pm/skills/devops/pm-triage-cron/references/cron-run-pitfalls.md`
   (2,369 B — the `/tmp` fixed-filename sibling collision + `COUNT:0` crosscheck
   pitfall) appeared in the window between the 10-16 follow-up push and the 10-17
   preflight. It is intended content: back it up, do **not** add an exclude.
   The one extra step vs category 2: it lives under a sibling skill, so read the
   file before upload (`grep -nE 'token|sk-|ghp_|api_key|\.env' <file>`). A triage
   transcript very often quotes a `grep "^GITHUB_TOKEN=..." .env` recipe — a
   variable NAME mention is fine (the preflight token scan passes it, since that
   scan matches full token *values*), a value or a `.env` dump is not.
   Classify it in the run note as "new reference doc, content inspected", e.g.
   2026-10-17's note.
   **Same shape inside THIS skill (verified 2026-10-30):** a `references/*.md`
   authored *after* the previous day's follow-up push also arrives as `A` the next
   morning — that run's recipe file (`references/index-and-table-append-recipe.md`)
   showed up on 10-30 alongside the legitimate `memories/archive/MEMORY-20261029.snapshot.md`.
   `A 2` in one preflight is therefore not automatically drift: check each path
   against categories 2/3 before touching an `EXCLUDE_*` set.

**Sanity arithmetic beats the presence/absence of `A`:** local count must equal
remote-at-PREV_HEAD count + `New` (`270 == 268 + 2`, 2026-10-30). If that identity
holds and every new path is explained, there is no exclude gap — no matter what
the script's hint says.

## Run it ONCE — write the diff to a file, then slice it

The probe prints a full unified diff per `M` file, so its stdout is routinely
thousands of lines and gets cut by `| head -60` / `| tail -70`. Do **not** run it
twice to see the head and then the tail: every execution re-reads the remote
tree, GETs a blob for each changed file, and (with no argument) derives
`parents[0]`. A second run doubles the API traffic and wall time for information
you already had.

Verified 2026-10-18: a clean 5-M run cost two full passes (~5 redundant blob
GETs) purely because the first output was piped through `tail -70` instead of
being kept.

**Repeat offence 2026-10-19** — same shape (`| tail -45`, then a second run with
`sed -n '1,40p'`). The rule was already written here, which is the point: a
pitfall that lives only in a reference file does not get read mid-run. SKILL.md's
probe pointer now carries the rule inline; keep it there.

Correct shape — dump to your private mkdtemp dir first, then read slices:

```bash
TMPD=$(mktemp -d /tmp/char-XXXXXX)
REPO_OWNER=OnePlusNDev python3 -u <skill>/scripts/characterize-diff-vs-prev-head.py \
  > "$TMPD/char.txt" 2>&1
grep -n '^--- M ' "$TMPD/char.txt"     # indexes every file's hunk block
```

Then `read_file`/`sed -n` only the block you need. (`>` into `/tmp` is fine; a
shell redirect into a `~/.hermes` path trips `tirith:dotfile_overwrite`.)

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

## 2026-09-29 worked example (5 M, 0 A, 0 D — and the anchor divergence)

| File | Hunks | Verdict |
|------|-------|---------|
| `cron/jobs.json` | `completed` +48/+1/+1, `next_run_at`/`last_run_at` → 2026-09-29, `updated_at` today | runtime churn |
| `memories/archive/ARCHIVE.md` | one new 2026-09-28 hindsight reflect row (bank 48 nodes/1228 links, op `4fb36962`) | runtime churn |
| `skills/devops/demo-pm-github-api/SKILL.md` | 09-29 filter-sanity lesson (a zero-task account beats `OnePlusNBoss` as a filter-validity probe) | carry-over lag |
| `skills/devops/hermes-profile-backup/SKILL.md` | the `skill_view`-truncation disambiguation ("read_file the on-disk SKILL.md, not the tmp dump") | carry-over lag |
| `references/skill-md-at-cap.md` | 09-28 status figure + the "Which file to `read_file`" trap section | carry-over lag |

This is the run that motivated the anchor section above: the preflight HEAD was
`8122b94d9407`, a concurrent sibling backup advanced `main` to `cdcabbeb7545`
before the script's Step 2, and the commit's parent was `cdcabbeb7545`. Both
anchors produced the same 5 M only because the sibling commit stayed outside
`demo-pm/`.

Note the SKILL.md hunk is `+11` chars and the pointer bump is same-length
(`2026-09-28` → `2026-09-29`), which is how a `latest:` bump fits under the 100K
cap when headroom is ~25 chars — see `references/skill-md-at-cap.md`.

## When the probe dies mid-run — mtime + commit-timestamp fallback (2026-10-22)

Verified 2026-10-22: the probe printed the `cron/jobs.json` block fine, then died on
ARCHIVE.md's blob GET:

```
RuntimeError: gh api repos/.../git/blobs/2157014b8a28 failed:
Get "...": net/http: TLS handshake timeout
```

That is transport flakiness in the *throwaway diagnostic*, NOT a failed backup — the push
had already succeeded (`Done:` + `exit=0`). Do not loop the probe to "make it finish", and
do not describe the run as failed. Classify the remaining `M` files from two cheap
independent signals instead:

1. **Local mtime** — `ls -lT <file> [<file>...]` (macOS `-T` adds seconds).
2. **Previous run's commit times** —
   ```bash
   gh api "repos/$OWNER/$REPO/commits?per_page=6" \
     --jq '.[] | (.sha[0:12] + "  " + .commit.author.date + "  " + (.commit.message|split("\n")[0]))'
   ```
   A demo-pm day leaves TWO commits: `backup: demo-pm <date>` (main) then the follow-up.

Decision rule: mtime **after** the previous run's *follow-up* commit ⇒ carry-over lag (that
run's `0/0/0` legitimately did not hold). mtime *between* main and follow-up ⇒ look closer.
mtime today and well before this run's own push ⇒ fresh same-day work, say so.

2026-10-22 numbers: previous main `8d647b38` 12:03:24Z, follow-up `8a2cb72b78dd` 12:05:28Z
(= 20:05:28 CST). `network-flakiness-and-verify-tooling.md` mtime 20:05:56 — **28 s** after
the follow-up push ⇒ carry-over lag; same verdict for the two 21:05 diagnostics docs; the
`pm-triage-cron` files (mtime 17:31 today) were fresh same-day work. All matched the hints
the probe had already printed before it died.

## Trap: `gh api commits?path=<file>` after the push answers with YOUR OWN commit

`gh api "repos/O/R/commits?path=demo-pm/<file>&per_page=1"` returns the *newest* commit
touching that path — which, immediately after your push, is today's backup commit. Every
`M` file then echoes the same today SHA and you learn nothing about when it last changed
*before* this run. Verified 2026-10-22: four files all answered
`83e91837ceb3  2026-10-22T12:10:53Z  backup: demo-pm 2026-10-22`.

If you genuinely need per-file remote history, pin it to the pre-push tree:

```bash
gh api "repos/$OWNER/$REPO/commits?path=demo-pm/<file>&sha=<PRE_PUSH_HEAD>&per_page=1"
```

Otherwise skip it — the mtime-vs-previous-commit-timestamp route above costs one call
instead of N.
