#!/usr/bin/env python3
# check_open_issues.py - Fetch open issues assigned to OnePlusNTester
import json, urllib.request, sys

def main():
    # Read token from .env file (line 4 since it follows the known format)
    tok = None
    with open('/Users/oneplusn/.hermes/profiles/demo-tester/.env') as f:
        for line in f:
            if len(line) > 15 and line[14] == '=' and line.startswith('GITHUB'):
                tok = line.split('=', 1)[1].strip()
                break
    if not tok or len(tok) < 30:
        print("ERROR: GITHUB_TOKEN not valid in .env")
        sys.exit(0)

    base = 'https://api.github.com/repos/demo-oneplusn/demo-workflow'
    url = base + '/issues?assignee=OnePlusNTester&state=open&per_page=100'

    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': 'token ' + tok,
        'X-GitHub-Api-Version': '2022-11-28',
    }
    req = urllib.request.Request(url, headers=headers)

    try:
        resp = urllib.request.urlopen(req, timeout=30)
    except Exception as e:
        if hasattr(e, 'code'):
            print('GH_API_ERROR|%d|%s' % (e.code, str(e)))
        else:
            print('GITHUB_API_ERROR|%s' % str(e))
        sys.exit(0)

    raw = resp.read().decode()

    try:
        data = json.loads(raw)
    except Exception as e:
        print('JSON_PARSE_ERROR|%s' % str(e))
        sys.exit(0)

    if isinstance(data, dict):
        msg = data.get('message', 'unknown error')
        status = data.get('status', '??')
        print('GH_API_ERROR|%d|msg=%s' % (status, msg))
        sys.exit(0)

    if not isinstance(data, list):
        print('UNEXPECTED_TYPE|%s' % str(type(data)))
        sys.exit(0)

    if len(data) == 0:
        print('NO_ISSUES_FOUND')
        print(json.dumps([], indent=2))
        return

    # Collect per-issue data - include comment info for analysis
    result = []
    for iss in data:
        num = iss['number']
        t = iss.get('title', '')[:80].replace('|', '-')
        s = iss['state']
        lbs = ','.join(l.get('name', '') for l in iss.get('labels', [])) or 'none'
        ncomments = iss.get('comments', 0)

        # Get last comment author via inline data if available, otherwise separate call
        ci = iss.get('comments_items', [])
        if not ci and ncomments > 0:
            try:
                cmsg_url = base + '/issues/%d/comments?per_page=1' % num
                cmsg_req = urllib.request.Request(
                    cmsg_url, headers=headers)
                cmsg_resp = urllib.request.urlopen(cmsg_req, timeout=15)
                ci = json.loads(cmsg_resp.read().decode())
                if not isinstance(ci, list):
                    ci = []
            except Exception:
                ci = []

        last_by = 'NO_COMMENTS'
        if ci and len(ci) > 0:
            last_by = ci[-1].get('user', {}).get('login', 'UNKNOWN')

        result.append({
            'number': num,
            'title': t,
            'state': s,
            'labels': lbs,
            'last_comment_by': last_by,
            'comments_count': ncomments,
        })

    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
