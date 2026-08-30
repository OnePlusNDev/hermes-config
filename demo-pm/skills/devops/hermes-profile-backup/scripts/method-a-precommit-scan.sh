#!/usr/bin/env bash
# Method A pre-commit push-protection scan — run from the cloned repo root
# (after rsync, before `git add -A`). Scans ALL modified/new files for token
# patterns and, on a hit, dumps the actual bytes to detect display truncation
# (repr() masking a full token).
#
# NOTE: preflight-backup-scan.py (scripts/) is the real security gate — it
# computes the M/A/D diff vs remote and scans ONLY upload candidates. This
# bash block is the Method A belt-and-suspenders check. Extracted from SKILL.md
# on 2026-08-29 to slim the doc; keep patterns in sync with preflight script.
#
# The local profile's skill reference docs may contain full unredacted tokens
# that rsync imported. Scan and redact BEFORE staging.
echo "=== Scanning for push protection triggers ==="
TARGETS=$( { git diff --name-only; git diff --name-only --cached; } 2>/dev/null | grep -E '\.(md|py|yaml|yml|json)$' | sort -u | head -50 )
if [ -n "$TARGETS" ]; then
  for f in $TARGETS; do
    [ -f "$f" ] || continue
    if grep -qE 'ghp_[A-Za-z0-9]{20,}|6768705f[0-9a-f]{20,}|R0lUSFVC[0-9A-Za-z+/=]{25,}|sk-[A-Za-z0-9]{20,}' "$f" 2>/dev/null; then
      echo "⚠️  TRIGGER in $f — inspecting actual bytes..."
      # Check if this is display truncation (repr() masking a full token)
      python3 -c "
import re
with open('$f', 'rb') as fh:
    data = fh.read()
text = data.decode('utf-8', errors='replace')
pat = re.compile(r'ghp_[A-Za-z0-9]{20,}|6768705f[0-9a-f]{30,}|R0lUSFVC[0-9A-Za-z+/=]{25,}')
for m in pat.finditer(text):
    print(f'  FULL TOKEN at pos {m.start()}: hex={m.group().encode().hex()}')
"
    fi
  done
fi
echo "=== Scan complete ==="
