# demo-pm backup run — 2026-11-20

## Result
**Method B (standalone subtree, no clone)** — **main commit FIRST-TRY, 0 aborts (no 422 race)**,
15th keyring flip caught at pre-flight, guard re-executed in the SAME shell call as the script.
Follow-up outcome is proven by the closing preflight assertion at the end of this note.
Main commit: `a00fb359c15a2871972d354817d8ab42eb90fc2a`
URL: https://github.com/OnePlusNDev/hermes-config/commit/a00fb359c15a2871972d354817d8ab42eb90fc2a
Diff: **7 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNTester`** (`permissions.push=false`) — the **15th observed keyring
  flip** (11-19 logged the 14th). Guard form (switch → re-read login AND `permissions.push`) read
  `OnePlusNDev` / `push=true`; the pre-push guard was re-executed immediately before the script in
  the same shell call and printed `GUARD: login=OnePlusNDev push=true`. No blob 404, no mid-run flip.
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9_-]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`;
  the only `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed**.
- `.env` excluded, never uploaded; no `auth.json` / `auth.lock` / `state.db*` in the remote tree.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`.

## Diff (7 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json                                                    (+10/-10)
M  demo-pm/memories/MEMORY.md                                                (+1/-1)
M  demo-pm/memories/USER.md                                                  (+1/-1)
M  demo-pm/memories/archive/ARCHIVE.md                                       (+14/-0)
M  demo-pm/skills/devops/hermes-profile-backup/references/run-note-diff-characterization.md (+40/-0)
M  demo-pm/skills/devops/hermes-profile-backup/references/tooling-gotchas-and-patch-anchoring.md (+44/-2)
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md (+8/-2)
```
Counts and content from `scripts/characterize-diff-post-push.py 69d6bf42027e` (prev blobs 318 /
new 318, identical 292); churn numbers re-read from the uploaded blobs after the push.

- **Routine runtime churn (4)** — task-polling `repeat.completed` 7155→**7203**, `next_run_at` →
  11-20T20:30, `last_run_at` → 11-20T20:00:49.089637, `updated_at` → 11-20T20:00:49.089936;
  config-backup 150→**151**, next 11-21T20:00, last 11-19T20:05:21.384120; memory-cleanup
  150→**151**, next 11-20T21:00, last 11-19T21:03:18.976187. `memories/MEMORY.md` + `USER.md` —
  header date only, 2026-11-18 → **2026-11-19** (bodies identical; snapshots 20261029 / 20261011 reused).
  `memories/archive/ARCHIVE.md` — new **2026-11-19 21:0x memory cleanup** section: `:9178` offline
  at first probe, launcher start → poll1 **and** poll2 `000` with `/tmp/h9178_p1.json` still holding
  the previous healthy body (**stale-body trap 10th consecutive**, trust only the HTTP code),
  poll3 200 healthy at ~30 s (warm pg0); consolidation op `a7b550db` **+161 ms**,
  `deduplicated=false`, counter **109→110**, bank 48 units / 1228 links (semantic 740 / temporal 469
  / entity 19) / 2 documents, `mental-model list` + `directive list` both empty; two reflect passes —
  primary **31,073 / 5,001**, a **new primary low** and the **first run whose primary fell BELOW the
  50 K baseline** (prior low 95,622 on 10-20), so **both** gates fired at once (`tokens: 31073 <
  baseline 50000` → "facts likely not fed" AND `wording: AFFIRMATIVE`, 29th consecutive wording
  trigger in the usual table-cell-negation + heading-count shape), disambig **133,133 / 4,918** was a
  genuine full-bank read (per-item 06-14/06-16/06-17 timeline, 13 bilingual duplicate groups, 3 soft
  tensions) and returned 「无内容性过期事实」 → 归档 0, keeping z.ai GLM → **drift day 15**;
  sessions **7,478 / 3,032 (>90d) / 5,978 (>30d)** (+50/day, recorded only — `auto_prune: false`).
- **Carry-over doc edits authored after the 11-19 follow-up push (3):**
  `run-note-diff-characterization.md` (+40: "Do not hand-roll the probe (2026-11-19)" — use the
  script with `--commit=<main sha>` instead of a throwaway `/tmp` probe; plus "Confirmed:
  `append-run-note-docs.py` in production" with the expected output shape and the
  write-before-push ordering rule);
  `tooling-gotchas-and-patch-anchoring.md` (+44/-2: "Six traps" → "**Eight traps**", new §7
  `execute_code` is refused in cron mode → `write_file` + `terminal("python3 …")`, new §8 `gh api`
  query strings must live in the SAME argv element — a split `"?recursive=1"` silently returns
  empty stdout and the traceback points at `json.loads`, not at the argv);
  `cleanup-run-endpoints-and-counts.md` (+8/-2: the 11-19 reflect row — 31,073 / 5,001 primary with
  both gates, disambig 133,133 / 4,918 — plus widening the observed band to **~31 K–407 K** and the
  corollary that a sub-baseline primary is not proof of a thin read).
- `config.yaml` is deliberately NOT in the diff: the remote blob already equalled the local one
  (17,021 bytes / 16,835 chars — the usual CJK-comment discrepancy).

## Preflight
- Local files (after excludes): **299**; remote HEAD at preflight `69d6bf42027e`, 318 blobs
- Preflight diff: `Modified: 7, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `69d6bf42027e` at preflight **and** at Step 2 (318 blobs), and **stayed there
  through Step 7** → **no ref-PATCH 422 race**; the ref PATCH succeeded on the first attempt.
- 7 blobs uploaded, subtree `1952ec7edb3e10627234a648d7ccc5227ff96684`, top tree
  `16274899c8e942da1fdd1c2d6907c1b7aee342df`, commit + ref in one clean pass.
- Closing assertion: after this follow-up lands, the preflight must read
  `Modified: 0, New: 0, Deleted: 0`.

## Post-push remote verification
- Remote HEAD `a00fb359c15a`; total blobs **318**, `demo-pm` blobs = **299** (== local file count
  299); by top dir: demo-pm 299, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 → siblings
  intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = **15**, non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `tmp_*`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + practice-notes table row + SKILL.md `latest:` pointer
`2026-11-19` → `2026-11-20` (same-length swap), pushed with the same standalone-subtree script.
Bullet and row written by `scripts/append-run-note-docs.py` (expect `INDEX count=1` / `ROW count=1`).
The closing preflight (`Modified: 0, New: 0, Deleted: 0`) is the proof that this follow-up's ref
PATCH landed.
