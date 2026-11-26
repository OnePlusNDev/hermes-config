# demo-pm backup run — 2026-11-26

## Result
**Method B (standalone subtree, no clone)** — main commit FIRST-TRY, 0 aborts (no 422 race).
Main commit: `72d95f62ca305484ac9bb86c2a653245544de83a`
URL: https://github.com/OnePlusNDev/hermes-config/commit/72d95f62ca305484ac9bb86c2a653245544de83a
Diff: **8 M, 0 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNDev`** (`push=true`) on the FIRST probe — **no keyring flip**
  (record stays at 18; 11-25 logged the 18th). No `gh auth switch` needed; no blob 404.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`.
- Preflight remote HEAD `ed3763d5cc93` (325 blobs) — a **sibling `demo-dev` backup** landed
  at 2026-11-26T12:00:50Z, minutes before this run; the same SHA was still HEAD at Step 2 and
  is the parent of the backup commit → no mid-run sibling, no ref-PATCH 422 race.
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9_-]{20,}` → **0** matches;
  non-empty `api_key:` → **0** matches; all **15** `api_key:` lines are `''`; the only
  `key_env` occurrence is a comment (line 695)
  → **no plaintext key found, no `key_env` replacement needed** (config.yaml unchanged since
  11-25: blob 17,021 bytes / 16,835 chars, the usual CJK-comment discrepancy).
- `.env` (296 B; names only: `GITHUB_USERNAME`, `GITHUB_EMAIL`, `GITHUB_TOKEN`, `GATEWAY_PORT`,
  `AGENT_NAME`, `AGENT_ROLE`, `DEEPSEEK_API_KEY`, `TERMINAL_ENV`) excluded, never uploaded;
  no `auth.json` / `auth.lock` / `state.db*` in tree.

## Diff (8 M, 0 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/MEMORY.md
M  demo-pm/memories/USER.md
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/demo-pm-github-api/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/references/tooling-gotchas-and-patch-anchoring.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/SKILL.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
```
Characterized with `scripts/characterize-diff-post-push.py ed3763d5cc93 72d95f62ca30` (read-only;
the push had already landed). Per-file: `jobs.json` +10/-10, `MEMORY.md` +1/-1, `USER.md` +1/-1,
`ARCHIVE.md` +10/-0, `demo-pm-github-api/SKILL.md` +1/-0,
`tooling-gotchas-and-patch-anchoring.md` +53/-1, `diagnostics/SKILL.md` +5/-3,
`cleanup-run-endpoints-and-counts.md` +6/-3. Summary `MODIFIED 8 / ADDED 0 / DELETED 0`,
matching the preflight exactly.

- **4 routine runtime churn** (numbers re-read from the uploaded remote blob) — task-polling
  `completed` 7443→**7491**, config-backup 156→**157** (`last_run_at` 2026-11-25T20:06:11.896509,
  `last_status: ok`), memory-cleanup 156→**157** (`last_run_at` 2026-11-25T21:03:18.444324,
  `last_status: ok`), `updated_at` 2026-11-26T20:01:00.906591; `MEMORY.md` / `USER.md` header
  2026-11-24 → **2026-11-25**; `ARCHIVE.md` = the 11-25 21:0x cleanup (+10 lines) — op
  `2e27594a-c61d-438b-860e-e1212b41d73d` +97 ms, `operations_by_status.completed` 114→**115**,
  `total_nodes 48 / total_links 1228` unchanged (no-op dedupe), primary **113,455 / 5,115** with
  the wording gate **34th consecutive**, disambig **321,798 / 7,510** → 「无内容性过期事实」;
  blob records `stale-body 陷阱第 13 次` (poll 1 AND poll 2 `000`, `/tmp/h9178_p1.json` still the
  previous healthy body, healthy poll 3); sessions **7,778 / 3,332 / 6,278** vs 7,728 / 3,282 /
  6,228 last round (all three +50 again — record, do not read as monotone).
- **4 carry-over doc edits** made since the 11-25 push: `demo-pm-github-api/SKILL.md` +1 (11-26
  API round note: one-pass template, `core_remaining=4953`, PM filter `5B×4`, `search
  total_count=0` → `[SILENT]`); `tooling-gotchas-and-patch-anchoring.md` +53/-1 (trap: the
  `git/commits/<sha>` object endpoint needs the full 40-char SHA — the 12-char form in preflight
  and backup logs 404s; the non-`git` `repos/O/R/commits/<sha>` path accepts the short form);
  `diagnostics/SKILL.md` +5/-3 and `cleanup-run-endpoints-and-counts.md` +6/-3 (same trap: pass the
  **one** named `MEMORY-<YYYYMMDD>.snapshot.md`, never the `MEMORY-*.snapshot.md` glob — with 4
  snapshots on disk `diff` errors `extra operand` because process substitution feeds only the first
  operand).

## Preflight
- Local files (after excludes): **306**; preflight remote HEAD `ed3763d5cc93`, 325 blobs
- Preflight diff: `Modified: 8, New: 0, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**

## Execution notes
- Remote HEAD was `ed3763d5cc93` at preflight AND at Step 2, and it is the **parent of the backup
  commit** → nothing landed in between, **no ref-PATCH 422 race**; ref PATCH succeeded first try.
- 8 blobs uploaded, subtree `c220735f092d53ba7333d4614a15770cc05d788e`, top tree
  `9697211d12c6404fc28589a910a03f83e8cbfc83`, commit + ref in one clean pass.
- Closing assertion: after this follow-up lands, the preflight must read
  `Modified: 0, New: 0, Deleted: 0` (that is the only proof the follow-up's ref PATCH landed).

## Post-push remote verification
- Remote HEAD `72d95f62ca30`; total blobs **325**, `demo-pm` blobs = **306** (== local file
  count 306); by top dir: demo-pm 306, demo-dev 5, demo-tester 8, tester-01 5, .gitignore 1 →
  siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = **15**, non-empty = **0**
- Sensitive-path leak check (`.env`, `auth.json`, `auth.lock`, `state.db*`, `processes.json`,
  `bin/tirith`, `/home/`, `/.local/`, `response_store.db`, `.hermes_history`) → **NONE**
- Temp/diagnostic script check (`.tmp_*`, `tmp_triage/`, `pm_health*`, `gh_health*`,
  `healthcheck_*`, `get_token`, `__pycache__`) → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
Run note + index bullet + practice-notes table row + SKILL.md `latest:` pointer
`2026-11-25` → `2026-11-26` (same-length swap; SKILL.md measured 100,901 B, at cap),
pushed with the same standalone-subtree script. Bullet and row written by
`scripts/append-run-note-docs.py` (expect `INDEX count=1` / `ROW count=1`).
Pre-follow-up preflight expected `Modified: 3, New: 1, Deleted: 0` (+ `jobs.json` if a cron tick
dirtied it again); the closing preflight must read `0/0/0`.
