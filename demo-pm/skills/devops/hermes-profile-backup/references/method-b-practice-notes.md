# Method B practice notes (extracted from SKILL.md 2026-09-21 to free cap space)

## Why runs go straight to Method B (no clone attempt)

Practice note (extended through 2026-09-11): runs 09-01 → 09-11 all went
STRAIGHT to Method B standalone-subtree with NO clone attempt — the repo is
625+ blobs and git/libcurl transport has repeatedly timed out in cron mode,
while the script never needs a worktree and absorbs concurrent HEAD advances by
re-reading the remote ref.

## The one-plain-re-run rule for the ref-PATCH 422 race

The ref-PATCH HTTP 422 "Update is not a fast forward" recurs **intermittently**, not
uniformly: the early stretch 09-06→09-23 hit it on most runs, but the recent window is a
minority (2 of the last 9 - 10-06 and 10-09). The cause is always the same: **any**
concurrent sibling-profile backup advances `main` during the ~1-2 min blob phase - do NOT
assume one fixed culprit (observed siblings include demo-tester and demo-dev, 2026-10-09,
which landed HEAD `93d20c3d`->`46ee50cb3b58` at 12:01:26Z). A "clean" run is thus the
expected case; seeing a 422 is normal, not a signal that something else is wrong.

Budget exactly ONE plain re-run: blob SHAs are idempotent, so the re-run just
re-parents the identical commit on the fresh HEAD. Do NOT rebase, do NOT attempt
tree surgery, and do NOT treat it as a partial failure — the first run's blobs are
already uploaded.

## Observed on recent runs

