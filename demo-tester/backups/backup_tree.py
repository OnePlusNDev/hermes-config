import base64, json, subprocess, os, sys

profile_dir = os.path.expanduser("~/.hermes/profiles/demo-tester")
prefix = "demo-tester"

def gh_api(method, path, data=None):
    cmd = ["gh", "api", path, "--method", method]
    if data:
        cmd.extend(["--input", "-"])
        proc = subprocess.run(cmd, input=json.dumps(data).encode(), capture_output=True, timeout=60)
    else:
        proc = subprocess.run(cmd, capture_output=True, timeout=30)
    if proc.returncode != 0:
        err = proc.stderr.decode().strip()[:200]
        if err:
            print(f"  gh err: {err}", file=sys.stderr)
        return None
    if proc.stdout:
        return json.loads(proc.stdout)
    return {}

def is_included(rel_path):
    """Check if a file should be backed up."""
    exclude_dirs = {
        ".git", "__pycache__", "node_modules", "audio_cache", "cache",
        "cron/output", "workspace", "skins", "backups", "desktop", "hindsight",
        "home", "logs", "memories", "sessions", "plugins"
    }
    exclude_files = {
        ".env", ".hermes_history", ".skills_prompt_snapshot.json", ".update_check",
        "auth.json", "auth.lock", "state.db", "state.db-shm", "state.db-wal",
        ".jobs.lock", ".tick.lock", ".DS_Store", "gateway.lock", "gateway.pid",
        "gateway_state.json", "ticker_heartbeat", "ticker_last_success",
        "ollama_cloud_models_cache.json", "provider_models_cache.json",
        "models_dev_cache.json", "processes.json", "sessions.db",
        "check_issues.py", "fetch_issues.py", ".gitignore"
    }
    parts = rel_path.split("/")
    if any(p in exclude_dirs for p in parts):
        return False
    fname = parts[-1]
    if fname in exclude_files:
        return False
    if fname.endswith(".bak"):
        return False
    return True

def collect_files(base_dir):
    """Recursively collect all files to back up."""
    results = []
    for root, dirs, files in os.walk(base_dir):
        rel = os.path.relpath(root, base_dir)
        if rel == ".":
            rel = ""
        # Filter dirs
        dirs[:] = [d for d in dirs if is_included(os.path.join(rel, d) if rel else d)]
        
        for f in files:
            rel_path = os.path.join(rel, f) if rel else f
            if is_included(rel_path):
                full_path = os.path.join(root, f)
                # Skip binary
                try:
                    with open(full_path, "rb") as fh:
                        chunk = fh.read(8192)
                    if b"\x00" in chunk:
                        continue
                except:
                    continue
                results.append((full_path, rel_path))
    return results

def create_trees_recursive(base_prefix, file_map):
    """
    file_map: {relative_path: blob_sha} for all files in the tree
    Creates git tree objects for each directory level.
    Returns the SHA of the root tree.
    """
    # Group files by their parent directory
    tree_entries = {}
    dir_trees = {}  # dir_path -> list of (name, type, sha)
    
    for rel_path, sha in file_map.items():
        parts = rel_path.split("/")
        if len(parts) == 1:
            # Top-level file
            name = parts[0]
            tree_entries[name] = ("blob", sha)
        else:
            # Nested file - need parent tree
            dir_path = "/".join(parts[:-1])
            name = parts[-1]
            if dir_path not in dir_trees:
                dir_trees[dir_path] = []
            dir_trees[dir_path].append((name, "blob", sha))
    
    # Also need to create subdirectory entries for dir_trees
    # Group dir_trees by parent
    dir_by_parent = {}
    for dir_path in dir_trees:
        parts = dir_path.split("/")
        if len(parts) == 1:
            parent = ""
        else:
            parent = "/".join(parts[:-1])
        name = parts[-1]
        if parent not in dir_by_parent:
            dir_by_parent[parent] = []
        dir_by_parent[parent].append((name, "tree", dir_path))
    
    # Process bottom-up: create tree objects for deepest dirs first
    depth_order = sorted(set(dir_trees.keys()), key=lambda x: -len(x.split("/")))
    
    tree_cache = {}  # dir_path -> sha
    for dir_path in depth_order:
        entries = []
        # Add file entries
        for name, etype, sha in dir_trees[dir_path]:
            mode = "100644" if etype == "blob" else "040000"
            entries.append({"path": name, "mode": mode, "type": etype, "sha": sha})
        # Add subdirectory entries
        for name, etype, sub_dir in dir_by_parent.get(dir_path, []):
            if sub_dir in tree_cache:
                entries.append({"path": name, "mode": "040000", "type": "tree", "sha": tree_cache[sub_dir]})
        
        data = {"tree": entries} if entries else {"tree": []}
        result = gh_api("POST", "repos/OnePlusNPM/hermes-config/git/trees", data)
        if not result or "sha" not in result:
            print(f"  FAILED to create tree for {dir_path}", file=sys.stderr)
            return None
        tree_cache[dir_path] = result["sha"]
        #print(f"  TREE: {dir_path} -> {result['sha'][:12]}")
    
    # Now build the root level (prefix/)
    root_entries = []
    for name, etype, sha in tree_entries.items():
        mode = "100644" if etype == "blob" else "040000"
        root_entries.append({"path": name, "mode": mode, "type": etype, "sha": sha})
    # Add subdirectories at root level
    for name, etype, sub_dir in dir_by_parent.get("", []):
        if sub_dir in tree_cache:
            root_entries.append({"path": name, "mode": "040000", "type": "tree", "sha": tree_cache[sub_dir]})
    
    data = {"tree": root_entries}
    result = gh_api("POST", "repos/OnePlusNPM/hermes-config/git/trees", data)
    if not result or "sha" not in result:
        print("  FAILED to create root tree", file=sys.stderr)
        return None
    prefix_sha = result["sha"]
    print(f"  {prefix} tree SHA: {prefix_sha[:12]}")
    return prefix_sha

