#!/usr/bin/env python3
import json
import urllib.request

# Read token from .env properly
token = ""
with open("/Users/oneplusn/.hermes/profiles/demo-pm/.env", "r") as f:
    for line in f:
        if line.startswith("GITHUB_TOKEN=***
_ token = line.strip().partition("=")[2]

if not token or token == "***":
    print("ERROR: GITHUB_TOKEN could not be read (masked).")
    exit(1)

url = (
    "https://api.github.com/repos/demo-oneplusn/demo-workflow/issues"
    "?assignee=OnePlusNPM&state=open"
)

req = urllib.request.Request(url, headers={
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github+json",
})

resp = urllib.request.urlopen(req)
data = resp.read().decode()
issues = json.loads(data)

print(f"\nTotal open issues assigned to OnePlusNPM: {len(issues)}\n")

if not issues:
    print("No issues to triage.\n")
    exit(0)

for i in issues:
    num = i["number"]
    title = i["title"]
    body = (i.get("body") or "")[:800]
    labels = [t["name"] for t in i.get("labels", [])]
    assignees = [a["login"] for a in i.get("assignees", [])]

    print(f"=== Issue #{num} ===")
    print(f"  Title:     {title}")
    print(f"  Labels:    {labels}")
    print(f"  Assignees: {assignees}")
    print(f"  Body:\n{body}\n")
