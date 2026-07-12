# demo-pm Backup 2026-07-11 — Hexdump Secret Redaction + gh API Push

## Summary

44-file backup to `OnePlusNPM/hermes-config`. Key events:
- No plaintext `sk-` keys in config.yaml (all `api_key: ''` using key_env pattern)
- Hex-encoded `ghp_` token found and redacted in a pm-triage-cron reference doc
- `git push` over HTTPS failed (port 443 timeout); successfully fell back to `gh api` Git Data API (Method B)

## Secret Redaction Details

**File:** `skills/devops/pm-triage-cron/references/2026-07-10-xxd-hexdump-token-extraction.md`

Three leak vectors were found and redacted:

| Vector | Location | Redacted content |
|--------|----------|-----------------|
| Python hex string | `h = '6768705f5a315379...'` | Replaced with `h = '***'` |
| Hexdump hex column | `5f54 4f4b 454e 3d67 6870 5f5a...` | Replaced with `2a2a 2a2a...` (asterisk hex) |
| Hexdump ASCII column | `_TOKEN=ghp_Z1Syf...` | Replaced with `_TOKEN=*********` |

The xxd output example had the full `ghp_` token readable in the ASCII representation column even after hex bytes were redacted — a separate leak channel that needed independent treatment.

## Push Method

Used the incremental Python script (`gh-api-git-data-incremental-push.py`), adapted:

| Parameter | Value |
|-----------|-------|
| Owner | `OnePlusNPM` (active account, matched repo owner — no auth switch needed) |
| Repo | `hermes-config` |
| Profile | `demo-pm` |
| Locals | 638 tracked files, 608 remote blobs |
| Changed | 13 modified, 31 new, 0 deleted |
| Unchanged | 594 entries merged from remote tree |

## Files Backed Up (by category)

- **Config**: `.gitignore` (expanded from 16→40+ patterns)
- **Cron**: `jobs.json` (runtime counters), `pm_triage_script.py` (new)
- **Memory**: `MEMORY.md`, `USER.md` (updated with session learnings)
- **Skills (updated)**: `hermes-profile-backup`, `hermes-profile-diagnostics`, `github-auth`, `github-issues`
- **Skills (new)**: `pm-triage-cron` (SKILL.md + 22 reference docs)
- **Backup skill refs**: 6 new workflow reference docs + incremental push script

## Excluded Files (rsync)

All 30+ exclusion categories applied. Key check: `home/.config/gh/hosts.yml` was already tracked from a prior backup but not re-committed (rsync excluded it). Legacy tracked credentials remain in git history — noted as a pitfall.
