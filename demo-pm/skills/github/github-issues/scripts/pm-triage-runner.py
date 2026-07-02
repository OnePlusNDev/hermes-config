#!/usr/bin/env python3
"""
PM Triage Runner — 项目牧羊人自动分诊 Cron 入口脚本

Deployment:
  1. Save to `/tmp/pm-triage-runner.py` during cron execution
  2. Run: `python3 /tmp/pm-triage-runner.py`
  3. Output goes to cron delivery — `[SILENT]` = no work, else report.

Requirements: Python 3 stdlib only (urllib, json, sys).
"""
import json
import subprocess
import sys
import os

# ─── Configuration ────────────────────────────────────────────────────────────

# 硬编码：cron 的 CWD 和 HOME 不可靠
PROFILE_DIR = os.path.expanduser('~/.hermes/profiles/demo-pm')
ENV_PATH = os.path.join(PROFILE_DIR, '.env')

# GitHub 信息
REPO_OWNER = 'demo-oneplusn'
REPO_NAME = 'demo-workflow'
PM_USER = 'OnePlusNPM'          # 当前 profile 的 GitHub 用户名

# 路由表：type:xxx → (assignee, role_desc)
ROUTING_TABLE = {
    'type:feature':      ('OnePlusNDev',   '开发工程师'),
    'type:bug':          ('OnePlusNDev',   '开发工程师'),
    'type:verification': ('OnePlusNTester', '测试工程师'),
    'type:research':     ('OnePlusNBoss',  '老板（人工决策）'),
    'type:docs':         ('OnePlusNBoss',  '老板（人工决策）'),
}

DEFAULT_ROUTE = ('OnePlusNBoss', '老板（人工决策 — 类型不明）')

# ─── Token Loading ────────────────────────────────────────────────────────────

def load_token():
    """Read GITHUB_TOKEN from .env, bypassing shell redaction."""
    with open(ENV_PATH, errors='replace') as f:
        for line in f:
            if line.startswith('GITHUB_TOKEN='):
                candidate = line.strip().split('=', 1)[1].strip().strip('\'"')
                if candidate and len(candidate) >= 10 and candidate != '***':
                    return candidate
    return None

# ─── GitHub API ───────────────────────────────────────────────────────────────

class GitHubAPI:
    BASE = 'https://api.github.com'

    def __init__(self, token):
        self.token = token
        self.headers = [
            '-H', f'Authorization: token {token}',
            '-H', 'Accept: application/vnd.github.v3+json',
            '-H', 'User-Agent: demo-pm-cron/1.0',
        ]

    def _request(self, method, path, data=None):
        url = f'{self.BASE}{path}'
        cmd = ['curl', '-s', '-X', method] + self.headers + ['--connect-timeout', '10', url]

        if data is not None:
            # Write body to temp file to avoid shell quoting issues with multi-line JSON
            body_str = json.dumps(data)
            body_path = f'/tmp/gh_body_{os.getpid()}.json'
            with open(body_path, 'w') as f:
                f.write(body_str)
            cmd = ['curl', '-s', '-X', method, '-d', f'@{body_path}'] + self.headers + ['--connect-timeout', '10', url]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        except subprocess.TimeoutExpired:
            print(f'[ERROR] {method} {path}: timeout after 30s', file=sys.stderr)
            return None
        finally:
            if data is not None and os.path.exists(body_path):
                os.unlink(body_path)

        if result.returncode != 0:
            print(f'[ERROR] {method} {path}: curl exited {result.returncode} — {result.stderr.strip()[:200]}', file=sys.stderr)
            return None

        raw = result.stdout.strip()
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            print(f'[ERROR] {method} {path}: JSON parse failed — {e}', file=sys.stderr)
            print(f'[DEBUG] Response (first 200): {raw[:200]}', file=sys.stderr)
            return None

    def get(self, path):
        return self._request('GET', path)

    def post(self, path, data):
        return self._request('POST', path, data)

    def delete(self, path, data):
        return self._request('DELETE', path, data)

