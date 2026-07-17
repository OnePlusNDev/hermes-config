#!/usr/bin/env python3
"""Read memory files and retain them into hindsight, then reflect for consolidation."""
import json
import sys
import os
import urllib.request

HINDSIGHT_URL = "http://127.0.0.1:8888"
MEMORIES_DIR = os.path.expanduser("~/.hermes/profiles/demo-tester/memories")
HERMES_HOME = os.path.expanduser("~/.hermes")

def read_file(path):
    with open(path, "r") as f:
        return f.read()

def retain_items(bank_id, items):
    """Retain memory items into hindsight bank."""
    url = f"{HINDSIGHT_URL}/v1/default/banks/{bank_id}/memories/retain"
    data = json.dumps({"items": items, "async": False}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

def reflect(bank_id, query):
    """Use hindsight reflect to consolidate knowledge."""
    url = f"{HINDSIGHT_URL}/v1/default/banks/{bank_id}/reflect"
    data = json.dumps({
        "query": query,
        "budget": "low",
        "max_tokens": 4096,
        "include": {"facts": {}}
    }).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e), "text": ""}

def main():
    # Step 1: Read memory files
    memory_md = read_file(os.path.join(MEMORIES_DIR, "MEMORY.md"))
    user_md = read_file(os.path.join(MEMORIES_DIR, "USER.md"))

    # Step 2: Retain into hindsight demo-tester bank
    items = [
        {
            "content": memory_md,
            "context": "Agent MEMORY.md - operational knowledge about model config, issue handling, feishu bot, hindsight setup",
            "document_id": "demo-tester-memory-md",
            "timestamp": "2026-06-17T17:03:00Z",
            "type": "world",
            "tags": ["agent_memory", "operational"]
        },
        {
            "content": user_md,
            "context": "Agent USER.md - user profile, collaboration protocol with MigbotBoss",
            "document_id": "demo-tester-user-md",
            "timestamp": "2026-06-17T23:17:00Z",
            "type": "world",
            "tags": ["user_profile", "collaboration_protocol"]
        }
    ]
    
    print("=== Step 1: Retain memories into hindsight ===")
    result = retain_items("demo-tester", items)
    print(json.dumps(result, indent=2))

    # Step 3: Use reflect for advanced consolidation
    print("\n=== Step 2: Reflect on memories for consolidation ===")
    reflect_result = reflect("demo-tester", 
        "Consolidate and summarize the following knowledge: "
        "1. All operational configuration (model, keys, hindsight setup, feishu) "
        "2. All issue handling rules and workflows "
        "3. All testing quality standards "
        "4. User collaboration protocol with MigbotBoss "
        "5. Feishu bot configuration and communication norms "
        "Output a well-organized, de-duplicated summary grouped by category. "
        "Flag any stale or superseded entries that could be archived."
    )
    print(json.dumps(reflect_result, indent=2))

if __name__ == "__main__":
    main()
