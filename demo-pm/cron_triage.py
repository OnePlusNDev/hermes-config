#!/usr/bin/env python3
"""PM triage cron: read env, query GitHub, classify and reassign issues."""
import os, re, json, urllib.request, urllib.error, sys

# Read .env manually
env_path = os.path.expanduser("~/.hermes/profiles/demo-pm/.env")
with open(env_path) as f:
    content = f.read()

m = re.search(r'^GITHUB_TOKEN=(.+)$', content, re.MULTILINE)
if not m:
    print("ERROR: GITHUB_TOKEN not found", file=sys.stderr)
    sys.exit(1)
token = m.group(1).strip().strip("'\"")

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json",
    "User-Agent": "demo-pm-cron"
}

# 1) Query open issues assigned to OnePlusNPM
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

# 2) Classification logic
def classify_issue(issue):
    labels = [l.get('name', '').lower() for l in issue.get('labels', [])]
    title = (issue.get('title') or '').lower()
    body = (issue.get('body') or '').lower()
    text = title + ' ' + body
    
    # Check type labels first
    if any('type:feature' in l for l in labels):
        return 'feature', 'OnePlusNDev', '功能开发任务'
    if any('type:bug' in l for l in labels):
        return 'bug', 'OnePlusNDev', 'Bug 修复任务'
    if any('type:verification' in l for l in labels):
        return 'verification', 'OnePlusNTester', '验证/测试任务'
    if any('type:research' in l for l in labels):
        return 'research', 'OnePlusNBoss', '研究型任务，需要老板决策方向'
    if any('type:docs' in l for l in labels):
        return 'docs', 'OnePlusNBoss', '文档任务，需要老板确认范围和优先级'
    
    # Fallback: keyword-based guessing
    dev_kw = ['开发', '实现', '新增', '修复', 'feature', 'bug', 'fix', 'implement', 'add', 'create', 'build', '重构', '优化']
    test_kw = ['测试', '验证', '审查', 'test', 'verify', 'review', 'check', 'audit']
    boss_kw = ['研究', '调研', '文档', 'research', 'docs', '研究', '决策', '方案', '规划', '计划']
    
    for kw in dev_kw:
        if kw in text:
            return 'feature', 'OnePlusNDev', f'关键词"${kw}"匹配，判定为开发任务'
    for kw in test_kw:
        if kw in text:
            return 'verification', 'OnePlusNTester', f'关键词"${kw}"匹配，判定为测试/验证任务'
    for kw in boss_kw:
        if kw in text:
            return 'research', 'OnePlusNBoss', f'关键词"${kw}"匹配，判定为需决策的任务'
    
    return 'unknown', 'OnePlusNBoss', '无法自动识别类型，交由老板人工判断'

# 3) Process each issue
results = []
for issue in issues:
    num = issue['number']
    title = issue['title']
    issue_type, assignee, reason = classify_issue(issue)
    
    # Scale estimate
    body_len = len(issue.get('body') or '')
    if body_len > 3000:
        scale = '大（L）'
    elif body_len > 1000:
        scale = '中（M）'
    else:
        scale = '小（S）'
    
    # Comment body (in Chinese)
    comment_body = (
        f"## 任务分诊报告\n\n"
        f"**识别类型**：{issue_type}\n\n"
        f"**规模评估**：{scale}\n\n"
        f"**指派给**：@{assignee}\n\n"
        f"**理由**：{reason}\n\n"
        f"---\n"
        f"*自动分诊由 demo-pm 项目牧羊人执行*"
    )
    
    print(f"\n{'='*60}")
    print(f"Issue #{num}: {title}")
    print(f"  Type: {issue_type}, Scale: {scale}, Assignee: {assignee}")
    print(f"  Reason: {reason}")
    
    # Post comment
    comment_url = f"https://api.github.com/repos/demo-oneplusn/demo-workflow/issues/{num}/comments"
    comment_data = json.dumps({"body": comment_body}).encode()
    comment_req = urllib.request.Request(comment_url, data=comment_data, headers={**headers, "Content-Type": "application/json"}, method='POST')
    try:
        with urllib.request.urlopen(comment_req) as resp:
            print(f"  ✓ Comment posted (status {resp.status})")
    except urllib.error.HTTPError as e:
        print(f"  ✗ Comment failed: {e.code} {e.reason}")
        print(f"    {e.read().decode()[:200]}")
        continue
    
    # Step 1: Remove current assignees
    current_assignees = [a['login'] for a in issue.get('assignees', [])]
    if current_assignees:
        remove_url = f"https://api.github.com/repos/demo-oneplusn/demo-workflow/issues/{num}/assignees"
        remove_data = json.dumps({"assignees": current_assignees}).encode()
        remove_req = urllib.request.Request(remove_url, data=remove_data, headers={**headers, "Content-Type": "application/json"}, method='DELETE')
        try:
            with urllib.request.urlopen(remove_req) as resp:
                print(f"  ✓ Removed assignees: {current_assignees}")
        except urllib.error.HTTPError as e:
            print(f"  ✗ Remove assignee failed: {e.code} {e.reason}")
            print(f"    {e.read().decode()[:200]}")
    
    # Step 2: Add new assignee
    add_url = f"https://api.github.com/repos/demo-oneplusn/demo-workflow/issues/{num}/assignees"
    add_data = json.dumps({"assignees": [assignee]}).encode()
    add_req = urllib.request.Request(add_url, data=add_data, headers={**headers, "Content-Type": "application/json"}, method='POST')
    try:
        with urllib.request.urlopen(add_req) as resp:
            print(f"  ✓ Assigned to @{assignee}")
    except urllib.error.HTTPError as e:
        print(f"  ✗ Add assignee failed: {e.code} {e.reason}")
        print(f"    {e.read().decode()[:200]}")
    
    results.append({"num": num, "title": title, "type": issue_type, "scale": scale, "assigned_to": assignee})

# Summary
print(f"\n{'='*60}")
print(f"Triage complete. {len(results)} issue(s) processed.")
for r in results:
    print(f"  #{r['num']}: {r['title']} → @{r['assigned_to']} [{r['type']}, {r['scale']}]")

if not results:
    print("No issues to triage.")
    sys.exit(0)
