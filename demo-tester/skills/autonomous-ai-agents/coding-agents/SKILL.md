---
name: coding-agents
description: "Delegate to external autonomous coding agents via CLI (Claude Code, OpenAI Codex, OpenCode)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]

metadata:
  hermes:
    tags: [Coding-Agent, Claude, Codex, OpenCode, Delegation, PR-Review, Feature-Build, Refactoring]
    related_skills: [hermes-agent, codebase-inspection]
---

# Coding Agents — CLI Orchestration Guide

Delegate coding tasks to external autonomous coding agent CLIs. This covers three agents in the same family — choose based on availability and user preference.

| Agent | Provider | Install | Key flag | Auth |
|-------|----------|---------|----------|------|
| **Claude Code** | Anthropic | `npm i -g @anthropic-ai/claude-code` | `-p` (print) or tmux interactive | API key or browser OAuth |
| **Codex** | OpenAI | `npm i -g @openai/codex` | `exec "prompt"` | API key or device-code OAuth |
| **OpenCode** | Provider-agnostic | `npm i -g opencode-ai` | `run "prompt"` or tmux interactive | OPENROUTER_API_KEY etc. |

## When to use

- User asks for features, bug fixes, PR reviews, refactoring
- User says "build this", "fix that", "review PR #N", "simplify"
- Parallel task execution across multiple repos/features

## Choosing an agent

No strong preference between them:
1. If the user names one → use that one
2. If Claude Code is installed → prefer it (most feature-rich)
3. Otherwise check for Codex → then OpenCode
4. For provider-specific needs (e.g., "use OpenRouter"), default to OpenCode

---

## Agent A: Claude Code (anthropic/claude-code)

Best for: complex reasoning tasks, PR reviews with inline comments, multi-step refactoring, MCP servers.

### Prerequisites

```bash
npm install -g @anthropic-ai/claude-code
# Then: claude auth login (browser OAuth), or set ANTHROPIC_API_KEY
claude --version  # v2.x+ required
```

### Two Modes

#### Mode 1: Print Mode (PREFERRED — one-shot, non-interactive)

Cleanest integration. Returns structured output, no dialog handling needed.

```bash
terminal(command="claude -p 'Add error handling to all API calls' --allowedTools 'Read,Edit' --max-turns 10", workdir="/path/to/project", timeout=120)
```

**Flags you need:**
| Flag | Purpose |
|------|---------|
| `-p` | One-shot mode (default; explicit is best practice) |
| `--allowedTools 'Read,Edit,Bash'` | Whitelist tools (security) |
| `--max-turns 10` | Prevent runaway loops |
| `--output-format json` | Structured JSON result |
| `--json-schema '{...}'` | Force structured extraction |
| `--bare` | Skip hooks/MCP for CI (fastest startup, needs API key) |

**Structured output parsing:**
```bash
# Results include session_id, num_turns, total_cost_usd, stop_reason
claude -p 'Analyze auth.py' --output-format json --max-turns 5
# → {"type":"result","subtype":"success","num_turns":3,"total_cost_usd":0.078,...}
```

**Piped input (analyze file contents):**
```bash
cat src/auth.py | claude -p 'Review for security issues' --max-turns 5
git diff main...feature-branch | claude -p 'Summarize these changes' --max-turns 3
```

#### Mode 2: Interactive PTY (tmux) — multi-turn sessions

For iterative work requiring conversation back-and-forth. **Always use tmux**, not raw `pty=true`.

```bash
# Create session
terminal(command="tmux new-session -d -s claude-work -x 140 -y 40")
# Launch and handle dialogs
terminal(command="tmux send-keys -t claude-work 'cd /path/to/project && claude' Enter")
# Handle trust dialog (Enter = accept default)
terminal(command="sleep 3 && tmux send-keys -t claude-work Enter")
# With --dangerously-skip-permissions, also handle permissions dialog (Down then Enter!)
# Send task
terminal(command="sleep 5 && tmux send-keys -t claude-work 'Refactor the auth module to use JWT' Enter")
# Monitor
terminal(command="sleep 10 && tmux capture-pane -t claude-work -p -S -30")
```

**Critical dialog handling:** `--dangerously-skip-permissions` defaults to "No, exit" — you MUST send Down then Enter. Print mode (`-p`) skips this entirely.

### PR Review Pattern

```bash
# Quick review from diff
terminal(command="cd ~/repo && git diff main...feature | claude -p 'Review diff for bugs and security issues' --max-turns 3", timeout=60)

# From GitHub PR number
terminal(command="claude -p 'Review this PR thoroughly' --from-pr 42 --max-turns 10", workdir="/path/to/repo", timeout=120)
```

### Parallel Claude Instances

```bash
for task in "fix auth" "add logging" "update tests"; do
  ts="task-$RANDOM"
  tmux new-session -d -s $ts
  tmux send-keys -t $ts "cd ~/project && claude -p '$task' --allowedTools 'Read,Edit,Bash' --max-turns 10" Enter
done
```

### Cost control

- **`--max-turns`** — always set; start with 5-10
- **`--effort low`** — for simple tasks (faster, cheaper)
- **Use `--allowedTools`** — restrict to what's needed
- **Use `/compact`** in interactive mode when context grows past 70%

### Pitfalls

