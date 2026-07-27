import os, re, json, urllib.request

env_path = os.path.expanduser('~/.hermes/profiles/demo-pm/.env')
with open(env_path) as f:
    content = f.read()

match = re.search(r'GITHUB_TOKEN=(.+)', content)
if not match:
    print('ERROR: GITHUB_TOKEN not found')
    exit(1)

token = match.group(1).strip().strip("'").strip('"')

url = 'https://api.github.com/repos/demo-oneplusn/demo-workflow/issues?state=open&assignee=OnePlusNPM'
req = urllib.request.Request(url)
req.add_header('Authorization', f'token {token}')
req.add_header('Accept', 'application/vnd.github.v3+json')

try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
except Exception as e:
    print(f'API_ERROR: {e}')
    exit(1)

if not isinstance(data, list):
    print(f'UNEXPECTED: {json.dumps(data, indent=2)}')
    exit(1)

if not data:
    print('NO_ISSUES')
    exit(0)

for issue in data:
    labels = [l['name'] for l in issue.get('labels', [])]
    assignees = [a['login'] for a in issue.get('assignees', [])]
    print(json.dumps({
        'number': issue['number'],
        'title': issue['title'],
        'labels': labels,
        'assignees': assignees,
        'body_snippet': (issue.get('body') or '')[:300]
    }))
