# 2026-07-13 cron 会话：全量仓库健康检查模式 + gh auth switch 首次尝试成功

## 核心发现

### 1. `gh auth switch --user OnePlusNPM` 首次尝试即成功

```bash
gh auth switch --user OnePlusNPM
# → ✓ Switched active account for github.com to OnePlusNPM
```

本会话中无需「二次切换回弹」工作区。确认 race condition 是**间歇性**的——并非每次都需要回弹。

后续尝试 `gh auth status --hostname github.com --active` 确认切换成功：
```
✓ Logged in to github.com account OnePlusNPM (keyring)
```

### 2. 全量仓库健康检查模式（新发现的诊断流程）

当 `--assignee OnePlusNPM` 返回空时，执行全量查询是有价值的诊断步骤：

```bash
gh issue list --repo demo-oneplusn/demo-workflow --state open --json number,title,labels,assignees --limit 20 | python3 -c "
import json, sys
issues = json.load(sys.stdin)
for i in issues:
    assignees = [a['login'] for a in i.get('assignees',[])]
    labels = [l['name'] for l in i.get('labels',[])]
    print(f'  #{i[\"number\"]}: {i[\"title\"][:60]}')
    print(f'    Labels: {labels}')
    print(f'    Assignees: {assignees or [\"(none)\"]}')
"
```

**输出示例（本会话）：**
```
#7: [验证报告] Issue 2 独立验证
    Labels: []
    Assignees: ['OnePlusNBoss']
#5: [测试] 全链路含验证：新增 subtract(a,b) 减法函数
    Labels: ['type:feature', 'priority:normal']
    Assignees: ['OnePlusNBoss']
#4: [测试] PM→Dev 路径：新增 multiply(a,b) 乘法函数
    Labels: ['type:feature', 'priority:normal']
    Assignees: ['OnePlusNBoss']
#2: [测试] 验证 PM 分诊流程：新增 add(a,b) 加法函数
    Labels: ['type:feature', 'priority:normal']
    Assignees: ['OnePlusNBoss']
```

**结论：** 所有 4 个 open issue 均 assign 给 OnePlusNBoss，无 unassigned issue。无 PM 分诊任务 → `[SILENT]`

### 3. `.env` 文件 GITHUB_TOKEN 过期确认

- `source .env; echo $GITHUB_TOKEN` → 40 字符（有值）
- 但 curl 使用该 token 请求 `https://api.github.com/user` → 401 Bad credentials
- `gh` CLI（keyring 认证）→ 正常工作

进一步确认 `.env` 的 token 已过期（与 2026-07-13 之前 session 的发现一致）。
所有依赖 `.env` 的方案（triage_issues.py、Python subprocess + GH_TOKEN 等）均不可用。

### 4. `gh issue list --user` 无效参数确认

```bash
gh issue list --repo demo-oneplusn/demo-workflow --assignee OnePlusNPM --state open --json number,title,state,labels,assignees,body --limit 50 --user OnePlusNPM
# → unknown flag: --user
```

`gh issue list` 根本没有 `--user` 标志。指定用户应使用：
- `gh auth switch --user <TARGET>`（切换活跃账号）
- 或直接使用 `--assignee <USER>`（API 层面过滤，不依赖活跃账号）

### 5. 认证方案优先级验证

本会话再次确认认证方案优先级（按可靠性）：

| 方案 | 本会话状态 | 说明 |
|------|-----------|------|
| 🥇 直接 `gh` CLI（keyring） | ✅ 正常工作 | 无需任何前置步骤 |
| ❌ `.env` token（过期） | ❌ 401 | 所有依赖 `.env` 的方案失败 |
| ❌ `gh auth token -u` | 未测试 | 本会话未使用，但应作为写操作的兜底 |

## 仓库状态快照

- **仓库：** `demo-oneplusn/demo-workflow`
- **Open Issues：** 4 个（#2, #4, #5, #7）
- **所有 assignee：** OnePlusNBoss（全部）
- **PM 任务：** 0 个
- **Unassigned：** 0 个
