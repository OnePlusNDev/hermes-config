# Demo-PM Backup Workflow — 2026-08-01

11-file incremental backup via Method A (rsync + git push). Clean run with three notable findings.

## Outcome

- Commit `df2a7f8` `backup: demo-pm 2026-08-01`, pushed `b454c25..df2a7f8 main -> main`
- 10 modified + 1 new file (561 blobs under `demo-pm/` on remote)
- config.yaml had NO plaintext api_key (all `api_key: ''` — clean, no `key_env` rewrite needed)
- Push protection pre-scan found full tokens in 7 files → redacted before commit (42 substitutions total)

## Finding 1: Two junk file patterns not covered by existing excludes

`git status` showed two untracked files that had to be manually removed before commit:

1. `demo-pm/._cron_triage_runner.py` — macOS AppleDouble metadata file. rsync creates `._*` sidecar files when copying from an APFS/HFS source with extended attributes. The old exclude list had no `._*` pattern.
2. `demo-pm/tmp_pm_triage.py` — temp script WITHOUT a leading dot. The existing `.tmp_*` exclude does not match `tmp_*.py`.

Fix: added `--exclude 'tmp_*.py'` and `--exclude '._*'` to rsync, `**/tmp_*.py` and `**/._*` to .gitignore. Also worth a pre-commit eyeball for both patterns (see Pre-commit leak check in SKILL.md).

## Finding 2: Active gh account flipped mid-run; repo-local helper insufficient

Sequence:

```bash
gh api user --jq '.login'     # → OnePlusNDev  (repo owner — looks fine)
git push                      # → 403 denied to OnePlusNPM
git config --local credential.helper '!gh auth git-credential'
git push                      # → STILL 403 denied to OnePlusNPM
gh api user --jq '.login'     # → OnePlusNPM  (account flipped!)
gh auth switch --user OnePlusNDev
git push                      # → SUCCESS
```

Root cause: `gh auth git-credential` serves the CURRENTLY ACTIVE account's token. Another process on the machine (sibling profile/cron/gateway sharing the keyring) switched the active account between our pre-flight check and the push. The repo-local helper only fixes stale credential *cache*, not an active-account change.

Lesson encoded in SKILL.md: re-check `gh api user --jq '.login'` immediately before `git push`, not just at run start.

## Finding 3: Redaction regex threshold `{8,}` beats `{15,}`/`{20,}`

First redaction pass used `ghp_[A-Za-z0-9]{15,}` + `6768705f[0-9a-f]{15,}` and left fragments behind:
- `ghp_Z1SyfZDw` (12 chars)
- `6768705f5a315379` (16 hex chars)

These partial prefixes still trigger GitHub push protection. Second pass with `{8,}` caught all 9 remaining. Files affected: `hermes-profile-backup/SKILL.md`, `pm-triage-cron/references/2026-07-10-xxd-hexdump-token-extraction.md`.

Also confirmed: full-tree grep (Stage 1/2) flags hits in files NOT in the commit set (e.g. `pm-triage-cron/SKILL.md` line 660 hex token, `native-mcp.md` `ghp_xx...xxxx` examples) — those blobs are not re-uploaded, so they don't block the push. The deciding scan is over `git status --porcelain` + `git ls-files --others --exclude-standard` targets only.
