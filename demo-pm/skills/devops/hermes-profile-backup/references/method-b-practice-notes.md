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
| 2026-09-22 | no | remote stable at cdefeb1d36b0 through the blob phase |
| 2026-09-23 | **yes** | remote advanced `9c55330dae07` → `a37580dda96f` between blob phase and ref PATCH; absorbed by the budgeted single plain re-run (attempt 3 clean). Same run also hit a NEW failure mode — see "Shared /tmp payload namespace" below. |
| 2026-09-24 | no | **first-try, no aborts at all** — the 09-23 `mkdtemp` payload fix held (no shared-`/tmp` deletion). Remote advanced `6c156eb1e2c4` → `46c22a23e2e5` (sibling demo-dev backup, 12:00:45Z) **before** the script's own Step 2, then stayed stable through commit time. Also: gh active account was owner-active throughout (09-23's `OnePlusNTester` flip did NOT recur, and the pre-push re-check held) — a data point that the flip is intermittent, not systematic. Follow-up commit likewise absorbed a fresh remote advance (`e51452458970`) on its Step 2. Closing preflight `Modified: 0, New: 0, Deleted: 0`. |
| 2026-09-26 | n/a — **1 abort, account flip (not the 422 race)** | Pre-flight active gh user was **`zhangtbj`** (`push=false`) → switched to `OnePlusNDev`; attempt 1 then died at the FIRST blob with `FATAL uploading demo-pm/cron/jobs.json: gh: Not Found (HTTP 404)` — a re-check showed `zhangtbj` active again, i.e. the keyring race re-flipped the account *between the pre-flight switch and the blob POST* (~1 min). Second switch → clean attempt 2 (7 blobs, subtree `7b528200e686`, commit `3734ef8ff71b`, **ref PATCH first try — no 422 race**; remote stable at `03b61c6a6c89` through the blob phase). Lessons: (a) the check-TWICE rule needs to fire as late as possible — the flip won; (b) the flipper can be an account NOT in the previously-recorded set (new: `zhangtbj`), so never special-case a single "known bad" account. |
| 2026-09-27 | **yes** | remote advanced `8c5cb9e94229` → `b3d2005d4c11` (concurrent sibling backup) during the blob phase; the ref PATCH died `HTTP 422 non-fast-forward` on attempt 1 → absorbed by the budgeted **single plain re-run** (attempt 2 clean, identical 4 blobs + subtree `bd929bdcb45a`, remote stable at `b3d2005d4c11` through commit time). Gh active account was `OnePlusNDev` (owner, `push=true`) throughout — **no flip**; 09-26's mid-run `zhangtbj` re-flip did not recur. Confirms the 422 race is driven by sibling `main` advances, independent of account state. |
| 2026-09-28 | **yes** | remote advanced `c8a48bb08efa` → `77e69333f412` (concurrent sibling backup) during the blob phase; the ref PATCH died `HTTP 422 non-fast-forward` on attempt 1 → absorbed by the budgeted **single plain re-run** (attempt 2 clean, identical 9 blobs + subtree `7652d181b1d8`, remote stable at `77e69333f412` through commit time). Pre-flight active gh user was **`zhangtbj`** (`push=false`, the 09-26 flipper) → `gh auth switch --user OnePlusNDev` required before any blob POST; the flip did **not** recur mid-run this time, so the pre-flight switch held. No network flakiness; the `mkdtemp` payload fix held. |
| 2026-09-29 | no | **1 abort — mid-run account flip** (NOT the 422 race): pre-flight active gh user was **`zhangtbj`** (`push=false`) → `gh auth switch --user OnePlusNDev`; the flip **recurred MID-RUN** — attempt 1 died at the FIRST blob with `FATAL uploading demo-pm/cron/jobs.json: gh: Not Found (HTTP 404)` (the documented "every blob-404 is an account flip" case) → second switch, clean re-run (blob SHAs idempotent, so the re-run costs nothing). Remote **stable at `cdcabbeb7545`** through commit time → no ref-PATCH 422 race. 5 blobs + subtree `eec00ef16904` + top tree `07e133c7e8c6` in one clean pass. No network flakiness; the `mkdtemp` payload fix held. |
| 2026-09-30 | no | **first-try, 0 aborts** — pre-flight active gh user was **`zhangtbj`** (`push=false`) → `gh auth switch --user OnePlusNDev`; re-checked immediately pre-run and the switch **held** (no mid-run flip). Remote **stable at `6cdc630521ec`** from preflight through commit time (no sibling advance) → 8 blobs + subtree `52cb600c33b4` + top tree `1ad643b365c8` in one clean pass, **no ref-PATCH 422 race**. No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-01 | no | **first-try, 0 aborts** — pre-flight active gh user was **`OnePlusNTester`** (`push=false`) → `gh auth switch --user OnePlusNDev`; re-checked immediately pre-run and the switch **held** (no mid-run flip). Remote **stable at `1fcd2063e654`** from preflight through commit time (no sibling advance) → 6 blobs + subtree `06db308902a5` + top tree `fac92ca2ab39` in one clean pass, **no ref-PATCH 422 race**. No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-03 | no | **first-try, 0 aborts** — pre-flight active gh user was **`OnePlusNDev`** (owner, `push=true`) — **no switch needed** (`GITHUB_TOKEN` unset), no mid-run flip. Remote **stable at `5b541e866d54`** from preflight through commit time (no sibling advance) → 8 blobs + subtree `874cf6a84a11` + top tree `102a5bd05ee7` in one clean pass, **no ref-PATCH 422 race**. No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-03 (2nd, 20:00) | no | **first-try, 0 aborts** — pre-flight active gh user was **`OnePlusNTester`** (`push=false`) → `gh auth switch --user OnePlusNDev`; re-checked immediately pre-run and the switch **held** (no mid-run flip). Remote **stable at `0377a76d082e`** from preflight through commit time (no sibling advance) → 2 blobs + subtree `96e0c79d5df4` + top tree `49d822cb7ed9` in one clean pass, **no ref-PATCH 422 race**. The 2 `D` = genuine local skill removals (apple/apple-notes, software-development/systematic-debugging). No network flakiness; the `mkdtemp` payload fix held. **First same-day repeat run** → run note uses the `YYYYMMDDb` suffix. |
| 2026-10-04 | no | **first-try, 0 aborts** — pre-flight active gh user was **`OnePlusNDev`** (owner, `push=true`) — **no switch needed** (`GITHUB_TOKEN` unset), no mid-run flip. Remote **stable at `7f5418a4ef91`** from preflight through commit time (no sibling advance) → 4 blobs + subtree `b3502ed58de2` + top tree `6c237a8753a4` in one clean pass, **no ref-PATCH 422 race**. No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-05 | no | **first-try, 0 aborts** — pre-flight active gh user was **`OnePlusNDev`** (owner, `push=true`) — **no switch needed** (`GITHUB_TOKEN` unset), no mid-run flip. Remote **stable at `b59147ff4803`** from preflight through commit time (no sibling advance) → 4 blobs + subtree `406e5ac8db02` + top tree `919563bb1650` in one clean pass, **no ref-PATCH 422 race**. No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-06 | **yes** | remote advanced `08d2e00d49ea` → `c332a3c5a980` (concurrent sibling backup) during the blob phase; attempt 1's ref PATCH died `HTTP 422 non-fast-forward` → absorbed by the budgeted **single plain re-run** (attempt 2 clean, identical 6 blobs + subtree `7aa4284ef2bf`, remote stable at `c332a3c5a980` through commit time). Pre-flight active gh user was **`OnePlusNTester`** (`push=false`) → `gh auth switch --user OnePlusNDev` (re-checked immediately pre-run, held, no mid-run flip). No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-07 | no | **first-try, 0 aborts** — pre-flight active gh user was **`JungleAssistant`** (`push=false`, a **NEW flipper account**) → `gh auth switch --user OnePlusNDev`; re-checked immediately pre-run and the switch **held** (no mid-run flip, `GITHUB_TOKEN` unset). Remote advanced `4cbcf4355bf9` → `79032de7d9e8` (concurrent sibling backup) *before* the script's own Step 2, then stayed **stable at `79032de7d9e8`** through commit time → 4 blobs + subtree `ef0a2e79644c` + top tree `9cb9d858a3fb` in one clean pass, **no ref-PATCH 422 race**. No network flakiness; the `mkdtemp` payload fix held. |

