#!/usr/bin/env python3
"""
PM Full Triage Script
=====================
Self-contained script for PM triage cron jobs:
1. Reads GITHUB_TOKEN from profile .env at runtime
2. Queries demo-oneplusn/demo-workflow for open issues assigned to OnePlusNPM
3. Classifies each issue by type label + keywords
4. Posts a Chinese comment explaining the triage decision
5. Reassigns (remove old -> add new) to the correct engineer
6. Outputs [SILENT] if no issues found -> suppresses cron delivery

Usage:
    python3 scripts/full_triage.py

Relies on: ~/.hermes/profiles/demo-pm/.env for GITHUB_TOKEN
No external dependencies (stdlib only: json, os, urllib.request).
"""

import json
import os
import urllib.request
import sys

# -- Configuration -----------------------------------------------------------

GH_USERNAME = "OnePlusNPM"
REPO = "demo-oneplusn/demo-workflow"
PROFILE_DIR = os.path.expanduser("~/.hermes/profiles/demo-pm")
ENV_PATH = os.path.join(PROFILE_DIR, ".env")

# Assignee mapping
ASSIGNEE_MAP = {
    "dev":  "OnePlusNDev",
    "test": "OnePlusNTester",
    "boss": "OnePlusNBoss",
}

# Keywords checked when no type label is present
DEV_KEYWORDS = ["开发", "实现", "新增", "修复", "feature", "bug",
                "add", "implement", "fix", "build", "写代码", "实现功能"]
TEST_KEYWORDS = ["测试", "验证", "审查", "test", "verify",
                 "review", "check", "确认", "验收"]
DOC_KEYWORDS = ["文档", "doc", "documentation", "文档编写", "readme", "说明"]
RESEARCH_KEYWORDS = ["调研", "研究", "research", "investigate", "探索", "分析"]

# -- Helpers -----------------------------------------------------------------


def get_token():
    """Read GITHUB_TOKEN from the profile .env file at runtime."""
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line.startswith("GITHUB_TOKEN="):
                return line.split("=", 1)[1].strip()
    sys.exit("ERROR: GITHUB_TOKEN not found in " + ENV_PATH)


def gh_get(url, token):
    """GET request to GitHub API."""
    req = urllib.request.Request(url)
    req.add_header("Authorization", "token " + token)
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "PM-Triage-Cron/1.1")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def gh_post(url, data, token):
    """POST (create comment, add assignee)."""
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body)
    req.add_header("Authorization", "token " + token)
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "PM-Triage-Cron/1.1")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def gh_delete_assignees(url, assignees, token):
    """Remove assignees from an issue (DELETE on /assignees)."""
    body = json.dumps({"assignees": assignees}).encode()
    req = urllib.request.Request(url, data=body)
    req.add_header("Authorization", "token " + token)
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "PM-Triage-Cron/1.1")
    req.add_header("Content-Type", "application/json")
    req.get_method = lambda: "DELETE"
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def classify_issue(issue):
    """Determine issue type and target assignee. Returns (type, assignee, reason)."""
    labels = [l["name"] for l in issue.get("labels", [])]
    title = issue.get("title", "")
    body = issue.get("body", "") or ""
    combined = (title + " " + body).lower()

    type_label = next((l for l in labels if l.startswith("type:")), None)

    has_dev = any(k in combined for k in DEV_KEYWORDS)
    has_test = any(k in combined for k in TEST_KEYWORDS)
    has_doc = any(k in combined for k in DOC_KEYWORDS)
    has_research = any(k in combined for k in RESEARCH_KEYWORDS)

    if type_label in ("type:feature", "type:bug") or has_dev:
        return ("feature/bug", ASSIGNEE_MAP["dev"],
                "此问题涉及开发实现或缺陷修复，需要开发工程师处理")
    elif type_label == "type:verification" or has_test:
        return ("verification", ASSIGNEE_MAP["test"],
                "此问题涉及测试验证或代码审查，需要测试工程师处理")
    elif type_label in ("type:research", "type:docs") or has_doc or has_research:
        tl = str(type_label) if type_label else "无"
        return ("research/docs", ASSIGNEE_MAP["boss"],
                f"此问题涉及调研或文档编写（标签: {tl}），暂交老板判断")
    else:
        return ("unknown", ASSIGNEE_MAP["boss"],
                f"未能明确识别问题类型（标签: {labels}），暂交老板决策")


# -- Main --------------------------------------------------------------------


def main():
    token = get_token()

    # Step 1: Query open issues assigned to PM
    search_url = (
        "https://api.github.com/search/issues"
        "?q=repo:" + REPO + "+assignee:" + GH_USERNAME + "+state:open"
        "&per_page=20"
    )
    data = gh_get(search_url, token)
    total = data.get("total_count", 0)

    if total == 0:
        print("No issues to triage. Silent exit.")
        print("SILENT")
        return

    issues = data.get("items", [])

    for issue in issues:
        num = issue["number"]
        title = issue["title"]
        issue_type, assignee, reason = classify_issue(issue)

        print(f"Issue #{num}: {title[:60]}")
        print(f"  Type: {issue_type} -> {assignee}")

        # Step 2: Post Chinese comment
        labels = [l["name"] for l in issue.get("labels", [])]
        type_label = next((l for l in labels if l.startswith("type:")), None)
        comment = (
            "## 自动分诊报告\n\n"
            "**识别类型**：" + issue_type + "\n"
            "**标签检测**：" + (type_label or "无 type 标签") + "\n"
            "**规模评估**：single-issue / 单任务规模\n\n"
            "**指派给**：@" + assignee + "\n"
            "**理由**：" + reason + "\n\n"
            "---\n"
            "*此分诊由 PM 项目牧羊人自动执行*"
        )
        comment_url = "https://api.github.com/repos/" + REPO + "/issues/" + str(num) + "/comments"
        gh_post(comment_url, {"body": comment}, token)
        print("  Comment posted")

        # Step 3: Reassign -- remove all, add one
        issue_url = "https://api.github.com/repos/" + REPO + "/issues/" + str(num)
        i_data = gh_get(issue_url, token)
        current = [a["login"] for a in i_data.get("assignees", [])]
        print("  Current assignees: " + str(current))

        assignees_url = issue_url + "/assignees"
        if current:
            gh_delete_assignees(assignees_url, current, token)
            print("  Removed: " + str(current))

        gh_post(assignees_url, {"assignees": [assignee]}, token)
        print("  Reassigned to: " + assignee)
        print("  OK Issue #" + str(num) + " done")

    print("=== Triage complete ===")


if __name__ == "__main__":
    main()
