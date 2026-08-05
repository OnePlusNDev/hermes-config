#!/usr/bin/env python3
"""PM 分诊脚本：读取 .env token，查询 assignee=OnePlusNPM 的 open issues"""
import json
import os
import urllib.request
import urllib.error

def load_token():
    env_path = os.path.expanduser("~/.hermes/profiles/demo-pm/.env")
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("GITHUB_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None

def api_get(url, token):
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "User-Agent": "demo-pm-triage",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8"))
        except Exception:
            return e.code, {"message": str(e)}

def main():
    token = load_token()
    if not token:
        print("ERROR: GITHUB_TOKEN not found in .env")
        return
    print("token loaded, length=%d" % len(token))
    url = "https://api.github.com/repos/demo-oneplusn/demo-workflow/issues?state=open&assignee=OnePlusNPM&per_page=100"
    status, data = api_get(url, token)
    if status != 200:
        print("API ERROR status=%s: %s" % (status, data))
        return
    issues = [i for i in data if "pull_request" not in i]
    print("open issues count: %d" % len(issues))
    for i in issues:
        print("---")
        print("number: %s" % i["number"])
        print("title: %s" % i["title"])
        print("labels: %s" % [l["name"] for l in i["labels"]])
        print("assignees: %s" % [a["login"] for a in (i.get("assignees") or [])])
        body = (i.get("body") or "")[:600]
        print("body: %s" % body)

if __name__ == "__main__":
    main()
