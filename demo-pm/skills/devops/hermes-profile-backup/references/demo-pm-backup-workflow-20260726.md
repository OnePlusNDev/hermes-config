# 2026-07-26 Cron Backup: repr() truncation, ghp_*** triggers push protection

## Summary

17-file backup via Method A (rsync + git push). Three push protection blocks resolved through two redaction passes.

## Key Learnings

### 1. Python `repr()` truncation masks full tokens

`repr(b'ghp_Z1...ghiu')` displayed as `ghp_Z1...ghiu` in tool output, but the actual bytes contained the **full 40-character token** `ghp_Z1...ghiu`. The `...` was display truncation by the tool context rendering, not the actual file content.

**Detection fix:** Used `line.hex()` to get the raw byte hex, which revealed the full token string.

### 2. `ghp_***...***` triggers push protection

The "redacted" pattern `ghp_***...***` still starts with `ghp_` — GitHub's push protection scans for any `ghp_` prefix, not just complete tokens. Three flaggings occurred:
- SKILL.md:779 — documentation text with `ghp_Z1...ghiu` in backtick code
- SKILL.md:812 — Python list literal `['ghp_Z1...ghiu', ...]` (was a full token, not `...`)
- 2026-07-25-grep-truncation-hides-full-tokens.md:18 — `ghp_Z1...ghiu` in code block

**Fix:** Replaced ALL `ghp_`-prefixed partial patterns with `[GHP_REDACTED]` instead of `ghp_***...***`.

### 3. Backup skill's own SKILL.md must be in scan scope

The initial redaction script's TARGET_FILES list only included sibling skills (`pm-triage-cron/`) and missed `hermes-profile-backup/SKILL.md` itself, which contained the full hex token on line 812.

**Fix:** Added the backup skill's own files to the redaction target list.

## Files Modified

17 files staged, 13 after redaction restored some to HEAD:
- 3 new reference files
- 10 modified config/memory/skill files
- 2 runtime files deleted (feishu_seen_message_ids.json, response_store.db)

## Commands Used

```bash
gh auth switch --user OnePlusNDev
gh repo clone OnePlusNDev/hermes-config /tmp/hermes-$(date +%s)
rsync -a --exclude ... ~/.hermes/profiles/demo-pm/ /tmp/hermes-*/demo-pm/
python3 /tmp/deep_redact.py   # byte-level replacement of full token hex strings
git add -A && git commit --amend --no-edit
git pull --rebase origin main  # remote had diverged
git push origin main           # succeeded after 2nd redaction pass
gh auth switch --user OnePlusNPM  # restore original
```
