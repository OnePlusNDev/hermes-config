# 2026-07-07 Session: urllib 正常工作的反例

## 背景

本次 cron 分诊轮询中，Python urllib 直接请求 GitHub API 正常工作（返回 HTTP 401，非 SSL 错误），推翻了此前「urllib 在 macOS 26.4 上**始终**抛出 `ssl.SSLEOFError`」的判断。

## 实际表现

| 尝试 | 结果 | 说明 |
|------|------|------|
| `urllib.request.urlopen(req)` 使用 `f"Bearer {token}"` | HTTP 401 Unauthorized | Auth header 格式错误，但网络层和 SSL 层正常 |
| 修正为 `f"token {token}"` 后重新请求 | `[]` (空列表) | 认证成功，API 正常工作 |

## 结论

- urllib 并非「始终」在 macOS 26.4 上 SSL 失败。成功与否可能取决于 Python 版本、OpenSSL 后端、或系统安全更新状态。
- 更准确的描述是「**可能**抛出 SSL 错误，遇到时改用 subprocess + curl」。
- Python 版本：3.13，macOS 26.4（Darwin）。

## 代码验证

```python
import subprocess, json, urllib.request

# 获取 token
result = subprocess.run(
    ["bash", "-c", "source ~/.hermes/profiles/demo-pm/.env && echo $GITHUB_TOKEN"],
    capture_output=True, text=True, timeout=15
)
token = result.stdout.strip()

# urllib 请求 — 正常工作
req = urllib.request.Request(
    "https://api.github.com/repos/demo-oneplusn/demo-workflow/issues" \
    "?assignee=OnePlusNPM&state=open&per_page=100",
    headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
)
with urllib.request.urlopen(req) as resp:
    issues = json.load(resp)
```
