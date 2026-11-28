# SKILL.md size cap — headroom is thin, keep it that way

**Status 2026-10-28: exactly 100,866 chars by `wc -c`, i.e. ~866 OVER the 100,000 limit** (it
grew ~320 B since the 10-23 measurement of 100,543 from intervening pointer prose). The only
body edit this run was the routine same-length `latest:` bump (`2026-10-27` → `2026-10-28`) via
the **generic `patch` tool**, which applied it silently and left the size **byte-identical**
(100,866 before → 100,866 after) — fourth consecutive run confirming the 10-08 finding that the
cap is a `skill_manage`-only validation. Practical consequence: **treat SKILL.md as frozen for
prose.** Same-length pointer swaps only; all new content goes into `references/` or `templates/`
with the pointer living in an *existing* line. The owed slim is still owed — the duplicated
push-protection table (~1.5 KB, see "To fix") remains the cheapest untaken win.

**Status 2026-09-27: 99,898 chars → 99,966** after adding a **68-char inline append** to the
existing "Post-push probe:" line pointing at the new
`scripts/characterize-diff-vs-prev-head.py`. An append this small clears the cap where a fresh
~300-char pointer line would be refused (the tool validates the *resulting* size) — so while at
cap, **extend an existing pointer line rather than adding a new one**. Headroom is now only
**~34 chars**: the next run that needs to grow the SKILL.md *body* must slim first (see "To fix").
Also added that run: `references/run-note-diff-characterization.md`. Both new support files are
pointed at a **second** time from `references/method-b-practice-notes.md` and
`templates/run-note-template.md` — belt-and-braces discoverability, in *addition to* (never
instead of) the SKILL.md line, so a future slim cannot orphan them. That is deliberately NOT
the "stuff the pointer into a reference file" workaround rejected below: the SKILL.md pointer
still exists.

**Status 2026-09-28: SKILL.md measured at 99,964 chars** (the 09-27 figure of 99,966 was 2 high —
`wc -c < SKILL.md` is the authority). The only body edit this run was a **+11-char** disambiguation
of the `skill_view` truncation warning in SKILL.md — rewriting an *existing* line still clears the
cap where a *new* line would not; headroom is now ~25 chars, so real body growth still needs a
slim first.

**Status 2026-10-08: the size cap is NOT enforced by the generic `patch` tool** — only by
`skill_manage(action='patch'/'edit')`. SKILL.md measured **100,052 chars (52 over the 100,000
limit)** and the daily `latest:` pointer bump (`2026-10-07` → `2026-10-08`) applied cleanly with
the generic `patch` tool (mode='replace', same-length edit), **no refusal**. So a routine run that
finds SKILL.md a few dozen chars over cap does **not** need to slim before the pointer bump: make
the (near-same-length) edit with the generic `patch` tool and proceed. The "Symptom" section below
is what `skill_manage` raises; it does not fire for the generic tool. Still slim when *growing the
body* materially, and keep the file near cap regardless (it loads into every run that reads the
skill). Verified this run: pointer bump succeeded, size stayed 100,052.

**Status 2026-09-23: SKILL.md had crept back to 100,665 chars (limit 100,000) → slimmed
the same run to 98,729 chars** by performing the "highest-value extraction" flagged
below: the ~90-line **Method A rsync `--exclude` list** moved to
`references/method-a-rsync-excludes.md`, replaced in SKILL.md by a 2-line placeholder plus
a pointer paragraph. Headroom after the slim is ~1.3 KB. The `latest:` pointer bump for
`2026-09-23` then succeeded.
**Do the extraction BEFORE the follow-up commit** — see the ordering warning at the bottom.

**Status 2026-09-21: SKILL.md was 100,142 chars (limit 100,000) → patched back
under the cap the same run** by extracting the Method B practice-note paragraph
to `references/method-b-practice-notes.md` and replacing it with a 3-line pointer.
Headroom after the slim was only a few hundred chars — and it was gone again within
two days (see the 09-23 status above). Budget for re-slimming on a recurring basis.

## Symptom (when it does bite)

Any `skill_manage(action='patch')` or `action='edit'` on this skill fails with:

```
SKILL.md content is 100,142 characters (limit: 100,000). Consider splitting
into a smaller SKILL.md with supporting files in references/ or templates/.
```

The refusal is **all-or-nothing**: you cannot add a small pointer line, because
the patch tool validates the *resulting* file size, not the delta. A ~300-char
addition is rejected even though you're only 142 chars over.

