#!/usr/bin/env python3
"""Cross-check helper: authoritative list endpoint + full health check."""
import json
import os
import urllib.request

PROFILE_DIR = os.path.expanduser("~/.hermes/profiles/demo-pm")
ENV_PATH = os.path.join(PROFILE_DIR, ".env")
REPO = "demo-oneplusn/demo-workflow"
ME = "OnePlusNPM"


def get_token():
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line.startswith("GITHUB_TOKEN="):
                return line.split("=", 1)[1].strip()
    raise SystemExit("ERROR: GITHUB_TOKEN not found")


def gh_get(url, token):
    req = urllib.request.Request(url)
    req.add_header("Authorization", "token " + token)
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "PM-Triage-Cron/1.1")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def main():
    token = get_token()

    # 1) Authoritative list endpoint: open issues assigned to me
    list_url = "https://api.github.com/repos/" + REPO + "/issues?state=open&assignee=" + ME + "&per_page=100"
    mine = gh_get(list_url, token)
    print("LIST assigned-to-me count:", len(mine))
    for i in mine:
        print("  #%d %s" % (i["number"], i["title"][:70]))

    # 2) Full health check: all open issues and their assignees
    all_url = "https://api.github.com/repos/" + REPO + "/issues?state=open&per_page=100"
    all_issues = [i for i in gh_get(all_url, token) if "pull_request" not in i]
    print("ALL open issues (excl PRs):", len(all_issues))
    for i in all_issues:
        assignees = [a["login"] for a in i.get("assignees", [])]
        labels = [l["name"] for l in i.get("labels", [])]
        print("  #%d assignees=%s labels=%s | %s" % (i["number"], assignees, labels, i["title"][:60]))

    # Decision
    if len(mine) == 0:
        print("CROSSCHECK: confirmed 0 issues assigned to PM -> SILENT")
    else:
        print("CROSSCHECK: %d issue(s) still assigned to PM -> need triage" % len(mine))


if __name__ == "__main__":
    main()
