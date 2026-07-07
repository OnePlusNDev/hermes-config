#!/usr/bin/env python3
"""PM triage: query open issues assigned to OnePlusNPM and process them."""
import json, os, subprocess, sys

# Load env
env_path = os.path.expanduser("~/.hermes/profiles/demo-pm/.env")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v

token = os.environ.get("GITHUB_TOKEN")
if not token:
    print("ERROR: GITHUB_TOKEN not found")
    sys.exit(1)

# Query open issues assigned to OnePlusNPM
url = "https://api.github.com/repos/demo-oneplusn/demo-workflow/issues?state=open&assignee=OnePlusNPM"
result = subprocess.run(
    ["curl", "-s", "-H", f"Authorization: token {token}", url],
    capture_output=True, text=True
)

try:
    issues = json.loads(result.stdout)
except json.JSONDecodeError:
    print(f"ERROR: JSON decode failed. Raw: {result.stdout[:500]}")
    sys.exit(1)

if not isinstance(issues, list):
    print(f"ERROR: API returned non-list: {issues.get('message', issues)}")
    sys.exit(1)

if not issues:
    print("[]")
    sys.exit(0)

output = []
for issue in issues:
    labels = [l["name"] for l in issue.get("labels", [])]
    number = issue["number"]
    title = issue["title"]
    body = (issue.get("body") or "")[:300]
    output.append(f"ID:{number}|TITLE:{title}|LABELS:{','.join(labels)}|BODY:{body}")

print("\n".join(output))