## What this means for a routine backup run

The daily workflow ends with three edits:

1. new `references/demo-pm-backup-workflow-YYYYMMDD.md` (write_file — **works**)
2. index bullet appended to `references/dated-runs-index.md` (patch — **works**)
3. `SKILL.md` `latest:` pointer bumped (patch — works **only while under cap**)

While there is headroom, all three work normally (the pointer bump for
`2026-09-21` succeeded). If step 3 starts returning the size error:
**do not skip steps 1 and 2** — the run note and the index bullet are the durable
record, the `latest:` pointer is just a convenience. Keep 1 and 2 accurate, note
in the run note that the pointer is stale, free space per "To fix" below, then
bump it. Do NOT work around it by stuffing the pointer into a reference file.

## To fix (needs a session that can read the whole file)

Free ~1 KB, then bump the pointer. Candidates for extraction, cheapest first:

- The **Method A rsync exclude list** (SKILL.md lines ~95–190, ~95 lines) — it is
  already mirrored three ways (`.gitignore` template, `scripts/gh-api-standalone-subtree-backup.py`
  `EXCLUDE_*`, `scripts/preflight-backup-scan.py` `EXCLUDE_*`). Method A is the
  rarely-used path; the canonical list could live in `references/method-a-rsync-excludes.md`
  with a pointer. **Highest-value extraction.**
- Redundant lines *inside* that list: `--exclude 'gateway.*'` already covers the
  following `gateway.lock`, `gateway.pid`, `gateway_state.json` lines.
- **Duplicated push-protection tables (found 2026-09-27 while reading SKILL.md end-to-end).**
  The "Concrete patterns that trigger this:" table appears **twice** (~lines 512–523 and again
  ~583–592, byte-identical rows), and the surrounding "graceful fallback on blob upload push
  protection" prose restates the same redaction rules a third time (~lines 551–592). Collapsing
  to a single occurrence is ~1.5 KB recovered with no information loss — the cheapest slim
  candidate after the Method A extraction above.
- The dated-run **narrative paragraphs** (e.g. the "Practice note (extended
  through 2026-09-11)" block) — largely superseded by `references/dated-runs-index.md`.

⚠️ `skill_view` returns a TRUNCATED blob for this file (it exceeds the tool's
response cap), so the file must be read with `read_file` + `offset`/`limit`
before any surgery. Do not patch a 100 KB file you haven't fully read.

### Which file to `read_file` — the trap (verified 2026-09-28)

Point `read_file` at the **on-disk SKILL.md**
(`~/.hermes/profiles/<profile>/skills/devops/hermes-profile-backup/SKILL.md`).
It has real newlines, so `offset`/`limit` slices work. Do **NOT** locate that
path with a recursive search — `find ~/.hermes -iname '*.md' -path '*hermes-profile-backup*'`
**TIMES OUT (180 s, exit 124)** because the profile tree carries `lsp/` + `node_modules`
(5000+ files). The path is stable and known, so hardcode it instead of shelling out to
`find` (verified 2026-10-04). ⚠️ `search_files(target='files')` is **NOT** a safe substitute
for a broad listing: a glob like `pattern='*'` over the profile root ALSO times out
(`limit_reason: search_timeout`, 0 results) on this tree — for a directory listing use plain
`ls` via terminal (verified 2026-10-05). A narrow filename glob (a specific file name) is
fine; the failure is broad recursive walks.

Do **NOT** point `read_file` at the temp path `skill_view` prints
(`... Full output saved to: /var/folders/.../hermes-results/call_00_*.txt`).
That dump is a **single-line JSON envelope** (`{"success": true, ... "content": "---\nname: ..."}`),
so it reports `total_lines: 0` and every `offset`/`limit` slice returns the same
unreadable mega-line — a wasted call.

If a raw dump is the only available source, json-extract `.content` into a fresh
file first (this restores the real newlines), then `read_file` it normally:

```bash
python3 -c "import json; d=json.load(open('/path/to/dump.txt')); open('/tmp/skill.md','w').write(d['content'])"
```

## How to actually READ this 100 KB file (practical paging)

`read_file` rejects a single read past ~100K characters, and SKILL.md is ~100.9 KB, so
`read_file(path, limit=2000)` on it fails outright. Page it instead: `offset=1, limit=250`,
then `offset=251, limit=250`, etc. — 250-line slices cover the whole file in five calls and
each returns cleanly (verified 2026-11-01). Loading it via `skill_view` first is only useful
for the `linked_files` map; the body comes back truncated, so go straight to the paged
`read_file` on the on-disk path.

