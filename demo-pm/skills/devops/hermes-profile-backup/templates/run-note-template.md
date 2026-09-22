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

## Diff (<n> M, <n> A, <n> D)
```
M  demo-pm/<path>
A  demo-pm/<path>
```
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
Run note + index bullet + SKILL.md `latest:` pointer `<prev>` → `<today>`, pushed with the
same standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.
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
