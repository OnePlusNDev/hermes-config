# `gh auth switch` Error: GH_TOKEN Env Var Blocks Switch

## Exact Error

When `GH_TOKEN` or `GITHUB_TOKEN` is set in the shell environment, `gh auth switch` fails with:

```
The value of the GH_TOKEN environment variable is being used for authentication.
To have GitHub CLI manage credentials instead, first clear the value from the environment.
```

Exit code: 1 (failure)

## Root Cause

The `gh` CLI checks `GH_TOKEN` env var before applying keychain-based auth switching. If the env var is present (even if it's a stale/redacted value from `.env`), `gh auth switch` refuses to modify the active account — the keychain credential is overridden by the env var.

## Resolution

```bash
# Before switch: unset both possible env var names
unset GH_TOKEN GITHUB_TOKEN

# Now switch works
gh auth switch --user TARGET_USER

# Verify the switch took effect
gh api user --jq '.login'
```

## Real Session Transcript

From a cron poll of the demo-tester profile:

```
# First attempt (fails):
$ gh auth switch --user OnePlusNTester
> The value of the GH_TOKEN environment variable is being used for authentication.
> To have GitHub CLI manage credentials instead, first clear the value from the environment.
> exit code: 1

# Fix:
$ unset GH_TOKEN && gh auth switch --user OnePlusNTester
> ✓ Switched active account for github.com to OnePlusNTester

# After work is done, switch back:
$ unset GH_TOKEN && gh auth switch --user OnePlusNDev
> ✓ Switched active account for github.com to OnePlusNDev
```

## Detection

Check which auth source is blocking the switch:

```bash
env | grep -i gh_token
```

If either `GH_TOKEN` or `GITHUB_TOKEN` appears, that's the blocker.

## Related

- SKILL.md pitfall: "gh auth switch fails when GH_TOKEN env var is set"
- `issue-handling-workflow` SKILL.md: polling keychain state table
- `code-verification` SKILL.md: Credential Handling → Shortcut: gh auth switch
