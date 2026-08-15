# demo-pm Backup Workflow — 2026-08-13

Clean Method A (rsync + git push) run. 12 changed files, 0 push-protection blocks, 0 redactions needed.

## Key discovery: `query_issues.py` exclude gap

A new diagnostic script at profile root (`query_issues.py`, reads GITHUB_TOKEN from `.env`) slipped through the rsync exclude list because its filename matched NO existing pattern:
- `tmp_*` — no (doesn't start with tmp_)
- `triage_*` — no
- `pm_triage_*` / `pm_healthcheck_*` — no

**Detection path:** it appeared as an untracked `??` file in `git status` after rsync. Content inspection (head of file) showed it opens `~/.hermes/profiles/demo-pm/.env` and regexes out `GITHUB_TOKEN`. Classified as diagnostic artifact, not config.

**Fix applied the same run (all four places):**
1. rsync `--exclude 'query_issues.py'`
2. Live repo `.gitignore` — added `**/query_issues.py` (also backfilled `**/triage_fetch.py` and `**/triage_v5.py`, which the live file was missing — confirmed the known live-.gitignore drift)
3. SKILL.md template heredoc
4. Config exclude list docs in SKILL.md

**Detection rule going forward:** any untracked `.py` at profile root in `git status` gets a content check. If it opens `.env` and reads a token, exclude it regardless of filename.

## Run sequence (what worked)

1. Pre-flight: `grep -nE 'sk-[A-Za-z0-9]{20,}' config.yaml` → 0 matches; all `api_key:` are `''` (empty string) — no plaintext keys, no key_env substitution needed. `.env` exists (296B) and is excluded.
2. gh account verified: `gh api user` → OnePlusNDev, `push=true` on OnePlusNDev/hermes-config. `GITHUB_TOKEN` env NOT set (no override risk).
3. Clone with unique temp dir: `gh repo clone OnePlusNDev/hermes-config /tmp/hermes-$(date +%s)`.
4. rsync WITHOUT `--delete` (tirith blast_rsync_delete workaround), full 40+ exclude list.
5. `git status --short` review → 12 files: 8 modified, 4 new (2 memory snapshots + 2 skill reference docs). Memory snapshots `MEMORY-YYYYMMDD.snapshot.md` are consistent with remote pattern (`MEMORY-20260710.snapshot.md` already tracked) — normal archive content, keep.
6. Token scan of all changed files (sk-/ghp_/6768705f/R0lUSFVC patterns) → 0 triggers.
7. `git add -A`, verify staged set has no `.env`/auth/triage/query_issues artifacts.
8. `git commit` → `git push` → **rejected (fetch first)**: concurrent `demo-dev` backup had advanced remote HEAD.
9. `git pull --rebase origin main` (clean, 1 commit rebased) → `git push` success (`60e8a25`).
10. Post-push remote verification (all clean):
    - Remote `demo-pm/config.yaml` plaintext key count = 0
    - Remote tree sensitive-file grep (`.env`, `auth.json`, `state.db`, `home/`, `.local/`, `query_issues.py`, triage/tmp/pm_* scripts) = NONE
    - Top-level dir distribution intact: demo-pm 575 blobs, demo-dev 5, demo-tester 8, tester-01 5 — no sibling-profile data loss

## Notes

- SKILL.md diff in this backup was the skill's own routine documentation updates (added 2026-08-11 pitfall sections from a prior run) — legitimate config content, no tokens.
- No account flip, no port-443 issues, no push protection this run — the concurrent-push rebase was the only friction, and it resolved with the standard `pull --rebase → push` pattern.
- `git status` grep for sensitive files will match `pm-triage-cron/` skill directory names (contains "triage") — these are legitimate skill docs, verify content before treating as leaks (same class as the known `home/` substring false positive).
