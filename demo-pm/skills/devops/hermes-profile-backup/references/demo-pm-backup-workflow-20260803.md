# Demo-PM Backup Workflow — 2026-08-03

Cron backup of `demo-pm` profile → `OnePlusNDev/hermes-config` (PUBLIC repo, main branch).

## Outcome

- **2 commits pushed** via gh API Git Data API (git clone failed on port 443 TLS handshake, as usual).
  - `a34b5138` — backup commit: 11 modified + 3 new files
  - `a8cc7704` — fix commit: 9 modified + 1 deleted
- Final HEAD: `a8cc7704`, 564 blobs under `demo-pm/`; sibling dirs intact (demo-dev: 5, demo-tester: 8, tester-01: 5).
- No plaintext `sk-` keys in config.yaml (all `api_key: ''`, key_env pattern in use) — no replacement needed.

## New learning #1: push protection let a full hex token through

`pm-triage-cron/SKILL.md` line 697 contained a **complete 80-hex-char token**:
`***`
which decodes to a full 40-char `[GHP_REDACTED]` GitHub PAT.

- The blob upload **SUCCEEDED** in commit `a34b5138` — push protection did not flag the hex form.
- In the same run, 7 other files with *fragments* (12-char `ghp_` prefixes, 16-hex-char strings)
  WERE blocked and gracefully skipped (kept remote blob).
- Fix: redacted the hex in the local SKILL.md (`h = '***'`), also redacted the xxd hex/ASCII columns
  and a base64 fragment (`# [BASE64_REDACTED]...YmdoaXUK` → `# [BASE64_REDACTED]`),
  re-ran the script → commit `a8cc7704` replaced the blob.
- Lesson: GitHub's encoded-token detection is inconsistent; the pre-upload scan is the real gate.
  Verify remote blobs after push (`gh api .../contents/...` + base64 decode + grep).

## New learning #2: script EXCLUDE_PREFIX drift on tmp_*.py

The standalone script's `EXCLUDE_PREFIX` had `".tmp_"` but NOT `"tmp_"`, so the no-dot temp
script `tmp_pm_triage.py` was collected and uploaded as a NEW file in commit `a34b5138`.
The SKILL.md exclude list documented `**/tmp_*.py` — the script was out of sync.

- Fix: `EXCLUDE_PREFIX = {"config.yaml.bak.", ".tmp_", "tmp_", "memory_backup_", "._"}` (script patched).
- Re-run then listed `D demo-pm/tmp_pm_triage.py` and removed it from the remote tree in commit `a8cc7704`.
- Lesson: when the SKILL.md exclude list grows, update the script's `EXCLUDE_PREFIX` /
  `EXCLUDE_NAMES` / `EXCLUDE_DIRS` in the SAME pass — they are a matched pair.

## Also noted

- `memory_backup_20260723.json` contained a real `sk-5c1...` DeepSeek key — correctly excluded
  by the `memory_backup_` prefix rule, never uploaded.
- Pre-upload token scan of 565 files: 55 regex hits, most false positives (`desk-rejected`,
  `task-specific` match `sk-[A-Za-z0-9]{8,}`) or documented examples with `...` — always
  verify hits before acting; filter placeholders (all-`x` suffixes) and `...`-containing strings.
