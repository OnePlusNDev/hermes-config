# demo-pm backup run — 2026-09-23

## Result
**Method B (standalone subtree, no clone)** — success, **NOT first-try: 2 aborted attempts**
(1 payload-file flake + 1 ref-PATCH 422 race), 3rd attempt clean.
Main commit: `763a2b6432940babf15d03ec438bbf1b63e6a45e`
URL: https://github.com/OnePlusNDev/hermes-config/commit/763a2b6432940babf15d03ec438bbf1b63e6a45e
Diff: **6 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → `OnePlusNTester` — **WRONG account, `gh auth switch --user OnePlusNDev` required**
  (the 09-17→09-22 runs mostly reported "no switch needed"; today the tester account was active again)
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; the
  only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; GITHUB_USERNAME, GITHUB_EMAIL, GITHUB_TOKEN, GATEWAY_PORT, AGENT_NAME,
  AGENT_ROLE, DEEPSEEK_API_KEY, TERMINAL_ENV) excluded, never uploaded; no
  `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (6 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/references/method-b-practice-notes.md
M  demo-pm/skills/devops/hermes-profile-backup/references/skill-md-at-cap.md
M  demo-pm/skills/devops/pm-triage-cron/scripts/pm_fetch.sh
```
`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local
one (17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **407**; remote HEAD `9c55330dae07`, 426 blobs
- Preflight diff: `Modified: 6, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**
- Note: the 09-22 closing assertion held — today's 6 M are genuinely new edits (cron,
  ARCHIVE, the 3 skill docs touched on 09-22, pm_fetch.sh), **no carry-over lag**.

## Execution notes — two aborted attempts, both root-caused

### Attempt 1 — FATAL: payload file vanished mid-upload (NEW pitfall, fixed today)
```
FATAL uploading demo-pm/skills/devops/hermes-profile-backup/SKILL.md:
open /tmp/gh_payload_1790164860156_67749.json: no such file or directory
```
Died on the **3rd** blob — the ~100 KB `SKILL.md`, i.e. the **largest** payload
(base64 ≈ 135 KB). The two small blobs before it uploaded fine.

**Root cause (confirmed by grep, not guessed):** the **demo-tester profile's cron job
blanket-cleans the SHARED `/tmp/gh_payload_*.json` namespace** — its own skill notes
record it as reaping "**200+ files from sibling sessions**", and its logs contain the
literal command `rm -f /tmp/gh_payload_*.json`. Any sibling that removes its own
payloads with that glob deletes **ours** too, because both profiles use the same
prefix in the same `/tmp`.

**Fix applied this run** to `scripts/gh-api-standalone-subtree-backup.py`:
`_PAYLOAD_DIR = tempfile.mkdtemp(prefix="hermes-backup-payload-")` and payloads now
written as `<_PAYLOAD_DIR>/payload_<ms>.json` — a private per-process directory with a
name that does not match the `gh_payload_*` glob, so sibling clean-ups cannot see it.
Blob SHAs are idempotent, so attempt 1's two uploads cost nothing to redo.

### Attempt 2 — ref PATCH 422 "Update is not a fast forward"
All 6 blobs uploaded, subtree `281485e7631ad144560ef4341f87d9280de616c3`, top tree
`fbbc9fa9348fde88be7bb907e6ed84eb455dc887`, commit `191c5384162d4e8916bf928bc6b6ad9dd6da74de`
created — then the ref PATCH was rejected. The remote had advanced
`9c55330dae07` → `a37580dda96f` via a concurrent sibling-profile backup.

**Budgeted exactly ONE plain re-run** (no rebase, no tree surgery — blobs already
uploaded, the re-run just re-parents the identical commit on the fresh HEAD).

### Attempt 3 — success
Remote `a37580dda96f` → `763a2b643294`. 6 blobs, same subtree, top tree
`57b2c448401bf9431704f3c92f9d28dcd75c54b1`, commit + ref in one clean pass.

## SKILL.md cap surgery (done BEFORE the follow-up commit, per the ordering rule)
SKILL.md was **100,665 chars — over the 100,000 ceiling**, so the `latest:` pointer bump
would have been refused outright (the patch tool validates the *resulting* size).
Applied the documented highest-value fix: extracted the ~90-line **Method A rsync
`--exclude` list** to the new **`references/method-a-rsync-excludes.md`**, replaced it in
SKILL.md with a 2-line placeholder + a pointer paragraph.
**SKILL.md: 100,665 → 98,729 chars** (~1.3 KB headroom), pointer bump then succeeded.
The list is mirrored in 4 places now (the new reference, `templates/gitignore-template.txt`,
and the `EXCLUDE_*` sets in both `scripts/` probes) — noted in SKILL.md that changing one
means changing all four.

## Post-push remote verification
- Remote HEAD `763a2b643294`; total blobs **426**, `demo-pm` blobs = **407** (== local file count 407);
  by top dir: demo-pm 407, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-09-22` → `2026-09-23`, plus the
cap-surgery artifacts (`references/method-a-rsync-excludes.md` new; `SKILL.md`,
`references/method-b-practice-notes.md`, `references/skill-md-at-cap.md` edited) and the
hardened backup script — all pushed with the same standalone-subtree script. Afterwards the
preflight is expected to report `Modified: 0, New: 0, Deleted: 0`.