1. **Interactive requires tmux** — Claude Code is TUI; raw PTY works but you lose capture-pane monitoring
2. **Permissions dialog defaults to "No, exit"** with `--dangerously-skip-permissions` — send Down then Enter
3. **Session resumption needs same working directory** as the original session
4. **Trust dialog only appears once per directory** — not on revisits
5. **`--max-turns` is print-mode only** — ignored in interactive sessions

---

## Agent B: OpenAI Codex (openai/codex)

Best for: batch operations, fast feature implementation, sandboxed work.

### Prerequisites

```bash
npm install -g @openai/codex
# Auth: OPENAI_API_KEY or Codex device-code OAuth
```

### One-Shot Tasks

**Requires a git repository.** Will refuse to run outside one.

```bash
# Basic one-shot (PTY required — Codex is interactive)
terminal(command="codex exec 'Add dark mode toggle' --full-auto", workdir="~/project", pty=true)

# Scratch work (Codex needs a git repo)
terminal(command="cd $(mktemp -d) && git init && codex exec 'Build a snake game'", pty=true)

# PR review in temp clone
REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && git fetch origin pull/42/head:pr-42 && git checkout pr-42 && codex exec 'Review changes vs main' --full-auto, pty=true)
```

**Flags:**
| Flag | Purpose |
|------|---------|
| `exec "prompt"` | One-shot execution |
| `--full-auto` | Auto-approve file changes within sandbox |
| `--yolo` | No sandbox (fastest, most dangerous) |
| `--sandbox danger-full-access` | Disable bubblewrap when it fails |

### Background Mode

```bash
terminal(command="codex exec --full-auto 'Refactor auth module'", workdir="~/project", background=true, pty=true, notify_on_complete=true)
# Returns session_id; monitor with process(action="poll") / process(action="log")
```

### Parallel Worktrees

```bash
git worktree add -b fix/issue-78 /tmp/issue-78 main
git worktree add -b fix/issue-99 /tmp/issue-99 main
codex exec 'Fix issue #78' --yolo, workdir="/tmp/issue-78", pty=true &
codex exec 'Add tests for #99' --yolo, workdir="/tmp/issue-99", pty=true &
```

### Hermes Gateway caveat

In gateway/sandboxed contexts, bubblewrap namespace errors (`setting up uid map: Permission denied`) may block Codex sandboxing. Use `--sandbox danger-full-access` and rely on explicit workdir + git diff review instead.

### Pitfalls

1. **Always use `pty=true`** — Codex hangs without a PTY
2. **Git repo required** — wrap in `mktemp -d && git init` for scratch
3. **Background without notify_on_complete runs silently** — always set it
4. **Don't kill slow sessions** — check progress first with poll

---

## Agent C: OpenCode (opencode.ai)

Best for: provider-agnostic work, TUI exploration, session management.

### Prerequisites

```bash
npm i -g opencode-ai@latest
# Auth: openencode auth list should show at least one provider
```

### One-Shot Tasks

**Does NOT need pty.**

```bash
terminal(command="opencode run 'Add retry logic to API calls'", workdir="~/project")

# Attach context files
terminal(command="opencode run 'Review config' -f config.yaml -f .env.example", workdir="~/project")

# Force model, show thinking
terminal(command="opencode run 'Refactor auth module' --model openrouter/anthropic/claude-sonnet-4 --thinking", workdir="~/project")
```

### Interactive TUI (Background)

**TTY required.**

```bash
terminal(command="opencode", workdir="~/project", background=true, pty=true)
# Returns session_id; submit via process(action="submit")
process(action="submit", session_id="<id>", data="Implement OAuth refresh flow")

# Exit: Ctrl+C ONLY. /exit is NOT valid — opens agent selector.
process(action="write", session_id="<id>", data="\x03")
```

### PR Review

```bash
terminal(command="opencode pr 42", workdir="~/project", pty=true)
```

### Session Management

```bash
opencode session list          # List past sessions
opencode stats                 # Token usage and cost
opencode -c                    # Continue last session
opencode -s ses_abc123         # Specific session
```

### Pitfalls

1. **`opencode run` does NOT need pty** — only interactive TUI does
2. **/exit is NOT valid** — use Ctrl+C to exit
3. **PATH mismatch** can select wrong binary; pin explicitly if needed: `$HOME/.opencode/bin/opencode`

---

## Common Patterns Across All Three Agents

### 1. Verification Smoke Test

Before doing real work, verify the agent responds:

```bash
# Claude Code
claude -p "Respond with exactly: SMOKE_OK" --max-turns 2

# Codex
codex exec "Respond with exactly: SMOKE_OK" --full-auto, pty=true

# OpenCode
opencode run "Respond with exactly: SMOKE_OK"
```

### 2. Report to User

After any agent completes, always summarize:
- What was built/fixed
- Files changed (git diff)
- Tests pass?
- Remaining risks/TODOs

### 3. Workdir Isolation Never Share one working directory across parallel sessions — use separate directories or git worktrees to prevent file collisions.

### 4. Cleanup Background Sessions

```bash
# Claude Code: tmux sessions persist; clean up explicitly
tmux kill-session -t claude-work

# Codex/OpenCode: process(action="kill", session_id="<id>")
```

---

## Decision Flow

1. **User names a specific agent** → use that one
2. **Complex reasoning / MCP / deep review** → Claude Code (print mode `-p` for single tasks)
3. **Batch operations / sandboxed work** → Codex
4. **Provider-specific or TUI needed** → OpenCode
5. **One-shot coding task, no preference** → Try Claude Code first (most reliable), then Codex, then OpenCode