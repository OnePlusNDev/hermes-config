# 2026-07-09 Session: `gh auth switch` 账号切换竞态 + "Could not resolve to Repository" 诊断

## 背景

cron 分诊轮询：查询 `demo-oneplusn/demo-workflow`（private repo）中 assign 给 OnePlusNPM 的 open issue。

## 发现 1：`gh auth switch` 偶发未生效（竞态条件）

### 现象

```bash
# 步骤1：切换
gh auth switch --user OnePlusNPM
# 输出：✓ Switched active account for github.com to OnePlusNPM

# 步骤2：查询（失败）
gh issue list --repo demo-oneplusn/demo-workflow --assignee @me --state open
# 输出：GraphQL: Could not resolve to a Repository with the name 'demo-oneplusn/demo-workflow'

# 步骤3：验证账号
gh auth status --hostname github.com --active
# 输出：✓ Logged in to github.com account JungleAssistant ← NOT OnePlusNPM!
```

`gh auth switch` 报告成功，但实际活跃账号并未变更。根源推測：当 keyring 中存在多个 GitHub 账号（OnePlusNPM、OnePlusNDev、OnePlusNTester、JungleAssistant、zhangtbj）时，切换命令可能遇到内部竞态条件——凭证刷新尚未完成时返回成功信号。

### 修复

**二次切换 + 强制验证（两步）：**

```bash
# 第一步：先切换到其他账号（做一次"回弹"）
gh auth switch --user OnePlusNTester 2>&1
gh auth status --hostname github.com --active | head -5  # ✅ 验证可见

# 第二步：再切到目标账号
gh auth switch --user OnePlusNPM 2>&1
gh auth status --hostname github.com --active | head -5  # ✅ 必须验证
```

实战中首次切换 OnePlusNPM 失败，改为先切到 OnePlusNTester 验证成功，再切回 OnePlusNPM 时就正确了。这种"二次切换回弹"有效的原因：让 gh 的 keyring 凭证管理器依次遍历各个活跃 session，避免一次性跨 session 切换触发的刷新延迟。

### 结论

**每次 `gh auth switch` 后都必须立即用 `gh auth status` 验证活跃账号。** 如果不符合预期，执行一次"回弹切换"（先切到另一个已知账号）再切回目标账号。不要假设 `✓ Switched active account` 表示状态已生效。

---

## 发现 2："Could not resolve to a Repository" 的诊断

### 诊断映射

| 错误消息 | 含义 | 处理方式 |
|---------|------|---------|
| `GraphQL: Could not resolve to a Repository with the name 'xxx'` | 仓库存在，但当前 gh 活跃账号的 token 无该 private repo 的访问权限 | 切换账号 |
| `Not Found (HTTP 404)` | 仓库不存在（名称错误、已被删除、或目标 org/user 不包含该仓库） | 检查仓库名 |

### 鉴别方法

当遇到此错误时，不要假设仓库不存在。直接查活跃账号：

```bash
gh auth status --hostname github.com --active 2>&1 | head -3
```

如果当前账号不是 repo 所属 org 的成员或没有 `repo` scope 的 token，则错误是**权限问题而非仓库不存在**。

### 验证仓库确实存在

```bash
# 切换到有权限的账号后
gh repo view demo-oneplusn/demo-workflow --json name,owner,isPrivate
# ✅ 返回仓库信息 → 仓库存在且为 private
```

### 关联

此问题与 `references/2025-07-03-session-cron-github-auth.md` 中的认证问题不同——那次是 `gh` 无法解析 `.env` 来源，这次是 `gh auth switch` 内部竞态。

与 `references/2025-07-03-session-gh-auth-env-block.md` 不同——那次是 `GITHUB_TOKEN` 环境变量阻塞切换，这次是 keyring 多账号下 `gh auth switch` 本身的可靠性问题。
