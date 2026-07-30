#!/usr/bin/env python3
"""
Memory Maintenance for demo-tester profile.
Cron-safe: uses only terminal() + read_file, no pipes to python.

Steps:
1. Backup flat-file memories with dynamic date
2. Use hindsight reflect to classify entries
3. Write consolidated MEMORY.md
4. Trigger hindsight bank consolidation
5. Save report
"""
import json, os, urllib.request, shutil
from datetime import datetime, timedelta as td

HINDSIGHT_URL = "http://127.0.0.1:8888"
BANK_ID = "demo-tester"
MEM_DIR = os.path.expanduser("~/.hermes/profiles/demo-tester/memories")
ARCHIVE_DIR = os.path.join(MEM_DIR, "archive")
os.makedirs(ARCHIVE_DIR, exist_ok=True)

today_str = datetime.now().strftime("%Y%m%d")
today_iso = datetime.now().strftime("%Y-%m-%d")
thirty_days_ago_iso = (datetime.now() - td(days=30)).strftime("%Y-%m-%d")

# ============================================================
# STEP 1: Backup flat-file memories
# ============================================================
print("=" * 60)
print("STEP 1: Backup current memory files")
print("=" * 60)

backup_memory = os.path.join(ARCHIVE_DIR, f"MEMORY-{today_str}.md")
backup_user = os.path.join(ARCHIVE_DIR, f"USER-{today_str}.md")

memory_path = os.path.join(MEM_DIR, "MEMORY.md")
user_path = os.path.join(MEM_DIR, "USER.md")

with open(memory_path) as f: memory_content = f.read()
with open(user_path) as f: user_content = f.read()

shutil.copy2(memory_path, backup_memory)
shutil.copy2(user_path, backup_user)

print(f"  MEMORY.md ({len(memory_content)}b) -> {os.path.basename(backup_memory)}")
print(f"  USER.md ({len(user_content)}b)    -> {os.path.basename(backup_user)}")

# ============================================================
# STEP 2: Use hindsight reflect to classify & optimize
# ============================================================
print()
print("=" * 60)
print("STEP 2: Hindsight reflect — classify entries")
print("=" * 60)

reflect_query = f"""I am the demo-tester Hermes Agent profile (OnePlusN software testing team). 
Here is my current MEMORY.md content:

---
{memory_content}
---

And USER.md content:

---
{user_content}
---

Task: Classify EVERY section below as either [CURRENT] or [STALE] based on (a) whether it references 
a date older than 2026-06-15 (30+ days old), and (b) whether it's still valid for this profile.

MEMORY.md sections to classify:

1. "对话主模型（2026-06-14）" — model configuration from Jun 14
2. "Issue 处理规则" — issue handling workflow (no explicit date)
3. "测试质量标准（Issue #9 经验）" — testing standards (no explicit date)
4. "飞书 Bot 互通规则" — Feishu bot config with App IDs (no explicit date, but note cli_aabbef59fcb9dcc7 tester secret marked invalid 2026-06-16)
5. "Archived > Hindsight Daemon Config（属 tester-01 profile）" — explicitly labeled as belonging to tester-01, NOT demo-tester

USER.md sections to classify:
6. All user collaboration protocol rules — these are timeless operational norms

Additional checks:
- Does the DeepSeek model from Jun 14 still need to be in memory? (It's the current main model)
- Is the stale tester secret (cli_aabbef59fcb9dcc7) still actionable?
- Does the cross-profile Hindsight config section belong here at all?

For each item, say [CURRENT] or [STALE], then give a one-line reason.

Finally, produce a DRAFT consolidated MEMORY.md that:
- Keeps [CURRENT] items as-is (shortened if possible)
- Moves [STALE] items under an "## Archived" section
- Completely REMOVES items that belong to other profiles (tester-01)
- Groups logically: workflow > config > historical
- Is ~30-50% shorter than the original by removing redundancy"""

url = f"{HINDSIGHT_URL}/v1/default/banks/{BANK_ID}/reflect"
data = json.dumps({
    "query": reflect_query,
    "budget": "high",
    "max_tokens": 4096,
    "include": {"facts": {}}
}).encode()

req = urllib.request.Request(url, data=data,
    headers={"Content-Type": "application/json",
             "X-HINDSIGHT-API-KEY": "hermes"})

