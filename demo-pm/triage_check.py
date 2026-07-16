#!/usr/bin/env python3
import subprocess, json, os, sys

# Read token from env file (sanitized)
with open(os.path.expanduser("~/.hermes/profiles/demo-pm/.env")) as f:
    for line in f:
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ[k] = v

token = os.environ.get("GITHUB_TOKEN", "")

headers = ["-H", f"Authorization: token {token}", "-H", "Accept: application/vnd.github.v3+json"]

# Query open issues assigned to OnePlusNPM
url = "https://api.github.com/repos/demo-oneplusn/demo-workflow/issues?state=open&assignee=OnePlusNPM"
result = subprocess.run(["curl", "-s"] + headers + [url], capture_output=True, text=True)
data = json.loads(result.stdout)

if isinstance(data, list):
    print(f"COUNT:{len(data)}")
    for i in data:
        labels = [l["name"] for l in i.get("labels", [])]
        assignees = [a["login"] for a in i.get("assignees", [])]
        # Remove newlines from title
        title = i["title"].replace("|", "/").replace("\n", " ")
        print(f"ISSUE:{i['number']}|{title}|{json.dumps(labels)}|{json.dumps(assignees)}")
else:
    print(f"ERROR:{json.dumps(data)}")
    sys.exit(1)
