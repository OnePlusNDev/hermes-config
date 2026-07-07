# 2025-07-03 会话：GITHUB_TOKEN 环境变量阻塞 gh auth switch

## 场景

cron 定时任务触发 PM 分诊流程，`gh` CLI 默认活跃账号为 OnePlusNDev（非 PM 身份）。

## 遇到的问题

### GITHUB_TOKEN 环境变量阻塞账号切换

执行 `gh auth switch --user OnePlusNPM` 时报错：

```
The value of the GITHUB_TOKEN environment variable is being used for authentication.
To have GitHub CLI manage credentials instead, first clear the value from the environment.
```

**原因**：之前执行了 `source ~/.hermes/profiles/demo-pm/.env`，该文件包含 `GITHUB_TOKEN=***`，加载后环境变量残留，导致 gh CLI 优先使用环境变量而非 keyring 凭据。

**解决方案**：
```bash
unset GITHUB_TOKEN
gh auth switch --user OnePlusNPM
# ✓ Switched active account for github.com to OnePlusNPM
```

### execute_code 在 cron 模式下被封锁

在 cron 模式下，`execute_code` 工具会返回：
```
BLOCKED: execute_code runs arbitrary local Python (including subprocess calls that bypass shell-string approval checks).
Cron jobs run without a user present to approve it.
```

所有逻辑必须用 `terminal()` / `read_file` / `write_file` / `patch` 实现。

### gh issue list 可直接用于查询（无需 gh api | jq）

切换账号后，直接使用：
```bash
gh issue list -R demo-oneplusn/demo-workflow --assignee OnePlusNPM --state open --json number,title,labels,body,assignees,state
```
即可获得结构化结果。比 `gh api | jq` 更简洁且无管道安全守卫问题。**前提是 gh auth switch 已成功切换账号。**

### 仓库状态（轮询时刻）

- 4 个 open issue，均未 assign 给 OnePlusNPM
- #2, #4, #5 分配给 OnePlusNBoss（type:feature）
- #7 无标签、无指派
- 本次轮询结果：无待分诊任务 → [SILENT]
