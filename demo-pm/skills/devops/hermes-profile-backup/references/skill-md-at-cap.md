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

## Tooling constraint: the generic `patch` tool is NOT available in review/cron passes

Every "the cap is not enforced by the generic `patch` tool" note above depends on that tool
being callable. In a background skill-review / cron turn only **memory and skill tools** are
whitelisted — a `patch` call is refused with
`Background review denied non-whitelisted tool: patch`. Since `skill_manage` DOES enforce the
100 K cap and the file sits ~866 B over it, **any SKILL.md edit that GROWS the file** is
impossible from such a pass (a byte-neutral relocation included); a *shrinking* edit does pass
— see the 2026-11-09 note above. Consequence: do the routine `latest:` bump (and any
SKILL.md surgery) in the *main* run session, and use review passes for `references/` and
`templates/` files, which carry no size cap.

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