**Maintain this table with one row per run** — the row belongs in the daily follow-up
commit alongside the run note, the index bullet, and the SKILL.md `latest:` pointer.
It is the only continuous record of the 422-race / account-flip recurrence, so a
skipped row makes the pattern look rarer than it is. (09-29 and 09-30 originally
shipped without rows; backfilled 2026-09-30.)

**Same-day repeat runs** (first hit 2026-10-03, which ran at both 10:36 and 20:00 CST): the
daily run-note filename is `YYYYMMDD.md`, so a second run on the same date takes a
`YYYYMMDDb.md` suffix (e.g. `demo-pm-backup-workflow-20261003b.md`) and gets its own table row
(labelled `2026-10-03 (2nd, HH:MM)`) and its own index bullet. This keeps each run's record
atomic and the index `grep -c '<file>.md' == 1` verification clean — appending a second section
to the existing same-date file instead would make that check read 2 and hide a real duplicate
from a future run. The SKILL.md `latest:` pointer stays at the date and is **not** re-bumped.

Note (2026-09-21): the remote ref can advance between the **preflight** and the
**backup script's own Step 2** (the script re-reads it, so this is harmless — it
just means the diff counts you saw in preflight may be recomputed against a newer
HEAD). Run `scripts/post-push-verify.py` *after* the commit, not after the
preflight, for the authoritative numbers.

