# Grep Display Truncation Hides Full Tokens

## The Trap

During the 2026-07-25 backup run, `grep -F "ghp_" file.md` showed:

```
36:1. ... 成功提取到完整 token `[TOKEN_REDACTED]`
```

The `...` looked like a **partial/truncated token** in the file content. It was actually **terminal display wrapping** — the terminal wrapped the long line, and the model read the wrapped display as literal `...` content.

## The Reality

The file actually contained the **full 40-character token**:

```
[TOKEN_REDACTED]
```

`sed -n '36p' file.md | xxd` confirmed this — the file had the complete unredacted GitHub PAT as literal text, not a truncated/partial pattern at all.

## How to Detect

**Never trust `...` in grep output when scanning for tokens.** Always verify with an unambiguous method:

```bash
# Method 1: xxd hex dump (unambiguous)
sed -n 'LINE' file.md | xxd | head -10
# Look for sequential byte patterns, not display-wrapped text

# Method 2: Python bytes repr (most reliable)
python3 -c "
with open('file.md', 'rb') as f:
    lines = f.readlines()
for i, line in enumerate(lines, 1):
    if b'ghp_' in line:
        print(f'Line {i}: {line!r}')
"
# The !r escape shows raw bytes — no wrapping, no truncation
```

## The Three-Stage Verification Protocol

After any token redaction pass, run all three stages before committing:

### Stage 1 — Full hex/base64 patterns
```bash
grep -rnE '6768705f[0-9a-f]{20,}|R0lUSFVC[0-9A-Za-z+/=]{15,}' demo-pm/ --include='*.md' --include='*.py'
```

### Stage 2 — Full live tokens
```bash
grep -rnE 'ghp_[A-Za-z0-9]{20,}|gho_[A-Za-z0-9]{20,}' demo-pm/ --include='*.md' --include='*.py'
```

### Stage 3 — Python regex deep scan
```bash
python3 -c "
import os, re
target = '/tmp/backup/demo-pm'
results = []
for root, dirs, files in os.walk(target):
    for f in files:
        fp = os.path.join(root, f)
        rel = os.path.relpath(fp, target)
        try:
            with open(fp, 'r') as fh:
                c = fh.read()
        except:
            continue
        m1 = re.findall(r'ghp_[A-Za-z0-9]{30,}', c)
        m2 = re.findall(r'6768705f[0-9a-f]{20,}', c)
        m3 = re.findall(r'R0lUSFVC[0-9A-Za-z+/=]{20,}', c)
        if m1 or m2 or m3:
            results.append((rel, m1[:2], m2[:2], m3[:2]))
for r, m1, m2, m3 in results:
    print(f'{r}: ghp={m1} hex={m2} b64={m3}')
if not results:
    print('ALL CLEAN — no remaining full token patterns')
"
```

Stage 3 in the 2026-07-25 backup found the full token (redacted), confirming stage 1 and 2 had been misled by display truncation.

## Files Redacted in This Run

14 files across two skill directories were redacted:
- `pm-triage-cron/SKILL.md` — full hex string + partial base64
- 6 `pm-triage-cron/references/*.md` — full ghp token, hex encoding, base64 encoding
- `hermes-profile-backup/SKILL.md` — partial `[TOKEN_REDACTED]` pattern
- 3 `hermes-profile-backup/references/*.md` — partial `[TOKEN_REDACTED]` pattern
- `github-issues/references/pm-triage-cron-workflow.md` — partial pattern
