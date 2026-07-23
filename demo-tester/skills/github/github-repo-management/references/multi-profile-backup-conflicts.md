# Multi-Profile Automated Backup — Conflict Resolution

When multiple Hermes profiles (demo-tester, demo-dev, demo-pm) all push config backups to the
**same** GitHub repository (`hermes-config`), force-pushes and rebase conflicts are inevitable.
This reference codifies the automated-resolution strategy.

## The Problem

```
profile-A (cron) ── force-push ──► remote/main @ commit-X
profile-B (cron) ── later push ──► "fetch first" error
                                     └── rebase conflicts because remote was force-pushed
```

The remote was overwritten by another process. Your local branch now has a divergent history
and git refuses to push. Any automated cron job must recover without manual intervention.

## Strategy: Accept Remote (`--theirs`) for Automated Backups

For **automated backup repos** (not collaborative development repos), the local state
is a full snapshot of the current profile. The remote was set by an equally-authoritative
process. **Both are valid snapshots, so taking either version is correct for the
final result.**

Resolution procedure:

```bash
# 1. Pull with rebase — will likely conflict
git pull --rebase origin main
# → CONFLICT (content): merge conflict in ...

# 2. For each conflicted file: accept the remote ('theirs') version
# In rebase mode, 'theirs' = the remote's version, 'ours' = your local version
git checkout --theirs .gitignore
git checkout --theirs demo-tester/cron/jobs.json
# ... repeat for all conflicted paths

# 3. Stage resolved files
git add .

# 4. Continue rebase with a no-op editor (no TTY in cron)
GIT_EDITOR=true git rebase --continue

# 5. Push
git push origin main
```

### Why `--theirs` and not `--ours`?

During a **rebase**, `--theirs` is the **remote's** version (the base being rebased onto),
and `--ours` is your local commit being replayed. So:

| Strategy | Result |
|----------|--------|
| `--theirs` | Keeps remote's version → remote wins |
| `--ours` | Keeps your local version → local wins |

For a backup where both states are snapshots from different times, either is acceptable.
`--theirs` is slightly safer because the remote has already been accepted by the CI chain
(webhook triggers, downstream jobs), and overwriting it again with `--ours` would
potentially revert files another profile added.

### Files that always use `--theirs`:

| File type | Reason |
|-----------|--------|
| `.gitignore` | Defines which files are tracked; remote patterns are already vetted |
| `cron/jobs.json` | Will be overwritten by next tick anyway |
| `skills/*/references/*.md` | References are additive; remote and local can coexist |
| `memories/*.md` | Memory files merge; either version is valid |

## Multi-Account Repo Discovery

When you know a repo name (`hermes-config`) but not which GitHub account owns it,
and you have multiple logged-in `gh` accounts:

```bash
# 1. List all logged-in accounts
gh auth status 2>&1 | grep "Logged in" | sed 's/.*account //'

# 2. For each account, try to view the repo
for account in OnePlusNDev OnePlusNPM OnePlusNTester; do
  echo "=== $account ==="
  gh repo view "$account/hermes-config" --json name,owner 2>&1 || echo "NOT FOUND"
done

# 3. The active account's token is what `gh` uses — switch if needed:
gh auth switch --user OnePlusNDev

# 4. Set the remote URL to the correct owner
git remote set-url origin https://github.com/OnePlusNDev/hermes-config.git
```

### Why `gh repo list` may return empty

```bash
gh repo list oneplusn --limit 20
# → (empty output)
```

This happens when:
- The active `gh` account does NOT own or collaborate on repos under that org/user
- The repo is owned by a **different** account than the one `gh` is currently logged in as

`gh repo list` only shows repos for the **active** account. To see repos from another
account, switch first:
```bash
gh auth switch --user OtherUser
gh repo list OtherUser --limit 20
```

## Force-Push vs. Rebase: When to Use Which

| Situation | Strategy | Command |
|-----------|----------|---------|
| Repo has single cron writer | Fast-forward push only | `git push origin main` |
| Repo has multiple cron writers, no human commits | Accept remote + rebase | `pull --rebase` + `--theirs` resolution |
| You know your local is more complete | Force push (use `--force-with-lease` for safety) | `git push --force-with-lease origin main` |
| Human has committed between cron runs | NEVER force push; pull manually | `git pull --rebase origin main` + manual resolution |

**Safety note:** `--force-with-lease` is safer than `--force` — it checks that your
local idea of the remote's state matches the actual remote, preventing accidental
overwrites of commits you haven't seen.
