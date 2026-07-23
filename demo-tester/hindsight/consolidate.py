#!/usr/bin/env python3
"""
Use hindsight files/retain endpoint to upload memories as documents,
then reflect to consolidate.
"""
import json
import os
import urllib.request
import io

HINDSIGHT_URL = "http://127.0.0.1:8888"
BANK_ID = "demo-tester"

def main():
    # Read the memory files
    mem_dir = os.path.expanduser("~/.hermes/profiles/demo-tester/memories")
    memory_md = open(os.path.join(mem_dir, "MEMORY.md")).read()
    user_md = open(os.path.join(mem_dir, "USER.md")).read()

    # First, try direct reflect with context (since the reflect endpoint works)
    print("=== Step 1: Reflect with memory context for consolidation ===")
    
    query = f"""I am the demo-tester agent (OnePlusN software testing team). 
Here is my current MEMORY.md content:

---
{memory_md[:1500]}
---

And USER.md content:

---
{user_md}
---

Please consolidate and optimize this knowledge. For each category below, either confirm it's still current or flag it as stale/archivable:

1. **Model Config**: Is the DeepSeek model + key setup still valid?
2. **Issue Handling Rules**: Are these still active and correct?
3. **Testing Standards**: From Issue #9 - are these still current best practices?
4. **Hindsight Setup** (Jun 17): This is about the tester-01 profile which is separate from demo-tester - flag as stale for this profile.
5. **Feishu Config**: App IDs, open IDs, secret expiry - flag stale entries.
6. **User Protocol**: Collaboration rules with MigbotBoss.

Output a consolidated, de-duplicated version suitable as the new MEMORY.md file. 
Group by {{{{category: rules, category: config, category: workflow}}}}.
Mark items that should be archived with [ARCHIVE] prefix."""

    url = f"{HINDSIGHT_URL}/v1/default/banks/{BANK_ID}/reflect"
    data = json.dumps({
        "query": query,
        "budget": "high",
        "max_tokens": 4096,
        "include": {"facts": {}}
    }).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
        print(json.dumps({"response": result.get("text","")[:200], "usage": result.get("usage")}, indent=2))
    except Exception as e:
        print(f"Reflect error: {e}")

if __name__ == "__main__":
    main()
