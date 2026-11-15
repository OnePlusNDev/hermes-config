# demo-pm backup run — 2026-11-15

## Result
**Method B (standalone subtree, no clone)** — **FIRST-TRY, 0 aborts (guard form pre-flight, no account loss, no 422 race)**.
Main commit: `2a06f1d1fb614bd659e67c8c4c9cddd4fc87dda9`
URL: https://github.com/OnePlusNDev/hermes-config/commit/2a06f1d1fb614bd659e67c8c4c9cddd4fc87dda9
Diff: **9 M, 2 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNTester`** (`permissions.push=false`) — the **9th observed keyring flip**
  (11-14 was the 8th). The guard branch (switch → re-read login AND `permissions.push` in the SAME
  shell call) read `OnePlusNDev` / `push=true`, and the re-check immediately before the script
  (second guard, same form) again read `OnePlusNDev` → switch held through commit time, no blob 404.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
  (only `OnePlusNDev/hermes-config` carries `demo-pm/`).
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9_-]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`;
  the only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**.
- `.env` (296 B; `GITHUB_USERNAME`, `GITHUB_EMAIL`, `GITHUB_TOKEN`, `GATEWAY_PORT`, `AGENT_NAME`,
  `AGENT_ROLE`, `DEEPSEEK_API_KEY`, `TERMINAL_ENV`) excluded, never uploaded; no `auth.json` /
  `auth.lock` / `state.db*` in the remote tree.

## Diff (9 M, 2 A, 0 D)
```
M  demo-pm/cron/jobs.json                                                        (+10/-10)
M  demo-pm/memories/MEMORY.md                                                    (+1/-1)
M  demo-pm/memories/USER.md                                                      (+1/-1)
M  demo-pm/memories/archive/ARCHIVE.md                                           (+1/-0)
M  demo-pm/skills/devops/hermes-profile-backup/references/method-b-practice-notes.md      (+8/-0)
M  demo-pm/skills/devops/hermes-profile-backup/references/skill-md-at-cap.md              (+7/-0)
M  demo-pm/skills/devops/hermes-profile-backup/templates/run-note-template.md            (+12/-0)
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md (+2/-0)
M  demo-pm/skills/devops/pm-triage-cron/references/assignee-query-verification.md         (+21/-0)
A  demo-pm/skills/devops/hermes-profile-backup/scripts/characterize-diff-post-push.py
A  demo-pm/skills/devops/pm-triage-cron/references/ssl-cert-env-pollution.md
```
Characterized ONCE against the **pre-push** HEAD `dc14c26aedd2` before the push
(`characterize-diff-vs-prev-head.py`, output `/tmp/char_1115.txt`), then re-verified after the
push with the new `characterize-diff-post-push.py` (same 9/2/0 set; prev blobs 308, new 310,
identical 280) — the per-file counts above come from the post-push run.

