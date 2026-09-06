#!/usr/bin/env python3
"""Crosscheck: verify triage state with authoritative list endpoint.

1. Query open issues assigned to OnePlusNPM (authoritative list endpoint).
2. Query ALL open issues in repo, print assignee health check.
"""
import json
import os
import urllib.request

GH_USERNAME = "OnePlusNPM"
REPO = "demo-oneplusn/demo-workflow"
ENV_PATH = os.path.expanduser("~/.hermes/profiles/demo-pm/.env")


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
    req.add_header("User-Agent", "PM-Triage-Cron-Crosscheck/1.1")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def main():
    token = get_token()

    # 1. Issues assigned to PM (authoritative)
    pm_url = ("https://api.github.com/repos/" + REPO
              + "/issues?state=open&assignee=" + GH_USERNAME + "&per_page=50")
    pm_issues = gh_get(pm_url, token)
    print("PM-assigned open issues (list endpoint):", len(pm_issues))
    for i in pm_issues:
        print("  #%d: %s" % (i["number"], i["title"][:70]))

    # 2. Full health check: all open issues and their assignees
    all_url = ("https://api.github.com/repos/" + REPO
               + "/issues?state=open&per_page=50")
    all_issues = [i for i in gh_get(all_url, token) if "pull_request" not in i]
    print("\nAll open issues:", len(all_issues))
    for i in all_issues:
        labels = ",".join(l["name"] for l in i.get("labels", []))
        assignees = ",".join(a["login"] for a in i.get("assignees", [])) or "(none)"
        print("  #%d: assignee=[%s] labels=[%s] %s"
              % (i["number"], assignees, labels, i["title"][:60]))

    # Decision
    if len(pm_issues) == 0:
        print("\nCROSSCHECK_RESULT: NO_PM_TASKS")
    else:
        print("\nCROSSCHECK_RESULT: PM_TASKS_FOUND")


if __name__ == "__main__":
    main()