## Shared `/tmp` payload namespace — sibling profiles delete our payload files

**Hit 2026-09-23 on attempt 1** (the first run of the day):

```
FATAL uploading demo-pm/skills/devops/hermes-profile-backup/SKILL.md:
open /tmp/gh_payload_1790164860156_67749.json: no such file or directory
```

It died on the **largest** payload (~100 KB `SKILL.md` → base64 ≈ 135 KB) after two small
blobs had uploaded fine. The payload file had been written moments earlier, so this is not
a write bug: something **deleted it mid-run**.

**Root cause (confirmed by grep):** the **demo-tester profile's cron job blanket-cleans
the shared `/tmp/gh_payload_*.json` namespace** — its own skill notes describe reaping
"200+ files from sibling sessions" and its logs contain the literal
`rm -f /tmp/gh_payload_*.json`. Both profiles used the *same* prefix in the *same* `/tmp`,
so a sibling's tidy-up deletes OUR in-flight payloads.

**Fix (applied 2026-09-23 to `scripts/gh-api-standalone-subtree-backup.py`):**

```python
_PAYLOAD_DIR = tempfile.mkdtemp(prefix="hermes-backup-payload-")
...
payload_file = os.path.join(_PAYLOAD_DIR, f"payload_{int(time.time()*1000)}.json")
```

A private per-process directory, with a prefix that does **not** match the
`gh_payload_*` glob → sibling clean-ups cannot see our payloads.

Rules:
- If you ever see `FATAL uploading <path>: open /tmp/gh_payload_...: no such file or
  directory`, do **not** treat it as a permissions/disk problem. Just re-run (blob SHAs
  are idempotent) — but also check that the private-dir fix is still in the script.
- More generally: **never assume `/tmp/<generic-name>` is yours** on this machine. Sibling
  profiles run concurrently and some of them sweep shared globs. Use `mkdtemp`.
- This is a *different* failure mode from the network `i/o timeout` in
  `network-flakiness-and-verify-tooling.md` §1: same "just re-run" remedy, entirely
  different cause. Read the error string before reaching for the network explanation.

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

## Characterizing the M set for the run note

After the push, classify each `M` as routine runtime churn vs benign carry-over
doc lag with `scripts/characterize-diff-vs-prev-head.py` — pass the **pre-push**
remote HEAD (the SHA the backup script logged at Step 2, or
`--commit=<your backup commit sha>`, which derives `parents[0]`).

Diffing against the CURRENT remote is the trap: right after a push the current
remote tree equals local, so everything reads `IDENTICAL` and you learn nothing.
Recipe + reading guide + worked example:
`references/run-note-diff-characterization.md`.
