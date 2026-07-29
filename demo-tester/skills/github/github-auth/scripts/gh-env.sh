#!/usr/bin/env bash
# GitHub environment detection helper for Hermes Agent skills.
#
# Usage (via terminal tool):
#   source skills/github/github-auth/scripts/gh-env.sh
#
# After sourcing, these variables are set:
#   GH_AUTH_METHOD  - "gh", "curl", or "none"
#   GITHUB_TOKEN    - personal access token (set if method is "curl")
#   GH_USER         - GitHub username
#   GH_OWNER        - repo owner  (only if inside a git repo with a github remote)
#   GH_REPO         - repo name   (only if inside a git repo with a github remote)
#   GH_OWNER_REPO   - owner/repo  (only if inside a git repo with a github remote)

# --- Auth detection ---

GH_AUTH_METHOD="none"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"
GH_USER=""

if command -v gh &>/dev/null && gh auth status &>/dev/null 2>&1; then
    GH_AUTH_METHOD="gh"
    GH_USER=$(gh api user --jq '.login' 2>/dev/null)
elif [ -n "$GITHUB_TOKEN" ]; then
    GH_AUTH_METHOD="curl"
else
    # Try multiple .env locations: global first, then profile-specific
    _found_token=false
    for _env_candidate in \
        "${HERMES_HOME:-$HOME/.hermes}/.env" \
        "$HOME/.hermes/.env" \
        "/Users/$(whoami)/.hermes/profiles/${HERMES_PROFILE:-tester-01}/.env" \
    ; do
        [ -f "$_env_candidate" ] || continue
        _token=$(grep "^GITHUB_TOKEN=" "$_env_candidate" 2>/dev/null | head -1 | cut -d= -f2 | tr -d '\n\r')
        # Skip commented-out, empty, or masked values
        [ -n "$_token" ] && [ "$_token" != "***" ] && [ "${_token:0:1}" != "#" ] && {
            GITHUB_TOKEN="$_token"
            GH_AUTH_METHOD="curl"
            _found_token=true
            break
        }
    done
    unset _env_candidate _token

    if ! $_found_token && [ -f "$HOME/.git-credentials" ] && grep -q "github.com" "$HOME/.git-credentials" 2>/dev/null; then
        GITHUB_TOKEN=$(grep "github.com" "$HOME/.git-credentials" | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
        [ -n "$GITHUB_TOKEN" ] && GH_AUTH_METHOD="curl"
    fi
    unset _found_token
fi

# Resolve username for curl method
if [ "$GH_AUTH_METHOD" = "curl" ] && [ -z "$GH_USER" ]; then
    GH_USER=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        https://api.github.com/user 2>/dev/null \
        | python3 -c "import sys,json; print(json.load(sys.stdin).get('login',''))" 2>/dev/null)
fi

# --- Repo detection (if inside a git repo with a GitHub remote) ---

GH_OWNER=""
GH_REPO=""
GH_OWNER_REPO=""

_remote_url=$(git remote get-url origin 2>/dev/null)
if [ -n "$_remote_url" ] && echo "$_remote_url" | grep -q "github.com"; then
    GH_OWNER_REPO=$(echo "$_remote_url" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
    GH_OWNER=$(echo "$GH_OWNER_REPO" | cut -d/ -f1)
    GH_REPO=$(echo "$GH_OWNER_REPO" | cut -d/ -f2)
fi
unset _remote_url

# --- Summary ---

echo "GitHub Auth: $GH_AUTH_METHOD"
[ -n "$GH_USER" ]       && echo "User: $GH_USER"
[ -n "$GH_OWNER_REPO" ] && echo "Repo: $GH_OWNER_REPO"
[ "$GH_AUTH_METHOD" = "none" ] && echo "⚠ Not authenticated — see github-auth skill"

export GH_AUTH_METHOD GITHUB_TOKEN GH_USER GH_OWNER GH_REPO GH_OWNER_REPO