## At cap, `skill_manage` permits only NON-GROWING SKILL.md edits (verified 2026-11-09)

Measured **100,086 chars** (over the 100,000 limit) at the start of that run. A ~+65-char
rewrite of the `skill_view`-truncation warning was **REFUSED** —
`SKILL.md content is 100,151 characters (limit: 100,000)`. The SAME edit, retightened to be
net **−11 chars**, then applied cleanly and left the file at ~100,075 chars — still over the
limit, yet accepted.

So the validation gates on **growth**, not on the absolute resulting size: when SKILL.md is
already over cap, shrinking or equal-length edits pass `skill_manage`; any edit that increases
the character count is refused no matter how small. Consequences: (a) the routine `latest:`
bump (same length) is always safe; (b) a genuinely new sentence must be *paid for* by
tightening the same line, and terser phrasing is a legitimate tool — the −11-char rewrite above
actually improved the warning ("skip `skill_view`, read the on-disk file") instead of merely
preserving it; (c) this refines the "Tooling constraint" note below — a review pass is not
frozen out of SKILL.md, only out of *growing* it.

## Opening a daily run with `skill_view` costs a 106 KB dump you still cannot read

Verified 2026-11-10: calling `skill_view('hermes-profile-backup')` first thing returned
**108,606 characters** of JSON and the tool saved it to a temp file with only a 1,500-char
preview — the skill body was not actually usable without a `python3 -c "json.load(...)['content']"`
extraction to `/tmp/skill_backup.md`, then `read_file` with offsets. Two tool calls and ~110 KB
of context spent to reach the same place that a single
`read_file("~/.hermes/profiles/demo-pm/skills/devops/hermes-profile-backup/SKILL.md")` reaches
directly. SKILL.md line 41 already says this; the failure mode is *skipping* it out of habit at
session start. Daily-run rule: `read_file` the on-disk SKILL.md, and only fall back to the
to the extraction recipe if some other tool has already produced the JSON dump.

**Fourth occurrence, 2026-11-21 — the fix is a *starting order*, not a reminder.** That run opened
with `skill_view('hermes-profile-backup')` out of habit and got a **109,380-char** truncated blob
(`Full output could not be saved to sandbox`), then still had to `read_file` lines 1–200 of the
on-disk SKILL.md for §Pre-Backup Security Check / §Method Selection. The warning that would have
prevented it lives at line 41 of the file you can only page *after* paying for the dump — so
"remember not to `skill_view`" cannot work. What works is ordering the run so no skill read is
needed first: (1) `grep` `config.yaml` for `sk-` / non-empty `api_key` (task-mandated, no skill
needed), (2) the auth guard, (3) `scripts/preflight-backup-scan.py` — its own header documents the
workflow. Only then read SKILL.md sections by offset if something is unclear. The `linked_files`
map is the one thing `skill_view` gives that a paged `read_file` does not; when you need the file
list, use `search_files(target='files')` on the skill's own directory (a narrow, non-recursive
glob — fine per the 2026-10-05 note) instead of paying 109 KB for it.

**Fifth occurrence, 2026-11-23 — the "starting order" rule only works if it is the literal first
action, and the persisted dump is NOT a recovery path.** That run opened with
`skill_view('hermes-profile-backup')` again, because the cron prompt's phrasing ("备份 Hermes 配置到
GitHub") fires the skill-read reflex before any planning happens — the routine reads like a task
that needs instructions, so step 1 becomes "load the skill". It is not: the task-mandated
`grep` of `config.yaml` for `sk-` / non-empty `api_key` needs no skill text, the auth guard needs
none, and `scripts/preflight-backup-scan.py` documents its own workflow in its header docstring.
Start at the grep, stay inside the cap, and read SKILL.md sections by offset only if something is
actually unclear.

And do not count on the truncated dump either: it is persisted as **one single JSON line** with
every newline escaped, so `read_file` on that path returns an unreadable mega-line, and
`execute_code` (the tool that could `json.loads` it) is blocked in cron mode. There is no cheap
recovery, which is the real cost of the reflex, not the 30 seconds of download.

