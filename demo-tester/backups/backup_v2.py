import base64, json, subprocess, os, sys

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
        # Try again with raw output
        print(f"  gh error ({path[:60]}): {err}", file=sys.stderr)
        return None
    if proc.stdout:
        return json.loads(proc.stdout)
    return {}

# Step 1: Get the latest commit and tree SHA
print("Step 1: Getting latest commit SHA...")
ref = gh_api("GET", "repos/OnePlusNPM/hermes-config/git/refs/heads/main")
if not ref:
    print("FAILED: Could not get ref")
    sys.exit(1)
latest_sha = ref["object"]["sha"]
print(f"  Latest commit: {latest_sha}")

# Step 2: Define files to back up (just the essential config)
essential_files = [
    "config.yaml",
    "RULES.md",
    "SOUL.md",
    "channel_directory.json", 
    "context_length_cache.yaml",
    "cron/jobs.json",
]

# Step 3: Create blobs for each file
print("Step 2: Creating blobs...")
blob_results = []
for f in essential_files:
    full_path = os.path.join(profile_dir, f)
    if not os.path.exists(full_path):
        print(f"  SKIP: {f} not found")
        continue
    with open(full_path, "rb") as fh:
        content = fh.read()
    content_b64 = base64.b64encode(content).decode()
    
    blob_data = {
        "content": content_b64,
        "encoding": "base64"
    }
    blob = gh_api("POST", "repos/OnePlusNPM/hermes-config/git/blobs", blob_data)
    if blob and "sha" in blob:
        blob_results.append((f, blob["sha"]))
        print(f"  OK: {f} -> {blob['sha'][:12]}")
    else:
        print(f"  FAIL: {f}")

if not blob_results:
    print("FAILED: No blobs created")
    sys.exit(1)

# Step 4: Get the current base tree SHA
print("Step 3: Getting base tree...")
base_tree = gh_api("GET", f"repos/OnePlusNPM/hermes-config/git/commits/{latest_sha}")
if not base_tree:
    print("FAILED: Could not get base commit")
    sys.exit(1)
base_tree_sha = base_tree["tree"]["sha"]
print(f"  Base tree: {base_tree_sha}")

# Step 5: Create a new tree with the new files
print("Step 4: Creating new tree...")
tree_entries = []
for fname, blob_sha in blob_results:
    tree_entries.append({
        "path": f"{prefix}/{fname}",
        "mode": "100644",
        "type": "blob",
        "sha": blob_sha
    })
    
# Also keep existing entries by including base tree
tree_data = {
    "base_tree": base_tree_sha,
    "tree": tree_entries
}
new_tree = gh_api("POST", "repos/OnePlusNPM/hermes-config/git/trees", tree_data)
if not new_tree or "sha" not in new_tree:
    print("FAILED: Could not create tree")
    print(f"  Response: {json.dumps(new_tree)[:200]}" if new_tree else "  No response")
    sys.exit(1)
new_tree_sha = new_tree["sha"]
print(f"  New tree: {new_tree_sha}")

# Step 6: Create a commit
print("Step 5: Creating commit...")
commit_data = {
    "message": "backup: demo-tester profile config (essential files)",
    "tree": new_tree_sha,
    "parents": [latest_sha]
}
commit = gh_api("POST", "repos/OnePlusNPM/hermes-config/git/commits", commit_data)
if not commit or "sha" not in commit:
    print("FAILED: Could not create commit")
    sys.exit(1)
commit_sha = commit["sha"]
print(f"  Commit: {commit_sha}")

# Step 7: Update the branch reference
print("Step 6: Updating branch ref...")
ref_data = {
    "sha": commit_sha,
    "force": True
}
result = gh_api("PATCH", "repos/OnePlusNPM/hermes-config/git/refs/heads/main", ref_data)
if not result:
    print("FAILED: Could not update branch ref")
    sys.exit(1)
print(f"  Branch updated successfully!")

# Summary
print(f"\n=== SUCCESS ===")
print(f"Files backed up ({len(blob_results)}):")
for fname, sha in blob_results:
    print(f"  {prefix}/{fname}")
print(f"Commit: {commit_sha[:12]}")
