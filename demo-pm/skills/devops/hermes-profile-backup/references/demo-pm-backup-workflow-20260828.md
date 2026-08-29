# Demo-PM Backup Workflow — 2026-08-28

## Outcome
- Clean backup via Method B (gh API Git Data API, `scripts/gh-api-standalone-subtree-backup.py`), REPO_OWNER=OnePlusNDev.
- 2 commits: `ee18c55a` (5 M + 6 A + 0 D, main backup) and `5c862fbf` (SKILL.md doc sync, 1 M).
- Post-push verification: remote config.yaml plaintext api_key count 0; no .env/auth.json/state.db/home/.local/bin in remote tree; demo-pm 585 blobs, siblings intact (demo-dev 5, demo-tester 8, tester-01 5).

## Security gate: config.yaml check
- No plaintext api_key found: all 15 `api_key:` values are empty `''`, no `sk-` matches → no key_env replacement needed.

## Exclude gap caught by preflight (7 new root-level diagnostics)
Preflight flagged 13 new files; 7 of them are root-level health/diagnostic scripts that read `.env` for GITHUB_TOKEN. None matched the existing exclude prefixes (`pm_healthcheck_`, `gh_health_`, `healthcheck_`):
- `gh_healthcheck.py` — uses os.environ (docstring: "source .env in same shell")
- `health_0828.py`, `health_check_0828.py` — os.environ
- `health_check.py`, `health_check_issues.py`, `pm_health_check.py`, `pm_healthcheck.py` — `open(PROFILE_DIR/.env)` and parse `GITHUB_TOKEN=` line

Detection rule applied: any root-level `.py`/`.sh` that opens `.env` / reads GITHUB_TOKEN is a diagnostic artifact → exclude regardless of filename (existing rule from 2026-08-13, 2026-08-26).

## Fix: broaden prefixes + ROOT-SCOPED health_ check
- EXCLUDE_PREFIX additions: `pm_health` (catches pm_healthcheck.py, pm_health_check.py, pm_healthcheck_0807b.py, pm_healthcheck_cron.py — old `pm_healthcheck_` missed the no-trailing-underscore variants), `gh_health` (catches gh_healthcheck.py + gh_health_*.sh).
- `health_` was NOT added to the prefix set. Instead a root-scoped check was added to `should_exclude()` in all 3 scripts:
  ```python
  if len(parts) == 1 and fname.startswith("health_"):
      return True
  ```
- ⚠️ NEAR-MISS: a blanket `health_` prefix made preflight show `D demo-pm/skills/creative/comfyui/scripts/health_check.py` — a LEGIT nested skill script (documented in comfyui SKILL.md as the verification checklist runner). A blanket prefix would have silently deleted it from the remote on push. Root-scoping preserved it (final diff Deleted: 0).

## Doc sync (4 places, per keep-in-sync rule)
- rsync `--exclude` list: `pm_health*`, `gh_health*`, `/health_*` (leading slash anchors to transfer root — root-scoped).
- .gitignore template: `**/pm_health*`, `**/gh_health*`, `demo-pm/health_*.py` + `demo-pm/health_check.py` (profile-root anchored, NOT `**/` — `**/` would hide legit nested files from `git add`).
- Exclude-docs bullets (~line 365, ~line 971): full description + root-scoping warning.

## Method B details
- curl 000 to github.com; `git ls-remote` timed out at 45s (git/libcurl transport); gh api worked → subtree script directly.
- Re-run pattern verified: the second (doc-sync) commit ran the same script again; it re-read remote HEAD, uploaded 1 blob, pushed cleanly. Blob uploads idempotent, so re-runs are cheap.
