# demo-pm backup run — 2026-11-27

## Result
**Method B (standalone subtree, no clone)** — main commit FIRST-TRY, 0 aborts (no 422 race).
Main commit: `c775fb2e19490a9c3eb6a11ee3282fdae17920b6`
URL: https://github.com/OnePlusNDev/hermes-config/commit/c775fb2e19490a9c3eb6a11ee3282fdae17920b6
Diff: **9 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNTester`** (`push=false`) → `unset GITHUB_TOKEN` + `gh auth switch --user OnePlusNDev`
  → re-probe `OnePlusNDev` / `push=true`. **19th keyring flip in the record** (11-25 logged the 18th;
  11-26 was a no-flip day); no blob 404.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`.
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9_-]{20,}` → **0** matches;
  non-empty `api_key:` → **0** matches; all **15** `api_key:` lines are `''`; the only `key_env`
  occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed** (config.yaml unchanged: blob
  17,021 bytes / 16,835 chars, the usual CJK-comment discrepancy).
- `.env` excluded, never uploaded (var **names only**: `GITHUB_USERNAME`, `GITHUB_EMAIL`,
  `GITHUB_TOKEN`, `GATEWAY_PORT`, `AGENT_NAME`, `AGENT_ROLE`, `DEEPSEEK_API_KEY`, `TERMINAL_ENV`);
  no `auth.json` / `auth.lock` / `state.db*` in tree.

## Diff (9 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/MEMORY.md
M  demo-pm/memories/USER.md
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/demo-pm-github-api/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/references/skill-md-at-cap.md
M  demo-pm/skills/devops/hermes-profile-backup/templates/run-note-template.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
```
Characterized with `scripts/characterize-diff-post-push.py d9f06b086e65` (read-only; the push had
already landed). Per-file: `jobs.json` +10/-10, `MEMORY.md` +1/-1, `USER.md` +1/-1, `ARCHIVE.md`
+11/-0, `demo-pm-github-api/SKILL.md` +7/-0, `skill-md-at-cap.md` +28/-0, `run-note-template.md`
+6/-0, `diagnostics/SKILL.md` +5/-0, `cleanup-run-endpoints-and-counts.md` +2/-0. Summary
`MODIFIED 9 / ADDED 0 / DELETED 0`, matching the preflight exactly.

- **4 routine runtime churn** (numbers re-read from the uploaded remote blob) — task-polling
  `completed` 7491→**7539**, config-backup 157→**158** (`last_run_at` 2026-11-26T20:05:34.878777,
  `last_status: ok`), memory-cleanup 157→**158** (`last_run_at` 2026-11-26T21:03:25.004185,
  `last_status: ok`), `updated_at` 2026-11-27T20:01:09.103941; `MEMORY.md` / `USER.md` header
  2026-11-25 → **2026-11-26**; `ARCHIVE.md` = the 11-26 21:0x cleanup (+11 lines) — op
  `0d6df0af-a2d6-439f-8e0d-cd7c105e6d70` **+145 ms**, `operations_by_status.completed` 115→**116**,
  `total_nodes 48 / total_links 1228` unchanged (no-op dedupe), primary **376,541 / 9,860**
  (new primary-input high for this bank; prior high 344,932 on 11-18) with the wording gate
  **35th consecutive**, disambig **245,043 / 6,066**, `stale-body 陷阱第 14 次` (poll 1 AND poll 2
  `000`, `/tmp/h9178_p2.json` already held a healthy body, healthy poll 3 ~20 s), sessions
  **7,828 / 3,382 / 6,328** vs 7,778 / 3,332 / 6,278 last round (all three +50 again — recorded,
  not to be read as monotone).
- **5 carry-over doc edits** made since the 11-26 push: `demo-pm-github-api/SKILL.md` +7 (11-27 four
  triage rounds, all `[SILENT]`, plus two fresh traps — `&cb=` instead of `?cb=` on bare endpoints
  → 404, and a curl-options **bash array** silently dropping `-K` auth → 404 on private repos);
  `skill-md-at-cap.md` +28 (7th `skill_view`-dump occurrence; one-call heredoc recovery);
  `run-note-template.md` +6 (re-run `post-push-verify.py` after the follow-up lands);
  `diagnostics/SKILL.md` +5 (`op`/`wait-op` positional `<op_id>` must precede the flags — argparse
  exit 2 otherwise) and `cleanup-run-endpoints-and-counts.md` +2 (11-26 reflect row).

## Preflight
- Local files (after excludes): **307**; preflight remote HEAD `d9f06b086e65`, 326 blobs
- Preflight diff: `Modified: 9, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `d9f06b086e65` at preflight AND at Step 2, and it is the **parent of the backup
  commit** → nothing landed in between, **no ref-PATCH 422 race**; ref PATCH succeeded first try.
- 9 blobs uploaded, subtree `c4b38ced99fb1e5f329e2040c4eb92eb3368e27f`, top tree
  `f23995e4b46a63cdd738282f895e35b5fd88f6f5`, commit + ref in one clean pass.
  The `mkdtemp` payload fix held; no network flakiness through the main commit (the follow-up is a
  second full push — see the closing assertion below).
- Closing assertion: after this follow-up lands, the preflight must read
  `Modified: 0, New: 0, Deleted: 0` (the only proof the follow-up's ref PATCH landed).

## Post-push remote verification
- Remote HEAD `c775fb2e1949`; total blobs **326**, `demo-pm` blobs = **307** (== local file count
  307); by top dir: demo-pm 307, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = **15**, non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + practice-notes table row + SKILL.md `latest:` pointer
`2026-11-26` → `2026-11-27` (same-length swap; SKILL.md measured 100,901 B, at cap),
pushed with the same standalone-subtree script. Bullet and row written by
`scripts/append-run-note-docs.py` (expect `INDEX count=1` / `ROW count=1`).
Pre-follow-up preflight expected `Modified: 3, New: 1, Deleted: 0` (+ `jobs.json` if a cron tick
dirtied it again); the closing preflight must read `0/0/0`.
