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
