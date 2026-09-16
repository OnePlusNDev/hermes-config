# demo-pm backup run — 2026-09-16

## Result
**Method B (standalone subtree, no clone)** — success, first ref PATCH attempt.
Main commit: `330e6831b82abf8d434232d7df488e841fbc1a1c`
URL: https://github.com/OnePlusNDev/hermes-config/commit/330e6831b82abf8d434232d7df488e841fbc1a1c

## Pre-flight
- `gh api user` → `OnePlusNDev` (repo owner; `permissions.push` = **true**, `admin` = true) — no account switch needed
- No `GITHUB_TOKEN` / `GH_TOKEN` in the cron env (`env | grep -E '^(GH|GITHUB)'` → only `GITHUB_EMAIL`, `GITHUB_USERNAME`)
  → no auth-override risk
- config.yaml plaintext scan: `sk-[A-Za-z0-9_-]{16,}` → **0** matches;
  all **15** `api_key:` lines are `''` (empty; non-empty count = 0); extra
  `(token|secret|password|api_key|key): '<6+ chars>'` scan → **NONE**
  → **no plaintext key found, no key_env replacement needed**
- `preflight-backup-scan.py` (REPO_OWNER=OnePlusNDev): Modified **6**, New **2**, Deleted **0**;
  token scan **CLEAN** → no exclude gaps, no `EXCLUDE_*` / rsync / gitignore changes needed
- `.env` (296 B; GITHUB_*, DEEPSEEK_API_KEY, etc.) excluded, never uploaded; no
  `auth.json` / `auth.lock` / `state.db*` in tree

## Diff (6 M, 2 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/memory-maintenance.md
M  demo-pm/skills/devops/pm-triage-cron/references/2026-09-14-session-clean-noop-and-skill-size-cap.md
M  demo-pm/skills/devops/pm-triage-cron/references/sibling-collision-and-empty-result.md
A  demo-pm/skills/devops/hermes-profile-backup/scripts/post-push-verify.py
A  demo-pm/skills/devops/pm-triage-cron/references/2026-09-16-sibling-round-filename-collision.md
```
`config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local one
(`52ecc36b2122df5bb2266c86edd8f231184985ae`), i.e. the 09-15 follow-up commit had already
swept in the current config. Nothing to re-upload, nothing stale.

## Execution notes
- Remote HEAD was `c01128e2d290` (= demo-dev's 09-16 sibling commit) at start and stayed there
  through commit time → **no ref-PATCH 422 race this run**; first-try success (ends the
  09-14 → 09-15 422 streak; 09-13 was also first-try).
- **Network flakiness cost 2 aborted attempts before the success** (new observation this run):
  attempts 1 and 2 both died with `dial tcp 20.205.243.168:443: i/o timeout` — first on the
  LAST blob POST (`2026-09-16-sibling-round-filename-collision.md`), then on the initial
  `git/trees/<sha>?recursive=1` GET. At that same moment `curl https://api.github.com` returned
  `000` three times in a row, while `gh api repos/.../git/refs/heads/main` answered on 5/5
  retries immediately after. Same lesson as 2026-08-16: `curl 000` is NOT a push failure, and a
  mid-phase i/o timeout is NOT a partial/failed backup — blob SHAs are idempotent, so a plain
  re-run is the correct (and only needed) response. Attempt 3 uploaded all 8 blobs and pushed
  first-try. No rebase, no tree surgery, no manual re-parent.
- `Done:` + exit 0 on attempt 3.

## Post-push remote verification
- `scripts/post-push-verify.py` → **ALL CHECKS PASS**; remote HEAD `330e6831b82a`
- Total blobs **640**; `demo-pm` blobs = **621** (== local file count 621); by top dir:
  demo-pm 621, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1
- Remote `demo-pm/config.yaml`: **16835 chars / 17021 bytes**; `sk-` matches = **0**;
  `api_key` lines = 15, non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**

## Bug fixed this run: post-push-verify.py reported a FALSE config.yaml FAIL
The brand-new `scripts/post-push-verify.py` (added by this same run's main commit) failed its
first execution with `[FAIL] config.yaml decodes: Incorrect padding`. Root cause: its `gh()`
helper hardcoded `--jq "."`, so the `/contents/` call returned the whole JSON envelope
(`{"content": ..., "encoding": "base64", ...}`) and the script base64-decoded THAT instead of
the `.content` field. Not a real leak — a manual `.content` fetch proved the remote file is
byte-identical to local (`52ecc36b...`, 0 `sk-`).
Fix: `gh()` gained a `jq="."` parameter; the config.yaml contents call now passes
`jq=".content"` (with an inline NOTE comment). Re-ran → **ALL CHECKS PASS**.
Corollary for run notes: the `16835` recorded here and in earlier notes is a **character** count
(the file holds CJK comments); the true **byte** length is 17021. Compare sizes in bytes, not
`len(str)`.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-09-15` → `2026-09-16` +
the `post-push-verify.py` `.content` fix, pushed with the same standalone-subtree script.
Afterwards the preflight is re-run and expected to report `Modified: 0, New: 0, Deleted: 0`.
