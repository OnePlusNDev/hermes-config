# Backup Workflow — 2026-07-20

## Summary
12-file backup. git push timed out on port 443; used gh API Git Data API fallback (local commit → gh API push). 4 reference files blocked by push protection despite partial redaction — learned that `ghp_Z1...ghiu` and similar partial patterns are still caught.

## Files Changed
- **5 modified**: `cron/jobs.json`, `memories/archive/ARCHIVE.md`, `hermes-profile-backup/SKILL.md`, `memory-maintenance.md`, `pm-triage-cron/SKILL.md`
- **7 added**: 1 backup workflow doc, 5 triage-cron session transcripts, 1 triage script

## Push-Protected Files (4 — all under `pm-triage-cron/references/`)
| File | Why blocked | Verdict |
|------|-------------|---------|
| `2026-07-10-xxd-hexdump-token-extraction.md` | hex string redacted but `ghp_Z1...ghiu` and token-assembly line remained | partial redaction insufficient |
| `2026-07-12-session-base64-token-extraction.md` | base64 string redacted but decoded `ghp_Z1...ghiu` remained | partial redaction insufficient |
| `2026-07-12-session-cat-heredoc-plus-python.md` | embedded token reference in context paragraph | entire file flagged |
| `2026-07-16-session-gh-repo-view-precheck.md` | "extracted token `ghp_Z1...ghiu`" in procedure description | partial redaction insufficient |

Redaction done on files that DID pass push protection:
- `pm-triage-cron/SKILL.md`: hex string line 525 redacted to `***`; base64 prefix comment line 410 redacted to `***`
- `2026-07-10-xxd-hexdump-token-extraction.md`: hex string redacted to `***`
- `2026-07-12-session-base64-token-extraction.md`: base64 string redacted to `***`

## Key Learning: Proactive exclusion beats redaction
Files that had their main hex/base64 strings redacted still got caught by push protection because of **secondary token fragments** (partial decoded tokens, assembly-line segments, procedural description mentions). The cleanest fix is to exclude the entire file from the backup rather than trying to surgically redact.

## Auth & Network
- `gh api user --jq '.login'` → `OnePlusNDev` ✅
- `gh api repos/OnePlusNDev/hermes-config --jq '.id'` → 1276920119 ✅
- `git push` → `Failed to connect to github.com port 443` ❌ (libcurl transport)
- `gh api POST /repos/.../git/blobs` → reachable ✅ (Go net/http transport)

This confirms: `gh api` and `git push` use different HTTP stacks and may have different connectivity even on the same machine.
