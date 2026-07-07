# Backup Run: 2026-07-06 — demo-pm profile

**Method**: A (rsync + git push via gh clone)

**Context**: Cron job, `OnePlusNDev` was the active gh account; repo owned by `OnePlusNTester`.

## Key outcomes

1. **Network check nuance confirmed**: `curl https://github.com` returned code `000` (timeout), but `gh api user` and `git push` both succeeded because gh CLI manages its own transport. This disproves the earlier assumption in the skill that `000` → push will fail. Pushed the skill patch accordingly.

2. **gh auth switch needed**: Active gh account was `OnePlusNDev`, repo belongs to `OnePlusNTester`.
   - `git push` initially failed with "Repository not found" (HTTP 404, not 403 — the active account didn't even see the private repo)
   - Fixed with `gh auth switch --user OnePlusNTester`
   - Switched back to `OnePlusNDev` after push

3. **Changes backed up**: 10 files (3 modified, 7 new):
   - `cron/jobs.json` — updated cron schedule
   - `hermes-profile-backup/SKILL.md` — skill patches
   - `pm-triage-cron/SKILL.md` + 6 new reference files + `pm_triage_script.py`

4. **No leaked artifacts**: `git add -A` staged only expected files. No `.env`, `auth.json`, `sessions/`, `processes.json`, or other excludables leaked through. The rsync exclude list and `.gitignore` are in sync.
