# 2026-07-13 Session: Python `open()` + `urllib.request` Succeeded

## Summary

This cron session demonstrated a clean working pattern: write a small Python script to `/tmp/` that reads `.env` via `open()` and queries GitHub API via `urllib.request`. Both steps succeeded where previous sessions reported failures (`.env` → literal `***`, urllib → SSL/handshake timeouts).

## What worked

```python
import os, json, urllib.request

with open(os.path.expanduser('~/.hermes/profiles/demo-pm/.env')) as f:
    for line in f:
        line = line.strip()
        if line.startswith('GITHUB_TOKEN=***            token = line.split('=', 1)[1]
            break

headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json'
}

# Auth verification
req = urllib.request.Request('https://api.github.com/user', headers=headers)
with urllib.request.urlopen(req) as resp:
    user = json.loads(resp.read())
# → AUTH_OK: OnePlusNPM

# Issue query
req = urllib.request.Request(
    'https://api.github.com/repos/demo-oneplusn/demo-workflow/issues?state=open&assignee=OnePlusNPM',
    headers=headers
)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read())
# → [] (no issues)
```

## Key observations

- **`.env` was NOT literal `***`** — `open()` returned the real 40-char token (ghp_...). Previous sessions' reports of `.env` containing literal `***` were either terminal display redaction (not file content) or environment-dependent.
- **urllib worked** — no SSL errors, no handshake timeouts, no 180s timeout. The intermittent nature of these failures is confirmed: sometimes it works.
- **Simpler than alternatives** — no gh auth switch, no keyring multi-account race, no bash heredoc quoting issues, no base64/xxd token extraction. Just write a .py file to /tmp/ and run it.

## Recommended approach ordering

1. **Try `gh` CLI first** (simplest, no token handling)
2. **If `gh` fails, write a Python script to /tmp/** with `open()` + `urllib.request`
3. Fall back to complex workarounds (base64, xxd, bash heredocs) only if both fail

## Results

- Query returned `[]` (no issues assigned to OnePlusNPM)
- Exited with `[SILENT]`
