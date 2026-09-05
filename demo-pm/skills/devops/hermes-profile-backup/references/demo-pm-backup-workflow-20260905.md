# demo-pm backup workflow — 2026-09-05

## Result
CLEAN Method B (standalone-subtree) run. Main commit `9039aa57` (4M+1A+0D).
Follow-up run-note commit (same session): this note + dated-runs-index bullet.

## Security check (pre-backup)
- config.yaml scanned: **NO plaintext keys** — all `api_key:` values are
  empty strings (`''`), zero `sk-` matches, no long plaintext secret values.
  No `key_env` replacement needed.
- Preflight scan: CLEAN (no full token patterns in upload candidates).

## Remote HEAD advance absorbed
Preflight read remote HEAD `02a146c2`; by the time the backup script ran
(Step 2), remote had advanced to `de474c3d` (concurrent backup from another
profile). The standalone-subtree script re-parents onto the CURRENT remote
HEAD at Step 1/2, so the advance was absorbed automatically — no rebase, no
fast-forward 422. Final commit `9039aa57` sits on `de474c3d`.

## Files backed up (main commit: 4 M + 1 A)
- M cron/jobs.json
- M memories/archive/ARCHIVE.md
- M skills/devops/hermes-profile-backup/SKILL.md
- M skills/devops/hermes-profile-backup/references/dated-runs-index.md
- A skills/devops/pm-triage-cron/scripts/crosscheck.py

## Post-push verification
- main ref == `9039aa578496100af1f81e5f2bcf793b14b6cd15` ✓
- Remote demo-pm/config.yaml plaintext-key count: **0** ✓
- Top-level distribution: demo-pm 600 blobs (599+1), siblings intact
  (demo-dev 5, demo-tester 8, tester-01 5) ✓
- Sensitive-file tree grep (.env/auth.json/state.db/home/.local/tmp/tmp_pm):
  NONE ✓

## Notes
- No local git clone present this run; used the standalone-subtree script
  directly (repo at 618 blobs — above the flat-tree 422 threshold).
- gh auth: OnePlusNDev active (owner, push=true) at start and throughout.
