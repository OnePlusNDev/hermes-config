#!/usr/bin/env python3
"""
Archive old memory files, then use hindsight reflect for consolidation.
"""
import json
import os
import datetime
import urllib.request
import urllib.error

HERMES_PROFILE = os.path.expanduser("~/.hermes/profiles/demo-tester")
MEMORIES_DIR = os.path.join(HERMES_PROFILE, "memories")
ARCHIVE_DIR = os.path.join(MEMORIES_DIR, "archive")
HINDSIGHT_URL = "http://127.0.0.1:8888"
BANK_ID = "demo-tester"

def main():
    today = datetime.date.today().isoformat()  # 2026-07-10
    
    # ---- Step 1: Archive old memory files ----
    print("=== Archiving Old Memory Files ===")
    
    # Backup MEMORY.md (created Jun 17, ~23 days old)
    memory_path = os.path.join(MEMORIES_DIR, "MEMORY.md")
    user_path = os.path.join(MEMORIES_DIR, "USER.md")
    
    memory_content = open(memory_path).read()
    user_content = open(user_path).read()
    
    # Archive: rename with date suffix
    archive_memory = os.path.join(ARCHIVE_DIR, f"MEMORY-20260617.md")
    archive_user = os.path.join(ARCHIVE_DIR, f"USER-20260617.md")
    
    with open(archive_memory, "w") as f:
        f.write(memory_content)
    print(f"Archived MEMORY.md -> {archive_memory} ({len(memory_content)} bytes)")
    
    with open(archive_user, "w") as f:
        f.write(user_content)
    print(f"Archived USER.md -> {archive_user} ({len(user_content)} bytes)")
    
    # ---- Step 2: Use hindsight reflect for consolidation ----
    print("\n=== Hindsight Consolidation ===")
    
    consolidation_query = (
        "I am consolidating operational memory files. "
        "Based on the following knowledge, produce a consolidated, de-duplicated, "
        "and organized summary grouped by category. "
        "Flag outdated entries that should be archived.\n\n"
        f"--- MEMORY.md ({len(memory_content)} chars) ---\n"
        f"{memory_content}\n\n"
        f"--- USER.md ({len(user_content)} chars) ---\n"
        f"{user_content}\n\n"
        "Output: A well-organized, consolidated knowledge doc in markdown format. "
        "Use these categories:\n"
        "1. # Model & Provider Config\n"
        "2. # Issue Handling Workflow\n"
        "3. # Testing Quality Standards\n"
        "4. # Hindsight / Daemon Config (archive these)\n"
        "5. # Feishu Bot Config (archive stale entries)\n"
        "6. # User Collaboration Protocol\n\n"
        "For archived items, put them under ## Archived (historical reference).\n"
        "The result should be ~40-60% shorter than the input by removing redundancy and stale entries."
    )
    
    url = f"{HINDSIGHT_URL}/v1/default/banks/{BANK_ID}/reflect"
    data_json = json.dumps({
        "query": consolidation_query,
        "budget": "high",
        "max_tokens": 4096,
        "include": {"facts": {}}
    }).encode()
    
    try:
        req = urllib.request.Request(url, data=data_json, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
        
        reflect_text = result.get("text", "")
        print(f"Reflect response ({len(reflect_text)} chars)")
        
        # Save the consolidation
        reflect_file = os.path.join(ARCHIVE_DIR, f"hindsight-consolidation-{today}.md")
        with open(reflect_file, "w") as f:
            f.write(f"# Hindsight Consolidation Report\n")
            f.write(f"Generated: {today}\n")
            f.write(f"Source: MEMORY.md (2026-06-17) + USER.md (2026-06-17)\n\n")
            f.write(reflect_text)
        
        size = os.path.getsize(reflect_file)
        print(f"Consolidation saved to {reflect_file} ({size} bytes)")
        
    except Exception as e:
        print(f"Hindsight reflect error (expected - bank may still be processing): {e}")
        # Write a simpler consolidation manually
    
    # ---- Step 3: Write consolidated MEMORY.md ----
    print("\n=== Writing Consolidated MEMORY.md ===")
    
    # Consolidate based on analysis
    consolidated = """## 对话主模型（2026-06-14）
- 对话主模型已切换为 deepseek（model=deepseek-v4-flash, provider=deepseek, base_url=api.deepseek.com/v1）
- .env 内仍保留 GLM_API_KEY 作为回退
§
## Issue 处理规则
- assignee 是 demo-tester（我）就必须处理，不管 status tag
- 处理流程（task-polling cronjob）：
  1. 搜索 assignee=demo-tester 的 open issue
  2. 无任务则 [SILENT]
  3. 有任务则：a.读所有 comment → b.回复告知开始处理+概述+计划 → c.执行 → d.回复结果 → e.reassign 给下一步 → f.无法完成时 @ 相关同事
§
## 测试质量标准（Issue #9 经验）
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

## Archived (historical, profile-specific)
### Hindsight Daemon Config（属 tester-01 profile，不适用于 demo-tester）
- 4 daemon 以 --daemon --idle-timeout 86400 启动，自管 PG
- 端口: tester-01=9177, pm-01=9178, dev-01=9179, rev-01=9180
- 每个 profile 在 home/.hindsight/profiles/ 下有独立 metadata.json + env
"""

    new_memory_path = os.path.join(MEMORIES_DIR, "MEMORY.md")
    with open(new_memory_path, "w") as f:
        f.write(consolidated)
    print(f"New MEMORY.md written ({len(consolidated)} bytes)")
    
    # USER.md stays as-is (user preferences don't age out quickly)
    print("USER.md preserved (no changes needed)")

if __name__ == "__main__":
    main()
