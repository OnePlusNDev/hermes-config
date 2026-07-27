#!/usr/bin/env python3
"""PM triage cron: fetch issues assigned to OnePlusNPM."""
import os, re, json, urllib.request, urllib.error, sys

# Read token from .env
env_path = os.path.expanduser("~/.hermes/profiles/demo-pm/.env")
with open(env_path) as f:
    content = f.read()
m = re.search(r'^GITHUB_TOKEN=(.+)$', content, re.MULTILINE)
if not m:
    print("ERROR: GITHUB_TOKEN not found", file=sys.stderr)
    sys.exit(1)
token = m.group(1).strip().strip("'\"")
print(f"Token extracted: {token[:8]}...{token[-4:]}", file=sys.stderr)

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json",
    "User-Agent": "demo-pm-cron"
}

# Query open issues assigned to OnePlusNPM
url = "https://api.github.com/repos/demo-oneplusn/demo-workflow/issues?assignee=OnePlusNPM&state=open&per_page=100"
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        issues = json.loads(resp.read().decode())
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} {e.reason}", file=sys.stderr)
    body = e.read().decode() if hasattr(e, 'read') else ""
    print(body, file=sys.stderr)
    sys.exit(1)

# Filter out pull requests
issues = [i for i in issues if 'pull_request' not in i]

if not issues:
    print("NO_ISSUES")
    sys.exit(0)

# Print full issue info
for i in issues:
    labels = [l.get('name', '') for l in i.get('labels', [])]
    assignees = [a['login'] for a in i.get('assignees', [])]
    print(json.dumps({
        'number': i['number'],
        'title': i['title'],
        'body': i.get('body', '')[:500],
        'labels': labels,
        'assignees': assignees,
        'state': i['state']
    }))
