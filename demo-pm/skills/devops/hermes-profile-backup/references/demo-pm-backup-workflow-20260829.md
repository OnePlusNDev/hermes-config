# Demo-PM Backup Workflow — 2026-08-29

## Outcome
- Clean backup via Method B (`scripts/gh-api-standalone-subtree-backup.py`), REPO_OWNER=OnePlusNDev.
- Commit `b1724919` (`backup: demo-pm 2026-08-29`): 5 M + 1 A + 0 D.
- Post-push verification: no .env/auth.json/state.db/triage_verify.py in remote tree; remote config.yaml plaintext api_key count 0; demo-pm 586 blobs; siblings intact (demo-dev, demo-tester, tester-01).

## Security gate: config.yaml check
- No plaintext api_key found: all 15 `api_key:` values are empty `''`, no `sk-` matches → no key_env replacement needed.

## Exclude gap: triage_verify.py (new root-level .env reader)
- Preflight showed `A demo-pm/triage_verify.py`; content check: it `open(ENV_PATH)`s `.env` and parses `GITHUB_TOKEN=` — same family as query_issues.py/get_token.sh.
- Name matched NO existing pattern (`triage_` family was covered only by explicit names triage_check/triage_fetch/triage_issues/triage_v5; EXCLUDE_PREFIX has `pm_triage_` but not bare `triage_`).
- Fix: added `triage_verify.py` to EXCLUDE_NAMES in BOTH scripts + SKILL.md rsync list + .gitignore template + exclude-docs bullet.
- Deliberately did NOT add a blanket `triage_` prefix — same near-miss as `health_` on 2026-08-28 (would risk deleting legit nested skill scripts named triage_*).

## b64 false positive in preflight: GITHUB_TOKEN=*** doc placeholder
- b64 hit `R0lUSFVCX1RPS0VOPWdocF8qCg==` decodes to `GITHUB_TOKEN=ghp_*\n` — SKILL.md doc example, NOT a real token. The old `real()` filter only stripped "xxx"/"..."/"xx", not `*`.
- SKILL.md is an upload candidate most runs (it gains a workflow ref each backup), so this false positive recurs.
- Fix: preflight `real()` now decodes b64 matches and filters any whose decoded text contains placeholder chars (`*`, `xxx`, `...`, `xx`) — call site `real(m3, decode_b64=True)`. `import base64` added.

## Stale REPO_OWNER defaults (doc drift)
- preflight script default + docstring said `OnePlusNPM`; actual repo is `OnePlusNDev/hermes-config` (backup script default was already correct). Fixed both. Check `gh repo view --json owner` when unsure.

## Stale local clone → Method B, not Method A
- `~/.hermes/repos/hermes-config` clone exists and `git status` says "up to date" — but it is BEHIND remote (local ed4bcb8 vs remote c928b535): `git status` only compares against the local `origin/main` ref, which itself can be stale. Must compare `git rev-parse HEAD` against `gh api .../git/refs/heads/main`.
- Used Method B (gh API subtree push) — correct call; a Method A push from a stale clone would diverge.
- Rule added to SKILL.md Method Selection: local clone present ≠ Method A; verify local HEAD == remote HEAD first.
