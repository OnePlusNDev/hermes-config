# Backup Workflow: 2026-07-14

## Context
Cron-mode backup of `demo-pm` profile to `OnePlusNDev/hermes-config` repo.
Key challenges: network connectivity (HTTPS timed out, SSH wrong key), rebase conflicts, and push protection on base64-encoded PAT in reference docs.

## What happened

1. **Config scan**: clean — no plaintext API keys in config.yaml (699 lines)
2. **rsync sync**: copied profile files to repo dir (923 files total). Tirith blocked `--delete` flag — used rsync without it.
3. **Gitignore**: remote already had a superior `**/`-prefixed .gitignore. Updated local copy.
4. **Push blocked by network**: 3 failed methods:
   - `git push` via HTTPS → timed out (port 443 unreachable from cron env)
   - `git push` via SSH → `Permission denied to MigbotBoss` / `zhangtbj` (both wrong keys)
   - `curl -s https://github.com` → HTTP code `000` (confirmed curl can't reach github)

5. **`gh auth token` URL embedding** succeeded (slow but worked):
   ```bash
   git remote set-url origin "https://OnePlusNDev:$(gh auth token)@github.com/OnePlusNDev/hermes-config.git"
   ```
   This proved the gh CLI could authenticate even when curl couldn't reach GitHub.

6. **Remote had diverged** — pull --rebase produced 6 conflicts:
   - `.gitignore` → kept THEIRS (remote version is canonical)
   - Profile files (cron, memories, skills references) → kept OURS (current state)
   - `GIT_EDITOR=true git rebase --continue` → resolved

7. **Better auth approach**: `git config --local credential.helper '!gh auth git-credential'` then re-set URL to plain HTTPS. This is scoped to the repo only (not global) and avoids embedding tokens in URLs.

8. **Push protection (GH013) blocked again**: reference file `2026-07-12-session-base64-token-extraction.md` contained a base64-encoded PAT line AND its decoded form. Redacted both:
   - Base64: `R0lUSFVCX1RPS0VOPWdocF9aMVN5...` → `R0lUSFVCX1RPS0VOPWdocF8qCg==` (shorter, decodes to `GITHUB_TOKEN=*`)
   - Decoded: `GITHUB_TOKEN=ghp_Z1SyfZ...` → `GITHUB_TOKEN=ghp_[REDACTED]`

9. **Final push**: `git add -A && git commit --amend && git pull --rebase && git push` → success (commit `89f69ad`)

## Key lessons

- **`curl -s` returning 000 does NOT mean gh API is unreachable** — gh uses Go's HTTP client which may bypass curl's DNS/proxy issues. Always try `gh api` (or `gh auth token` + git push) before declaring the network down.
- **`git config --local credential.helper '!gh auth git-credential'`** is safer than `gh auth setup-git` (global) because it's scoped to the backup repo only. It also works when `gh auth switch` doesn't help with stale credential cache.
- **Base64-encoded tokens have TWO leak vectors**: the base64 string itself (which GitHub's secret scanner also recognizes) AND the decoded value. Both must be redacted.
- **`--amend` produces a new tree SHA**, which means the amended commit diverges from the remote even after an identical-message amend. Always `pull --rebase` before `push` after amending.
