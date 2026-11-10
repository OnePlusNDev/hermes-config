# demo-pm backup run — 2026-11-10

## Result
**Method B (standalone subtree, no clone)** — **FIRST-TRY, 0 aborts (no 422 race, no mid-run account flip)**.
Main commit: `c239ca900c01ea3425222f30f901165607669b2c`
URL: https://github.com/OnePlusNDev/hermes-config/commit/c239ca900c01ea3425222f30f901165607669b2c
Diff: **9 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNDev`** (repo owner, `permissions.push=true`) with **no switch needed**
  (`GITHUB_TOKEN` unset) — the 11-09 keyring flip did **not** recur; no mid-run flip.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`; `password: ''` /
  `secret: ''` both empty; the only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**
- `.env` (296 B; `GITHUB_USERNAME`, `GITHUB_EMAIL`, `GITHUB_TOKEN`, `GATEWAY_PORT`, `AGENT_NAME`,
  `AGENT_ROLE`, `DEEPSEEK_API_KEY`, `TERMINAL_ENV`) excluded, never uploaded; `auth.json` (164 B),
  `auth.lock` (0 B), `state.db` (2.11 GB) present locally and excluded — none in the remote tree.

## Diff (9 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/MEMORY.md
M  demo-pm/memories/USER.md
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/hermes-profile-backup/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/references/run-note-diff-characterization.md
M  demo-pm/skills/devops/hermes-profile-backup/references/skill-md-at-cap.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
```
Characterized ONCE pre-push with `characterize-diff-vs-prev-head.py 8cbaf5e3eaf3` → exit 0,
`MODIFIED 9 / ADDED 0 / DELETED 0` (local 283 vs remote-at-PREV 283), output in
`/tmp/char_20261110.txt`.

- **Routine runtime churn (4):** `cron/jobs.json` — task-polling `completed` 6675→6723,
  config-backup / memory-cleanup counters 140→141 ×2, `next_run_at` roll to 11-10/11-11,
  per-job `last_run_at` (task-polling 11-10T20:01:02, memory-cleanup 11-09T20:05:28,
  memory-archive 11-09T21:09:39), `updated_at` 11-10T20:01:02; `memories/MEMORY.md` — header
  only, 最后更新 2026-11-08 → 2026-11-09 (body byte-identical, still reuses
  `archive/MEMORY-20261029.snapshot.md`); `memories/USER.md` — header only, 2026-11-08 →
  2026-11-09 (body identical, reuses `archive/USER-20261011.snapshot.md`); `memories/archive/ARCHIVE.md`
  — new **2026-11-09 21:01-21:07 memory cleanup** row (daemon offline at first probe, started,
  poll 1 `http_code=000` stale-body trap again then healthy on poll 2 in ~10-15 s; consolidation op
  `edac0161-681e-4970-8180-7c3f19b3c410` +351 ms, `deduplicated=false`, counter 99→100;
  **NEW failure shape: first reflect hit an HTTP 504 at the 300 s wall clock while the daemon
  stayed alive** — identical `budget=high` resend succeeded, no restart; primary
  **112,764 / 6,762**, wording gate AFFIRMATIVE for the **19th consecutive** time on the
  archive-recommendation + date-conditional pair; disambiguation **306,054 / 8,532** concluding
  「无内容性过期事实」; bank↔flat-file LLM-key drift now six consecutive days — logged, no data
  mutated; new identity contradiction logged 待人工确认; session stats 6,978 / >90d 2,532 /
  >30d 5,476).
- **Benign carry-over doc lag, authored after the 11-09 follow-up push (5):**
  `hermes-profile-backup/SKILL.md` (one-line rewrite of the `skill_view`-truncation warning —
  "Daily run: skip `skill_view` (100 K JSON dump, truncates) → `read_file` on-disk SKILL.md");
  `hermes-profile-backup/references/run-note-diff-characterization.md` (new section: a
  session-start refs read is NOT an anchor — only preflight-vs-Step-2 divergence counts);
  `hermes-profile-backup/references/skill-md-at-cap.md` (new section: at/over cap, `skill_manage`
  permits only NON-GROWING SKILL.md edits — a net −11-char rewrite passed at 100,151 chars while
  a +65-char one was refused; the "Tooling constraint" note refined accordingly);
  `hermes-profile-diagnostics/SKILL.md` (504-vs-crash bullet: do NOT restart on a 504, just
  resend); `hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md` (new
  "Reflect failure modes — crash vs HTTP 504 wall-clock timeout" section + the 11-09 token row
  112,764 / 6,762 + disambig 306,054 / 8,532, 19th-shape, drift extended to six days).

`config.yaml` deliberately NOT in the diff: the remote blob already equalled the local one
(16,835 chars / 17,021 bytes — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **283**; preflight read remote HEAD **`8cbaf5e3eaf3`** (302 blobs).
  Local 283 == remote `demo-pm` 283: the extra file vs the 11-09 main push (282) is that day's own
  run note, added by the follow-up commit — not a new file today.
- Preflight diff: `Modified: 9, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Preflight and the script's Step 2 both read **`8cbaf5e3eaf3`** (302 blobs) — no sibling landing
  in the gap, so there was **no preflight→Step-2 divergence** and no ref-PATCH 422 race.
- 9 blobs uploaded in one clean pass: `cron/jobs.json` `60e9b1c39e53`, `MEMORY.md` `50445eb80caa`,
  `USER.md` `ab8e23c60ec1`, `ARCHIVE.md` `63c5d3f9b7d9`, backup `SKILL.md` `9e80f465651e`,
  `run-note-diff-characterization.md` `781520541d48`, `skill-md-at-cap.md` `5d1772452547`,
  diagnostics `SKILL.md` `247e88f85d83`, `cleanup-run-endpoints-and-counts.md` `eba1bcc5c2fd`;
  subtree `2f02b58baf3e07a73bd039a89e290ae75921a07d`, top tree
  `ca3bd89f0c1cd961a5ba0c952de119849beefac6`, commit + ref PATCH on the first attempt
  (`Remote HEAD now: c239ca900c01`).
- No network flakiness in the main push (no 443 timeout, no `unexpected EOF`); the `mkdtemp`
  payload fix held. Follow-up cleanliness is asserted only by the closing-preflight `0/0/0`
  check, not by the log.

## Post-push remote verification
- Remote HEAD `c239ca900c01`; total blobs **302**, `demo-pm` blobs = **283**
  (== local file count 283); by top dir: demo-pm 283, demo-dev 5, demo-tester 8, tester-01 5,
  `.gitignore` 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path / temp-diagnostic leak checks → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
All FOUR items: run note + `references/dated-runs-index.md` bullet +
`references/method-b-practice-notes.md` "Observed on recent runs" row + SKILL.md `latest:`
`2026-11-09` → `2026-11-10` (same-length in-place swap; SKILL.md is over its 100 K cap, so no
new prose goes in it). Pushed with the same standalone-subtree script; the closing preflight is
expected to read `Modified: 0, New: 0, Deleted: 0`.
