#!/usr/bin/env python3
"""Fetch open issues assigned to OnePlusNPM from demo-oneplusn/demo-workflow."""
import os, sys, json, urllib.request, subprocess

# Read token from .env
with open(os.path.expanduser('~/.hermes/profiles/demo-pm/.env')) as f:
    for line in f:
        if line.startswith('GITHUB_TOKEN='):
            token = line.split('=', 1)[1].strip()
            break

url = "https://api.github.com/repos/demo-oneplusn/demo-workflow/issues?assignee=OnePlusNPM&state=open&per_page=50"
req = urllib.request.Request(url)
req.add_header('Authorization', f'token {token}')
req.add_header('Accept', 'application/vnd.github.v3+json')

try:
    resp = urllib.request.urlopen(req)
    issues = json.loads(resp.read())
    if isinstance(issues, list):
        for i in issues:
            labels = [l['name'] for l in i.get('labels', [])]
            print(json.dumps({
                'number': i['number'],
                'title': i['title'],
                'state': i['state'],
                'labels': labels,
                'body_preview': (i['body'] or '')[:500],
                'assignees': [a['login'] for a in i.get('assignees', [])],
                'html_url': i['html_url']
            }, ensure_ascii=False))
        if not issues:
            print("NO_ISSUES_FOUND")
    else:
        print(f"ERROR: {issues.get('message', str(issues))}")
except Exception as e:
    print(f"FETCH_ERROR: {e}")
    sys.exit(1)
