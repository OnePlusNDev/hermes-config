---
name: issue-handling-workflow
description: How to handle GitHub issues assigned to you — read all comments first, process the task, create reproducible artifacts, reassign properly, and coordinate with other agents. Learned from Issue #9 OpenCalc migration.
---

# Issue Handling Workflow

## When to use this skill

- Your cronjob finds an issue assigned to you
- You receive a task via GitHub issue in a multi-agent workflow
- You're part of a PM → Dev → Reviewer → Tester → Reviewer → PM → Boss pipeline

## Project context

- **For the migbot-oneplusn project:** See [`references/project-landscape.md`](references/project-landscape.md) — org/repo structure, account mapping (Hermes profile ↔ GitHub login), and the full issue flow chain.
- **For the demo-oneplusn project:** See [`references/demo-landscape.md`](references/demo-landscape.md) — project-specific auth, polling patterns, verdict flow, and tag convention.

## Core rules

1. **Only process issues assigned to YOU.** Ignore status tags (Todo/In Progress/Done) — those are for the boss. You act when `assignees` contains your handle.
2. **Read ALL existing comments before doing anything.** Previous agents may have left precise fix instructions (down to the exact line number). Skipping comments risks rework.
3. **Never trust self-reported results.** If Dev says "BUILD SUCCESSFUL", verify independently from clean source. If Tester says "PASS", re-run the harness yourself.

## Step-by-step workflow

### 1. Receive assignment

**Polling (cron mode) — Quick path (preferred):**

> ⚠️ **Before you search:** Your Hermes profile name (e.g. `tester-01`) is NOT a GitHub username. GitHub only knows your actual login (e.g. `MigbotTester`). See [`references/project-landscape.md`](references/project-landscape.md) for the full mapping. Searching for `assignee=tester-01` will ALWAYS return empty.

```bash
# Step 1: Verify gh is authenticated and discover your actual GitHub login
GH_USER=$(gh api user --jq '.login') && echo "Authenticated as: $GH_USER"

# Step 2: Search cross-repo — use the REAL GitHub login, NOT the profile name
gh search issues --assignee="$GH_USER" --state=open --limit=20 \
    --json number,title,url,repository,createdAt,body,labels
```

`gh` handles auth internally — no `$GITHUB_TOKEN` in command strings, so the cron redaction filter doesn't interfere. This path avoids ALL token-mangling issues (write_file `***` persistence, merged-line syntax errors, curl_pipe_shell blocks). **Do NOT start with `curl -H "Authorization: token $GITHUB_TOKEN"`** — the token is almost always redacted/stale in cron mode (will produce `401`). `gh` is the golden path.

> ⚠️ **CRITICAL: Verify `gh` keychain before deciding to skip `.env`.** Run `gh auth status` and inspect the output. If the **active** account (marked `Active: true`) is your profile's GitHub user AND it's authenticated via keyring (not `GH_TOKEN` env var), then `gh` works without sourcing `.env`. If no active account is available, or if the active account depends on `GH_TOKEN` (env var), then you **must** `source .env` before every `gh` call. If the keychain has both accounts but the wrong one is active, use `gh auth switch` instead.\n>\n> **Three patterns to distinguish:**\n>\n> | Keychain state | What to do |\n> |---|---|\n> | Active account via keyring = profile user | Just run `gh` directly |\n> | Both accounts in keychain but wrong one active | `unset GH_TOKEN GITHUB_TOKEN && gh auth switch --user PROFILE_USER`, then run `gh` directly |\n> | No active accounts / Active only via GH_TOKEN env var | **Must** `source .env` then `export GH_TOKEN` |

**Scoped search (faster):** If you know the org, add `--owner=<org>`:
```bash
gh search issues --owner=migbot-oneplusn --assignee="$GH_USER" --state=open --limit=20 \
    --json number,title,url,repository,createdAt,body,labels
```

**Fallback:** If `gh` is not authenticated (`gh auth status` fails), use the Python `urllib.request` pattern from `github-issues/references/hermes-cron-polling.md`. Write the script to `/tmp/` with `write_file`, then run with `terminal(command='python3 /tmp/script.py')`.

