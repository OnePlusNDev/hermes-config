# PR Body @-mention Trap

## The Problem

A developer writes in a PR body:

```
### 下一步：交 @OnePlusNTester 做 AC 验证
```

This looks like a task assignment but is **not** one. The tester:

- Is NOT listed as a reviewer on the PR (`gh pr view N --json reviewRequests`)
- Is NOT assigned to any open issue
- Has no formal work request

Acting on PR body text alone is wrong — it's a process gap, not a task.

## Real Example (2026-06-29 session)

- PR #6 (demo-oneplusn/demo-workflow): body included `交 @OnePlusNTester 做 AC 验证`
- No review request, no issue assignment
- Correct behavior: ignore during routine polls, only probe if explicitly told work is missing

## What to Do

| Scenario | Action |
|----------|--------|
| Routine cron poll, no assigned issues | `[SILENT]` — ignore PR body mentions |
| Teammate told you work was missed | Probe with `gh search prs --mentions="$GH_USER"` |
| You find the PR during unrelated work | Ignore — process gap is the developer's/PM's problem, not yours |

## Root Cause

The workflow has a missing step: after Dev pushes a PR and mentions the tester, PM should create a verification issue and assign it to the tester. If PM doesn't, the tester never learns about it. This is not the tester's fault or responsibility to fix.