| Date | 422 race? | Notes |
|------|-----------|-------|
| 2026-09-17 | no | remote stable at 7a2b4e395427 through blob phase |
| 2026-09-18 | no | 232 D (curator archive) — see `curator-archive-churn-triage.md` |
| 2026-09-19 | no | remote stable at e18164653ec6 |
| 2026-09-20 | no | remote stable at 4aaad6fc05a2 |
| 2026-09-21 | no | remote advanced twice *between preflight and blob phase* (cf2cef12 → c82057b2 → 07eea1c3) via concurrent sibling backups, then stable through commit time |
| 2026-09-22 | no | remote stable at cdefeb1d36b0 through the blob phase |
| 2026-09-23 | **yes** | remote advanced `9c55330dae07` → `a37580dda96f` between blob phase and ref PATCH; absorbed by the budgeted single plain re-run (attempt 3 clean). Same run also hit a NEW failure mode — see "Shared /tmp payload namespace" below. |
| 2026-09-24 | no | **first-try, no aborts at all** — the 09-23 `mkdtemp` payload fix held (no shared-`/tmp` deletion). Remote advanced `6c156eb1e2c4` → `46c22a23e2e5` (sibling demo-dev backup, 12:00:45Z) **before** the script's own Step 2, then stayed stable through commit time. Also: gh active account was owner-active throughout (09-23's `OnePlusNTester` flip did NOT recur, and the pre-push re-check held) — a data point that the flip is intermittent, not systematic. Follow-up commit likewise absorbed a fresh remote advance (`e51452458970`) on its Step 2. Closing preflight `Modified: 0, New: 0, Deleted: 0`. |
| 2026-09-26 | n/a — **1 abort, account flip (not the 422 race)** | Pre-flight active gh user was **`zhangtbj`** (`push=false`) → switched to `OnePlusNDev`; attempt 1 then died at the FIRST blob with `FATAL uploading demo-pm/cron/jobs.json: gh: Not Found (HTTP 404)` — a re-check showed `zhangtbj` active again, i.e. the keyring race re-flipped the account *between the pre-flight switch and the blob POST* (~1 min). Second switch → clean attempt 2 (7 blobs, subtree `7b528200e686`, commit `3734ef8ff71b`, **ref PATCH first try — no 422 race**; remote stable at `03b61c6a6c89` through the blob phase). Lessons: (a) the check-TWICE rule needs to fire as late as possible — the flip won; (b) the flipper can be an account NOT in the previously-recorded set (new: `zhangtbj`), so never special-case a single "known bad" account. |
| 2026-09-27 | **yes** | remote advanced `8c5cb9e94229` → `b3d2005d4c11` (concurrent sibling backup) during the blob phase; the ref PATCH died `HTTP 422 non-fast-forward` on attempt 1 → absorbed by the budgeted **single plain re-run** (attempt 2 clean, identical 4 blobs + subtree `bd929bdcb45a`, remote stable at `b3d2005d4c11` through commit time). Gh active account was `OnePlusNDev` (owner, `push=true`) throughout — **no flip**; 09-26's mid-run `zhangtbj` re-flip did not recur. Confirms the 422 race is driven by sibling `main` advances, independent of account state. |
| 2026-09-28 | **yes** | remote advanced `c8a48bb08efa` → `77e69333f412` (concurrent sibling backup) during the blob phase; the ref PATCH died `HTTP 422 non-fast-forward` on attempt 1 → absorbed by the budgeted **single plain re-run** (attempt 2 clean, identical 9 blobs + subtree `7652d181b1d8`, remote stable at `77e69333f412` through commit time). Pre-flight active gh user was **`zhangtbj`** (`push=false`, the 09-26 flipper) → `gh auth switch --user OnePlusNDev` required before any blob POST; the flip did **not** recur mid-run this time, so the pre-flight switch held. No network flakiness; the `mkdtemp` payload fix held. |
| 2026-09-29 | no | **1 abort — mid-run account flip** (NOT the 422 race): pre-flight active gh user was **`zhangtbj`** (`push=false`) → `gh auth switch --user OnePlusNDev`; the flip **recurred MID-RUN** — attempt 1 died at the FIRST blob with `FATAL uploading demo-pm/cron/jobs.json: gh: Not Found (HTTP 404)` (the documented "every blob-404 is an account flip" case) → second switch, clean re-run (blob SHAs idempotent, so the re-run costs nothing). Remote **stable at `cdcabbeb7545`** through commit time → no ref-PATCH 422 race. 5 blobs + subtree `eec00ef16904` + top tree `07e133c7e8c6` in one clean pass. No network flakiness; the `mkdtemp` payload fix held. |
| 2026-09-30 | no | **first-try, 0 aborts** — pre-flight active gh user was **`zhangtbj`** (`push=false`) → `gh auth switch --user OnePlusNDev`; re-checked immediately pre-run and the switch **held** (no mid-run flip). Remote **stable at `6cdc630521ec`** from preflight through commit time (no sibling advance) → 8 blobs + subtree `52cb600c33b4` + top tree `1ad643b365c8` in one clean pass, **no ref-PATCH 422 race**. No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-01 | no | **first-try, 0 aborts** — pre-flight active gh user was **`OnePlusNTester`** (`push=false`) → `gh auth switch --user OnePlusNDev`; re-checked immediately pre-run and the switch **held** (no mid-run flip). Remote **stable at `1fcd2063e654`** from preflight through commit time (no sibling advance) → 6 blobs + subtree `06db308902a5` + top tree `fac92ca2ab39` in one clean pass, **no ref-PATCH 422 race**. No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-03 | no | **first-try, 0 aborts** — pre-flight active gh user was **`OnePlusNDev`** (owner, `push=true`) — **no switch needed** (`GITHUB_TOKEN` unset), no mid-run flip. Remote **stable at `5b541e866d54`** from preflight through commit time (no sibling advance) → 8 blobs + subtree `874cf6a84a11` + top tree `102a5bd05ee7` in one clean pass, **no ref-PATCH 422 race**. No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-03 (2nd, 20:00) | no | **first-try, 0 aborts** — pre-flight active gh user was **`OnePlusNTester`** (`push=false`) → `gh auth switch --user OnePlusNDev`; re-checked immediately pre-run and the switch **held** (no mid-run flip). Remote **stable at `0377a76d082e`** from preflight through commit time (no sibling advance) → 2 blobs + subtree `96e0c79d5df4` + top tree `49d822cb7ed9` in one clean pass, **no ref-PATCH 422 race**. The 2 `D` = genuine local skill removals (apple/apple-notes, software-development/systematic-debugging). No network flakiness; the `mkdtemp` payload fix held. **First same-day repeat run** → run note uses the `YYYYMMDDb` suffix. |
| 2026-10-04 | no | **first-try, 0 aborts** — pre-flight active gh user was **`OnePlusNDev`** (owner, `push=true`) — **no switch needed** (`GITHUB_TOKEN` unset), no mid-run flip. Remote **stable at `7f5418a4ef91`** from preflight through commit time (no sibling advance) → 4 blobs + subtree `b3502ed58de2` + top tree `6c237a8753a4` in one clean pass, **no ref-PATCH 422 race**. No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-05 | no | **first-try, 0 aborts** — pre-flight active gh user was **`OnePlusNDev`** (owner, `push=true`) — **no switch needed** (`GITHUB_TOKEN` unset), no mid-run flip. Remote **stable at `b59147ff4803`** from preflight through commit time (no sibling advance) → 4 blobs + subtree `406e5ac8db02` + top tree `919563bb1650` in one clean pass, **no ref-PATCH 422 race**. No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-06 | **yes** | remote advanced `08d2e00d49ea` → `c332a3c5a980` (concurrent sibling backup) during the blob phase; attempt 1's ref PATCH died `HTTP 422 non-fast-forward` → absorbed by the budgeted **single plain re-run** (attempt 2 clean, identical 6 blobs + subtree `7aa4284ef2bf`, remote stable at `c332a3c5a980` through commit time). Pre-flight active gh user was **`OnePlusNTester`** (`push=false`) → `gh auth switch --user OnePlusNDev` (re-checked immediately pre-run, held, no mid-run flip). No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-07 | no | **first-try, 0 aborts** — pre-flight active gh user was **`JungleAssistant`** (`push=false`, a **NEW flipper account**) → `gh auth switch --user OnePlusNDev`; re-checked immediately pre-run and the switch **held** (no mid-run flip, `GITHUB_TOKEN` unset). Remote advanced `4cbcf4355bf9` → `79032de7d9e8` (concurrent sibling backup) *before* the script's own Step 2, then stayed **stable at `79032de7d9e8`** through commit time → 4 blobs + subtree `ef0a2e79644c` + top tree `9cb9d858a3fb` in one clean pass, **no ref-PATCH 422 race**. No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-08 | no | **first-try, 0 aborts** — pre-flight active gh user was **`zhangtbj`** (`push=false`, a known flipper) → `gh auth switch --user OnePlusNDev`; re-checked immediately pre-run and the switch **held** (no mid-run flip, `GITHUB_TOKEN` unset). Remote **stable at `292113d1acc2`** from preflight through commit time (no sibling advance) → 3 blobs + subtree `8f40df208898` + top tree `559f668c4352` in one clean pass, **no ref-PATCH 422 race**. No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-09 | **yes** | remote advanced `93d20c3dbbd9` → `46ee50cb3b58` (concurrent sibling **demo-dev** backup, 12:01:26Z) during the blob phase; attempt 1's ref PATCH died `HTTP 422 non-fast-forward` → absorbed by the budgeted **single plain re-run** (attempt 2 clean, identical 3 blobs + subtree `be98e85cafe3`, remote stable at `46ee50cb3b58` through commit time). Pre-flight active gh user was **`OnePlusNDev`** (owner, `push=true`) — **no switch needed** (`GITHUB_TOKEN` unset), no mid-run flip. No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-10 | no | **first-try, 0 aborts** — pre-flight active gh user was **`OnePlusNTester`** (`push=false`) → `gh auth switch --user OnePlusNDev`; re-checked immediately pre-run and the switch **held** (no mid-run flip, `GITHUB_TOKEN` unset). Remote **stable at `ee1d16446a25`** from preflight through commit time (no sibling advance) → 3 blobs + subtree `856f8a32170a` + top tree `5df4b9aefe3d` in one clean pass, **no ref-PATCH 422 race**. No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-11 | **yes** | remote advanced `e151b784b4bf` → `b5089466ba27` (concurrent sibling backup) during the blob phase; attempt 1's ref PATCH died `HTTP 422 non-fast-forward` → absorbed by the budgeted **single plain re-run** (attempt 2 clean, identical 4 blobs + subtree `650ad2f24c19`, remote stable at `b5089466ba27` through commit time). Pre-flight active gh user was **`OnePlusNTester`** (`push=false`) → `gh auth switch --user OnePlusNDev` (re-checked immediately pre-run, held, no mid-run flip). No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-12 | no | **first-try, 0 aborts** — pre-flight active gh user was **`OnePlusNDev`** (owner, `push=true`) — **no switch needed** (`GITHUB_TOKEN` unset), no mid-run flip. Remote **stable at `478bbfe983c6`** from preflight through commit time (no sibling advance) → 8 blobs + subtree `53520d8b8021` + top tree `c217470be839` in one clean pass, **no ref-PATCH 422 race**. No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-13 | no | **first-try, 0 aborts** — pre-flight active gh user was **`JungleAssistant`** (`push=false`, the 10-07 flipper) → `gh auth switch --user OnePlusNDev`; re-checked immediately pre-run and the switch **held** (no mid-run flip, `GITHUB_TOKEN` unset). Remote **stable at `68e7f0a1c6b8`** from preflight through commit time (no sibling advance) → 5 blobs + subtree `f208acfb1140` + top tree `f9e3947c047f` in one clean pass, **no ref-PATCH 422 race**. No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-14 | no | **first-try, 0 aborts** — pre-flight active gh user was **`zhangtbj`** (`push=false`, a known flipper since 2026-09-26) → `gh auth switch --user OnePlusNDev`; re-checked immediately pre-run and the switch **held** (no mid-run flip, `GITHUB_TOKEN` unset). Remote **stable at `aa1e15833e0e`** from preflight through commit time (no sibling advance) → 3 blobs + subtree `68fa7c6fbd99` + top tree `aef641369173` in one clean pass, **no ref-PATCH 422 race**. No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-15 | no | **first-try, 0 aborts** — pre-flight active gh user was **`OnePlusNTester`** (`push=false`) → `gh auth switch --user OnePlusNDev`; re-checked immediately pre-run and the switch **held** (no mid-run flip, `GITHUB_TOKEN` unset). Remote **stable at `70e3c15e297c`** from preflight through commit time (no sibling advance) → 4 blobs + subtree `3b9993fe0d9e` + top tree `d2c74ac00e69` in one clean pass, **no ref-PATCH 422 race**. No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-16 | no | **first-try, 0 aborts** — pre-flight active gh user was **`OnePlusNDev`** (owner, `push=true`) — **no switch needed** (`GITHUB_TOKEN` unset), no mid-run flip. Remote **stable at `4ad2bdfe0e85`** from preflight through commit time (no sibling advance) → 4 blobs + subtree `735e6829e1c4` + top tree `6267aa4b8f43` in one clean pass, **no ref-PATCH 422 race**. No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-17 | no | **first-try, 0 aborts** — pre-flight active gh user was **`OnePlusNDev`** (owner, `push=true`) — **no switch needed** (`GITHUB_TOKEN` unset), no mid-run flip. Remote **stable at `7ef238af2599`** from preflight through commit time (no sibling advance) → 4 blobs + subtree `f2f99cf1202d` + top tree `17be3a117898` in one clean pass, **no ref-PATCH 422 race**. No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-19 | no | **first-try, 0 aborts** — pre-flight active gh user was **`OnePlusNTester`** (`push=false`) → `gh auth switch --user OnePlusNDev`; re-checked immediately pre-run and the switch **held** (no mid-run flip, `GITHUB_TOKEN` unset). Remote **stable at `d1454b937e52`** from preflight through commit time (no sibling advance) → 5 blobs + subtree `ca3c3ccb9100` + top tree `da91d032ea8e` in one clean pass, **no ref-PATCH 422 race**. No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-20 | no | **first-try, 0 aborts** — pre-flight active gh user was **`OnePlusNTester`** (`push=false`) → `gh auth switch --user OnePlusNDev`; re-checked immediately pre-run (`push=true`) and the switch **held** (no mid-run flip, `GITHUB_TOKEN` unset). Remote **stable at `1373e9ff9327`** from preflight through commit time (no sibling advance) → 8 blobs + subtree `09a1a69d6bc3` + top tree `3a62971987e4` in one clean pass, **no ref-PATCH 422 race**. No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-21 | **yes (1)** | **one aborted attempt, clean on the plain re-run** — pre-flight active gh user was **`OnePlusNDev`** (owner, `push=true`) — **no switch needed** (`GITHUB_TOKEN` unset), no mid-run flip. Remote moved `68d5da9921bc` → `e2edf5ebcbf3` (concurrent **demo-dev** backup at 12:00:55Z) between the blob phase and the ref PATCH, so the first commit `e69fffb3c243` was rejected `Update is not a fast forward (HTTP 422)`; the budget-one plain re-run re-read HEAD, re-uploaded the same 4 blobs (idempotent) → subtree `33b26569c7d2` + top tree `2d376ba62d62`, pushed clean. No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-22 | no | **first-try, 0 aborts** — pre-flight active gh user was **`OnePlusNTester`** (`push=false`) → `gh auth switch --user OnePlusNDev`; re-checked immediately pre-run (`push=true`) and the switch **held** (no mid-run flip, `GITHUB_TOKEN` unset). Remote **stable at `533503f33055`** from preflight through commit time (no sibling advance) → 8 blobs + subtree `b8c9d0ab6087` + top tree `5b3fc18597b3` in one clean pass, **no ref-PATCH 422 race**. 7 M / 1 A / 0 D: cron/jobs.json + ARCHIVE.md runtime churn, three 10-21-evening skill-doc edits as benign carry-over lag, plus today's pm-triage-cron work (SKILL.md, pm_fetch.sh, NEW `references/token-extraction-and-404-diagnosis.md` — content-inspected, no token patterns). No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-23 | no | **first-try, 0 aborts** — pre-flight active gh user was **`OnePlusNDev`** (owner, `push=true`/`admin=true`) — **no switch needed** (`GITHUB_TOKEN` unset), no mid-run flip. Remote **stable at `befc945f97e8`** from preflight through commit time (no sibling advance) → 9 blobs + subtree `d5ebd2ce879a` + top tree `8649f37cffcb` in one clean pass, **no ref-PATCH 422 race**. 7 M / 2 A / 0 D: cron/jobs.json + ARCHIVE.md runtime churn, four 10-22-evening/10-23-overnight doc edits as benign carry-over lag (incl. NEW `references/2026-10-22-http2-false-empty.md`), plus today's pm-triage-cron work (SKILL.md, pm_fetch.sh `fetch_best` retry helper, NEW `references/2026-10-23-skill-view-oversize-and-sibling-script-collision.md` — no token patterns). Characterization probe ran clean (no transport error). No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-24 | no | **first-try, 0 aborts** — pre-flight `gh api user` returned **`OnePlusNDev`** but `permissions.push=false`; `gh auth status` showed **`OnePlusNTester`** active, i.e. the keyring race had flipped the account BEFORE the run (first time seen as a push=false on the owner itself, not as a blob 404). `gh auth switch --user OnePlusNDev` → `admin=true/push=true`, re-checked immediately pre-run and the switch **held** (`GITHUB_TOKEN` unset). Remote **stable at `a9b19e4264e8`** from preflight through commit time (no sibling advance) → 11 blobs + subtree `c799586921c1` + top tree `c3bc6d8c7a39` in one clean pass, **no ref-PATCH 422 race**. 10 M / 1 A / 0 D: **`RULES.md` shipped real content over a 0-byte remote blob** (144 lines / 4537 B, restored from demo-tester at 01:02 today), cron/jobs.json + ARCHIVE.md runtime churn, six 10-23-evening doc edits as benign carry-over lag, plus today's pm_fetch.sh `--max-time` + `sz=${sz:-0}` guard and NEW `references/2026-10-24-rules-md-was-empty-and-restored.md` (no token patterns). No network flakiness; the `mkdtemp` payload fix held. |
| 2026-10-25 | n/a — **1 abort, account flip TWICE inside one run** | Pre-flight two-read check caught **`OnePlusNTester`** (`push=false`) → `gh auth switch --user OnePlusNDev` verified `admin=true/push=true` — but the switch was **undone within ~1 min**: the pre-run re-check embedded in the *same shell call* as the script invocation read `OnePlusNTester` again, and attempt 1 died at the FIRST blob with `FATAL uploading demo-pm/cron/jobs.json: gh: Not Found (HTTP 404)`. Second switch + one plain re-run → Steps 1–7 clean (7 blobs, subtree `07c1e7ed67b3`, commit `68e0c832072e`, ref PATCH first try — **no 422 race**). A sibling **demo-dev** commit (`ac39b49dd3f2`, 12:01:13Z) landed between our preflight read and the run; the script re-read HEAD at Step 2 and parented on it → no rebase, no 422. 7 M / 0 A / 0 D (cron/jobs.json 5907→5954 & 124→125; ARCHIVE.md 10-24 reflect row; five 10-24-evening doc edits as benign carry-over lag). Follow-up (2 M / 1 A) then hit one **transient `unexpected EOF`** on the verify/preflight GETs → plain re-run → `Modified: 0, New: 0, Deleted: 0`. |
| 2026-10-26 | no | **first-try, 0 aborts — first clean-auth run after the 10-24 + 10-25 flips** — pre-flight two-read check returned **`OnePlusNDev`** with `permissions.push=true`; **no switch needed** (`GITHUB_TOKEN` unset) and no mid-run flip. Remote printed `7b73541258b5` on the first auth probe, then **`0c87dec6d9c3`** at both preflight and the script's Step 2 (a sibling landed in between) and stayed there through commit time → **no ref-PATCH 422 race**. 6 blobs + subtree `1cfb2813060f` + top tree `8832a7b58b87`, main commit `0b64f584bb42`; **6 M / 0 A / 0 D** (cron/jobs.json counters 5955→6003 & 125→126 ×2; ARCHIVE.md 10-25 reflect row 109,123/5,832 + disambig 167,123/6,440, completed 84→85; four 10-25-evening doc edits as benign carry-over lag). Follow-up **3 M / 1 A** (run note + index bullet + SKILL.md `latest:`; `cron/jobs.json` re-dirtied as expected) → commit `39b13879f0d3`, closing preflight `Modified: 0, New: 0, Deleted: 0`, `post-push-verify.py` ALL CHECKS PASS (demo-pm 265 blobs == local 265). 10-25's `unexpected EOF` transport flakiness did **not** recur. ⚠️ This run shipped the follow-up WITHOUT the practice-notes table row and backfilled it as a post-run doc edit — see the 4-item follow-up checklist in `templates/run-note-template.md`. |
| 2026-10-27 | no | **1 abort — account flip inside one run (blob 404, not a 422)** — pre-flight `gh api user` → **`OnePlusNTester`** (`push=false`) → `gh auth switch --user OnePlusNDev` verified owner; the pre-push re-check read **`OnePlusNTester` again, now `push=true`** (so a login-only check would have passed) and attempt 1 died at the first blob with `FATAL uploading demo-pm/cron/jobs.json: gh: Not Found (HTTP 404)`. Second switch + one plain re-run → Steps 1–7 clean (6 blobs, subtree `37b3b4b09a69`, top tree `a9ab75593864`, commit `614945b19a0d`). Remote moved `39b13879f0d3` → **`7bc7f64e54ba`** between preflight and Step 2 (sibling profile landed); script re-read HEAD and parented on the fresh one → **no ref-PATCH 422 race**. 6 M / 0 A / 0 D (cron/jobs.json 6002→6051 & 126→127 ×2; ARCHIVE.md 10-26 reflect row 158,635/7,214 + disambig 426,048/5,915, completed 85→86, first reflect crashed at LinkExpansion → daemon restart → retry OK; four 10-26-evening doc edits as benign carry-over lag). Follow-up shipped **all FOUR** items (run note + index bullet + SKILL.md `latest:` + this row) → closing preflight `Modified: 0, New: 0, Deleted: 0`, `post-push-verify.py` ALL CHECKS PASS (demo-pm 265 blobs == local 265). No network flakiness. |
| 2026-10-28 | no | **first-try, 0 aborts — clean-auth run, no flip** — pre-flight `gh api user` → **`OnePlusNDev`** with `permissions.push=true`; **no switch needed** (`GITHUB_TOKEN` unset) and no mid-run flip. First preflight read HEAD `7e5dec0b7450`; a sibling **demo-dev** backup (`443b060192ac`, 12:01:40Z) landed immediately after, and both the re-run preflight and the script's Step 2 read `443b060192ac`, stable through commit time → **no ref-PATCH 422 race**. 6 blobs + subtree `af93e4d14913` + top tree `164404d5c7e6`, main commit `b31530b21853`; **6 M / 0 A / 0 D** (cron/jobs.json counters 6051→6098 & 127→128 ×2; ARCHIVE.md 10-27 reflect row 161,682/10,170 + disambig 166,107/6,698, completed 86→87, first single-pass no-crash reflect in days; four 10-27-evening doc edits as benign carry-over lag). The characterize probe was run with no PRE_PUSH_HEAD and its derived `parents[0]` happened to be the true pre-push HEAD **only because the intervening commit was a sibling profile, not our own follow-up** — pass the SHA explicitly when that is not guaranteed. Follow-up shipped **all FOUR** items → closing preflight `Modified: 0, New: 0, Deleted: 0`, `post-push-verify.py` ALL CHECKS PASS (demo-pm 266 blobs == local 266). No network flakiness. |
| 2026-10-29 | no | **1 abort - account flip inside one run (blob 404, not a 422)** - pre-flight `gh api user` -> **`OnePlusNTester`** (`push=false`) -> `gh auth switch --user OnePlusNDev` verified `push=true`; the keyring race re-flipped before the first blob POST (attempt 1: `FATAL uploading demo-pm/channel_directory.json: gh: Not Found (HTTP 404)`, re-check showed `OnePlusNTester` again) -> second switch + the budgeted **single plain re-run** completed Steps 1-7 (idempotent blob SHAs, zero cost). Remote moved `7e20cda6357c` -> `cc044d95c496` between preflight and Step 2 (sibling landed) and the script parented on the fresh HEAD -> **no ref-PATCH 422 race**; 6 blobs + subtree `379feeef7155` + top tree `94536c6e840b`, main commit `0fb65412cd13`; **6 M / 0 A / 0 D** (channel_directory.json `updated_at` only; cron/jobs.json 6099->6147 & 128->129 x2; ARCHIVE.md 10-28 reflect row 99,303/6,200 + disambig 279,166/5,455, completed 87->88, date-conditional wording gate 4th time; three 10-28-evening doc edits as benign carry-over lag). Recurrence data point: this is the **3rd account flip in 5 days** (10-25 twice-in-one-run, 10-27, 10-29) after a clean 10-26/10-28 pair - the check-TWICE rule still needs to fire as late as possible, and a blob-404 must never be read as a missing repo or a rate limit. Follow-up shipped **all FOUR** items -> closing preflight `Modified: 0, New: 0, Deleted: 0`, `post-push-verify.py` ALL CHECKS PASS (demo-pm 267 blobs == local 267). No network flakiness. |
| 2026-10-30 | no | **1 abort - account flip inside one run (blob 404, not a 422)** - pre-flight `gh api user` -> **`OnePlusNTester`** (`push=false`) -> `gh auth switch --user OnePlusNDev` verified `push=true`; the keyring race undid it within ~20 s (the pre-run two-read check in the same shell call read `ACTIVE=OnePlusNTester PUSH=false`) so attempt 1 died at the first blob with `FATAL uploading demo-pm/cron/jobs.json: gh: Not Found (HTTP 404)` -> second switch + the budgeted **single plain re-run** completed Steps 1-7 (idempotent blob SHAs, zero cost). Remote **stable at `e1d028d82175`** from preflight through commit time (no sibling advance) -> **no ref-PATCH 422 race**; 7 blobs + subtree `e3b7f306ed70` + top tree `d7430918360d`, main commit `89e9a7474fc8`; **5 M / 2 A / 0 D** (cron/jobs.json 6147->6195 & 129->130 x2; MEMORY.md header 2026-09-29 -> 2026-10-29 - the 30-day archive fired; ARCHIVE.md 10-29 row: MEMORY.md 30.0d archived to a 1798-char snapshot, USER.md 18.0d not due, daemon fully cold (0 postgres procs) yet healthy in ~10-20 s vs 3.4 min on 10-28, consolidation +461 ms 88->89, reflect 112,261/5,243, wording gate date-conditional 5th time / 9th consecutive, disambig 174,811/5,638; two 10-29-evening doc edits as benign carry-over lag; **2 A = legit new includes, not drift**: the `MEMORY-20261029.snapshot.md` rollover + `index-and-table-append-recipe.md`). Recurrence data point: **4th account flip in 6 days** (10-25 twice, 10-27, 10-29, 10-30) - the check-TWICE rule fired ~20 s before the script and still lost; the real recovery remains "every blob-404 is a flip -> switch -> one plain re-run". No network flakiness. |

