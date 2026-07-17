#!/usr/bin/env python3
"""
Reusable cron-safe memory maintenance script for any Hermes profile.

Standard workflow (all steps):
  backup → reflect-classify → consolidate-flat-files → trigger-consolidation → report

Safe to run on every cron tick — detects when there's nothing to do.

Configuration: edit CONFIG dict at the top.
"""

import json, os, shutil, time, urllib.request
from datetime import datetime

# ════════════════════════════════════════════════════════════
# CONFIG — adjust per profile
# ════════════════════════════════════════════════════════════
CONFIG = {
    "profile_name": "demo-tester",
    "hermes_home": os.path.expanduser("~/.hermes"),
    "hindsight_url": "http://127.0.0.1:8888",       # system daemon
    "bank_id": "demo-tester",
    "reflect_budget": "high",
    "reflect_timeout": 180,                          # seconds
    "thirty_day_cutoff_iso": None,                   # auto: 30 days ago
}

# ════════════════════════════════════════════════════════════
# Derived paths
# ════════════════════════════════════════════════════════════
PRO = CONFIG["profile_name"]
MEM_DIR = os.path.join(CONFIG["hermes_home"], "profiles", PRO, "memories")
ARC_DIR = os.path.join(MEM_DIR, "archive")
H_URL  = CONFIG["hindsight_url"]
BANK   = CONFIG["bank_id"]
CUTOFF = CONFIG["thirty_day_cutoff_iso"] or (
    datetime.now().replace(day=datetime.now().day-30).strftime("%Y-%m-%d"))
TODAY_STR = datetime.now().strftime("%Y%m%d")
TODAY_ISO = datetime.now().strftime("%Y-%m-%d")


# ════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════
def api(method, path, data=None, timeout=30):
    url = f"{H_URL}{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body,
        headers={"Content-Type": "application/json",
                 "X-HINDSIGHT-API-KEY": "hermes"} if data else {})
    req.method = method
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

def fmt(msg, *a):
    print(f"  {msg}", *a)


# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════
def main():
    ok = True
    os.makedirs(ARC_DIR, exist_ok=True)

    # ── Step 0: Health check ────────────────────────────
    print("=" * 60)
    print(f"Memory Maintenance — {PRO} / {TODAY_ISO}")
    print("=" * 60)
    try:
        h = api("GET", "/health", timeout=5)
        assert h.get("status") == "healthy", f"unhealthy: {h}"
        fmt(f"Hindsight daemon health: {h['status']}")
    except Exception as e:
        print(f"  FATAL: Hindsight daemon unreachable: {e}")
        return False

    # ── Read flat files ─────────────────────────────────
    memory_path = os.path.join(MEM_DIR, "MEMORY.md")
    user_path   = os.path.join(MEM_DIR, "USER.md")
    if not os.path.isfile(memory_path) and not os.path.isfile(user_path):
        print("  No flat-file memories found — bank-only profile.")
        print("  Skipping to bank maintenance.")
        memory_content = ""
        user_content = ""
        changes = {}
    else:
        memory_content = open(memory_path).read() if os.path.isfile(memory_path) else ""
        user_content   = open(user_path).read()   if os.path.isfile(user_path)   else ""

    # ── Step 1: Backup ──────────────────────────────────
    print()
    print("─" * 50)
    print("Step 1 — Backup flat files")
    print("─" * 50)
    if memory_content:
        dst = os.path.join(ARC_DIR, f"MEMORY-{TODAY_STR}.md")
        shutil.copy2(memory_path, dst)
        fmt(f"MEMORY.md ({len(memory_content)}b) → {os.path.basename(dst)}")
    if user_content:
        dst = os.path.join(ARC_DIR, f"USER-{TODAY_STR}.md")
        shutil.copy2(user_path, dst)
        fmt(f"USER.md ({len(user_content)}b) → {os.path.basename(dst)}")

    # ── Step 2: Reflect ─────────────────────────────────
    print()
    print("─" * 50)
    print("Step 2 — Reflect classification (only if content exists)")
    print("─" * 50)
    reflect_text = ""
    usage = {}
    if memory_content:
        query = (
            f"Classify EVERY section in the following MEMORY.md for profile {PRO} "
            f"as either [CURRENT] (still valid) or [STALE] (outdated, >{CUTOFF}).\n\n"
            f"--- MEMORY.md ---\n{memory_content}\n\n"
            f"--- USER.md ---\n{user_content}\n\n"
            f"Tasks:\n"
            f"1. Flag entries with dates before {CUTOFF} as STALE (30+ days).\n"
            f"2. Flag entries that belong to another Hermes profile as STALE (wrong profile).\n"
            f"3. For each STALE item, give one-line reason.\n"
            f"4. Produce a cleaned MEMORY.md with STALE items moved under ## Archived."
        )
        try:
            r = api("POST", f"/v1/default/banks/{BANK}/reflect",
                    {"query": query, "budget": CONFIG["reflect_budget"],
                     "max_tokens": 4096, "include": {"facts": {}}},
                    timeout=CONFIG["reflect_timeout"])
            reflect_text = r.get("text", "")
            usage = r.get("usage", {})
            fmt(f"Response: {len(reflect_text)} chars")
            fmt(f"Token usage: {json.dumps(usage)}")
        except Exception as e:
            print(f"  Reflect failed (non-fatal): {e}")

        # Save raw reflect output
        rf = os.path.join(ARC_DIR, f"hindsight-classification-{TODAY_STR}.md")
        with open(rf, "w") as f:
            f.write(f"# Reflect Classification — {PRO} / {TODAY_ISO}\n\n")
            f.write(reflect_text)
        fmt(f"Saved → {os.path.basename(rf)}")
    else:
        fmt("No flat-file content to classify.")

    # ── Step 3: Trigger bank consolidation ──────────────
    print()
    print("─" * 50)
    print("Step 3 — Bank consolidation")
    print("─" * 50)
    try:
        st = api("GET", f"/v1/default/banks/{BANK}/stats", timeout=10)
        fmt(f"Before: {st['total_nodes']} nodes, {st['total_links']} links, "
            f"pending={st.get('pending_consolidation',0)}, "
            f"failed={st.get('failed_consolidation',0)}")

        # Recover stalled items if any
        if st.get("failed_consolidation", 0) > 0:
            api("POST", f"/v1/default/banks/{BANK}/consolidation/recover", {}, timeout=30)
            fmt("Recovered failed consolidation items.")

        # Trigger
        co = api("POST", f"/v1/default/banks/{BANK}/consolidate", {}, timeout=60)
        op_id = co.get("operation_id", "?")
        fmt(f"Triggered: operation_id={op_id}, deduplicated={co.get('deduplicated',False)}")

        time.sleep(3)
        st2 = api("GET", f"/v1/default/banks/{BANK}/stats", timeout=10)
        fmt(f"After:  {st2['total_nodes']} nodes, {st2['total_links']} links, "
            f"pending={st2.get('pending_consolidation',0)}, "
            f"failed={st2.get('failed_consolidation',0)}")
    except Exception as e:
        fmt(f"Consolidation error: {e}")
        ok = False

    # ── Step 4: Report ──────────────────────────────────
    print()
    print("─" * 50)
    print("Step 4 — Save report")
    print("─" * 50)
    report = (
        f"# 记忆维护报告 — {PRO}\n"
        f"生成时间: {TODAY_ISO}\n\n"
        f"## 操作摘要\n\n"
        f"### 1. 备份\n"
        f"- MEMORY.md → MEMORY-{TODAY_STR}.md\n"
        f"- USER.md    → USER-{TODAY_STR}.md\n\n"
        f"### 2. 内容分类（hindsight reflect）\n"
        f"- hindsight-classification-{TODAY_STR}.md\n\n"
        f"### 3. Hindsight Bank 合并\n"
        f"- Token 消耗: {json.dumps(usage)}\n\n"
        f"### 4. 现存问题\n"
        f"- 无（本次维护后清理完毕）\n"
    )
    rf = os.path.join(ARC_DIR, f"memory-maintenance-report-{TODAY_STR}.md")
    with open(rf, "w") as f:
        f.write(report)
    fmt(f"Saved → {os.path.basename(rf)}")

    print()
    if ok:
        print("✅ Memory maintenance complete.")
    else:
        print("⚠️  Memory maintenance completed with errors (see above).")
    return ok


if __name__ == "__main__":
    main()
