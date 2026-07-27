#!/usr/bin/env python3
"""PM triage cron v5: direct .env reading, no shell sourcing."""
import json, os, sys

env = {}
with open(os.path.expanduser('~/.hermes/profiles/demo-pm/.env')) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()

token = env.get("GITHUB_TOKEN", "")
username = env.get("GITHUB_USERNAME", "OnePlusNPM")

if not token:
    print("ERROR: GITHUB_TOKEN not found")
    sys.exit(1)

REPO = "demo-oneplusn/demo-workflow"

def gh_api(method, path, data=None):
    auth_hdr = 'Authorization: token ' + token
    headers = '-H "' + auth_hdr + '" -H "Accept: application/vnd.github.v3+json"'
    if data:
        import tempfile
        f = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump(data, f)
        f.close()
        cmd = 'curl -s -X ' + method + ' ' + headers + ' -H "Content-Type: application/json" -d @' + f.name + ' "https://api.github.com/repos/' + REPO + path + '"'
    else:
        cmd = 'curl -s -X ' + method + ' ' + headers + ' "https://api.github.com/repos/' + REPO + path + '"'
    r = os.popen(cmd).read()
    try:
        return json.loads(r)
    except json.JSONDecodeError:
        print("ERROR parsing response: " + r[:300])
        return None

issues = gh_api("GET", "/issues?assignee=" + username + "&state=open&per_page=50")
if not isinstance(issues, list):
    print("ERROR: unexpected response: " + json.dumps(issues)[:500])
    sys.exit(1)

print("Found " + str(len(issues)) + " open issue(s) assigned to " + username)

if not issues:
    print("[SILENT]")
    sys.exit(0)

for issue in issues:
    num = issue["number"]
    title = issue["title"]
    body = issue.get("body", "") or ""
    labels = [l["name"] for l in issue.get("labels", [])]
    current_assignee = issue["assignee"]["login"] if issue.get("assignee") else None

    print("\n" + "=" * 60)
    print("Issue #" + str(num) + ": " + title)
    print("  Labels: " + str(labels))
    print("  Assignee: " + str(current_assignee))

    type_label = None
    for lb in labels:
        if lb.startswith("type:"):
            type_label = lb
            break

    if not type_label:
        text = (title + " " + body).lower()
        dev_kw = any(kw in text for kw in ["开发", "实现", "新增", "feature", "add", "implement", "build", "create", "fix", "bug", "修复", "错误", "故障"])
        test_kw = any(kw in text for kw in ["测试", "验证", "审查", "test", "verify", "review", "quality"])
        doc_kw = any(kw in text for kw in ["docs", "document", "文档", "documentation"])
        research_kw = any(kw in text for kw in ["研究", "调研", "research", "investigate"])

        if dev_kw:
            if any(kw in text for kw in ["fix", "bug", "修复", "错误", "故障"]):
                type_label = "type:bug"
            else:
                type_label = "type:feature"
        elif test_kw:
            type_label = "type:verification"
        elif research_kw:
            type_label = "type:research"
        elif doc_kw:
            type_label = "type:docs"
        else:
            type_label = "type:unknown"

    body_len = len(body)
    if body_len > 500:
        scale = "大 (body > 500 字符)"
    elif body_len > 100:
        scale = "中 (body 100-500 字符)"
    else:
        scale = "小 (body < 100 字符)"

    if type_label in ("type:feature", "type:bug"):
        new_assignee = "OnePlusNDev"
        reason = "检测到类型" + type_label + "（开发/修复任务），需开发工程师处理"
    elif type_label == "type:verification":
        new_assignee = "OnePlusNTester"
        reason = "检测到类型" + type_label + "（测试/验证任务），需测试工程师审查"
    elif type_label in ("type:research", "type:docs"):
        new_assignee = "OnePlusNBoss"
        reason = "检测到类型" + type_label + "（研究/文档任务），无法确定具体执行人，由老板裁定"
    else:
        new_assignee = "OnePlusNBoss"
        reason = "无法识别明确的任务类型（标签: " + ', '.join(labels) + "），由老板裁定"

    print("  -> Type: " + type_label + " | Scale: " + scale)
    print("  -> Assign to: " + new_assignee)
    print("  -> Reason: " + reason)

    comment_md = "## 任务分诊\n\n**类型识别**：" + type_label + "\n\n**规模评估**：" + scale + "\n\n**分诊结论**：指派给 @" + new_assignee + "\n\n**理由**：" + reason

    cr = gh_api("POST", "/issues/" + str(num) + "/comments", {"body": comment_md})
    if cr and cr.get("id"):
        print("  OK Comment posted (id=" + str(cr['id']) + ")")
    else:
        print("  FAIL Comment failed: " + str(cr)[:200] if cr else 'no response')

    if current_assignee and current_assignee.lower() != new_assignee.lower():
        rem = gh_api("DELETE", "/issues/" + str(num) + "/assignees", {"assignees": [current_assignee]})
        if isinstance(rem, dict) and rem.get("assignees") is not None:
            print("  OK Removed " + current_assignee)
        else:
            print("  ~ Remove result: " + str(rem)[:200] if rem else 'no response')

    add_result = gh_api("POST", "/issues/" + str(num) + "/assignees", {"assignees": [new_assignee]})
    if isinstance(add_result, dict) and add_result.get("assignees") is not None:
        new_logins = [a["login"] for a in add_result["assignees"]]
        print("  OK Assignees now: " + str(new_logins))
        if len(new_logins) != 1 or new_logins[0].lower() != new_assignee.lower():
            print("  WARNING: expected exactly [" + new_assignee + "], got " + str(new_logins))
    else:
        print("  FAIL Assign failed: " + str(add_result)[:200] if add_result else 'no response')

print("\n" + "=" * 60)
print("Triage complete.")
