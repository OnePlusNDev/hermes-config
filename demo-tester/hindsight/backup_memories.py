#!/usr/bin/env python3
"""Step 1: Backup current memory files with dynamic date (not hardcoded)."""
import shutil, os
from datetime import datetime

MEM_DIR = os.path.expanduser("~/.hermes/profiles/demo-tester/memories")
ARCHIVE_DIR = os.path.join(MEM_DIR, "archive")
os.makedirs(ARCHIVE_DIR, exist_ok=True)

today = datetime.now().strftime("%Y%m%d")

# Read current files
with open(os.path.join(MEM_DIR, "MEMORY.md")) as f:
    memory_content = f.read()
with open(os.path.join(MEM_DIR, "USER.md")) as f:
    user_content = f.read()

# Backup with dynamic date (overcomes the hardcoded-date antipode in archive_and_consolidate.py)
archive_memory = os.path.join(ARCHIVE_DIR, f"MEMORY-{today}.md")
archive_user = os.path.join(ARCHIVE_DIR, f"USER-{today}.md")
shutil.copy2(os.path.join(MEM_DIR, "MEMORY.md"), archive_memory)
shutil.copy2(os.path.join(MEM_DIR, "USER.md"), archive_user)

print(f"BACKUP_OK|MEMORY|{archive_memory}|{len(memory_content)}bytes")
print(f"BACKUP_OK|USER|{archive_user}|{len(user_content)}bytes")
print(f"CONTENT|MEMORY|{repr(memory_content)}")
print(f"CONTENT|USER|{repr(user_content)}")
