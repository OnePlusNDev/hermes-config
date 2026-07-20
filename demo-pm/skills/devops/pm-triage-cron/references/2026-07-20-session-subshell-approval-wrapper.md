# 2026-07-20 Cron 会话：Subshell Approval Wrapper 引号破坏 + 两步资源提取模式确认

## 概要

本轮 cron 会话验证了「两步资源提取」模式（`gh auth token > /tmp/file` + `GH_TOKEN=$(cat /tmp/file) gh api`）在 subshell `$(...)` 被 approval wrapper 破坏时的正确工作方式。

## 认证发现

### 多账号 keyring 快照

```bash
gh auth status 2>&1 | grep -E '(Logged|account|active)'
```

| 账号 | 活跃状态 | Token scopes |
|------|---------|-------------|
| OnePlusNDev | ✅ active | repo, read:org, read:user |
| OnePlusNTester | inactive | repo, read:org, read:user |
| JungleAssistant | inactive | repo, read:org, read:user |
| OnePlusNPM | inactive | repo, read:org, read:user |

**总账号数：** 4 个（活跃：OnePlusNDev）。PM 账号（OnePlusNPM）非活跃——本次 cron 运行正常。

### 工作流验证

#### ❌ 失败路径：直接 `$(...)` subshell

```bash
# 所有以下方式均因 approval wrapper 额外引号层而失败：
TOKEN=*** auth token --hostname github.com --user OnePlusNPM)
# → /bin/bash: eval: line 2: syntax error near unexpected token `)'
```

#### ✅ 成功路径：两步资源提取

```bash
# 第 1 步：写 token 到临时文件（不受 approval wrapper 影响）
gh auth token --hostname github.com --user OnePlusNPM > /tmp/gh_token_npm.txt
head -c 10 /tmp/gh_token_npm.txt
# → ghp_Z1SyfZ  ✅

# 第 2 步：用最小 subshell 读取
GH_TOKEN=*** /tmp/gh_token_npm.txt) gh api "repos/demo-oneplusn/demo-workflow/issues?state=open&assignee=OnePlusNPM&per_page=100" --jq 'length'
# → 0  ✅
```

#### 关于 `--jq` 数组括号的注意点

`--jq '[.[] | {number, title}]'` 的 `[]` 外层数组在 subshell + approval wrapper 组合中有时解析失败。改用 `--jq 'length'`（纯数字）或 `--jq '.[] | {key: val}'`（每行一个 JSON）可避免：

```bash
# ✅ 每行一条 JSON（无外层数组）
GH_TOKEN=*** /tmp/gh_token_npm.txt) gh api "repos/demo-oneplusn/demo-workflow/issues?state=open&per_page=5" --jq '.[] | {number, title, assignees: [.assignees[].login], labels: [.labels[].name]}'
# → {"assignees":["OnePlusNBoss"],"labels":[],"number":7,"title":"[验证报告] Issue 2 独立验证"}
# → {"assignees":["OnePlusNBoss"],"labels":["type:feature"],"number":6,"title":"feat: 新增 subtract(a, b) 减法函数并附测试"}
```

## 全量仓库快照

```python
# 5 个 open issue，全部 assign 给 OnePlusNBoss：
# #7: [验证报告] Issue 2 独立验证 → 无标签 → 已 assign 给 OBoss
# #6: feat: 新增 subtract(a, b) 减法函数并附测试 → type:feature → 已 assign 给 OBoss
# #5: [测试] 全链路含验证：新增 subtract(a,b) 减法函数 → type:feature → 已 assign 给 OBoss
# #4: [测试] PM→Dev 路径：新增 multiply(a,b) 乘法函数 → type:feature → 已 assign 给 OBoss
# #2: [测试] 验证 PM 分诊流程：新增 add(a,b) 加法函数 → type:feature → 已 assign 给 OBoss
```

## 结论

- **0 个待分诊任务** → `[SILENT]` 正确
- 两步资源提取模式成功验证——`> /tmp/file` + `$(cat /tmp/file)` 是最简免疫 subshell 破坏的路径
- `gh api "..." --jq '.[] | {fields}'` 逐行输出模式替代 `'[.[] | ...]'` 数组包装，避免花括号冲突