- **Routine runtime churn (4):** `cron/jobs.json` — task-polling `completed` 6915→**6963**,
  `next_run_at` → 11-15T20:30, `last_run_at` → 11-15T20:01:39; config-backup `completed` 145→146,
  next 11-16T20:00, last 11-14T20:05:08; memory-archive 145→146, next 11-15T21:00,
  last 11-14T21:02:57; `updated_at` → 11-15T20:01:39. Note the pre-push characterization probe
  (run before the 20:01:39 tick of this job's own scheduler) read 6962 / `updated_at`
  20:00:50; the blob upload landed AFTER that tick, so the pushed blob carries the post-tick
  values — verified by re-reading the remote blob (`completed` 6963,
  `updated_at` 20:01:39, remote == local byte-for-byte).
  `memories/MEMORY.md` — header only, 最后更新 2026-11-13 → **2026-11-14** (body byte-identical,
  still reuses `archive/MEMORY-20261029.snapshot.md`); `memories/USER.md` — header only, same bump
  (body identical, reuses `archive/USER-20261011.snapshot.md`); `memories/archive/ARCHIVE.md` —
  new **2026-11-14 21:00-21:05 memory cleanup** row (`:9178` offline at first probe → launcher
  start; **poll1 AND poll2 `http_code=000` while `/tmp/h9178_p1.json` still held the previous
  round's `{"status":"healthy"}` body — stale-body trap 6th consecutive**, healthy only at poll 3,
  ~20-30 s warm pg0, pid 86500; consolidation op `e7bfe70f` **+388 ms**,
  `deduplicated=false`, counter **104→105**, `pending=0`/`failed=0`; nodes 48 / 1228 links /
  2 documents stable; both reflect passes fine at `--bank demo-pm-memory`, no crash, no 504 —
  primary **154,472 / 6,766** @ `budget=high`, wording gate **24th consecutive** in a
  「## 记忆健康度评估结论」 + 「总体：良好但存在三类轻中度问题——0 项超期归档」 +
  「### 1. 过期事实（>30 天）：**无**」 shape (negation after keyword) + a date-relative-baseline
  conditional 「若当前实际日期已远晚于 2026-06-17，则上述所有配置类事实…在现实中都已超 30 天」;
  disambig **187,408 / 6,139** = 「无内容性过期事实」 with a 6-row category table and the sharpened
  `secret 10014` judgement (**exists only inside the source-document paragraph text, never
  extracted as a standalone fact** → no archivable object at all); bank↔flat-file LLM-key drift
  **10th consecutive day** — logged, no data mutated).
- **Carry-over doc edits authored after the 11-14 follow-up push (5):**
  `hermes-profile-backup/references/method-b-practice-notes.md` (+8: the 11-14 confirmation that
  the guard form turned the previous day's abort into a no-op, incl. "keep it, including on the
  follow-up");
  `hermes-profile-backup/references/skill-md-at-cap.md` (+7: the new
  `scripts/characterize-diff-post-push.py` documented as pointed-at-from-the-template-only on
  purpose, to be given a SKILL.md pointer at the next slim);
  `hermes-profile-backup/templates/run-note-template.md` (+12: new "If the push already landed
  before you characterized" section naming the post-push probe and demanding the quoted
  `+A/-D` counts);
  `hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md` (+2: the 11-14 row
  154,472 / 6,766 + disambig 187,408 / 6,139 with the 24th-gate shape and the `secret 10014`
  "no archivable object" correction);
  `pm-triage-cron/references/assignee-query-verification.md` (+21: **坑 5** — four-way
  `HTTP=000 bytes=0` + `curl: (77)` traced to a polluted `SSL_CERT_FILE`, unset → 200; with the
  判据速查 line).
- **New files (2):** `hermes-profile-backup/scripts/characterize-diff-post-push.py` (post-push
  counterpart probe, exercised twice this run) and
  `pm-triage-cron/references/ssl-cert-env-pollution.md` (the detail doc behind 坑 5).
- `config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local one
  (17,021 bytes; 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **291**; remote HEAD `dc14c26aedd2`, 308 blobs (demo-pm 289)
- Preflight diff: `Modified: 9, New: 2, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**; preflight and the backup
  script agreed on the same HEAD and the same 9-M/2-A set (no sibling landing this run)

## Execution notes
- Remote HEAD was `dc14c26aedd2` at preflight, at Step 2 and at commit time → **no ref-PATCH
  422 race**; the ref PATCH succeeded on the first attempt.
- 11 blobs uploaded, subtree `3d23ff16441edc8df2f209e720138de7566b2c99`, top tree
  `f2660f34ec5c7415e97c8f638ba9c1937b51da4e`, commit + ref in one clean pass.
- Closing preflight must read `Modified: 0, New: 0, Deleted: 0` after the follow-up commit.

## Post-push remote verification
- Remote HEAD `2a06f1d1fb61`; total blobs **310**, `demo-pm` blobs = **291** (== local file count
  291 at the main commit); by top dir: demo-pm 291, demo-dev 5, demo-tester 8, tester-01 5,
  .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + SKILL.md `latest:` pointer `2026-11-14` → `2026-11-15` +
`references/method-b-practice-notes.md` "Observed on recent runs" table row, pushed with the same
standalone-subtree script. Afterwards the preflight is expected to report
`Modified: 0, New: 0, Deleted: 0`.

A second follow-up push then corrected one number in THIS note: the pre-push characterization
probe had read `cron/jobs.json` before the scheduler's own 20:01:39 tick, so the first draft quoted
`completed` 6962 / `updated_at` 20:00:50 while the uploaded blob — and the remote file — carry the
post-tick 6963 / 20:01:39. Lesson for the next run: the pre-push probe shows the state at PROBE
time, not at UPLOAD time, so any file the scheduler rewrites every tick must be re-read from the
remote blob before its numbers are quoted in the note.
