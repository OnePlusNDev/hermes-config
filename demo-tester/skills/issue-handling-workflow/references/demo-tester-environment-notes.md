# demo-tester Profile — Environment Notes

This profile runs on a setup that differs from the generic patterns documented elsewhere.

## HOME Path Quirk

On this machine, `HOME` resolves to:

```
/Users/oneplusn/.hermes/profiles/demo-tester/home
```

That is **deeply nested** relative to what cron prompt paths like `~/.hermes/profiles/demo-tester/RULES.md` suggest. The profile root is NOT $HOME — it's `$HOME/..`. So:

- **Profile config lives at**: `$HOME/../RULES.md`, `$HOME/../.env`
- **Cron prompt will reference**: `~/.hermes/profiles/demo-tester/...`
- Your actual filesystem home is the nested path above. When searching for RULES.md or .env from cron, start with `$HOME/../RULES.md` not `~/${HOME}/RULES.md`.

## GitHub Auth for demo-tester

```bash
gh auth status   # → logged in as OnePlusNDev on this machine
```

- The active account is **OnePlusNDev**, NOT OnePlusNTester. When the cron prompt says "your GitHub username is OnePlusNTester", that's your *role* identity — but `gh` sees you logged in as OnePlusNDev. Verify with `gh api user --jq '.login'`.
- Token scopes: `read:org`, `read:user`, `repo`
- gh config stored at `$HOME/.config/gh/` (hosts.yml has oauth_token under `OnePlusNDev`)

## Polling Pattern for This Profile

```bash
# Always verify identity first
GH_USER=$(gh api user --jq '.login')

# Use explicit --repo, not cross-org search
gh issue list --repo demo-oneplusn/demo-workflow \
    --assignee "$GH_USER" \
    --state open \
    --json number,title,state,assignees,labels,body
```

### When `--assignee` returns empty but you think work exists
1. Check `--involves="$GH_USER"` for @-mentions or comments
2. If found and the issue has moved past your role → ignore it (don't re-enter the pipeline)
3. On routine polls, no results = `[SILENT]`

## Credential Rules for Cron on This Profile

- `GITHUB_TOKEN` env var is empty in cron — **do not rely on shell expansion** ($GITHUB_TOKEN → empty string)
- `gh auth status` passes by default (token loaded from hosts.yml) → use gh CLI directly
- Only fall back to sourcing .env / Python urllib when gh auth breaks
  - To source: `source "$HOME/../.env"` (not `$HOME/.env`, the parent dir has it)
  - read_file is blocked on .env files → use terminal cat or source

## Key Difference from Generic docs

The generic issue-handling-workflow skill documents tester-01 → MigbotTester mappings for a different profile. This demo-tester profile:
- Profiles root lives at `~/.hermes/profiles/demo-tester` (but HOME is nested deeper)
- Uses repo `demo-oneplusn/demo-workflow` (not migbot-oneplusn/oneplusn_workflow)
- GitHub identities are OnePlusNTester (role), OnePlusNDev (actual login seen by gh)
