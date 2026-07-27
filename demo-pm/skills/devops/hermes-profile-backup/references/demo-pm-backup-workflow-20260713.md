# Backup Workflow: 2026-07-13

## Context
Cron-mode backup of `demo-pm` profile to `OnePlusNDev/hermes-config` repo. Method A (rsync + git push).

## What happened
1. Config scan: **clean** — no plaintext API keys in config.yaml
2. Clone, rsync, gitignore update, commit all succeeded normally
3. **git push rejected** by GitHub Push Protection (GH013): 3 reference docs contained hex-encoded / base64-encoded / partially-shielded GITHUB_TOKEN patterns:
   - `2026-07-10-xxd-hexdump-token-extraction.md` — xxd output with hex bytes of the token and a Python hex literal
   - `2026-07-12-session-base64-token-extraction.md` — base64-encoded token string
   - `2026-07-12-session-cat-heredoc-plus-python.md` — `ghp_Z1...ghiu` in prose text

4. **Redaction pass**: 10+ `patch()` calls across 3 files:
   - xxd hex bytes → `2a2a 2a2a...`
   - ASCII column → `***`
   - Hex string literal `'6768705f...'` → `'***'`
   - Base64 string `R0lUSFVC...` → `***`
   - Partial token `ghp_Z1...ghiu` → `ghp_***...***`
   - Token fragment `ZOVGCrkIPckXiZ8J` → `***`
   - Full concatenation line → `ghp_***...***`

5. **Pre-commit scan**: `grep -n 'ghp_[A-Za-z0-9]\|6768705f\|R0lUSFVC'` confirmed zero remaining matches

6. **Amend + rebase + push**:
   - `git add -A && git commit --amend --no-edit` — replaced old commit
   - `git push` → rejected: "fetch first" (remote had diverged from the earlier failed push)
   - `git pull --rebase` — rebased the amended commit on the drifted remote
   - `git push` → **success**

## Key lessons
- **Push protection hits Method A too**, not just gh API — the git pre-receive hook scans blob content regardless of transport
- **`git commit --amend` alone is not enough** after a failed push — the remote has the (rejected) commit SHA in its object DB even though no ref points to it; the divergence triggers a non-fast-forward rejection
- **Always verify with grep** after redacting — hex columns can be redacted but leave the ASCII column readable
- **Multi-file redactions**: redact all flagged files in one pass, `git add -A` once, `git commit --amend --no-edit` once
