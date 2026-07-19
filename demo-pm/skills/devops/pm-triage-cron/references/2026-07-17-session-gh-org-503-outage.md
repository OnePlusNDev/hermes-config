# 2026-07-17 Cron 会话：GitHub 组织级 503 服务中断

## 摘要

本次 cron 轮询中，`demo-oneplusn` 组织及其所有仓库的 API 均返回 HTTP 503 Service Unavailable，持续至少 5 分钟，无法完成分诊。

## 环境

- Profile: `demo-pm`
- 目标仓库: `demo-oneplusn/demo-workflow`
- 目标组织: `demo-oneplusn`（Organization 类型）
- GitHub Token: classic PAT（40 字符，含 `repo` scope）
- 认证方式: Python `urllib.request` + `Authorization: token` header
- 重试间隔: 3 秒 → 10 秒 → 15 秒（共 3-4 次）

## 观察记录

### 正常工作的端点

```
GET https://api.github.com/                         → 200
GET https://api.github.com/users/OnePlusNPM/repos   → 200
GET https://api.github.com/users/demo-oneplusn       → 200（确认是 Organization 类型）
```

### 返回 503 的端点

```
GET https://api.github.com/repos/demo-oneplusn/demo-workflow        → 503
GET https://api.github.com/repos/demo-oneplusn/demo-workflow/issues → 503
GET https://api.github.com/orgs/demo-oneplusn                       → 503
```

### 响应特征

所有 503 返回 GitHub 的 "Unicorn!" 错误 HTML 页面：

```html
<strong>No server is currently available to service your request.</strong>
```

非标准 JSON 错误格式——HTML 页面中有 unicorn 图片和样式。

### 诊断结论

- **非 token 问题**：相同 token 访问用户个人仓库成功
- **非网络问题**：GitHub API 根端点 200 OK
- **非仓库不存在**：`users/demo-oneplusn` 返回 200（组织存在）
- **是组织级别服务中断**：`orgs/demo-oneplusn` 也返回 503
- **持续 5+ 分钟**：多次重试均失败

## 组织 vs 用户：API 层级差异

| 特性 | 用户 (User) | 组织 (Organization) |
|------|-------------|---------------------|
| API 端点 | `/users/{login}` | `/orgs/{org}` |
| repos 查询 | `/users/{login}/repos` | `/orgs/{org}/repos` |
| repo 查询 | `/repos/{user}/{repo}` | `/repos/{org}/{repo}` |
| 后端路由 | 独立服务实例 | 独立服务实例 |

**关键推论：** 503 出现在 `orgs/` 和 `repos/demo-oneplusn/` 但不出现在 `users/` 端点，说明 `demo-oneplusn` 组织的后端路由实例宕机，而非整个 GitHub 服务不可用。

## 鉴别方法

```bash
# 第一步：检查根端点和用户端点（预期 200）
curl -s -o /dev/null -w "%{http_code}" https://api.github.com/
curl -s -o /dev/null -w "%{http_code}" https://api.github.com/users/demo-oneplusn

# 第二步：检查 org 端点和 repo 端点（如 503 则确认 org 级中断）
curl -s -o /dev/null -w "%{http_code}" https://api.github.com/orgs/demo-oneplusn
curl -s -o /dev/null -w "%{http_code}" https://api.github.com/repos/demo-oneplusn/demo-workflow

# 第三步：检查 GitHub 状态页
curl -s https://www.githubstatus.com/api/v2/summary.json | python3 -m json.tool
```

## 对未来的影响

1. 首次发现此错误模式，需在 PM 分诊 cron 中增加 503 检测与报告逻辑
2. 区分「无 issue = 正常静默退出」和「API 503 = 需通知用户」两种场景
3. 单次 503 可能短暂，多次重试（3次+）仍失败时才确认为持续中断
