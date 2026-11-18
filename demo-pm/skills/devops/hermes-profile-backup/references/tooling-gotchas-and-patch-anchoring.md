# Tooling gotchas: script usage + patch anchoring

Four traps that all cost time on 2026-11-17. None are environment failures — they are
properties of the scripts and of the `patch` tool as used on this skill's own files.

## 1. The backup scripts implement no `--help`

`gh-api-standalone-subtree-backup.py` and `gh-api-standalone-backup.py` **ignore unknown
argv entirely and run the full backup.** There is no usage/help branch.

Verified 2026-11-17: `python3 gh-api-standalone-subtree-backup.py --help 2>&1 | head -30` was
intended to print usage. It instead executed Steps 1–7 and **created and pushed the run's main
commit** (the pipe closing at Step 5 did not stop it; the commit landed clean).

Rules:
- **Never probe the interface by running it.** Read the module docstring (`read_file` on the
  first ~30 lines) when you need to know what a script takes.
- When it genuinely matters, pass `--help`-style flags only to scripts you have already seen
  branch on `sys.argv`.
- If you do trigger a run this way: the state is not corrupt (the run is idempotent and the
  preflight already gated the content), but **verify remote HEAD immediately** and treat that
  commit as the main commit rather than pushing a second one.

## 2. `characterize-diff-vs-prev-head.py` has a stale default baseline — the preflight wins

With no `PRE_PUSH_HEAD` argument the probe prints:

```
NOTE: no PRE_PUSH_HEAD given - derived parents[0] of current main (<sha>). Correct ONLY if no
sibling commit landed after yours.
```

That caveat covers siblings, but there is a **second** way it goes wrong: if the remote HEAD is
*yesterday's follow-up commit*, then `parents[0]` predates that follow-up, so the probe reports
**the follow-up's own four items as still-modified/added.** 2026-11-17 read `9 M / 2 A` from the
probe while the truth, measured against actual HEAD, was **`7 M / 1 A`** — and the landed commit
contained exactly 8 files.

Rules:
- **Quote the preflight's `Modified/New/Deleted` as the authoritative count** — it diffs against
  the real current HEAD.
- Use `characterize-*` only for *per-file content* ("is this routine churn or a real edit?"), and
  ignore its headline totals whenever the note says it derived the baseline.
- If the numbers disagree, say so explicitly in the run note (one sentence: probe baseline was
  `ca797b5e908b`, preflight baseline was the follow-up commit, here is why they differ) rather
  than silently quoting one.
- To make the probe correct, pass the SHA: `characterize-diff-vs-prev-head.py <PRE_PUSH_HEAD>`.

## 3. A Python-appended index bullet is ONE physical line

Bullets written by the append helper (`write_file` a `BULLET = ("..." "..." "...")` script) land
as a single line with no internal newlines. A `patch` `old_string` transcribed from the Python
source (adjacent string literals, or a line-wrapped display of it) therefore **can never match** —
`patch` has no fuzzy rescue across a newline that isn't in the file.

Anchor instead on a **short fragment inside the single line**, addressed by the bullet's own
filename so it stays unique:

```
`references/demo-pm-backup-workflow-<YYYYMMDD>.md` -- Method B run, **FIRST-TRY, 0 aborts (no 422 race)**:
```

Shorter is better; the filename prefix is what makes it unique.

## 4. Never let a mid-sentence `old_string` shear off the clause after it

2026-11-17: replacing

```
**no ref-PATCH 422 race**. Churn re-read from the uploaded blobs: task-polling 7011->**7059**
```

with text that ended `...so this is *not* a zero-422 day.` **deleted the `Churn re-read … 7059`
clause** and left a stray `day., config-backup 147->**148**`. `patch` reports success; nothing
warns.

Rules for editing inside a long table row or bullet:
- Carry the **entire remaining clause in BOTH** `old_string` and `new_string`, or
- anchor on a boundary that ends the replacement naturally (`|`, a closing backtick, a full stop
  followed by a capital letter, the row terminator ` |`).
- **Re-read the joined sentence after the patch** — `grep -o '.\{0,60\}<new phrase>.\{0,90\}'` —
  and confirm the text that follows is what you expect. This is the only cheap way to catch a
  shear, because the tool's own diff hunk will show the line as replaced, not truncated.

## 5. The "no 422 race" claim hides in the HEADLINE

The run note's `## Result` first line and the index bullet's opening clause are where
`FIRST-TRY, 0 aborts (no 422 race)` gets written — and the template's existing rule
("do NOT write 'no network flakiness' until the FOLLOW-UP has landed green") is easy to satisfy in
the body while the headline still asserts a clean day.

2026-11-17: main commit clean, **follow-up hit the 422 race** (sibling `demo-dev` landed between
its Step 2 and Step 7) and needed the one budgeted plain re-run. The note had already shipped with
`(no 422 race)` in the headline.

- Decide the headline **after** the follow-up outcome is known, but the note ships *inside* the
  follow-up — so write it as a two-part claim from the start:
  `main commit FIRST-TRY, 0 aborts; the FOLLOW-UP needed one budgeted re-run for the 422 race`
  (adjust to "follow-up also clean" only once you have seen its `Done:` line).
- If the wrong version already shipped, **a small correction commit is the documented remedy**
  (3 doc files: run note Result + Execution notes, index bullet headline, practice-notes row).
  Under-counting the 422 recurrence log is worse than one extra commit — that log is what future
  runs use to judge whether the race is getting worse.
