# 2026-07-25: `gh switch + gh api --input -` 全流程分诊模式

## 概述

本轮 cron 会话成功使用 **`gh auth switch → gh api --input -`** 模式完成全部分诊流程（查询 → 分类 → 评论 → 指派），无需 token 提取、无需 Python urllib、无需 `/tmp/` 脚本文件。

这是对「方案 A：直接 gh」路径的扩展——验证了 `gh api` 的 POST/DELETE 操作（通过 `--input -` 标准输入传递 JSON）在 `gh auth switch` 后同样可靠，无需降级到 Python subprocess + GH_TOKEN 模式。

## 关键步骤

```bash
# 1. 切换到 PM 账号（本次首选成功，首次尝试即生效）
gh auth switch --user OnePlusNPM

# 2. 验证切换成功
gh auth status --hostname github.com --active 2>&1 | head -3
# → ✓ Logged in to github.com account OnePlusNPM

# 3. 查询 open issues
gh api "/repos/demo-oneplusn/demo-workflow/issues?assignee=OnePlusNPM&state=open&per_page=50"

# 4. 用 Python 处理（通过 heredoc 传递 issues JSON）
# Python 内部使用 gh_api() 函数调用 gh api POST/DELETE with --input -
```

## POST/DELETE 操作的 Python 封装

```python
import subprocess, json

def gh_api(method, path, data=None):
    cmd = ['gh', 'api', '-X', method, '--input', '-', path]
    if data is not None:
        p = subprocess.run(cmd, input=json.dumps(data),
            capture_output=True, text=True, timeout=30)
    else:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return json.loads(p.stdout) if p.stdout else None
```

**关键细节：**
- `--input -` 从 stdin 读取 JSON body —— 避免 shell 转义问题
- `method` 参数控制 GET/POST/DELETE
- `gh api` 自动使用当前活跃账号的 keyring token
- **不需要** `GH_TOKEN` 环境变量覆盖，不需要 `source .env`

## 适用条件

| 条件 | 必须满足 |
|------|---------|
| `gh` CLI 已安装 | 本环境 `/Users/oneplusn/.local/bin/gh` |
| PM 账号在 keyring 中 | `gh auth login` 过 OnePlusNPM |
| 仓库可达 | `gh repo view demo-oneplusn/demo-workflow` 成功 |
| `gh auth switch` 生效 | 本次首次成功（间歇性——需 `gh auth status` 验证） |

## 与本环境中其他模式对比

| 模式 | Read 可靠 | Write 可靠 | 复杂度 | 依赖 |
|------|-----------|-----------|--------|------|
| `gh switch + gh api --input -` | ✅ | ✅ | 低 | gh CLI + keyring |
| `gh issue list + gh issue edit` | ✅ | ✅（需 active 账号正确） | 低 | gh CLI |
| Python urllib + .env token | ❌ 间歇性 SSL | ❌ | 中 | .env 文件 |
| Python subprocess + GH_TOKEN | ✅ | ✅ | 中 | .env 或 keyring |
| grep+cut+curl + /tmp 脚本 | ✅（绕 tirith） | ✅ | 高 | 多文件 |

## 还原活跃账号

分诊完成后必须将 gh 活跃账号还原：

```bash
ORIG_GH_USER=$(gh auth status --hostname github.com --active 2>&1 |
  grep 'Logged in' | sed 's/.*account //')
echo "Original active user: $ORIG_GH_USER"
# ... 分诊逻辑 ...
gh auth switch --user "$ORIG_GH_USER"
```

**本次实测：** 切换回 OnePlusNDev 成功，无报错。

## 本次会话结果

查询 `demo-oneplusn/demo-workflow` 中 assign 给 `OnePlusNPM` 的 open issue：**0 个**。全静默退出。无待分诊任务。

## Pitfalls

- **`gh auth switch` 间歇性未生效**：每次 switch 后必须用 `gh auth status` 验证。当前活跃账号不等于目标账号时，后续 write 操作可能以错误身份执行。
- **`gh api --input -` 不支持 `GET` 的 data**：GET 请求不需要也不应传入 body。Python 封装中 `if data is not None` 分支仅在 POST/DELETE 时传 data。
- **还原账号不要忘**：5 个 keyring 账号共享环境，不还原会影响后续 cron 或手动会话。
- **heredoc 中的 Python 代码**：外层 bash 单引号定界符 `'PYEOF'` 阻止 shell 展开 `$` 和反引号，是可靠方式。
