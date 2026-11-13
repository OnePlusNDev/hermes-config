# demo-pm backup run — 2026-11-13

## Result
**Method B (standalone subtree, no clone)** — **1 aborted attempt (account flip, NOT the 422 race); attempt 2 clean, FIRST-TRY after the switch**.
Main commit: `63cbd536849bcf6ea7b121e622f46e484ba6edca`
URL: https://github.com/OnePlusNDev/hermes-config/commit/63cbd536849bcf6ea7b121e622f46e484ba6edca
Diff: **8 M, 1 A, 0 D**.

## Pre-flight
- `gh api user` → **`OnePlusNDev`** (owner, repo `permissions.push=true`, `admin=true`, `GITHUB_TOKEN` unset)
  with **no switch needed**. But the re-check IMMEDIATELY before the script printed **`OnePlusNTester`**
  — the 7th observed keyring flip — and attempt 1 died at the FIRST blob with
  `FATAL uploading demo-pm/cron/jobs.json: gh: Not Found (HTTP 404)`. `gh auth switch --user OnePlusNDev`
  → verified `push=true`, then a plain re-run (attempt 2) was clean with no further flip.
- Repo root confirms target: `.gitignore`, `demo-dev`, `demo-pm`, `demo-tester`, `tester-01`
  (only `OnePlusNDev/hermes-config` carries `demo-pm/`).
- config.yaml plaintext scan (task-mandated): `sk-[A-Za-z0-9]{20,}` → **0** matches;
  `api_key: '<non-empty>'` → **0** matches; all **15** `api_key:` lines are `''`;
  `password: ''` / `secret: ''` both empty → **no plaintext key found, no `key_env` replacement needed**.
- `.env` (296 B; `GITHUB_USERNAME`, `GITHUB_EMAIL`, `GITHUB_TOKEN`, `GATEWAY_PORT`, `AGENT_NAME`,
  `AGENT_ROLE`, `DEEPSEEK_API_KEY`, `TERMINAL_ENV`) excluded, never uploaded; no `auth.json` /
  `auth.lock` / `state.db*` in the remote tree.

## Diff (8 M, 1 A, 0 D)
```
M  demo-pm/cron/jobs.json
M  demo-pm/memories/MEMORY.md
M  demo-pm/memories/USER.md
M  demo-pm/memories/archive/ARCHIVE.md
M  demo-pm/skills/devops/demo-pm-github-api/SKILL.md
M  demo-pm/skills/devops/hermes-profile-backup/references/network-flakiness-and-verify-tooling.md
M  demo-pm/skills/devops/hermes-profile-backup/references/skill-md-at-cap.md
M  demo-pm/skills/devops/hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md
A  demo-pm/skills/devops/demo-pm-github-api/references/2026-11-13-inline-source-and-bearer.md
```
Characterized ONCE pre-push with `characterize-diff-vs-prev-head.py d43f5c00d6c2` → exit 0,
`MODIFIED 8 / ADDED 1 / DELETED 0` (local 287 vs remote-at-PREV 286), output in `/tmp/char_20261113.txt`.

- **Routine runtime churn (4):** `cron/jobs.json` — task-polling `completed` 6819→**6866**,
  `next_run_at` → 11-13T20:30, `last_run_at` 11-13T19:30:59; config-backup `completed` 143→144,
  next 11-14T20:00, last 11-12T20:05:22; memory-archive 143→144, next 11-13T21:00,
  last 11-12T21:04:21; `updated_at` → 11-13T20:00:29. `memories/MEMORY.md` — header only,
  最后更新 2026-11-11 → 2026-11-12 (body byte-identical, still reuses
  `archive/MEMORY-20261029.snapshot.md`); `memories/USER.md` — header only, 2026-11-11 → 2026-11-12
  (body identical, reuses `archive/USER-20261011.snapshot.md`); `memories/archive/ARCHIVE.md` —
  new **2026-11-12 21:01-21:06 memory cleanup** row (daemon **healthy on poll 1**, ~10 s warm pg0 —
  no stale-body trap this time; consolidation op `3c977d70-bd5e-48cc-bcb5-c800ac75583c`
  **completed +33 ms**, `deduplicated=false`, counter **102→103**, `pending=0` / `failed=0`;
  nodes 48 / 1228 links / 2 documents stable; reflect both passes succeeded, no crash, no 504 —
  primary **199,108 / 7,105** @ `budget=high`, wording gate **22nd consecutive** in a NEW shape
  (「健康评分」 opening + 「## 1. 过期事实（30 天以上）：没有」 heading with the negation AFTER the
  keyword + date-conditional clause + 「目前无需归档任何内容」 close); disambiguation
  **299,045 / 7,120** 「无内容性过期事实」 with a 7-row table; bank↔flat-file LLM-key drift
  **8th consecutive day** — logged, no data mutated).