**The flip can be lost even when the check sits in the SAME shell call as the script**
(verified 2026-10-25). Sequence: switch → verify `push=true` → (same `terminal` call)
`A=$(gh api user ...)` reads the owner → script starts → first blob POST 404. So
"check immediately before the run" is necessary but **not sufficient**: the only reliable
recovery is the documented one — treat every blob-404 as a flip, `gh auth switch` again,
and plain re-run (blob SHAs idempotent, costs nothing). Do not tighten this into a polling
loop before the script; that just widens the window. Two flips in one run is a new
severity data point, not a new mechanism.

**Re-confirmed 2026-10-30 with the tightest window yet:** switch verified
`push=true`, then the two-read check glued to the script invocation (~20 s later,
same `terminal` call) already printed `ACTIVE=OnePlusNTester PUSH=false`, and attempt 1
died on the first blob 404. That makes **4 flips in 6 days** (10-25 twice, 10-27, 10-29,
10-30) against a clean 10-26/10-28 pair — the flip is bursty, so a clean run says nothing
about the next one. Practical consequence: do NOT spend calls trying to *prevent* the flip
(no switch-verify loops, no adding a third read). Budget the abort instead — every run's
first blob POST may 404, and the cost of recovery is one `gh auth switch` + one plain re-run.

**Maintain this table with one row per run** — the row belongs in the daily follow-up
commit alongside the run note, the index bullet, and the SKILL.md `latest:` pointer.
It is the only continuous record of the 422-race / account-flip recurrence, so a
skipped row makes the pattern look rarer than it is. (09-29 and 09-30 originally
shipped without rows; backfilled 2026-09-30.)

