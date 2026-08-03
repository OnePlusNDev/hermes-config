#!/usr/bin/env python3
"""分诊轮询辅助脚本：查询仓库 open issues 并打印摘要"""
import json
import os
import sys
import urllib.request

# 读取 token
env_path = os.path.expanduser("~/.hermes/profiles/demo-pm/.env")
token = None
with open(env_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line.startswith("GITHUB_TOKEN="):
            token = line.split("=", 1)[1].strip()
            break

if not token:
    print("ERROR: GITHUB_TOKEN not found")
    sys.exit(1)

API = "https://api.github.com/repos/demo-oneplusn/demo-workflow/issues"


def fetch(url):
    req = urllib.request.Request(url, headers={
        "Authorization": "token " + token,
        "Accept": "application/vnd.github+json",
        "User-Agent": "demo-pm-cron",
    })
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "mine"
    if mode == "mine":
        data = fetch(f"{API}?state=open&assignee=OnePlusNPM&per_page=100")
    else:
        data = fetch(f"{API}?state=open&per_page=100")
    if isinstance(data, dict):
        print("API_ERROR:", data.get("message", "unknown"))
        sys.exit(0)
    print("count:", len(data))
    for i in data:
        labels = [l["name"] for l in i.get("labels", [])]
        assignees = [a["login"] for a in i.get("assignees", [])]
        print("---")
        print("number:", i["number"])
        print("title:", i["title"])
        print("labels:", labels)
        print("assignees:", assignees)
        print("state:", i["state"])
        body = (i.get("body") or "").strip().replace("\n", " ")[:400]
        print("body:", body)


if __name__ == "__main__":
    main()