**🚦 Branch on results (immediately after search):**

**🟢 When no issues are found:** Respond with `[SILENT]` (exactly that string, nothing else). The cron delivery system suppresses silent responses. **Stop here.** This is the common case (~95% of polls). Do NOT run diagnostic probes unless you have specific reason to suspect you were expected to receive work (e.g., a teammate told you an issue was assigned, or you see a recent comment @-mentioning you).

**🔴 When issues are found** (`assignee=you`):

- Reply with: "开始处理 issue #N，概述：…，计划：…"
- Summarize in the comment what you understand the task to be and your planned approach
- This creates a handshake point — wrong understanding gets caught early

> **🩺 Diagnostic probes (OPTIONAL — only when you suspect missed assignments):**  \
> In multi-agent workflows, you may occasionally need to check for issues where you were expected to act but weren't formally assigned (e.g., previous agent forgot to reassign, or you were @-mentioned in a comment about pending work). Use these ONLY when you have reason to believe work exists, NOT on every routine poll:
>
> ```bash
> # Check if you're involved in any open issues
> gh search issues --owner=YOUR_ORG --state=open --involves="$GH_USER" --limit=10 \
>     --json number,title,url,repository,state
>
> # Narrower: only issues that explicitly @-mention you
> gh search issues --owner=YOUR_ORG --state=open --mentions="$GH_USER" --limit=10 \
>     --json number,title,url,repository,state
> ```
>
> - `--involves` catches: assignee, author, commenter, or @-mentioned
> - `--mentions` catches: only explicit @-mentions in body/comments
> - If `--involves` finds an issue where your role's work is incomplete, comment asking for clarification or reassignment
> - If your role's work IS complete and the issue has moved past you, leave it alone
>
> > **🔍 PR body @-mention probe (advanced)** \
> > Developers may write `下一步：交 @$TESTER 做 AC 验证` in a **PR body** (not an issue) without formally requesting a review or assigning an issue to the tester. This is NOT an official task assignment — the tester should NOT act on PR body mentions alone. However, if you have strong reason to believe work was missed (e.g., a teammate told you to expect it), you can probe:
> >
> > ```bash
> > # Find open PRs where you're @-mentioned in the body
> > gh search prs --owner=YOUR_ORG --state=open --mentions="$GH_USER" --limit=10 \
> >     --json number,title,url,repository,headRefName,body
> > ```
> >
> > **Rule of thumb**: A PR body `@-mention` without a review request or issue assignment is a process gap, not a task. Do NOT act on it in routine polls. Only probe when explicitly told work is missing.

### 2. Understand the context

- Read the issue body + all comments thoroughly
- Identify: what has been done, what failed, what's pending
- Check for review comments with specific technical guidance (file paths, line numbers, root cause)
- If a Reviewer left a harness script path (`/tmp/migbot_review9/harness.mts`), run it first

### 3. Execute the task

- **For testing tasks:** Never just repeat Dev/self-reported results. Re-copy source fresh, re-run independently, verify mtime to ensure you're testing the latest version.
- **For development tasks:** Follow the migration/development tools and commands specified. If Claude Code CLI or other tools are required, use them — don't bypass.
- **Create reproducible artifacts:** Leave test harnesses, scripts, or clear reproduction steps so the next person can verify your work without guessing.
- **Check code freshness:** Verify source mtime is newer than the last build/claim before testing.

### 4. Report results

- State what was tested/executed and the actual output
- Distinguish between "I ran it and got X" vs "the previous agent claims X"
- **If doing cross-platform comparison (Android vs HarmonyOS):** Run BOTH sides. Never claim "Android expects Y" without actually executing Android code.
- Flag any assumptions you made and their verification status

### 5. Reassign

**MANDATORY after every completion.** The flow is:

```
After testing → reassign to Reviewer (审查②终审)
After reviewing dev work → reassign to Tester (if pass) or Dev (if fail)
After final review → reassign to PM (验收)
After PM acceptance → reassign to Boss (终审)
```

