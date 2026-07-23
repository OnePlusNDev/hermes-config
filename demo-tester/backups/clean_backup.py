import base64, json, subprocess, os, sys, glob

profile_dir = os.path.expanduser("~/.hermes/profiles/demo-tester")
prefix = "demo-tester"

def gh_api(method, path, data=None):
    cmd = ["gh", "api", path, "--method", method]
    if data:
        cmd.extend(["--input", "-"])
        proc = subprocess.run(cmd, input=json.dumps(data).encode(), capture_output=True, timeout=30)
    else:
        proc = subprocess.run(cmd, capture_output=True, timeout=30)
    if proc.returncode != 0:
        err = proc.stderr.decode().strip()[:300]
        print(f"  gh error: {err}", file=sys.stderr)
        return None
    if proc.stdout:
        return json.loads(proc.stdout)
    return {}

def get_sanitized_file_list():
    """Get files that should be backed up (no runtime/sensitive files)."""
    exclude_patterns = [
        ".env", ".hermes_history", ".skills_prompt_snapshot.json", ".update_check",
        "auth.json", "auth.lock", "state.db", "state.db-shm", "state.db-wal",
        ".jobs.lock", ".tick.lock", ".DS_Store", "gateway.lock", "gateway.pid",
        "gateway_state.json", "ticker_heartbeat", "ticker_last_success",
        "ollama_cloud_models_cache.json", "provider_models_cache.json",
        "models_dev_cache.json", "processes.json", "fetch_issues.py",
        "sessions.db", "check_issues.py"
    ]
    exclude_dirs = [
        "audio_cache", "cache", "cron/output", "workspace", "skins", 
        "backups", "desktop", "hindsight", "home", "logs", "memories",
        "sessions", "plugins"
    ]
    # Exclude backup files
    exclude_suffixes = [".bak"]
    
    results = []
    for root, dirs, files in os.walk(profile_dir):
        # Skip excluded dirs by name
        rel_root = os.path.relpath(root, profile_dir)
        if rel_root == ".":
            rel_root_parts = []
        else:
            rel_root_parts = rel_root.split(os.sep)
        
        # Check if any part of the path is in exclude_dirs
        if any(p in exclude_dirs for p in rel_root_parts):
            dirs[:] = []
            continue
        
        # Filter out excluded dirs for traversal
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith(".")]
        
        for f in files:
            if f in exclude_patterns:
                continue
            if any(f.endswith(s) for s in exclude_suffixes):
                continue
            
            full_path = os.path.join(root, f)
            rel_path = os.path.join(rel_root, f) if rel_root else f
            
            # Skip binary files
            try:
                with open(full_path, "rb") as fh:
                    chunk = fh.read(8192)
                if b"\x00" in chunk:
                    continue
            except:
                continue
            
            results.append((full_path, prefix + "/" + rel_path))
    
    return results

def create_tree_entries_recursive(base_prefix, base_dir):
    """Create tree entries for a directory by listing files."""
    entries = []
    for root, dirs, files in os.walk(base_dir):
        rel_root = os.path.relpath(root, base_dir)
        if rel_root == ".":
            rel_path_base = base_prefix
        else:
            rel_path_base = base_prefix + "/" + rel_root
        
        # Skip excluded dirs
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in (
            "audio_cache", "cache", "cron/output", "workspace", "skins",
            "backups", "desktop", "hindsight", "home", "logs", "memories",
            "sessions", "plugins", "node_modules", "__pycache__", ".git"
        )]
        
        for f in files:
            if f in (".env", ".hermes_history", ".skills_prompt_snapshot.json", 
                     ".update_check", "auth.json", "auth.lock", "state.db",
                     "state.db-shm", "state.db-wal", ".jobs.lock", ".tick.lock",
                     ".DS_Store", "gateway.lock", "gateway.pid", "gateway_state.json",
                     "ticker_heartbeat", "ticker_last_success",
                     "ollama_cloud_models_cache.json", "provider_models_cache.json",
                     "models_dev_cache.json", "processes.json",
                     "sessions.db", "check_issues.py", ".gitignore"):
                continue
            if any(f.endswith(s) for s in [".bak"]):
                continue
            
            full_path = os.path.join(root, f)
            
            # Skip binary files
            try:
                with open(full_path, "rb") as fh:
                    chunk = fh.read(8192)
                if b"\x00" in chunk:
                    continue
            except:
                continue
            
            tree_path = os.path.join(rel_path_base, f) if rel_path_base else base_prefix + "/" + f
            entries.append((full_path, tree_path))
    
    return entries

# Step 1: Get latest commit
print("Step 1: Getting latest commit...")
ref = gh_api("GET", "repos/OnePlusNPM/hermes-config/git/refs/heads/main")
latest_sha = ref["object"]["sha"]
print(f"  Latest commit: {latest_sha}")

# Step 2: Get the root tree to find existing entries
print("Step 2: Getting root tree...")
commit = gh_api("GET", f"repos/OnePlusNPM/hermes-config/git/commits/{latest_sha}")
root_tree_sha = commit["tree"]["sha"]
print(f"  Root tree: {root_tree_sha}")

root_tree = gh_api("GET", f"repos/OnePlusNPM/hermes-config/git/trees/{root_tree_sha}")
existing_entries = root_tree["tree"]
print(f"  Existing entries: {[e['path'] for e in existing_entries]}")

