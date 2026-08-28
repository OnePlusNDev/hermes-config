# 2026-08-27 backup workflow: preflight diff-scope scan catches exclude gaps before upload

## Summary
Clean 56-blob Method B push (gh API Git Data API subtree; `git clone` timed out on port 443).
Commit `00d2863d29bc` · https://github.com/OnePlusNPM/hermes-config/commit/00d2863d29bc7db1a7e0295540768e5248be57f6
- 13 modified, 43 new, 1 deleted (`cron/pm_triage_script.py` legacy cleanup via exclude prefix)
- 0 push protection skips; all `api_key: ''` in config.yaml (no plaintext, no key_env replacement)

## New technique: preflight diff-scope token scan (`scripts/preflight-backup-scan.py`)
Before running the backup script, compute the M/A/D diff vs the remote tree and scan
ONLY upload candidates (changed + new files) for token patterns. Caught 3 exclude
gaps BEFORE any blob was uploaded:
- `tmp_triage/` dir — 7 files (fetch_*.sh, parse_*.py, mine.json, all_issues.json,
  healthcheck_0827b.py); 3 files contained token patterns. EXCLUDE_DIRS was missing it.
- `gh_health_20260827.sh` — sources `.env`, `export GH_TOKEN=...` (root diagnostic,
  same family as `get_token.sh`).
- `healthcheck_20260827.py` — reads `.env` GITHUB_TOKEN via dynamic key construction
  (same family as `pm_healthcheck_*.py`).

Workflow: run preflight → patch EXCLUDE sets + SKILL.md → re-run preflight until clean
→ run backup. Diff went 52 new → 43 new after exclusions (9 files removed).

## Exclude families added (already in SKILL.md + script)
- `EXCLUDE_DIRS` += `tmp_triage`
- `EXCLUDE_PREFIX` += `gh_health_`, `healthcheck_`
- SKILL.md updated in all 3 exclude locations (rsync block, .gitignore, exclude docs list)

## b64 doc-example triage (no redaction needed)
Preflight flagged `R0lUSFVCX1RPS0VOPWdocF8qCg==` in 5 files (SKILL.md + 4 NEW workflow refs:
20260811/15/16/18). Triage:
1. Decode: `echo R0lUSFVCX1RPS0VOPWdocF8qCg== | base64 -d | xxd` → `GITHUB_TOKEN=***`
   (hex `2a` = literal asterisk) — intentionally redacted doc example, NOT a live token.
2. Remote SKILL.md already carries the identical string (count=1) and passed prior pushes.
3. `grep -cE 'ghp_[A-Za-z0-9]{20,}|6768705f[0-9a-f]{20,}'` on the 5 flagged files → 0.
Result: byte-identical doc example, no redaction.

## Post-push leak-grep false positive
`grep healthcheck` over remote tree paths flagged
`demo-pm/skills/devops/pm-triage-cron/references/2026-07-13-session-full-repo-healthcheck-pattern.md`.
Confirmed: NOT in this commit (pre-existing, unchanged), 0 tokens, content is a workflow
note. Filename-substring hits on `skills/*` docs are false positives — verify content
before acting (consistent with SKILL.md "Remote leak-check false positives" pitfall).

## gh auth
Active user `OnePlusNDev` at start; `gh repo view OnePlusNPM/hermes-config` failed
("Could not resolve") with the wrong active account. `gh auth switch --user OnePlusNPM`
fixed it. Pre-push auth check remains mandatory every run.