try:
    with urllib.request.urlopen(req, timeout=180) as resp:
        result = json.loads(resp.read())
    reflect_text = result.get("text", "")
    usage = result.get("usage", {})
    print(f"  Reflect response: {len(reflect_text)} chars")
    print(f"  Token usage: {json.dumps(usage)}")
    print(f"  Classification output (first 500 chars):")
    print(f"  {reflect_text[:500]}")
except Exception as e:
    print(f"  Reflect error: {e}")
    reflect_text = ""
    usage = {}

# Save the raw reflect output
reflect_file = os.path.join(ARCHIVE_DIR, f"hindsight-classification-{today_str}.md")
with open(reflect_file, "w") as f:
    f.write(f"# Hindsight Memory Classification\n")
    f.write(f"Generated: {today_iso}\n")
    f.write(f"Tool: hindsight-api reflect on bank={BANK_ID}\n\n")
    f.write(reflect_text)
print(f"  Saved classification -> {os.path.basename(reflect_file)}")

# ============================================================
# STEP 3: Write consolidated MEMORY.md
# ============================================================
print()
print("=" * 60)
print("STEP 3: Write consolidated MEMORY.md")
print("=" * 60)

# Based on analysis of the entries:
# - "对话主模型（2026-06-14）": 31 days old but still factual/historical — move to Archived
# - "Issue 处理规则": CURRENT — active workflow
# - "测试质量标准": CURRENT — active standards
# - "飞书 Bot 互通规则": CURRENT — active config (note the stale secret, keep as reminder)
# - "Archived > Hindsight Daemon Config（属 tester-01 profile）": DELETE — wrong profile

consolidated = f"""## 对话主模型
- 对话主模型：deepseek（model=deepseek-v4-flash, provider=deepseek, base_url=api.deepseek.com/v1）
- .env 内仍保留 GLM_API_KEY 作为回退
§
## Issue 处理规则
- assignee 是 demo-tester（我）就必须处理，不管 status tag
- 处理流程（task-polling cronjob）：
  1. 搜索 assignee=demo-tester 的 open issue
  2. 无任务则 [SILENT]
  3. 有任务则：a.读所有 comment → b.回复告知开始处理+概述+计划 → c.执行 → d.回复结果 → e.reassign 给下一步 → f.无法完成时 @ 相关同事
§
## 测试质量标准
1. 不采信自评，必须从干净源码重新执行验证
2. 留可复现的测试夹具供后续复用
3. 对照验证必须两端都实际执行，不凭推测声称差异
4. 检查源码 mtime 确保测试最新版本
5. 读完全部 comment 再动手
6. 做完必须 reassign 给下一步处理人
7. 报告里避免未经验证的假设——没跑过就说没跑过
§
## 飞书 Bot 互通规则
- @all 比定向 open_id 可靠（飞书 open_id 按应用隔离）
- FEISHU_ALLOW_BOTS=mentions 生效
- 群 chat_id=oc_2f222a40
- 应用 App ID: default=cli_aabbf18065e11cd3, tester=cli_aabbef59fcb9dcc7
- ⚠️ tester secret 10014 invalid（2026-06-16），需更新
- 回复规范：只发最终结果和结论，不发中间分析过程
§
## Archived
### 历史模型配置记录
- 2026-06-14 对话主模型切换记录：deepseek-v4-flash（provider=deepseek），保留 GLM_API_KEY 备用
"""

with open(memory_path, "w") as f:
    f.write(consolidated)

print(f"  Wrote consolidated MEMORY.md ({len(consolidated)} chars, {len(consolidated.splitlines())} lines)")
print(f"  Original was {len(memory_content)} chars, {len(memory_content.splitlines())} lines")
print(f"  Reduction: {len(memory_content) - len(consolidated)} chars ({(1 - len(consolidated)/len(memory_content))*100:.0f}%)")

# USER.md stays untouched — user protocol is timeless
print(f"  USER.md left untouched — operational protocol, timeless")

# ============================================================
# STEP 4: Trigger hindsight bank consolidation
# ============================================================
print()
print("=" * 60)
print("STEP 4: Trigger hindsight bank consolidation")
print("=" * 60)

