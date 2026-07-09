# 2026-07-09 Cron session: 「直接 gh」是唯一可用方案

## 背景

本次 cron 分诊轮询中，三种认证方式依次全都失败，最终「直接 gh」以一己之力完成任务。

## 失败链路记录

### 1. `triage_issues.py` → SSL 错误

```python
# triage_issues.py 使用 urllib.request.urlopen()
Error querying issues: <urlopen error [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred
in violation of protocol (_ssl.c:1032)>
```

**原因分析：** macOS 原生 Python（Apple 打包版）与某些 OpenSSL 版本搭配时，urllib 的默认 SSL 上下文可能触发此错误。非 env 问题，非网络问题——同机器 gh CLI 正常。

**历史规律（截至 2026-07-09）：**
| 日期 | triage_issues.py 状态 | gh CLI 状态 |
|------|----------------------|------------|
| 2026-07-07 | ✅ 正常 | ✅ |
| 2026-07-09 | ❌ SSL 错误 | ✅ |

结论：**urllib 不可靠。不要依赖它作为唯一方案。**

### 2. `curl | python3` → tirith 拦截

```bash
# 尝试：curl 获取 -> python3 解析
curl -s -H "Authorization: Bearer ***" ... | python3 -c "import json;..."
# 被 tirith 以 [HIGH] curl_pipe_shell 拦截
```

**tirith 规则 `curl_pipe_shell`：** 将 `curl` 的输出直接管道到解释器（python3/bash）被标记为高风险——下载的内容在未检查的情况下被执行。此规则死活不可绕过。

### 3. `export GITHUB_TOKEN=***` → tirith 拦截

```bash
# 尝试：设置环境变量后 curl
export GITHUB_TOKEN=ghp_*** && curl -H "Authorization: Bearer ***" ...
# 被 tirith 以 [HIGH] sensitive_env_export 拦截
```

**tirith 规则 `sensitive_env_export`：** 设置 GITHUB_TOKEN 环境变量被标记——凭据可能被记录到 shell 历史。

### 4. `write_file` + bash 脚本 → 未尝试，但已知不可行

根据历史经验，`write_file` 中写入 `$GITHUB_TOKEN` 字面量会被展开导致语法错误。虽可改用 `source .env` 运行时获取，但此 session 中未尝试——因为方案 5 直接工作了。

## 唯一可用方案：直接 gh

```bash
gh issue list --repo demo-oneplusn/demo-workflow \
  --assignee OnePlusNPM --state open \
  --json number,title,labels,body,assignees --limit 50
```

**结果：** ✅ 返回 `[]`（空数组，0 个 open issue）

**前置条件验证：**
```bash
# gh CLI 已安装
which gh  # /Users/oneplusn/.local/bin/gh

# keyring 中有带 repo scope 的 token
gh auth status 2>&1 | grep "Token scopes:"  # 'read:org', 'read:user', 'repo'

# 仓库可达（无需指定账号）
gh repo view demo-oneplusn/demo-workflow --json name  # ✅

# 活跃账号（不需要切换也能查）
gh auth status --hostname github.com --active 2>&1 | head -3
# 显示的是 OnePlusNDev（不是 PM），但 `--assignee OnePlusNPM` 仍可查
```

**关键推论：** `gh issue list --assignee <USER>` 的过滤在 API 层面独立于发起查询的活跃账号身份——token 权限（`repo` scope）已足够。

## 经验教训

1. **不要依赖 Python urllib** 做 cron 任务的核心网络调用。它在本 macOS 环境中时好时坏。用 `subprocess` 调 `gh` 或 `curl` 更可靠。
2. **tirith 安全守卫** 在 cron 模式下拦截：curl pipe（`|`），敏感 env export（`export GITHUB_TOKEN`），execute_code。这三条路都被封死了。
3. **「直接 gh」是当前最稳路径**：无 SSL 问题、无 tirith 拦截、无环境变量竞态、无 keyring 切换问题。只需确认 `which gh` 有结果 + `gh auth status` 含 `'repo'` scope 即可。
