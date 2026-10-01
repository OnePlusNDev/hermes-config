# Run-note template — daily demo-pm backup

Copy this to `references/demo-pm-backup-workflow-YYYYMMDD.md` and fill in the
placeholders. Then append an index bullet to `references/dated-runs-index.md`
(see the unique-anchor warning below).

Keep it short: this is the record of one run, not a tutorial. The value is in
the numbers (SHAs, counts, diff shape) that let a future run notice drift.

---

```markdown
# demo-pm backup run — YYYY-MM-DD

## Result
**Method B (standalone subtree, no clone)** — <success, FIRST-TRY | N aborted attempts>.
Main commit: `<40-char sha>`
URL: https://github.com/OnePlusNDev/hermes-config/commit/<sha>
Diff: **<n> M, <n> A, <n> D**.

## Pre-flight
- `gh api user` → `<login>` (repo owner) — <no switch needed | switched from X>
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **<n>** matches;
  `api_key: '<non-empty>'` → **<n>** matches; all **<n>** `api_key:` lines are `''`; the
  only `key_env` occurrence is a comment (line <n>)
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (<n> B; <var names>) excluded, never uploaded; no
  `auth.json` / `auth.lock` / `state.db*` in tree
  (list var **names only**, never values — `grep -oE '^[A-Z_]+=' .env | tr -d '='` — so the note
  never quotes a secret)

## Diff (<n> M, <n> A, <n> D)
```
M  demo-pm/<path>
A  demo-pm/<path>
```
Characterize each `M` against the **pre-push** remote HEAD with
`scripts/characterize-diff-vs-prev-head.py <PRE_PUSH_HEAD>` (or `--commit=<sha>`) and state per
file whether it is routine runtime churn or benign carry-over lag — see
`references/run-note-diff-characterization.md`. Do NOT diff against the current remote: right
after a push it equals local and everything reads `IDENTICAL`.
`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local
one (<n> bytes; <n> chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **<n>**; remote HEAD `<12-char sha>`, <n> blobs
- Preflight diff: `Modified: <n>, New: <n>, Deleted: <n>` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `<sha>` at blob-phase start and **stayed there through commit time** →
  **no ref-PATCH 422 race**; the ref PATCH succeeded on the first attempt.
- <no network flakiness | N aborted attempts + what fixed it>
- <n> blobs uploaded, subtree `<sha>`, top tree `<sha>`, commit + ref in one clean pass.

## Post-push remote verification
- Remote HEAD `<sha>`; total blobs **<n>**, `demo-pm` blobs = **<n>** (== local file count <n>);
  by top dir: demo-pm <n>, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **<n>** `sk-` matches; `api_key` lines = <n>, non-empty = **<n>**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `<prev>` → `<today>` +
`references/method-b-practice-notes.md` "Observed on recent runs" table row, pushed with the
same standalone-subtree script. (The table row is part of the follow-up, not optional — a skipped
row leaves the 422-race / account-flip recurrence log stale, which is exactly what happened on
09-29 and 09-30.) Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.

**Fold ALL doc edits into this commit** — including any reference-file additions or
triage-recipe edits (e.g. a new `references/*.md`, or an update to
`references/curator-archive-churn-triage.md`). An edit made *after* the follow-up push
breaks the `0/0/0` closing assertion and costs an extra commit to re-sync. Verified
2026-09-25: an after-the-fact `curator-archive-churn-triage.md` edit required a 3rd
commit (`5f8e78cf1073`); the clean pattern is to draft every doc change, then push the
follow-up once.
```

---

## ⚠️ Appending the index bullet: the anchor must be UNIQUE

Every bullet in `dated-runs-index.md` ends with the **identical** tail:

```
..., siblings intact (demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1)
```

So `patch(mode='replace')` anchored on just the last line's tail is ambiguous —
it would match earlier bullets too. Anchor on a fragment unique to the *previous*
run's bullet, e.g. `demo-pm 401 blobs (== local count)` (verified 2026-09-21).

Verify the append landed exactly once — both checks must print `1`:

```bash
grep -c '<YYYYMMDD>.md' references/dated-runs-index.md   # 1 = appended once, not duplicated
grep -c 'latest: <today>' ../SKILL.md                    # 1 = pointer moved, no stale duplicate
```

## Why `patch` and not a shell append

A heredoc/redirect targeting a path under `~/.hermes` trips
`tirith:dotfile_overwrite` in cron mode. Use the `patch` tool.

The `patch` tool will warn "was modified by sibling subagent … but this agent
never read it" even when your view is current (reading the tail via
`terminal(tail -…)` does not register as a read). **Benign — do not abandon the
append over it.** The `grep -c` == 1 checks above are the real verification.