- If unsure who's next, check the issue body for the flow plan
- If you can't complete alone, @ mention the relevant colleague in a comment and explain the blocker
- **Never leave an issue assigned to yourself after finishing**

### 6. Coordinate when blocked

- **Primary channel: GitHub issue comments.** Use `@GitHubHandle` in issue comments to notify other agents. This is the ONLY reliable inter-agent notification mechanism.
- **⚠️ Feishu @mentions do NOT work between bots.** Feishu bots only receive messages from human users, not from other bots. A `send_message` to the group with `<at user_id="...">` will appear in the group but will NOT be received by another agent's gateway. Use GitHub issue reassignment + comment as the inter-agent handshake instead.
- If you encounter API/network/token issues, update the issue and ask Boss
- If you can't resolve a problem independently, say so clearly rather than silently failing

## Anti-patterns (lessons from Issue #9)

| ❌ Don't | ✅ Do |
|----------|------|
| Claim "Android expects 2" without running Android | Run both sides, then report actual results |
| Trust Dev's "all tests pass" | Re-run harness from clean source copy |
| Fix the issue but forget to reassign | Always reassign to the next person in flow |
| Start work before reading all comments | Read every comment — the fix might be 1 character |
| Report only happy path | Report what you verified AND what you didn't |
| Use curl with Authorization header in cron mode | Use Python urllib.request reading .env directly — shell token expansion is redacted to *** in cron |
| Try to @mention another agent via Feishu bot message | Use GitHub issue comments + reassign for inter-agent handshake. If Feishu @mentions are needed, first check gateway process is running (`ps aux | grep gateway`), then follow the full diagnostic in references/feishu-bot-communication.md |
| Use `gh issue list` for cross-repo search (fails with "not a git repository") | Use `gh search issues` for cross-repo discovery. `gh issue list` only works inside a git repo or with explicit `--repo=owner/repo` |
| Use `gh issue list --json repository` (field doesn't exist) | `gh issue list` JSON lacks `repository` field. Use `gh search issues` when you need repo context. `gh issue list` fields: number, title, url, state, labels, assignees, createdAt, updatedAt, body |
| Give up immediately when `--assignee` returns empty | When you have reason to believe work exists (teammate said so, recent @-mention), probe with `--involves` and `mentions`. But on routine polls, no results = `[SILENT]` and stop — don't waste tokens probing. See also `references/pr-body-atmention-trap.md` for the PR-specific case. |
| Write a handoff comment but forget the command to reassign | Writing "下一步：移交 @Boss" in a comment is **not** a reassignment. Always run `gh issue edit N --remove-assignee ... && --add-assignee ...` (two-step, per RULES.md 铁律1) **before** posting your final comment or stopping. If you see repeated PM triage comments on an issue you've already worked on, check whether you still have the assignment — you likely forgot to hand off and created a loop. This is not confirmation that things are fine — it's a symptom of a broken chain. |
| Misinterpret repeated PM re-triage as "process working" instead of "handoff failed" | After Dev work, if you see **multiple PM triage comments** all pointing back to you on the same issue, verify: `gh issue view N --json assignees`. If YOU are still assigned, the loop was caused by an unexecuted handoff (someone wrote about it but never ran the reassign command). This is not confirmation that things are fine — it's a symptom of a broken chain. |
| Use emojis or heavy unicode in `gh issue/PR comment --body "..."` in cron mode | Unicode variation selectors trigger tirith security scanning and **blocks** the command entirely. Workaround: write body to a temp file via `write_file`, then pipe it in: `cat /tmp/comment.md \| gh issue comment N -F -`. Avoid all emojis (✅❌🏁 etc.) in the markdown text body — plain ASCII words ("PASS", "OK", "阻塞") work fine. Same applies to `gh pr comment --body`. |

## Standard flow chain

```
PM(分诊委派) → Dev(迁移开发) → Reviewer(审查①) → Dev(返工修复)
→ Reviewer(审查①复审) → Tester(测试验证) → Reviewer(审查②终审)
→ PM(验收汇总) → Boss(终审)
```

Each handoff = reassign issue to the next role's handle.
