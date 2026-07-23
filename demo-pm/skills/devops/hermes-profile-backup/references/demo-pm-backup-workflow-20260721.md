# Demo-PM Backup Workflow — 2026-07-21

**Key events:** Redacted hex/base64 tokens in cross-skill SKILL.md + references; `git push` timed out on port 443; gh API Git Data push succeeded.

## Stats

| Metric | Value |
|--------|-------|
| Files changed | 26 (6 modified + 17 new + 3 deleted) |
| Remaining tracked blobs | 539 in `demo-pm/` |
| Push protection blocks | 0 — all redactions thorough |
| Push method | gh API (port 443 timed out for libcurl) |

## Redaction detail

Three files had encoded tokens that were redacted before staging:

1. **`pm-triage-cron/references/2026-07-10-xxd-hexdump-token-extraction.md`**
   - Hex string `6768705f5a315379...` → `***`
   - xxd hex byte column `67 68 70 5f 5a 31 53 79...` → `2a 2a 2a ...`

2. **`pm-triage-cron/references/2026-07-12-session-base64-token-extraction.md`**
   - Base64 string `R0lUSFVCX1RPS0VOPWdocF9a...` → `***`
   - Decoded line `GITHUB_TOKEN=ghp_Z1Syf...` → `GITHUB_TOKEN=***`

3. **`pm-triage-cron/SKILL.md`** (cross-reference cascade)
   - Same hex string as #1 at line 561 → `***`

## Push failure pattern

**Symptom:** `git push` failed with `fatal: unable to access ... Failed to connect to github.com port 443`
**Diagnosis:** libcurl blocked; `gh api` (Go net/http) worked fine
**Workaround:** Wrote `/tmp/gh-api-push.py` that used `git ls-tree -r HEAD` + gh API Git Data API to upload 23 blobs, create tree, commit, and update ref
**Verification:** `gh api repos/OnePlusNPM/hermes-config/git/trees/main?recursive=1` confirmed 539 blobs

## Lessons

- **`timeout` command not available on macOS.** The skill's `timeout 60 git push origin main` fails with `command not found`. Either rely on `terminal()`'s built-in timeout or install coreutils for `gtimeout`.
- **Thorough redaction passes push protection.** Replacing hex string + base64 string + decoded line + xxd hex column with `***` is sufficient — 0 files were blocked.
- **`.gitignore` drifts.** The repo's `.gitignore` was missing `**/triage_check.py` and `**/.tmp_*` (both were correct in the SKILL.md template but a previous backup created `.gitignore` before those patterns were added). After updating `.gitignore`, `git rm --cached` was needed to remove the three already-tracked `.tmp_*` and `.skills_prompt_snapshot.json` files from git tracking.
- **Legacy tracked excluded files.** `.skills_prompt_snapshot.json`, `.tmp_cron_triage.py`, and `.tmp_triage.sh` existed in the remote tree from a previous backup. Used `git rm --cached` to remove from tracking (does not delete local copies).
