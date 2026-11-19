# demo-pm backup run — 2026-11-19

## Result
**Method B (standalone subtree, no clone)** — **main commit FIRST-TRY, 0 aborts (no 422 race)**,
14th keyring flip caught at pre-flight, guard re-executed in the SAME shell call as the script.
Follow-up commit outcome is proven by the closing preflight assertion at the end of this note.
Main commit: `cb317a42e844d277f4c65f761210b1195f6e45e5`
URL: https://github.com/OnePlusNDev/hermes-config/commit/cb317a42e844d277f4c65f761210b1195f6e45e5
Diff: **9 M, 1 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNTester`** (`permissions.push=false`) — the **14th observed keyring
  flip** (11-18 logged the 13th). Guard form (switch → re-read login AND `permissions.push`) read
  `OnePlusNDev` / `push=true`; the pre-push guard was re-executed immediately before the script in
  the same shell call and printed `GUARD: login=OnePlusNDev push=true`. No blob 404, no mid-run flip.
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9_-]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`;
  the only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**.
- `.env` excluded, never uploaded; no `auth.json` / `auth.lock` / `state.db*` in the remote tree.

## Diff (9 M, 1 A, 0 D)
```
M  demo-pm/cron/jobs.json                                                    (+10/-10)
M  demo-pm/memories/MEMORY.md                                                (+1/-1)
M  demo-pm/memories/USER.md                                                  (+1/-1)
M  demo-pm/memories/archive/ARCHIVE.md                                       (+14/-0)
M  demo-pm/skills/devops/demo-pm-github-api/SKILL.md                          (+1/-0)
M  demo-pm/skills/devops/hermes-profile-backup/references/tooling-gotchas-and-patch-anchoring.md (+28/-1)
M  demo-pm/skills/devops/hermes-profile-backup/templates/run-note-template.md (+5/-0)
M  demo-pm/skills/devops/hermes-profile-diagnostics/SKILL.md                  (+8/-3)
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md (+67/-0)
A  demo-pm/skills/devops/hermes-profile-backup/scripts/append-run-note-docs.py (+?)
```
Diffs characterized by fetching the parent-commit blobs and diffing locally (no clone needed).

- **Routine runtime churn (4)** — task-polling `repeat.completed` 7107→**7155**, `next_run_at` →
  11-19T20:30, `last_run_at` → 11-19T20:01:18.982569, `updated_at` → 11-19T20:01:18.983259;
  config-backup 149→**150**, next 11-20T20:00, last 11-18T20:06:26.918887; memory-cleanup
  149→**150**, next 11-19T21:00, last 11-18T21:07:13.776416. `memories/MEMORY.md` + `USER.md` — header
  date only, 2026-11-17 → **2026-11-18** (bodies identical; snapshots 20261029 / 20261011 reused).
  `memories/archive/ARCHIVE.md` — new **2026-11-18 21:0x memory cleanup** section: `:9178` offline
  at first probe (only the global `:8888` `python3.1` listener), launcher start → poll1 `000` with
  `/tmp/h9178_p1.json` still holding the previous healthy body (**stale-body trap 9th consecutive**,
  trust only the HTTP code), poll2 200 healthy (~10–20 s, warm pg0); consolidation op `045875e3`
  **+522 ms**, `deduplicated=false`, counter **108→109**, bank 48 units / 1228 links (semantic 740 /
  temporal 469 / entity 19) / 2 documents, `mental-model list` + `directive list` both empty; two
  reflect passes — primary **344,932 / 11,993** with the wording gate firing a **28th consecutive**
  time in a new shape (「## 0. 审计范围与数据现状」 pre-declaration + 「A 类：已过期 / 被更新事实取代」
  table + an explicit **numeric** verdict 「需要归档 / 删除的事实条数：**2 条**」), disambig
  **174,335 / 8,345** which **retracted that 2-item verdict outright** (「这 2 条中，没有任何一条满足
  内容失效条件」→ 无内容性过期事实, 归档 0: the deepseek-v4-pro record is a different scope from
  daemon-side z.ai GLM, and `secret 10014` has no in-bank fix evidence so archiving would destroy the
  only pending lead), keeping z.ai GLM → **drift day 14**; sessions **7,428 / 2,982 (>90d) /
  5,928 (>30d)** (+50/day, recorded only — `auto_prune: false`), zero archiving.