**Step 5 (subtree build) can hang for minutes even when the API is healthy — plain re-run, budget ONE.**
Verified 2026-10-24: the main push was first-try with 11 blobs, but the *follow-up* run's 4
blobs all uploaded fine and then Step 5 never returned — `terminal(timeout=300)` killed it
with the log ending at `=== Step 5: building profile subtree ===` and the remote HEAD still
at the pre-run SHA (so nothing half-committed). A quick `preflight-backup-scan.py` (GET tree)
answered in seconds, proving the API was reachable — the hang was in one of the ~40 small
`POST /git/trees` calls the recursive build fires. The plain re-run completed Step 5 -> commit
-> ref in one pass, blob SHAs identical (idempotent, so the retry costs nothing but the tree
POSTs). Rules: (1) treat a Step-5 hang exactly like the 422 race — ONE plain re-run, no
script edits; (2) a still-unchanged remote HEAD is the proof that nothing was half-committed,
so never "clean up" a commit that was never created; (3) do NOT write `no network flakiness`
in the run note until the follow-up commit has also landed green.

**Same-day repeat runs** (first hit 2026-10-03, which ran at both 10:36 and 20:00 CST): the
daily run-note filename is `YYYYMMDD.md`, so a second run on the same date takes a
`YYYYMMDDb.md` suffix (e.g. `demo-pm-backup-workflow-20261003b.md`) and gets its own table row
(labelled `2026-10-03 (2nd, HH:MM)`) and its own index bullet. This keeps each run's record
atomic and the index `grep -c '<file>.md' == 1` verification clean — appending a second section
to the existing same-date file instead would make that check read 2 and hide a real duplicate
from a future run. The SKILL.md `latest:` pointer stays at the date and is **not** re-bumped.