# ─── Triage Logic ─────────────────────────────────────────────────────────────

def identify_type(labels):
    """Extract type from labels. Returns (type_keyword, label_name) or None."""
    for label in labels:
        name = label.get('name', '')
        if name in ROUTING_TABLE:
            return name
    return None

def assess_scale(title, body):
    """Heuristic scale assessment."""
    title_lower = title.lower()
    if any(kw in title_lower for kw in ['全链路', '含验证', '跨模块', '跨部门']):
        return '中'
    if any(kw in title_lower for kw in ['重构', '架构', '多文件']):
        return '大'
    return '小'

def build_comment_body(issue, type_label, assignee, role_desc, scale):
    """Build Chinese-language triage comment."""
    title = issue.get('title', '(无标题)')
    number = issue.get('number', '?')

    type_display = type_label or '未知'
    reason = f'类型: {type_label} → {role_desc}' if type_label else '类型不明，需人工决策'

    return f"""## 自动分诊

**Issue**: #{number} {title}

- **类型识别**: {type_display}
- **规模评估**: {scale}
- **指派给**: @{assignee}
- **理由**: {reason}

---

> 本注释由项目牧羊人自动生成。"""

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    # 1. 加载 token
    token = load_token()
    if not token:
        print('[ERROR] 无法从 .env 读取 GITHUB_TOKEN', file=sys.stderr)
        sys.exit(1)

    gh = GitHubAPI(token)

    # 2. 验证认证
    user = gh.get('/user')
    if not user:
        print('[ERROR] GitHub 认证失败', file=sys.stderr)
        sys.exit(1)
    print(f'[INFO] 已认证为: {user.get("login")}')

    # 3. 查询指派给自己的 open issue
    issues = gh.get(f'/repos/{REPO_OWNER}/{REPO_NAME}/issues?assignee={PM_USER}&state=open&per_page=100')
    if not issues:
        print('[SILENT]')
        return

    print(f'[INFO] 发现 {len(issues)} 个待分诊 issue')

    for issue in issues:
        # 跳过 PR（GitHub API 把 PR 也返回在 /issues 里）
        if 'pull_request' in issue:
            continue

        number = issue['number']
        title = issue['title']
        body = issue.get('body') or ''
        labels = issue.get('labels', [])

        print(f'\n[ISSUE #{number}] {title}')

        # 4. 识别类型
        type_label = identify_type(labels)
        if type_label:
            assignee, role_desc = ROUTING_TABLE[type_label]
        else:
            assignee, role_desc = DEFAULT_ROUTE

        scale = assess_scale(title, body)
        print(f'  类型: {type_label or "不明"} | 规模: {scale} | 指派: {assignee}')

        # 5. 获取当前 assignee
        current_assignees = [a['login'] for a in issue.get('assignees', [])]
        if assignee in current_assignees:
            print(f'  跳过: 已指派给 {assignee}')
            continue

        # 6. 写中文 comment
        comment_body = build_comment_body(issue, type_label, assignee, role_desc, scale)
        result = gh.post(f'/repos/{REPO_OWNER}/{REPO_NAME}/issues/{number}/comments',
                         {'body': comment_body})
        if result:
            print(f'  ✓ Comment posted')
        else:
            print(f'  ✗ Comment failed')
            continue

        # 7. 两步变更 assignee
        #    7a. Remove current
        for old_assignee in current_assignees:
            gh.delete(f'/repos/{REPO_OWNER}/{REPO_NAME}/issues/{number}/assignees',
                      {'assignees': [old_assignee]})
            print(f'  ✓ Removed assignee: {old_assignee}')

        #    7b. Add new
        result = gh.post(f'/repos/{REPO_OWNER}/{REPO_NAME}/issues/{number}/assignees',
                         {'assignees': [assignee]})
        if result:
            print(f'  ✓ Assignee changed to: {assignee}')
        else:
            print(f'  ✗ Assignee change failed')

if __name__ == '__main__':
    main()