**Addendum, 2026-11-24 — sixth occurrence, and the dump IS greppable (the "no cheap recovery"
claim above overstates it).** The reflex fired again off the identical cron-prompt phrasing, burning
~107 KB of context. But the persisted dump is only unreadable to `read_file`; plain `grep` still
works on it, because escaping the newlines leaves all the text in place on the one physical line.
One call — `grep -n "Method B\|scripts/\|preflight\|## " <dump-path> | head -80` — surfaced the
method-selection, preflight and script-trio pointers this run needed, and `grep -o` can lift a
specific passage. So the dump is a *slow* recovery that burns context, not a dead end.

None of that is a licence to keep loading it: greppability is the reason the reflex is survivable,
not the reason it is harmless. Start at the `config.yaml` grep; treat retrieving the dump as the
recovery path after a mistake, never as the first step.

**Eighth occurrence, 2026-11-27 — BOTH start-of-session reflexes fail; go straight to disk.**
`skill_view('hermes-profile-backup')` was paid again (~110 KB; dump path under `/var/folders/…`),
and `read_file` on that dump is useless — it reports `total_lines: 0` because the whole payload is
**one JSON line**. The next reflex, `execute_code` to unwrap it, is refused outright in cron mode:

```
BLOCKED: execute_code runs arbitrary local Python (including subprocess calls that bypass
shell-string approval checks). Cron jobs run without a user present to approve it.
```

So in cron there is **no** in-process recovery path for the dump — the heredoc recipe above only
works through `terminal("python3 - <<'EOF' …")`, never `execute_code`. Cheapest path, worked first
try: locate the skill on disk, then page it —

```bash
ls -d ~/.hermes/profiles/<profile>/skills/devops/<skill>   # profile-local, NOT ~/.hermes/skills/
# then read_file(<that dir>/SKILL.md, offset, limit)
```

Two calls, zero dump. Note the structural catch: the dump is only reachable *via* `skill_view`,
which is the thing to avoid, so another occurrence note here cannot prevent occurrence nine —
only the line-41 pointer in SKILL.md can (it now also names `execute_code`).

**Seventh occurrence, 2026-11-26 — cheapest recovery is a one-call heredoc, not `python3 -c`.**
The reflex fired again at session start (108 KB dump under `/var/folders/...`, and `read_file` on it
returned `total_lines: 0, file_size: 110461` — the documented single-line envelope). Recovery that
worked first try in ONE `terminal` call:

```bash
python3 - <<'EOF'
import json
d = json.load(open("<dump path printed by the tool result>"))
open("/tmp/skill_backup.md","w").write(d["content"])
print(len(d["content"]), list(d.get("linked_files",{})))
EOF
```

then page `/tmp/skill_backup.md` with `read_file(offset, limit)`. The heredoc sidesteps the
nested-quote escaping that makes the `python3 -c "json.load(...)['content']"` one-liner easy to
mangle, and printing `linked_files` keys restores the map `skill_view` would have handed back.
Total recovery cost: 2 calls. Reflex cost: ~110 KB of context.

Because the warning lives *inside* the file you can only read after paying that cost, the durable
fix has to be a channel that is read *before* the reflex. Profile memory is the best one when
enabled: a single line like "config-backup cron: read `hermes-profile-backup/SKILL.md` from disk,
never `skill_view`" is injected every turn. When memory is unavailable, the only pre-reflex text
is the cron prompt and roughly line 41 of SKILL.md — which is why that line has to stay short and
imperative ("Daily run: skip `skill_view` … → `read_file` on-disk SKILL.md") rather than growing
into a paragraph. Recurrence notes in THIS file do not prevent occurrence eight; they only document
it.


**Third occurrence, 2026-11-12 — two refinements for the recovery path:**
- In a **cron RUN turn `execute_code` is refused** (`BLOCKED: execute_code runs arbitrary local
  Python … Cron jobs run without a user present to approve it`), so the extraction must go
  through `terminal("python3 -c \"import json; …\"")`. Do not burn a call on `execute_code` first.
- **`read_file` on the dump file itself fails** (>100 K characters, single line) and the tool
  truncates long lines, so the only usable route is: json-load → write `.content` to a fresh
  `/tmp/*.md` → `read_file` that with `offset`/`limit`. That reconstructed file is byte-identical
  to SKILL.md with real newlines — after this 2026-11-12 recovery the run was clean (first-try
  main + follow-up push, closing preflight `0/0/0`), so the extra two calls cost nothing beyond
  context. The rule stands: skip `skill_view` entirely on a daily run.

## Tooling constraint: the *review* turn is restricted — a cron RUN turn is not (refined 2026-11-11)

