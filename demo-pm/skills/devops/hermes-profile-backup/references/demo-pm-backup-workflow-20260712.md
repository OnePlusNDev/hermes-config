# demo-pm Backup Workflow — 2026-07-12

## Key Patterns

### 1. Git credential helper 403 despite matching active gh user

`gh api user --jq '.login'` → `OnePlusNDev` (correct repo owner).  
Yet `git push` → 403: `denied to OnePlusNTester`.

**Root cause:** git's credential helper had cached OnePlusNTester's token. The `gh auth switch --user OnePlusNDev` forced gh to re-configure the credential helper, and the second push attempt then used the correct credentials.

**Fix:** Always run `gh auth switch --user $REPO_OWNER` (or `gh auth setup-git`) before pushing, even when the active user already appears correct. The old conditional check (`if active_user != repo_owner`) is insufficient.

### 2. GitHub Push Protection scanned ALL files in the commit blob

Initial push was rejected with 3 flagged locations — all in `references/` and `*.md` files of the `pm-triage-cron` skill. After redacting just those 3, the amended commit triggered the scanner again on additional files.

**Lesson:** When GitHub secret scanning fires on a commit, it scans **every blob in that commit**. Redact ALL hex-encoded tokens, base64-encoded tokens, and partial `ghp_`/`sk-`/`github_pat_`/`AKIA` patterns across ALL files in the commit — not just the ones initially flagged. Do a full grep sweep:

```bash
grep -rn 'ghp_[A-Za-z0-9]' demo-pm/ --include='*.md' --include='*.yaml' --include='*.json'
grep -rn '676870' demo-pm/ --include='*.md'  # hex prefix for ghp_
grep -rn 'R0lUSFVC' demo-pm/ --include='*.md'  # base64 prefix for GITHUB_TOKEN=
```

### 3. Files redacted

| File | Token vector | Redaction applied |
|------|-------------|-------------------|
| `pm-triage-cron/references/2026-07-10-xxd-hexdump-token-extraction.md` | Full hex token string, xxd hex bytes + ASCII column, partial token fragments | Hex → `***`, hexdump → `*` bytes |
| `pm-triage-cron/references/2026-07-12-session-base64-token-extraction.md` | Base64-encoded `GITHUB_TOKEN=`, partial token | Base64 → `***`, token → `ghp_***...***` |
| `pm-triage-cron/references/2026-07-12-session-cat-heredoc-plus-python.md` | Partial token fragment | → `ghp_***...***` |
| `pm-triage-cron/SKILL.md` | 3x `ghp_Z1...ghiu`, 1x full hex string, 1x partial base64, 3x xxd hexdump lines | All → `***` / `ghp_***...***` / `*` bytes |
| Plus 5 more reference files with partial `ghp_Z1...ghiu` patterns | Partial token fragments | → `ghp_***...***` |

### 4. Rebase + push (no force needed)

After the amended commit diverged from `origin/main` (demo-tester had pushed 3 new commits), a simple `git rebase --onto origin/main <parent>` followed by `git push` succeeded. No force push was needed because the rebase made it a fast-forward.

### 5. Active user info

- Active gh account: `OnePlusNDev`
- Other accounts on machine: `OnePlusNTester`, `JungleAssistant`, `OnePlusNPM`, `zhangtbj`
- Repo: `OnePlusNDev/hermes-config` (private)
- Profile: `demo-pm`