- **Carry-over doc edits authored after the 11-18 follow-up push (5):**
  `demo-pm-github-api/SKILL.md` (+1: `write_file` silently rewrites `-u "OnePlusNPM:$TOK"` to
  `AUTH=*** "OnePlusNPM:$TOK")` on disk — verified via `repr()`, so it is real corruption, not display
  masking; workaround is a `chmod 600` curl config file read with `-K`);
  `tooling-gotchas-and-patch-anchoring.md` (+28/-1: "four traps" → "six traps", new §6 on the
  `latest:` pointer — the `(` belongs to an earlier clause so anchor on the inner fragment
  `latest: <date>; full per-run index`, plus the same-length-swap/100901-byte note and a pointer to
  the new writer script);
  `run-note-template.md` (+5: reusable `append-run-note-docs.py` writer documented);
  `hermes-profile-diagnostics/SKILL.md` (+8/-3: canonical cleanup order re-verified 2026-11-18 / 28
  gate triggers, helper scripts live under the SKILL's `scripts/` not the profile's, and the one-call
  `hindsight -p <p> bank consolidate <bank> --wait --poll-interval 5` form);
  `cleanup-run-endpoints-and-counts.md` (+67: the 11-18 reflect row — 344,932 / 11,993 with disambig
  174,335 / 8,345 — plus the "disambig can retract the primary, quote the retraction" rule, the
  11-18 startup calibration, helper-script paths, the hand-rolled two-pass recipe, and the
  `python3 open(...,'a')` append alternative with its chars≠bytes caveat).
- **New script (1):** `hermes-profile-backup/scripts/append-run-note-docs.py` — idempotent writer for
  today's index bullet + practice-notes table row (collapses newlines to one physical line, inserts
  the row after the last `| 20…` row, prints `INDEX count=N` / `ROW count=N`, exit 0 only when both
  are exactly 1). **First used on this run.**
- `config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local one
  (17,021 bytes / 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **298**; remote HEAD at preflight `97b9133c1d72`, 316 blobs
- Preflight diff: `Modified: 9, New: 1, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- A sibling landed between the preflight and the blob phase: Step 2 read HEAD
  **`5466036f9eb9`** (316 blobs) instead of the preflight's `97b9133c1d72` (316 blobs). Blob count and
  the **9 M / 1 A / 0 D** set were identical and the remote stayed at `5466036f9eb9` through Step 7,
  so the commit is parented on the fresh HEAD and the ref PATCH succeeded first try (**no ref-PATCH
  422 race**).
- 10 blobs uploaded, subtree `b59af1d96b11a553a8fa3a7238c106844fb7d90c`, top tree
  `bb3d49c7017f197a7cc3e1b82a22b64f85bf7b6d`, commit + ref in one clean pass.
- Closing assertion: after this follow-up lands, the preflight must read
  `Modified: 0, New: 0, Deleted: 0`.

## Post-push remote verification
- Remote HEAD `cb317a42e844`; total blobs **317**, `demo-pm` blobs = **298** (== local file count
  298); by top dir: demo-pm 298, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 → siblings
  intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = **15**, non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `tmp_*`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + practice-notes table row + SKILL.md `latest:` pointer
`2026-11-18` → `2026-11-19` (same-length swap), pushed with the same standalone-subtree script. The
index bullet and row are written by the new `scripts/append-run-note-docs.py` (first real use — it
must print `INDEX count=1` / `ROW count=1`). The closing preflight
(`Modified: 0, New: 0, Deleted: 0`) is the proof that this follow-up's ref PATCH landed.