Every "the cap is not enforced by the generic `patch` tool" note above depends on that tool
being callable. Which passes can call it is **not** a property of "is this a cron job" — it is a
property of the *turn type*, and the two got conflated in the first version of this note:

- **Background skill-review / curator turn** — only memory + skill tools are whitelisted; a
  `patch` call is refused with `Background review denied non-whitelisted tool: patch`.
- **Scheduled cron RUN turn** (the daily backup job itself) — the **full toolset is present**.
  Verified 2026-11-11: that run called `patch` three times (SKILL.md `latest:` bump
  `2026-11-10` → `2026-11-11`, plus the `dated-runs-index.md` bullet and the
  `method-b-practice-notes.md` table row) with no refusals, and the SKILL.md swap left the file
  **byte-identical at 100,859 B**.

So the correct rule is *check, don't assume*: the SKILL.md `latest:` bump and any byte-neutral
surgery are normally done in the run session, where `patch` has always been available here —
including equality-length swaps on a file that is 859 B over cap. `skill_manage` still enforces
the cap (growth refused, shrink/equal accepted — see the 2026-11-09 note), so use `skill_manage`
only for `references/` and `templates/`, which carry no size cap.

⚠️ Do not read this note — or the earlier "not available in review/cron passes" wording — as
"cron jobs cannot edit SKILL.md". That framing caused a needless detour before the 2026-11-11
run re-tested it. If a `patch` call is refused mid-run, then fall back to `skill_manage` with a
non-growing edit; do not pre-emptively skip the bump.

## Known structural defect to fix during the next slim (found 2026-11-01)

The **Method Selection** table is split in three. Rows **A** and **B** sit together
(~lines 78-79), then ~17 lines of prose (clone-currency warning, Method B practice notes,
dated-run-notes pointer), then row **C** (`Python + Content API`) is orphaned at ~line 99 —
outside the table, before `## Method A`. A reader scanning the table sees only A and B and
easily misses Method C entirely (this run's agent almost did).

Fix is byte-neutral: move the row-C line up to sit directly under row B, leave the prose
below the completed table. Do it in the same edit batch as the next cap slim, and re-check
`wc -c` afterwards — the move adds no characters, only reorders lines.

## Support files that exist (so they aren't lost)

- `scripts/characterize-diff-post-push.py` (added 2026-11-14) — post-push counterpart to
  `scripts/characterize-diff-vs-prev-head.py`: derives the changed set from the PREV commit tree vs
  the pushed tree, then diffs each old blob against the local file. Use it when the main commit
  already landed (the pre-push probe then reads IDENTICAL for everything). SKILL.md carries **no**
  pointer to it on purpose (adding one would grow a file that is already over cap); it is pointed
  at from `templates/run-note-template.md` §"If the push already landed". **Add a SKILL.md pointer
  to it during the next slim**, next to the existing `Post-push probe:` line.
- `templates/run-note-template.md` — starter for the daily run note, **plus** the
  index-append rules. It carries the ⚠️ unique-anchor warning that could not be
  added to SKILL.md: every bullet in `dated-runs-index.md` ends with the identical
  tail `siblings intact (demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1)`,
  so a `patch` anchor on "the last line" is NOT unique. Anchor on that run's
  distinctive fragment (e.g. `demo-pm 401 blobs (== local count)`) and verify with
  `grep -c '<YYYYMMDD>.md' references/dated-runs-index.md` == 1.

## ⚠️ Ordering: surgery done AFTER the follow-up commit breaks the NEXT morning's 0/0/0

Verified 2026-09-22. The 09-21 run slimmed SKILL.md and created its three extracted
support files (`method-b-practice-notes.md`, `skill-md-at-cap.md`,
`run-note-template.md`) — but that surgery happened **after** the 09-21 follow-up
commit had already been pushed. The next morning's preflight therefore reported
`Modified: 3, New: 3, Deleted: 0`, and the 09-21 closing assertion failed.

**This is NOT a failed push.** The 0/0/0 check only proves sync for edits that
existed at push time; it cannot cover surgery performed later in the same session.
So when a preflight shows a small residual M/A block that is *entirely skill-doc
edits made the previous evening* (a slew of `references/*.md` + `SKILL.md`, no
sensitive paths, token scan CLEAN), treat it as carry-over: push it as today's
main commit, say so in the run note, and move on. Do **not** go hunting for a lost
commit or try to re-push the previous evening's work.

Ordering rule: do the SKILL.md/reference surgery **before** the follow-up commit
in the same session, or knowingly accept that the next run carries the residual.
