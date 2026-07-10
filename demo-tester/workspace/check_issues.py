"""Check for open issues assigned to OnePlusNTester in demo-oneplusn/demo-workflow."""
import json
import os
import subprocess

# Load token from .env
with open('/Users/oneplusn/.hermes/profiles/demo-tester/.env') as f:
    ghp_token = None
    env_lines = f.readlines()
    for line in env_lines:
        if line.startswith('GITHUB_TOKEN='):
            val = line.strip().split('=', 1)[1]
            if '*' not in val and len(val) >= 30:
                ghp_token = val
                break

if not ghp_token:
    print("ERROR: GITHUB_TOKEN not found or masked")
    exit(1)

# Query issues via gh (which is already authenticated)
result = subprocess.run(
    ['gh', 'issue', 'list', '--repo', 'demo-oneplusn/demo-workflow',
     '--assignee', 'OnePlusNTester', '--state', 'open'],
    capture_output=True, text=True
)

if result.returncode != 0:
    # Try with raw GitHub API via curl
    env = os.environ.copy()
    env['GITHUB_TOKEN'] = ghp_token
    
    import urllib.request
    url = "https://api.github.com/repos/demo-oneplusn/demo-workflow/issues?assignee=OnePlusNTester&state=open"
    req = urllib.request.Request(url, headers={'Authorization': f'token {ghp_token}'})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            if not data:
                print("No open issues assigned to OnePlusNTester")
                exit(0)
            for issue in data:
                assigns = [a['login'] for a in issue.get('assignees', [])]
                comments = issue.get('comments', 0)
                print(f"ISSUE #{issue['number']}: {issue['title']}")
                print(f"  Assignees: {assigns}")
                print(f"  Comments: {comments}")
                print(f"  State: {issue['state']} | Created: {issue['created_at']}")
                body = (issue.get('body') or '')[:300]
                if body:
                    print(f"  Body preview: {body[:200]}...")
                print("---")
    except Exception as e:
        # Fall back to gh CLI for fetching details
        result = subprocess.run(
            ['gh', 'issue', 'list', '--repo', 'demo-oneplusn/demo-workflow'],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"gh issue list error: {result.stderr}")
            exit(1)
        print("FALLBACK gh output:\n", result.stdout)
else:
    print(result.stdout if result.stdout.strip() else "No open issues assigned to OnePlusNTester")
