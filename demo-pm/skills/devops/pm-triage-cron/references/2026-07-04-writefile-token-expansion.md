# write_file 中 `$GITHUB_TOKEN` 被展开的陷阱

## 现象

在 `write_file` 写入的 Python 脚本中，如果包含 `$GITHUB_TOKEN`（例如在 f-string 或字符串中），该标记会被**展开为实际 token 值**，而非作为字面量写入文件。

这导致：

1. **语法错误**——展开后的 token 值可能包含破坏 Python 字符串语法的字符
2. **Token 泄露**——token 值被嵌入到磁盘上的脚本文件中

## 复现步骤

```python
# 错误的做法：$GITHUB_TOKEN 在 write_file content 中被展开
write_file(
    path="/tmp/triage.py",
    content="""
...
     "-H", f"Authorization: token $GITHUB_TOKEN",
...
"""
)
# 结果：$GITHUB_TOKEN 展开为实际 token → 被展开的 token 可能含特殊字符破坏语法
```

## 正确做法

**脚本不嵌入 token，而是在运行时从 .env 读取：**

```python
#!/usr/bin/env python3
import subprocess

# 运行时通过 shell 读取 .env
result = subprocess.run(
    "source ~/.hermes/profiles/demo-pm/.env > /dev/null 2>&1 && printf '%s' \"$GITHUB_TOKEN\"",
    shell=True, capture_output=True, text=True, timeout=10
)
token = result.stdout.strip()

# 然后通过 subprocess 传递
auth_header = f"Authorization: token {token}"
result = subprocess.run(
    ["curl", "-s", "-H", auth_header,
     "-H", "Accept: application/vnd.github.v3+json",
     "https://api.github.com/repos/demo-oneplusn/demo-workflow/issues"],
    capture_output=True, text=True, timeout=30
)
```

或者使用 `gh` CLI 的 `GH_TOKEN` 环境变量传递模式（更推荐）：

```python
#!/usr/bin/env python3
import json, subprocess, sys

with open('/Users/oneplusn/.hermes/profiles/demo-pm/.env') as f:
    token = None
    for line in f:
        line = line.strip()
        if line.startswith('GITHUB_TOKEN='):
            token = line[len('GITHUB_TOKEN='):]
            break

result = subprocess.run(
    ['/Users/oneplusn/.local/bin/gh', 'issue', 'list', '--repo', 'demo-oneplusn/demo-workflow',
     '--assignee', 'OnePlusNPM', '--state', 'open',
     '--json', 'number,title,labels,body,assignees,url', '--limit', '50'],
    capture_output=True, text=True, timeout=30,
    env={'GH_TOKEN': token}
)
```

## 原理

`write_file` 工具在写入内容时会对 `$VARIABLE` 模式进行 shell 级展开。无论是否在 Python 字符串内、f-string 内、或注释内，只要包含 `$XXX` 字符序列且 XXX 是环境变量名，都会被展开。

## 规避策略

- 任何脚本中不要**字面书写** `$GITHUB_TOKEN` 作为占位符
- 脚本运行时再通过 `source .env` 或 `open().readlines()` 获取 token
- 使用 `gh` 命令直接操作，避免在脚本中嵌入 token 值
