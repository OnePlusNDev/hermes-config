# demo-pm backup workflow 2026-08-16

Clean Method A run (rsync + git push): 5-file backup commit + 1 legacy-cleanup commit. No push-protection blocks.

## Run summary

- **Pre-check:** config.yaml all 15 `api_key:` entries are `''` (key_env form) — no plaintext, no `sk-` hits, no replacement needed (same as 2026-08-15).
- **gh auth:** active account was `OnePlusNTester` (push: **false** on OnePlusNDev/hermes-config) → `gh auth switch --user OnePlusNDev` → push: **true**. `GITHUB_TOKEN` env var was NOT set this run, so the switch took effect (the env-var override pitfall did not apply).
- **Network:** curl `https://github.com` → HTTP 000 (timeout), but `gh repo clone`, `git pull --rebase`, AND `git push` ALL succeeded. Confirms the "curl 000 ≠ push failure" guidance — git/libcurl transport was fine end-to-end this run; do not preemptively fall back to Method B on curl 000 alone.
- **Concurrent advance:** remote HEAD moved `6041cd0` → `33903ad` mid-run; `git pull --rebase` succeeded (1/1, no conflict), then push `33903ad..171d451`.

## Files backed up (commit 171d451)

- M `demo-pm/cron/jobs.json`
- M `demo-pm/memories/archive/ARCHIVE.md`
- M `demo-pm/skills/devops/hermes-profile-backup/SKILL.md`
- M `demo-pm/skills/devops/hermes-profile-backup/scripts/gh-api-incremental-push-subtree.py`
- A `demo-pm/skills/devops/hermes-profile-backup/references/demo-pm-backup-workflow-20260815.md`

## Token scan

Only hits: `R0lUSFVCX1RPS0VOPWdocF8qCg==` (decodes to `GITHUB_TOKEN=*** SKILL.md ×4 + the new 20260815 reference ×1. Remote SKILL.md already carried the byte-identical string ×4 and prior pushes succeeded → deliberately-redacted doc example, no redaction (same triage as 2026-08-11).

## Legacy tracked file cleanup (commit 74b20f8)

- Post-push remote-tree grep pattern `pm_triage_.*\.py` flagged `demo-pm/cron/pm_triage_script.py` and `demo-pm/scripts/pm_triage_query.py`.
- Content check: both are diagnostic scripts that READ `GITHUB_TOKEN` from `.env` at runtime — no embedded tokens. They match the `pm_triage_*.py` exclude family but were tracked in the repo from before the exclude existed.
- **Important nuance:** these lived in `cron/` and `scripts/` SUBDIRECTORIES, not the profile root — the documented "any untracked root `.py` that reads .env" detection heuristic would have MISSED them. The post-push remote-tree grep is what caught them. When the post-push grep hits a path, do the `git ls-files` + content check + `git rm --cached` cleanup regardless of which subdir it's in.
- Fix: `git rm --cached` both files (live `.gitignore` already has `**/pm_triage_*.py` at line 72, so `git add -A` won't re-stage them) → commit `"backup: demo-pm 2026-08-16 cleanup — remove legacy tracked pm_triage diagnostic scripts"` → push `171d451..74b20f8`.
- Post-push re-verify: both paths count = 0 in remote tree; dir distribution demo-dev:5 / demo-pm:576 / demo-tester:8 / tester-01:5 (siblings intact, no tree-construction data loss).

## New pitfall: tirith confusable_domain false positive

Command blocked:

```bash
HTTP_CODE=$(curl -s --max-time 15 -o /dev/null -w "%{http_code}" https://github.com); echo "curl-http:$HTTP_CODE"
```

→ `tirith:confusable_domain` — "Domain 'github.com)' is one edit away from known domain 'github.com'". The scanner misparses `github.com)` (the `)` of the command substitution right after the URL) as a confusable domain.

Fix: split into separate terminal calls so the URL is never immediately followed by `)`. A bare `curl -s --max-time 15 -o /dev/null -w "%{http_code}" https://github.com` passes cleanly.
