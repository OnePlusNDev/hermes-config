# SKILL.md size cap — headroom is thin, keep it that way

**Status 2026-09-21: SKILL.md was 100,142 chars (limit 100,000) → patched back
under the cap the same run** by extracting the Method B practice-note paragraph
to `references/method-b-practice-notes.md` and replacing it with a 3-line pointer.
Headroom after the slim is only a few hundred chars.

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
- The dated-run **narrative paragraphs** (e.g. the "Practice note (extended
  through 2026-09-11)" block) — largely superseded by `references/dated-runs-index.md`.

⚠️ `skill_view` returns a TRUNCATED blob for this file (it exceeds the tool's
response cap), so the file must be read with `read_file` + `offset`/`limit`
before any surgery. Do not patch a 100 KB file you haven't fully read.

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
