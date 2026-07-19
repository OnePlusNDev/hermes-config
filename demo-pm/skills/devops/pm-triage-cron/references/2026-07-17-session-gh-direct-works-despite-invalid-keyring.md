# 2026-07-17 cron 会话：gh 直接查询成功，尽管所有 keyring token 显示无效

## 概要

本轮 cron 观察到 `gh auth status` 报告**所有 4 个 GitHub 账号的 keyring token 均无效**，但 `gh repo view` 和 `gh issue list` 均正常工作，顺利返回仓库信息和 issue 数据。这一结果表明：**gh CLI 在终端输出层报告「token invalid」不意味着实际 API 调用会失败**。

## 观测数据

### auth status 输出（source .env 之后）

```
github.com
  X Failed to log in to github.com account OnePlusNTester (keyring)
  - Active account: true
  - The token in keyring is invalid.

  X Failed to log in to github.com account OnePlusNDev (keyring)
  - Active account: false
  - The token in keyring is invalid.

  X Failed to log in to github.com account JungleAssistant (keyring)
  - Active account: false
  - The token in keyring is invalid.

  X Failed to log in to github.com account OnePlusNPM (keyring)
```

### 实际结果

| 命令 | 结果 | 说明 |
|------|------|------|
| `gh repo view demo-oneplusn/demo-workflow --json name,owner` | ✅ 返回 JSON 数据 | 认证通过 |
| `gh issue list --repo ... --assignee OnePlusNPM` | ✅ 返回 `[]`（无 PM 任务） | 查询正常工作 |
| `gh issue list --state open --json ...` | ✅ 返回 4 个 issue 的完整数据 | 认证通过 |

## 解释

`gh auth status` 输出的「token invalid」是针对 keyring 中存储的旧 token（可能已吊销或过期），但 gh CLI 在运行时优先使用了其他有效凭证源：

1. **环境变量 `GITHUB_TOKEN`**（从 `.env` source 加载）：即使 `gh auth status` 报告其「invalid」，实际 API 调用仍可能成功——因为 status 检查的是 token 在 keyring 中的注册状态，而非其 API 可操作性
2. **macOS keychain 层缓存**：系统 keychain 可能缓存了有效的凭证副本，gh 在 API 调用时使用该凭证而非 keyring 中的注册凭证

## 操作结论

- **核心推荐不变**：「直接 gh」是唯一可靠的一步方案。不要被 `gh auth status` 中的 ❌ 标记或「token invalid」提示影响判断——gh CLI 的 API 调用功能可能独立于 status 报告而正常工作
- 如果 `gh repo view` 成功但 `gh issue list` 返回 `[]`，说明是真无任务而非假阴性——不需要切换到其他认证方案
- 如果 `gh repo view` 也失败（返回 Could not resolve / 401），才是真正的认证问题，需要排查

## 关联

- 2026-07-13 曾确认 `.env` 的 `GITHUB_TOKEN` 过期（返回 401），但本轮（2026-07-17）gh 直接查询正常工作——说明 keyring 或环境变量 token 的状态随时间变化，每次轮询独立评估
- 验证了 `references/2026-07-16-session-gh-repo-view-precheck.md` 的预检模式可靠——`gh repo view` 成功即可继续，无需逐个验证 token