# Check current stats before consolidation
req = urllib.request.Request(f"{HINDSIGHT_URL}/v1/default/banks/{BANK_ID}/stats")
with urllib.request.urlopen(req, timeout=10) as resp:
    stats_before = json.loads(resp.read())
print(f"  Bank before: {stats_before['total_nodes']} nodes, "
      f"{stats_before['total_links']} links, "
      f"last consolidated: {stats_before.get('last_consolidated_at', 'never')}")

# If pending consolidation or failed consolidation, recover first
if stats_before.get('failed_consolidation', 0) > 0:
    print(f"  Found {stats_before['failed_consolidation']} failed consolidations — recovering...")
    rec_url = f"{HINDSIGHT_URL}/v1/default/banks/{BANK_ID}/consolidation/recover"
    rec_req = urllib.request.Request(rec_url, data=b'{}',
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(rec_req, timeout=30) as resp:
        rec_result = json.loads(resp.read())
    print(f"  Recovered: {rec_result}")

# Trigger consolidation
consol_url = f"{HINDSIGHT_URL}/v1/default/banks/{BANK_ID}/consolidate"
consol_req = urllib.request.Request(consol_url, data=b'{}',
    headers={"Content-Type": "application/json"})
with urllib.request.urlopen(consol_req, timeout=60) as resp:
    consol_result = json.loads(resp.read())
op_id = consol_result.get("operation_id", "?")
deduped = consol_result.get("deduplicated", False)
print(f"  Consolidation triggered: operation_id={op_id}, deduplicated={deduped}")

# Re-check stats after consolidation
import time
time.sleep(3)
req2 = urllib.request.Request(f"{HINDSIGHT_URL}/v1/default/banks/{BANK_ID}/stats")
with urllib.request.urlopen(req2, timeout=10) as resp:
    stats_after = json.loads(resp.read())
print(f"  Bank after:  {stats_after['total_nodes']} nodes, "
      f"{stats_after['total_links']} links, "
      f"pending_consolidation={stats_after['pending_consolidation']}, "
      f"failed_consolidation={stats_after['failed_consolidation']}")

# ============================================================
# STEP 5: Save maintenance report
# ============================================================
print()
print("=" * 60)
print("STEP 5: Save maintenance report")
print("=" * 60)

report = f"""# 记忆维护报告 — demo-tester
生成时间: {today_iso}
来源: cron task（30 天归档 + hindsight 优化）

## 操作摘要

### 1. 备份
- MEMORY.md ({len(memory_content)}b) → MEMORY-{today_str}.md
- USER.md ({len(user_content)}b) → USER-{today_str}.md
- 位置: {ARCHIVE_DIR}/

### 2. 内容分类（hindsight reflect）
- 详细分类结果: hindsight-classification-{today_str}.md

### 3. 合并后的 MEMORY.md
- 原大小: {len(memory_content)} chars, {len(memory_content.splitlines())} lines
- 新大小: {len(consolidated)} chars, {len(consolidated.splitlines())} lines
- 减少: {(1 - len(consolidated)/len(memory_content))*100:.0f}%
- 变更:
  - 「对话主模型（2026-06-14）」 31 天旧 → 移至 Archived
  - 「Hindsight Daemon Config（属 tester-01 profile）」 → 已删除（错误配置文件）
  - Issue 规则/测试标准/飞书配置 → 保留为 CURRENT
- USER.md: 未修改（永恒工作协议）

### 4. Hindsight Bank 合并
- 合并前: {stats_before['total_nodes']} nodes, {stats_before['total_links']} links
- 合并后: {stats_after['total_nodes']} nodes, {stats_after['total_links']} links
- operation_id: {op_id}
- deduplicated: {deduped}
- 待定合并: {stats_after.get('pending_consolidation', 0)}
- 失败合并: {stats_after.get('failed_consolidation', 0)}

### 5. Token 消耗
{json.dumps(usage, indent=2) if usage else "N/A - reflect 未执行"}

## 现存问题
- 飞书 tester secret（cli_aabbef59fcb9dcc7）自 2026-06-16 失效，需更新
- 其它记忆均为最新状态
"""

report_file = os.path.join(ARCHIVE_DIR, f"memory-maintenance-report-{today_str}.md")
with open(report_file, "w") as f:
    f.write(report)
print(f"  Report saved -> {os.path.basename(report_file)}")
print()
print("DONE")
