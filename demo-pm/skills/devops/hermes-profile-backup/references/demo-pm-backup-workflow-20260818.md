# demo-pm Backup Workflow — 2026-08-18

**Result:** Clean 4-file backup (3 modified + 1 new). Local commit via Method A, push via Method B (gh API subtree script) — first-try success. Remote HEAD: `c74cf084274486d1969bef50183151c36062a33c`.

## Sequence
1. **Pre-backup scan:** `config.yaml` clean — no `sk-[A-Za-z0-9]{20,}` matches; all 15 `api_key:` lines are `''` (safe; no key_env replacement needed).
2. **gh auth:** active account `OnePlusNTester` has no push on `OnePlusNDev/hermes-config` (`permissions.push=false`). Confirmed correct repo via `contents/` listing (contains `demo-pm/`). No `GITHUB_TOKEN` env var → `gh auth switch --user OnePlusNDev` works; push=true after switch.
3. Clone to unique dir `/tmp/hermes-backup-$(date +%s)` (no cleanup needed; dispose-on-reboot).
4. rsync with full exclude list, NO `--delete` (tirith blast_rsync_delete) — exit 0, absolute DST verified (`echo "DST=[...]"`).
5. git status: 4 changes — M `cron/jobs.json` (run counters/timestamps), M `hermes-profile-backup/SKILL.md`, M `pm-triage-cron/SKILL.md` (new 08-18 session notes), ?? `pm-triage-cron/references/2026-08-18-session-source-env-loop-curl-confirm.md`. No leaked files.
6. **Token scan** (ASCII-only script at /tmp, no emoji): Stage 1/3 flagged only the known doc example `R0lUSFVCX1RPS0VOPWdocF8qCg==` (decodes to `GITHUB_TOKEN=***`); remote SKILL.md carries the byte-identical string ×4 and prior pushes passed → no redaction (same triage as 2026-08-11/15/16). Stage 2 hits (`ghp_xx...xxxx`, `sk-xxx...xxxx`) are placeholders in `native-mcp.md`, which is NOT in the commit set → no action. `git diff` itself contains zero token patterns.
7. Commit `bd57cc1` (4 files, 79 insertions / 14 deletions).
8. ⚠️ **Account flip AGAIN (documented pattern):** pre-push check right after commit showed `OnePlusNTester` — the flip happened during the clone→commit phase (~2 min). Re-switched to `OnePlusNDev`, verified, then proceeded. This is the Nth confirmation: always check `gh api user --jq '.login'` immediately before any push/API phase.
9. **git transport failure (documented pattern):** `git pull --rebase` → `fatal: ... Error in the HTTP2 framing layer`; `git push` → timed out at 150s. curl had returned 200 and `gh api` worked fine — git/libcurl flaky end-to-end again (same as 2026-08-17). Went straight to Method B, zero git retries burned.
10. **Method B:** copied `scripts/gh-api-incremental-push-subtree.py` to `/tmp/gh-api-push-subtree.py`, patched WORKTREE to the clone path, ran as OnePlusNDev → first-try success: 4 blobs uploaded, recursive subtree + top tree built, commit `c74cf084` created on remote HEAD `56fc9eb` (re-read at Step 1), ref updated, assert passed.

## Post-push verification (all pass)
- Remote `demo-pm/config.yaml` decoded → 0 `sk-[A-Za-z0-9]{20,}` matches.
- Tree paths dumped to file + grep: no `.env`/`auth.*`/`state.db*`/`processes.json`/`bin/tirith`/`home/`/`.local/`; no temp scripts (`triage_*`, `tmp_*`, `pm_healthcheck_*`, `query_issues.py`).
- Distribution via `awk -F/ '{print $1}' /tmp/remote_paths.txt | sort | uniq -c`: `.gitignore` 1, `demo-dev` 5, `demo-pm` 578, `demo-tester` 8, `tester-01` 5 — siblings intact. Blob count 596 → 597 = exactly +1 for the new reference doc (sanity check that the new file landed and nothing else changed).
- New reference doc confirmed present remotely.

## New pitfall captured (added to SKILL.md)
**Copy the subtree script to /tmp before patching WORKTREE.** Patching the skill's own `scripts/gh-api-incremental-push-subtree.py` in place leaves the stale clone-path constant in the skill dir; the next backup's rsync copies it and git reports a phantom "modified" diff on every future run. `cp <skill_dir>/scripts/gh-api-incremental-push-subtree.py /tmp/gh-api-push-subtree.py` + patch the copy avoids the churn.
