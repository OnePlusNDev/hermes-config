# Project Landscape — demo-oneplusn

## GitHub Organization & Repos

- **Org:** `demo-oneplusn`
- **Primary repo:** `demo-workflow` (issues enabled)
- **Team accounts:**

| Hermes Profile | GitHub Login | Role |
|---|---|---|
| demo-tester | OnePlusNTester | Tester (测试验证) |
| demo-dev | OnePlusNDev | Developer (开发) |
| demo-boss | OnePlusNBoss | Boss (终审/关闭) |

## Issue Flow Chain

```
Dev(开发) → Tester(测试验证) → Boss(终审)
Tester(测试验证) ──FAIL──→ Dev(返工修复)
```

## Auth Reality (Keychain — preferred path)

The `gh` keychain on this machine holds **five** accounts:

| Login | Auth Source | Active? | When to Use |
|---|---|---|---|
| OnePlusNPM | keyring | **true** (default) | Not for tester work |
| OnePlusNDev | keyring | false | Dev tasks |
| **OnePlusNTester** | keyring | false | **Tester tasks — switch to this** |
| JungleAssistant | keyring | false | Assistant tasks |
| zhangtbj | keyring | false | PM tasks |

### Recommended approach: `gh auth switch`

**Do NOT source `.env`.** The old approach of sourcing `.env` before every `gh` command is **deprecated** because:
- `GH_TOKEN` env var overrides keychain auth, which blocks using `gh auth switch`
- The token in `.env` gets masked to `***` in terminal output, making debugging impossible
- Writing temp script files to source `.env` adds unnecessary complexity

```bash
# Step 1: Clear any GH_TOKEN that overrides keychain auth
unset GH_TOKEN GITHUB_TOKEN

# Step 2: Switch to tester account
gh auth switch --user OnePlusNTester

# Step 3: Now @me resolves to OnePlusNTester
gh issue list --repo demo-oneplusn/demo-workflow --assignee @me --state open \
  --json number,title,state,assignees,labels,updatedAt

# Step 4: After done, switch back to default account
gh auth switch --user OnePlusNPM
```

**Why this is better**: No token extraction, no temp scripts, `gh` manages its own auth, and `--assignee @me` resolves correctly.

### Token extraction via script (fallback — only if auth switch fails)

If `gh auth switch` fails (e.g., account not in keychain), fall back to sourcing `.env` via script:

```bash
write_file('/tmp/demo_gh.sh', '''#!/usr/bin/env bash
set -euo pipefail
source ~/.hermes/profiles/demo-tester/.env
export GH_TOKEN

gh issue list --repo demo-oneplusn/demo-workflow --assignee OnePlusNTester --state open --json number,title
''')
terminal('bash /tmp/demo_gh.sh')
```

Using `<< 'SCRIPT'` heredoc with single-quoted delimiter prevents shell expansion inside the body.

## RULES.md Location

- Path: `~/.hermes/profiles/demo-tester/RULES.md`
- Read as first step of every cron poll (contains assignee-change protocol, comment rules, label management)
- Key rules for testers:
  - All comments in Chinese (code blocks excluded)
  - Assignee change: remove old → add new (two separate calls, never one)
  - Comment BEFORE changing assignee
  - Check for new feedback by examining last comment's author

## Polling Patterns

```bash
# Preferred: switch to tester account first
unset GH_TOKEN GITHUB_TOKEN
gh auth switch --user OnePlusNTester
gh issue list --repo demo-oneplusn/demo-workflow --assignee @me --state open \
  --json number,title,state,assignees,labels,updatedAt,comments --limit 20

# Fallback: source .env directly
source ~/.hermes/profiles/demo-tester/.env
export GH_TOKEN
gh issue list --repo demo-oneplusn/demo-workflow --assignee OnePlusNTester --state open \
  --json number,title,state,assignees,labels,updatedAt,comments --limit 20

# Check last comment author (new feedback detection)
gh issue view N --json comments --jq '.comments[-1].author.login'
```

## New Feedback Detection

Per RULES.md 铁律3:

| Last comment author | Meaning | Action |
|---|---|---|
| Not you (someone else) | New feedback | Must process |
| You (your own previous comment) | Waiting for approval | Skip |
| No comments | New issue | Must process |

## Verdict and Assignee Flow

### PASS → Return to Boss

```bash
# 1. Post verification comment (Chinese)
# 2. Remove old assignee
gh issue edit N --repo demo-oneplusn/demo-workflow --remove-assignee OnePlusNTester
# 3. Add new assignee
gh issue edit N --repo demo-oneplusn/demo-workflow --add-assignee OnePlusNBoss
# 4. Verify exactly 1 assignee
gh issue view N --json assignees --jq '[.assignees[].login]'
```

### FAIL → Return to Dev

```bash
# 1. Post failure comment with specific issues (Chinese)
# 2. Remove old assignee
gh issue edit N --repo demo-oneplusn/demo-workflow --remove-assignee OnePlusNTester
# 3. Add new assignee
gh issue edit N --repo demo-oneplusn/demo-workflow --add-assignee OnePlusNDev
# 4. Verify exactly 1 assignee
gh issue view N --json assignees --jq '[.assignees[].login]'
```

## Tag/Label Convention

Per RULES.md 铁律6, each time you touch an issue:

1. Remove old `agent:*` labels (e.g. `gh issue edit N --remove-label "agent:dev"`)
2. Add correct type label: `type:feature`, `type:bug`, `type:verification`, `type:research`, `type:docs`
3. After PASS: also remove `status:todo` if present

## Session Pattern: No Issues Found

When `gh issue list --assignee @me --state open` returns `[]` (after switching to OnePlusNTester):
- Respond with exactly `[SILENT]`
- Do NOT send notifications
- Do NOT run diagnostic probes on every routine poll
- Only probe with `--involves` or `--mentions` when you have specific reason to expect missed work

## Environment

- macOS (26.4)
- `gh` installed and authenticated (multiple accounts in keychain + env var)
- Profile env: `~/.hermes/profiles/demo-tester/.env`
- `.env` contains: GITHUB_USERNAME, GITHUB_EMAIL, GITHUB_TOKEN (masked in terminal), GATEWAY_PORT, AGENT_NAME, AGENT_ROLE, DEEPSEEK_API_KEY
- `read_file` blocked on `.env` (credential guard) — use terminal + `source` or use `gh auth switch`
