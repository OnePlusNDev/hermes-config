# demo-pm backup workflow 2026-08-15

Clean Method A -> B fallback run: config.yaml had NO plaintext keys, git
transport timed out on `pull --rebase`, subtree script pushed on top of a
concurrently-advanced remote HEAD. 7 files changed (5 modified + 2 new
reference docs), commit `6041cd0f`.

## Config secret check (clean — no key_env replacement needed)
- `grep -nE 'sk-[A-Za-z0-9]{20,}' config.yaml` -> no matches.
- All 15 `api_key:` lines were `''` (empty, non-sensitive); `secret: ''` empty;
  `access_token_env: BWS_ACCESS_TOKEN` is an env ref. Report format that worked:
  state plainly "no plaintext key found" + the empty-value evidence + the
  post-push remote re-check count (0).

## Pre-commit scan — remote-existing doc example, no redaction
- Flagged `R0lUSFVCX1RPS0VOPWdocF8qCg==` (decodes to `GITHUB_TOKEN=ghp_*\n`, a
  deliberately-redacted doc example) in the backup skill's own SKILL.md.
- Verified NOT new this run with local-clone checks (faster than the gh API
  blob fetch): `git show HEAD:<file> | grep -c <string>` = 4 (already in HEAD),
  and `git diff <file>` showed only docs-only additions (exclude-list bullets).
  No redaction; all 9 blob uploads passed push protection.

## Transport timeout on pull --rebase -> Method B
- `git pull --rebase origin main` hung: `fatal: unable to access
  https://github.com/OnePlusNDev/hermes-config.git/: Recv failure: Operation
  timed out` — git/libcurl transport flaky while `gh api` worked fine.
- Pre-check before deciding: `git rev-parse HEAD^` (60e8a25) != remote HEAD
  (06ec701) — a concurrent backup had advanced main, so a plain push would be
  non-fast-forward and a rebase would be needed.
- Ran `scripts/gh-api-incremental-push-subtree.py` with `WORKTREE` patched to
  the clone path. It re-reads remote HEAD at Step 1 and parents the new commit
  on it, absorbing the concurrent advance automatically — no manual rebase.
- Local commit (75ed047) contents == pushed tree; remote HEAD now 6041cd0f.

## Post-push verification (all passed)
- Remote `demo-pm/config.yaml` plaintext `sk-` count = 0.
- No sensitive paths (`/\.env|auth.json|state.db|.../`) or temp/diagnostic
  scripts (`triage_*.py`, `query_issues.py`, `tmp_pm_triage.py`, ...) in tree.
- Sibling profiles intact: demo-dev 5, demo-tester 8, tester-01 5; demo-pm 577
  blobs (594 -> 596 total: +2 new files).

## Notes
- Subtree script Step 3 diff previously double-uploaded new files (they were in
  BOTH `changed` and `new_files`). Fixed — `changed` now excludes paths absent
  from the remote.
- Skip /tmp cleanup per existing pitfall (tirith blocks `/tmp` deletion in cron).