# Separate the demo-tester entry (to replace) from others (to keep)
other_entries = [e for e in existing_entries if e["path"] != prefix]
print(f"  Keeping entries: {[e['path'] for e in other_entries]}")

# Step 3: Create clean demo-tester tree
print("\nStep 3: Creating clean demo-tester file blobs...")
file_entries = create_tree_entries_recursive(prefix, profile_dir)
print(f"  Found {len(file_entries)} files to back up")

# Create blobs for each file
blob_map = {}  # rel_path -> sha
for full_path, tree_path in file_entries:
    with open(full_path, "rb") as fh:
        content = fh.read()
    content_b64 = base64.b64encode(content).decode()
    
    blob_data = {"content": content_b64, "encoding": "base64"}
    blob = gh_api("POST", "repos/OnePlusNPM/hermes-config/git/blobs", blob_data)
    if blob and "sha" in blob:
        blob_map[tree_path] = blob["sha"]
        print(f"  OK: {tree_path}")
    else:
        print(f"  FAIL: {tree_path}")

if not blob_map:
    print("FATAL: No blobs created")
    sys.exit(1)

# Step 4: Create tree entries organized by depth (subdirectories first)
print("\nStep 4: Creating directory trees...")

# Group files by directory
from collections import defaultdict
dir_groups = defaultdict(list)
for tree_path, sha in blob_map.items():
    parts = tree_path.split("/")
    if len(parts) > 2:  # Has subdirectory
        dir_path = "/".join(parts[:2])
        dir_groups[dir_path].append((tree_path, sha))
    else:
        dir_groups[tree_path.rsplit("/", 1)[0] if "/" in tree_path else tree_path].append((tree_path, sha))

# Group subdirectory entries
sub_trees = {}
group_by_parent = defaultdict(list)
for tree_path, sha in blob_map.items():
    parts = tree_path.split("/")
    # demo-tester/file -> parent is demo-tester
    # demo-tester/skills/category/X/SKILL.md -> parent is demo-tester/skills/category
    if len(parts) > 2:
        # e.g. demo-tester/skills/category/X/SKILL.md
        # parent = demo-tester/skills/category/X for blob
        # We need tree entries for intermediate dirs
        parent = "/".join(parts[:-1])
        sub_trees[tree_path] = {"path": tree_path, "mode": "100644", "type": "blob", "sha": sha}

# Actually, this tree construction is getting complex. Let me use the simpler approach:
# Create one flat list of tree entries, and let the API handle subtree creation.
# Actually the git tree API can handle this if we just pass all entries as blobs.

# Let me try a simpler approach: create ONE tree with ALL entries as flat paths
print("  Creating flat tree with all file entries...")
demo_tester_tree_entries = []
for tree_path, sha in blob_map.items():
    entry = {
        "path": tree_path,
        "mode": "100644",
        "type": "blob",
        "sha": sha
    }
    demo_tester_tree_entries.append(entry)

# For subdirectories, we need tree entries too. 
# Actually, git trees create intermediate directories automatically 
# when you have nested paths in blobs. So we don't need explicit tree entries.

# Create the git tree
tree_data = {"tree": demo_tester_tree_entries}
demo_tree = gh_api("POST", "repos/OnePlusNPM/hermes-config/git/trees", tree_data)
if not demo_tree or "sha" not in demo_tree:
    print("FAILED: Could not create demo-tester tree")
    sys.exit(1)
demo_tester_tree_sha = demo_tree["sha"]
print(f"  demo-tester tree: {demo_tester_tree_sha}")

# Step 5: Create the root tree (replacing demo-tester with our clean tree)
print("\nStep 5: Creating root tree...")
new_root_entries = list(other_entries)
new_root_entries.append({
    "path": prefix,
    "mode": "040000",
    "type": "tree",
    "sha": demo_tester_tree_sha
})

root_tree_data = {"tree": new_root_entries}
new_root = gh_api("POST", "repos/OnePlusNPM/hermes-config/git/trees", root_tree_data)
if not new_root or "sha" not in new_root:
    print("FAILED: Could not create root tree")
    sys.exit(1)
new_root_sha = new_root["sha"]
print(f"  New root tree: {new_root_sha}")

# Step 6: Create commit
print("\nStep 6: Creating commit...")
commit_data = {
    "message": "backup: demo-tester profile config (sanitized - no runtime/sensitive files)",
    "tree": new_root_sha,
    "parents": [latest_sha]
}
new_commit = gh_api("POST", "repos/OnePlusNPM/hermes-config/git/commits", commit_data)
if not new_commit or "sha" not in new_commit:
    print("FAILED: Could not create commit")
    sys.exit(1)
commit_sha = new_commit["sha"]
print(f"  Commit: {commit_sha}")

# Step 7: Update branch ref
print("\nStep 7: Updating branch ref...")
ref_data = {"sha": commit_sha, "force": True}
result = gh_api("PATCH", "repos/OnePlusNPM/hermes-config/git/refs/heads/main", ref_data)
if not result:
    print("FAILED: Could not update ref")
    sys.exit(1)
print("  Branch updated!")

print(f"\n=== SUCCESS ===")
print(f"Files backed up: {len(blob_map)}")
print(f"Commit: {commit_sha[:12]}")