Note (2026-09-21): the remote ref can advance between the **preflight** and the
**backup script's own Step 2** (the script re-reads it, so this is harmless — it
just means the diff counts you saw in preflight may be recomputed against a newer
HEAD). Run `scripts/post-push-verify.py` *after* the commit, not after the
preflight, for the authoritative numbers.

## Known gh keyring accounts — the flipper set is OPEN

`gh auth status` on this machine lists SIX accounts: **`OnePlusNDev`** (owns
`hermes-config` — the ONLY valid push target), plus `OnePlusNTester`,
`OnePlusNPM`, `zhangtbj`, `JungleAssistant`, `OnePlusNBoss`. The active account
flips among them between (and sometimes during) runs — **two flippers were
brand-new on first appearance** (`zhangtbj` 2026-09-26, `JungleAssistant`
2026-10-07), so treat the set as open-ended and **never** treat a recognized
login as safe-to-skip. A blob POST returning HTTP 404 (not 403) is
the classic symptom of a mid-run flip. (The roster above is a snapshot —
re-derive it with `gh auth status` each run; the *lesson*, not the exact list,
is what's durable.)

### `gh api user` is NOT a sufficient flip detector — read `permissions.push`

Verified 2026-10-24 (first time this signature appeared): `gh api user --jq '.login'`
returned **`OnePlusNDev`** — the repo owner, i.e. exactly the value the check-twice rule
tells you is fine — yet the very next call,
`gh api repos/$OWNER/$REPO --jq '.permissions'`, returned
`{"admin":false,"push":false,"pull":true,...}`. `gh auth status` then showed
**`OnePlusNTester`** as the *active* account. So the keyring race can hand `gh api user`
the owner's identity while the requests are actually authenticated as a read-only sibling.

Why this matters: every previously documented symptom is **late** — a blob `HTTP 404`,
a `403 denied to <X>`, or a ref-PATCH 422. This one is **pre-flight and cheap**. Rules:

- Treat the preflight as **two reads**: `gh api user --jq '.login'` AND
  `gh api repos/$OWNER/$REPO --jq '.permissions.push'`. The owner always has
  `admin=true/push=true`; `push=false` **while `gh api user` names the owner** means a
  sibling account is active → `gh auth switch --user $REPO_OWNER` (after
  `unset GITHUB_TOKEN`) and re-read both.
- Never conclude "no switch needed" from the login alone. On 2026-10-24 the login check
  said owner and the permission check said read-only; the switch was required and then
  held for the whole run.
- A `push=false` preflight is **not** a permissions/repo problem — do not go hunting for
  collaborator access or repo visibility. Switch accounts first, re-read, and only then
  investigate.

### The mirror case: `permissions.push=true` on the WRONG account (2026-10-27)

Verified 2026-10-27 — the exact inverse of the 10-24 signature, and the more dangerous
one because it looks *healthy*: `gh api user --jq '.login'` → **`OnePlusNTester`** while
`gh api repos/$OWNER/$REPO --jq '.permissions.push'` → **`true`**. (That sibling account
now holds write access, so the permission probe — the whole remedy of the 10-24 section —
passes on the wrong identity.) The first blob POST then died
`FATAL uploading demo-pm/cron/jobs.json: gh: Not Found (HTTP 404)`.

So neither read is sufficient alone; the preflight must assert **both**:

```bash
ACTIVE=$(gh api user --jq '.login')
PUSH=$(gh api repos/$REPO_OWNER/hermes-config --jq '.permissions.push')
# proceed ONLY if ACTIVE == $REPO_OWNER  AND  PUSH == true
```

- `ACTIVE != REPO_OWNER` → switch, regardless of `push`. Do not reason "it has push, so
  it's fine" — blob POSTs 404 for a non-owner identity even with write access.
- `ACTIVE == REPO_OWNER && PUSH == false` → switch (the 10-24 signature).
- A login-only check would have waved this run through; a permission-only check would
  have too. Keep both lines in the same shell call as the script invocation, and accept
  that even that can be undone (see the 10-25 section above) — the real recovery remains
  "every blob-404 is a flip → switch → one plain re-run".

## Shared `/tmp` payload namespace — sibling profiles delete our payload files

**Hit 2026-09-23 on attempt 1** (the first run of the day):

```
FATAL uploading demo-pm/skills/devops/hermes-profile-backup/SKILL.md:
open /tmp/gh_payload_1790164860156_67749.json: no such file or directory
```

It died on the **largest** payload (~100 KB `SKILL.md` → base64 ≈ 135 KB) after two small
blobs had uploaded fine. The payload file had been written moments earlier, so this is not
a write bug: something **deleted it mid-run**.

**Root cause (confirmed by grep):** the **demo-tester profile's cron job blanket-cleans
the shared `/tmp/gh_payload_*.json` namespace** — its own skill notes describe reaping
"200+ files from sibling sessions" and its logs contain the literal
`rm -f /tmp/gh_payload_*.json`. Both profiles used the *same* prefix in the *same* `/tmp`,
so a sibling's tidy-up deletes OUR in-flight payloads.

**Fix (applied 2026-09-23 to `scripts/gh-api-standalone-subtree-backup.py`):**

```python
_PAYLOAD_DIR = tempfile.mkdtemp(prefix="hermes-backup-payload-")
...
payload_file = os.path.join(_PAYLOAD_DIR, f"payload_{int(time.time()*1000)}.json")
```

A private per-process directory, with a prefix that does **not** match the
`gh_payload_*` glob → sibling clean-ups cannot see our payloads.

Rules:
- If you ever see `FATAL uploading <path>: open /tmp/gh_payload_...: no such file or
  directory`, do **not** treat it as a permissions/disk problem. Just re-run (blob SHAs
  are idempotent) — but also check that the private-dir fix is still in the script.
- More generally: **never assume `/tmp/<generic-name>` is yours** on this machine. Sibling
  profiles run concurrently and some of them sweep shared globs. Use `mkdtemp`.
- This is a *different* failure mode from the network `i/o timeout` in
  `network-flakiness-and-verify-tooling.md` §1: same "just re-run" remedy, entirely
  different cause. Read the error string before reaching for the network explanation.

## Sibling advance BETWEEN the main and follow-up commit is harmless

The daily flow is **two** commits: the main backup, then the follow-up (run note + index
bullet + SKILL.md `latest:` + practice-notes row). A sibling profile can push inside that
window, so the follow-up's Step 2 legitimately prints a remote HEAD that is **not** our
main commit. Verified 2026-10-19: main `8f60c15f`, follow-up Step 2 saw `1eeface2`
(a `demo-dev`/sibling push landed in between).

This is **not** a lost commit and **not** a ref-PATCH 422 race. The script re-reads the
base top-level tree at Step 2 and only swaps the `demo-pm` entry, so the follow-up is a
normal fast-forward **on top of** the sibling's commit and the sibling's files are
preserved by construction (post-push verify confirmed `demo-dev 5, demo-tester 8,
tester-01 5` intact).

Do **not** re-run the main backup, and do **not** try to "reset" the ref. Verify instead:

1. our main commit still exists — `gh api repos/$OWNER/$REPO/git/commits/<main-sha>`;
2. the follow-up commit's parent == the sibling HEAD the script printed at Step 2;
3. closing preflight reports `Modified: 0, New: 0, Deleted: 0`;
4. `post-push-verify.py` shows `demo-pm` blobs == local file count and siblings intact.

A same-day lesson on the other probe: running `characterize-diff-vs-prev-head.py` twice
(once for the tail, once for the head) still happens even though
`run-note-diff-characterization.md` documents the rule — a pitfall buried in a reference
file does not get read mid-run. SKILL.md now carries the "run ONCE → file → slice" rule
inline at the probe pointer for that reason.

## Invoking the Method B script (cron, macOS)

Do **not** prefix the invocation with the shell's `timeout` command — macOS ships
no GNU `timeout` binary, so `timeout 570 python3 gh-api-standalone-subtree-backup.py`
dies instantly with `timeout: command not found` (hit 2026-09-22). Use the
`terminal` tool's own timeout parameter instead (`terminal(..., timeout=600)`), or
`gtimeout` if coreutils is installed. Plain invocation pattern:

```bash
cd /tmp && REPO_OWNER=OnePlusNDev python3 \
  ~/.hermes/profiles/demo-pm/skills/devops/hermes-profile-backup/scripts/gh-api-standalone-subtree-backup.py
```

Running it from `/tmp` with the script path under `~/.hermes` is fine in cron mode
(no tirith hit); a clean 6-blob + subtree + commit pass finishes well inside 600 s.
Pipe through `| tail -70` — the script's useful output is the Step 1–7 log.

## Characterizing the M set for the run note

After the push, classify each `M` as routine runtime churn vs benign carry-over
doc lag with `scripts/characterize-diff-vs-prev-head.py` — pass the **pre-push**
remote HEAD (the SHA the backup script logged at Step 2, or
`--commit=<your backup commit sha>`, which derives `parents[0]`).

Diffing against the CURRENT remote is the trap: right after a push the current
remote tree equals local, so everything reads `IDENTICAL` and you learn nothing.
Recipe + reading guide + worked example:
`references/run-note-diff-characterization.md`.

**Always pass the SHA — never run it with no argument.** The no-arg default derives
`parents[0]` of the *current* main, and because every day's run ends with a follow-up
commit, that parent is yesterday's **main** commit, not yesterday's remote HEAD. Result
(2026-10-27): the probe reported `MODIFIED 8 / ADDED 1` while preflight against remote
HEAD reported `6 M / 0 A / 0 D` — the extra three were yesterday's follow-up contents
(`SKILL.md` `latest:`, `dated-runs-index.md` bullet, and the previous day's run note
reading as ADDED). Reading that as "exclude drift" or re-running the probe wastes a
cycle; the signature to recognize is **exactly +1 A (a `demo-pm-backup-workflow-YYYYMMDD.md`)
and +2 M (SKILL.md + dated-runs-index.md) over the preflight count**.

Prefer `--commit=<your main backup commit sha>` (its `parents[0]` *is* the true pre-push
HEAD), or pass the SHA the script logged at Step 2. Then state the authoritative diff in
the run note from the **preflight** numbers and treat the characterize output as the
per-file explanation only.
