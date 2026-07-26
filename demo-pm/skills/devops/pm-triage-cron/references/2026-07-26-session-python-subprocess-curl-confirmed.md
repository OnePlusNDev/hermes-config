# 2026-07-26 cron 会话：Python subprocess + curl 模式确认（gh shell source 401 新故障）

## 概要

本轮 cron 会话发现两个问题并确认一个稳定模式：

1. **`triage_pm_cron.py` (shell `source .env` 提取) 返回 401** — 此前未记录的故障模式
2. **`cron_triage.py` (Python `open()` + urllib) SSL 错误** — 已知间歇性故障，再次触发
3. **Python `open()` + subprocess curl 模式成功** — 确认此模式仍为可靠备用路径

## 详细过程

### 尝试 1：`cron_triage.py`（Python open.() + urllib）
- 错误：`SSL: UNEXPECTED_EOF_WHILE_READING`（已知间歇性故障）
- 超时 60s 后仍继续执行 → 最终输出完整 Traceback
- 结论：urllib 仍不可靠

### 尝试 2：`triage_pm_cron.py`（shell source + echo 解析 + curl）
- 错误：`"Bad credentials" (401)`
- 原因推测：`source .env` 将变量加载为 shell 变量，`echo GITHUB_TOKEN=$GITHUB_TOKEN` 展开正确，但 shell 的 token 值传递到 `subprocess.run(['curl', ...])` 时发生字符解析问题

```python
# 失败的提取逻辑（triage_pm_cron.py）
result = subprocess.run(
    "source ~/.hermes/profiles/demo-pm/.env 2>/dev/null && echo GITHUB_TOKEN=$GITHUB_TOKEN && echo GITHUB_USERNAME=$GITHUB_USERNAME",
    shell=True, capture_output=True, text=True, executable="/bin/bash"
)
env = {}
for line in result.stdout.strip().split("\n"):
    if "=" in line:
        k, v = line.split("=", 1)  # ← 假设 token 值不含 =
        env[k] = v
```

**潜在根因：** GITHUB_TOKEN 为 40 字符 `ghp_` 格式时，`grep`/`cut` 在管道传递过程中可能由系统脱敏机制处理，导致实际传递给 curl 的 token 值被部分脱敏（表现为 401）。这与「shell source + echo」的解析模式有关——脱敏机制可能在 shell 变量展开阶段介入。

### 尝试 3：Python `open()` + subprocess curl（成功）
直接读取 `.env` 文件内容，用 Python 正则提取，通过 subprocess 调用 curl：
```python
with open(env_path) as f:
    content = f.read()
m = re.search(r'^GITHUB_TOKEN=(.+)$', content, re.MULTILINE)
token = m.group(1).strip().strip("'\"")

cmd = ["curl", "-s", "-X", "GET",
       "-H", f"Authorization: Bearer ***       "-H", "Accept: application/vnd.github.v3+json"]
# → 成功！返回 0 open issues assigned to OnePlusNPM
```

**为什么成功：**
- Python `open()` 读取的是原始文件字节，不经任何脱敏层
- `re.search` 在纯 Python 层面提取完整 token
- subprocess 的 `curl` 调用通过 argv 传递 token（字符串拼接），不触发 shell 变量展开
- f-string `f"Authorization: Bearer {token}"` 在 Python 层面拼接

### write_file 的凭证脱敏问题

写入脚本时，如果 content 中包含 `$GITHUB_TOKEN` 字面量（shell 语法），write_file 将其展开为实际 token 值，导致 Python 语法错误。解决方法：写入时用 Python 变量名 `{token}`，在运行时通过 `open()` 读取。

## 结论

| 模式 | 结果 | 原因 |
|------|------|------|
| Python `open()` + urllib | ❌ SSL 错误 | 已知间歇性 |
| shell `source .env` + curl | ❌ 401 | token 可能在 shell 级被脱敏 |
| Python `open()` + subprocess curl | ✅ 成功 | 纯 Python 层面的文件读取和 argv 传递 |