# === MAIN ===

# Step 1: Get latest commit
print("Step 1: Getting latest commit...")
ref = gh_api("GET", "repos/OnePlusNPM/hermes-config/git/refs/heads/main")
if not ref:
    print("FATAL: Cannot get ref")
    sys.exit(1)
latest_sha = ref["object"]["sha"]
print(f"  Commit: {latest_sha}")

# Step 2: Collect files
print("\nStep 2: Collecting files (excluding runtime/sensitive)...")
files = collect_files(profile_dir)
print(f"  Found {len(files)} files")

# Step 3: Create blobs
print("\nStep 3: Creating blobs...")
file_map = {}
batch_size = 10
for i in range(0, len(files), batch_size):
    batch = files[i:i+batch_size]
    for full_path, rel_path in batch:
        with open(full_path, "rb") as fh:
            content = fh.read()
        content_b64 = base64.b64encode(content).decode()
        blob_data = {"content": content_b64, "encoding": "base64"}
        blob = gh_api("POST", "repos/OnePlusNPM/hermes-config/git/blobs", blob_data)
        if blob and "sha" in blob:
            file_map[rel_path] = blob["sha"]
        else:
            print(f"  FAIL: {rel_path}")
    print(f"  Progress: {min(i+batch_size, len(files))}/{len(files)} blobs created")

if not file_map:
    print("FATAL: No blobs created")
    sys.exit(1)
print(f"  Total blobs: {len(file_map)}")

# Step 4: Create demo-tester tree
print("\nStep 4: Building demo-tester tree...")
prefix_sha = create_trees_recursive(prefix, file_map)
if not prefix_sha:
    sys.exit(1)

# Step 5: Get root tree and create new root
print("\nStep 5: Creating root tree...")
commit = gh_api("GET", f"repos/OnePlusNPM/hermes-config/git/commits/{latest_sha}")
root_tree_sha = commit["tree"]["sha"]
root_tree = gh_api("GET", f"repos/OnePlusNPM/hermes-config/git/trees/{root_tree_sha}")

# Keep all existing entries except demo-tester
other_entries = [e for e in root_tree["tree"] if e["path"] != prefix]
print(f"  Other entries: {[e['path'] for e in other_entries]}")

new_root_entries = list(other_entries)
new_root_entries.append({
    "path": prefix,
    "mode": "040000",
    "type": "tree",
    "sha": prefix_sha
})
new_root = gh_api("POST", "repos/OnePlusNPM/hermes-config/git/trees", {"tree": new_root_entries})
if not new_root or "sha" not in new_root:
    print("FAILED: Could not create root tree")
    sys.exit(1)
print(f"  Root tree SHA: {new_root['sha'][:12]}")

# Step 6: Create commit
print("\nStep 6: Creating commit...")
commit_data = {
    "message": "backup: demo-tester profile config (sanitized)",
    "tree": new_root["sha"],
    "parents": [latest_sha]
}
new_commit = gh_api("POST", "repos/OnePlusNPM/hermes-config/git/commits", commit_data)
if not new_commit or "sha" not in new_commit:
    print("FAILED: Could not create commit")
    sys.exit(1)
commit_sha = new_commit["sha"]
print(f"  Commit: {commit_sha}")

# Step 7: Update branch
print("\nStep 7: Updating branch ref...")
ref_data = {"sha": commit_sha, "force": True}
result = gh_api("PATCH", "repos/OnePlusNPM/hermes-config/git/refs/heads/main", ref_data)
if not result:
    print("FAILED: Could not update ref")
    sys.exit(1)
print("  Branch updated!")

print(f"\n=== BACKUP COMPLETE ===")
print(f"Files: {len(file_map)}")
print(f"Commit: {commit_sha[:12]}")