- **Carry-over doc edits authored after the 11-12 follow-up push (4):**
  `demo-pm-github-api/SKILL.md` (+3 bullets: no inline `source .env` in `terminal` — use a
  standalone script with adjacent-quote key assembly; Bearer auth yielding a 5-byte fake-empty
  body that must not be read as "no work"; pointer to the new reference file);
  `hermes-profile-backup/references/network-flakiness-and-verify-tooling.md` (correction:
  `/git/commits/<short-sha>` 404s — use the `/commits` list endpoint and match on the prefix;
  the same call attributes a sibling that landed mid-run);
  `hermes-profile-backup/references/skill-md-at-cap.md` (third occurrence: in a cron RUN turn
  `execute_code` is refused → `terminal(python3 -c ...)`; `read_file` on the dump fails >100 K,
  so json-load → write `.content` to a fresh `/tmp/*.md` → `read_file` with offset/limit);
  `hermes-profile-diagnostics/references/cleanup-run-endpoints-and-counts.md` (11-12 token row
  199,108 / 7,105 + disambig 299,045 / 7,120, gate 22nd, drift day 8; plus the
  `~/.local/bin/hindsight` CLI-path note).
- **New include-list file (1 A):** `demo-pm-github-api/references/2026-11-13-inline-source-and-bearer.md`
  — legitimately new reference doc, NOT exclude-set drift.

`config.yaml` deliberately NOT in the diff: the remote blob already equalled the local one
(16,835 chars / 17,021 bytes).

## Preflight
- Local files (after excludes): **287**; preflight read remote HEAD **`d43f5c00d6c2`** (305 blobs).
  Local 287 == remote `demo-pm` 287 after the push.
- Preflight diff: `Modified: 8, New: 1, Deleted: 0` — **no new exclude gaps**
- Token scan on upload candidates: **CLEAN - no full token patterns**
- No sibling landed this run: preflight, attempt-1 Step 2 and attempt-2 Step 2 all read
  `d43f5c00d6c2` (305 blobs), and the ref PATCH saw the same base.

## Execution notes
- **Attempt 1 aborted after 0 blobs**: the pre-check one call earlier read `OnePlusNDev`, the
  immediate pre-script re-check read `OnePlusNTester`, and the first blob POST returned
  `HTTP 404` (the account-flip signature, not a missing repo). `gh auth switch` → attempt 2.
- 9 blobs uploaded in one clean pass: `cron/jobs.json` `42da8167dda9`, `MEMORY.md` `e839de0cfa7d`,
  `USER.md` `f4c5af89794f`, `ARCHIVE.md` `bfdc9ca05650`, `demo-pm-github-api/SKILL.md` `545ca27d8104`,
  `network-flakiness-and-verify-tooling.md` `0c0b261c6379`, `skill-md-at-cap.md` `3a3190465b27`,
  `cleanup-run-endpoints-and-counts.md` `e0a9bbb8ed13`,
  `2026-11-13-inline-source-and-bearer.md` `a97504604291`; subtree
  `4243d23cb5c5a9ecfdf85805d7f50f7dd60120aa`, top tree `7222c5f875419d1cbf2a09aa9bbebf1830d82579`,
  commit + ref PATCH on the first attempt of attempt 2 (`Remote HEAD now: 63cbd536849b`).
- Remote HEAD stayed `d43f5c00d6c2` from Step 2 through commit time → **no ref-PATCH 422 race**.
- No network flakiness (no port-443 timeout, no HTTP2 framing error). Follow-up cleanliness is
  asserted only by the closing-preflight `0/0/0` check, not by the log.

## Post-push remote verification
- Remote HEAD `63cbd536849b`; total blobs **306**, `demo-pm` blobs = **287** (== local file count 287);
  by top dir: demo-pm 287, demo-dev 5, demo-tester 8, tester-01 5, `.gitignore` 1 → siblings intact
- Remote `demo-pm/config.yaml`: **0** `sk-` matches; `api_key` lines = 15, non-empty = **0**
- Sensitive-path / temp-diagnostic leak checks → **NONE**
- `scripts/post-push-verify.py` → **ALL CHECKS PASS** on the first execution.

## Follow-up commit (this session)
All FOUR items: run note + `references/dated-runs-index.md` bullet +
`references/method-b-practice-notes.md` "Observed on recent runs" row + SKILL.md `latest:`
`2026-11-12` → `2026-11-13` (same-length in-place swap; SKILL.md is over its 100 K cap, so no
new prose goes in it). Pushed with the same standalone-subtree script; the closing preflight is
expected to read `Modified: 0, New: 0, Deleted: 0`.
