# Demo Project Landscape — demo-oneplusn

## GitHub Organization & Repos

- **Org:** `demo-oneplusn`
- **Primary issue-tracking repo:** `demo-workflow` (issues enabled)
- **Purpose:** End-to-end issue triage pipeline proving PM→Dev→Tester→Boss handoff

## Hermes Profile ↔ GitHub Account Mapping

| Hermes Profile | GitHub Login | Role in Pipeline |
|---|---|---|
| demo-pm | OnePlusNPM | PM (分诊委派 / 验收汇总) |
| — | OnePlusNDev | Dev (开发实现) |
| — | OnePlusNTester | Tester (测试验证) |
| — | OnePlusNBoss | Boss (终审 / 未知类型兜底) |

> **Critical:** The cron prompt may reference the Hermes profile name (e.g. `demo-pm`), but GitHub only knows `OnePlusNPM` (the GitHub login). Always verify your actual login with `gh api user --jq '.login'` or by checking which username appears in the issue's `assignees` list.

## Issue Triage Rules (PM Role)

The PM scans `demo-workflow` issues assigned to `OnePlusNPM` and routes them by label:

| Label Pattern | Routed To | Rule |
|---|---|---|
| `type:feature` or `type:bug` + keywords: 开发/实现/新增/修复 | `OnePlusNDev` | Feature → Dev |
| `type:verification` + keywords: 测试/验证/审查 | `OnePlusNTester` | Verification → Tester |
| `type:research`, `type:docs`, or any ambiguous/unlabeled issue | `OnePlusNBoss` | Unknown → Boss (with explanation) |

### Step-by-step PM Triage

1. Query repo `demo-oneplusn/demo-workflow` for open issues assigned to `OnePlusNPM`
2. For each issue, read its labels and title/body:
   - Identify `type:*` label as the primary classifier
   - If no label, fall back to title/body keywords
3. Write a **Chinese** comment on the issue (code blocks and identifiers in English) explaining:
   - Identified type
   - Size estimate (small/medium/large based on body length and scope keywords)
   - Who it's being reassigned to and why
4. Change assignee in **two steps** — remove self first, then add new assignee:
   ```bash
   # Step 1: Remove self (OnePlusNPM)
   curl -s -X DELETE \
     -H "Authorization: Bearer $TOKEN" \
     "https://api.github.com/repos/demo-oneplusn/demo-workflow/issues/$NUMBER/assignees" \
     -d '{"assignees":["OnePlusNPM"]}'

   # Step 2: Add target
   curl -s -X POST \
     -H "Authorization: Bearer $TOKEN" \
     "https://api.github.com/repos/demo-oneplusn/demo-workflow/issues/$NUMBER/assignees" \
     -d '{"assignees":["TARGET_USER"]}'
   ```
5. If no issues are assigned to PM → output `[SILENT]` and exit (no notification sent)

### Size Estimation Heuristics

| Signal | Size |
|---|---|
| Issue body < 3 lines, single well-defined scope | Small |
| Issue body 3–10 lines, multiple scenarios or files mentioned | Medium |
| Issue body > 10 lines, cross-component changes, multiple acceptance criteria | Large |

## Auth Notes for demo-pm

- Token is stored in `~/.hermes/profiles/demo-pm/.env` under `GITHUB_TOKEN=ghp_...`
- `gh` CLI availability: **not assumed** for this profile's cron context
- Preferred cron-safe approach: Python `urllib.request` (read `.env` directly) + `curl -o` (save to file, no pipe-to-python)
- Token extraction via `grep "^GITHUB_TOKEN=*** \`cat ... | cut -d'=' -f2-\`` works in terminal but values are display-masked — use Python's file-read approach for reliability

## Known Quirks

- **Two-step assignment is mandatory:** The GitHub Issues API does not support bulk-replace of assignees. You must `DELETE /assignees` for the old user, then `POST /assignees` for the new one. The final count should be exactly 1 assignee.
- **Comment before reassign:** Write the triage comment BEFORE changing assignee — if the API call fails, the comment still persists as a record.
- **Empty RULES.md:** The demo-pm profile's `RULES.md` (~/.hermes/profiles/demo-pm/RULES.md) is intentionally empty (0 bytes). The coding SOUL.md and the cron job prompt itself serve as the governing rules.
- **Unassigned issues are not the PM's responsibility:** Issues with no assignee at all are skipped — the PM only acts on issues formally assigned to `OnePlusNPM`. Issues #6–#7 in the demo repo were intentionally left unassigned as part of the test fixture.
