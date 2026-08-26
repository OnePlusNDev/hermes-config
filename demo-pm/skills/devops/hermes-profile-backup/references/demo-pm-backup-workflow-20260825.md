# demo-pm backup workflow — 2026-08-25

Clean 3-file Method A run (clone → rsync → commit → push). No plaintext keys, no push-protection blocks, no redaction needed. All-git transport worked end-to-end.

## Run summary
- **Method**: A (rsync without `--delete`, full exclude list)
- **Changed files (3)**:
  - `demo-pm/cron/jobs.json` — cron counters + next/last run timestamps (benign runtime state)
  - `demo-pm/memories/archive/ARCHIVE.md` — +1 line archive
  - `demo-pm/skills/devops/hermes-profile-backup/scripts/gh-api-standalone-backup.py` — 4-line update
- **Commit**: local `3a1bdf7` → rebased onto concurrent remote → pushed as `1f0dadb` (`fc194da..1f0dadb`)

## Security check
- config.yaml: ALL 15 `api_key:` values are empty strings `''`; `session_key`, `password`, `secret` empty; `secrets:` section uses env refs (`BWS_ACCESS_TOKEN`). No plaintext `sk-` keys → no key_env replacement needed.
- Two-layer pre-commit token scan (shallow grep + Python regex covering `ghp_`/hex/base64/`sk-`/`gho_`/`github_pat_`) on the 3 changed files: CLEAN.
- Post-push remote verification: remote config.yaml plaintext-key grep count = 0; 598 blob paths, no sensitive files; top-level distribution intact (demo-dev 5, demo-pm 579, demo-tester 8, tester-01 5).

## Pitfalls confirmed (no new workaround needed)
- **Account flip happens even with `GITHUB_TOKEN` UNSET**: pre-flight check showed active = OnePlusNDev (owner, push=true); right before push, active had flipped to OnePlusNPM. `unset GITHUB_TOKEN; gh auth switch --user OnePlusNDev` fixed it; push succeeded. Confirms the flip is a keyring race, not env-var driven — pre-push re-check is mandatory every run.
- **Remote advanced mid-run** (concurrent profile backup landed): push rejected non-fast-forward; `git pull --rebase origin main` then `git push` succeeded on first retry.
- Network: curl to github.com returned 200, gh API fine, git clone/pull/push all worked — no transport issue this run.
