# 2026-07-21 Cron 会话：gh CLI 挂死 + Python 独立脚本成功

## 概要

本轮 cron 轮询中，`gh` CLI 在首次调用时完全挂死（180s 超时，`exit_code=124`），而 Python 独立脚本写至 `/tmp/fetch_issues.py` 的方案成功完成查询并返回 `[]`（无待分诊任务）。

## 失败路径：`gh` 超时

```bash
# 尝试了两次 `gh issue list`，均 180s 后 exit_code=124
# 尝试了 `gh auth status`，同样超时
# `which gh` 成功（找到 /Users/oneplusn/.local/bin/gh）
```

**可能原因：** 系统 keyring 服务（`secd`）在 cron headless 环境中阻塞，`gh` 试图访问钥匙串时进入不可中断的 I/O 等待。

## 成功路径：Python `/tmp` 独立脚本

**完整工作流：**

1. **write_file 写入脚本到 /tmp (不包含 token 字面量)**：
   ```python
   # /tmp/fetch_issues.py
   import os, json, urllib.request, urllib.error
   
   env_path = os.path.expanduser("~/.hermes/profiles/demo-pm/.env")
   token = None
   with open(env_path) as f:
       for line in f:
           line = line.strip()
           if line.startswith("GITHUB_TOKEN=***               token = line.split("=", 1)[1].strip()
               break
   
   url = "https://api.github.com/repos/demo-oneplusn/demo-workflow/issues?state=open&assignee=OnePlusNPM&per_page=50"
   req = urllib.request.Request(url)
   req.add_header("Authorization", f"token {token}")
   req.add_header("Accept", "application/vnd.github.v3+json")
   req.add_header("User-Agent", "demo-pm-cron")
   
   with urllib.request.urlopen(req, timeout=30) as resp:
       data = json.loads(resp.read().decode())
       print(json.dumps(data, indent=2, ensure_ascii=False))
   ```

2. **terminal() 执行**（通过 `python3 /tmp/fetch_issues.py`）

3. **结果：`[]`** — 无待分诊任务，[SILENT] 退出

## 关键教训

### 1. `gh` 不可靠性再次确认

这不是第一次 `gh` 挂死（2026-07-20 也有 subshell 相关挂死）。**本环境下 `gh` 挂死不再是「偶发」而是「间歇性频繁」**。应始终在首次 `gh` 调用前做短超时探测：

```bash
gh --version 2>&1 | timeout 10 head -1
```

### 2. Python 独立脚本仍是最稳健的 fallback

`write_file` → `/tmp/script.py` → `terminal("python3 /tmp/script.py")` 在本 session 中零问题完成。需要注意：
- 脚本内用 `open().read()` 或 `open().readline()` 读取 `.env`，**不**在 write_file 内容中嵌入 token
- 用 `f"token {token}"` 拼接 auth header（f-string 在 write_file 中不会被脱敏，因为 `{token}` 本身不是凭据模式；之前 `{token}` 被脱敏的 case 是另一个版本的行为）
- 设置 `timeout=30` 在 urllib 层面，防止无限等待

### 3. Sibling subagent 竞态 (再次确认)

`write_file` 返回了 warning：
```
_was_modified_by_sibling_subagent: /private/tmp/fetch_issues.py was modified by sibling subagent...
```
已在 2026-07-11 和 2026-07-16 观测到。本环境并行 cron/agent 活动频繁，`/tmp/` 文件竞态仍在持续。

## 下次建议

1. 默认流程：先 `timeout 10 gh --version` 探测 gh 是否可用
2. 可用 → 走 gh CLI 路径（最简洁）
3. 挂死 → 立即降级到 Python 独立脚本路径（无需重试 gh）
4. 脚本写入 `/tmp/fetch_issues_$(date +%s).py` 避免 sibling 竞态
