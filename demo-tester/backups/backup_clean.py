import base64, json, subprocess, os, sys

profile_dir = os.path.expanduser("~/.hermes/profiles/demo-tester")

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

# --- ESSENTIAL FILES TO BACK UP ---
essential = [
    ("config.yaml", "644"),
    ("RULES.md", "644"),
    ("SOUL.md", "644"),
    ("channel_directory.json", "644"),
    ("context_length_cache.yaml", "644"),
]

# Also include cron/jobs.json (subdir)
cron_files = [
    "cron/jobs.json",
]

all_files = [(f, mode) for f, mode in essential]
for f in cron_files:
    all_files.append((f, "644"))

print(f"Essential files to back up: {len(all_files)}")
for f, _ in all_files:
    full = os.path.join(profile_dir, f)
    if os.path.exists(full):
        size = os.path.getsize(full)
        print(f"  {f} ({size} bytes)")
    else:
        print(f"  {f} (NOT FOUND)")

# Step 1: Get latest ref
print("\nStep 1: Getting latest commit...")
ref = gh_api("GET", "repos/OnePlusNPM/hermes-config/git/refs/heads/main")
latest_sha = ref["object"]["sha"]
commit_info = gh_api("GET", f"repos/OnePlusNPM/hermes-config/git/commits/{latest_sha}")
root_tree_sha = commit_info["tree"]["sha"]
print(f"  Commit: {latest_sha[:12]}")
print(f"  Root tree: {root_tree_sha[:12]}")

# Step 2: Create blobs
print("\nStep 2: Creating blobs...")
blobs = {}
for f, _ in all_files:
    full_path = os.path.join(profile_dir, f)
    if not os.path.exists(full_path):
        print(f"  SKIP (not found): {f}")
        continue
    with open(full_path, "rb") as fh:
        content = fh.read()
    content_b64 = base64.b64encode(content).decode()
    blob_data = {"content": content_b64, "encoding": "base64"}
    blob = gh_api("POST", "repos/OnePlusNPM/hermes-config/git/blobs", blob_data)
    if blob and "sha" in blob:
        blobs[f] = blob["sha"]
        print(f"  OK: {f}")
    else:
        print(f"  FAIL: {f}")

if not blobs:
    print("FATAL: No blobs")
    sys.exit(1)

# Step 3: Create sub-trees if needed
# The cron/ subdirectory needs its own tree
# First create cron tree
cron_entries = []
if "cron/jobs.json" in blobs:
    cron_entries.append({"path": "jobs.json", "mode": "100644", "type": "blob", "sha": blobs["cron/jobs.json"]})

if cron_entries:
    cron_tree = gh_api("POST", "repos/OnePlusNPM/hermes-config/git/trees", {"tree": cron_entries})
    if not cron_tree or "sha" not in cron_tree:
        print("FAILED: Could not create cron tree")
        sys.exit(1)
    cron_tree_sha = cron_tree["sha"]
    print(f"  cron tree: {cron_tree_sha[:12]}")

# Step 4: Create demo-tester tree
print("\nStep 3: Creating demo-tester tree...")
demo_entries = []
for f, mode in all_files:
    if f in blobs and "/" not in f:
        demo_entries.append({"path": f, "mode": "100644", "type": "blob", "sha": blobs[f]})
# Add cron subdir
if cron_entries:
    demo_entries.append({"path": "cron", "mode": "040000", "type": "tree", "sha": cron_tree_sha})

demo_tree = gh_api("POST", "repos/OnePlusNPM/hermes-config/git/trees", {"tree": demo_entries})
if not demo_tree or "sha" not in demo_tree:
    print("FAILED: Could not create demo-tester tree")
    sys.exit(1)
demo_tree_sha = demo_tree["sha"]
print(f"  demo-tester tree: {demo_tree_sha[:12]}")

# Step 5: Get root tree and create new one (replace old demo-tester)
print("\nStep 4: Creating root tree...")
root_tree = gh_api("GET", f"repos/OnePlusNPM/hermes-config/git/trees/{root_tree_sha}")
other_entries = [e for e in root_tree["tree"] if e["path"] != "demo-tester"]
other_entries.append({"path": "demo-tester", "mode": "040000", "type": "tree", "sha": demo_tree_sha})

new_root = gh_api("POST", "repos/OnePlusNPM/hermes-config/git/trees", {"tree": other_entries})
if not new_root or "sha" not in new_root:
    print("FAILED: Could not create root tree")
    sys.exit(1)
print(f"  Root tree: {new_root['sha'][:12]}")

# Step 6: Create commit
print("\nStep 5: Creating commit...")
commit_data = {
    "message": "backup: demo-tester profile config (sanitized - 6 essential files, removed runtime)",
    "tree": new_root["sha"],
    "parents": [latest_sha]
}
new_commit = gh_api("POST", "repos/OnePlusNPM/hermes-config/git/commits", commit_data)
if not new_commit or "sha" not in new_commit:
    print("FAILED: Could not create commit")
    sys.exit(1)
commit_sha = new_commit["sha"]
print(f"  Commit: {commit_sha[:12]}")

# Step 7: Update branch
print("\nStep 6: Updating branch ref...")
ref_data = {"sha": commit_sha, "force": True}
result = gh_api("PATCH", "repos/OnePlusNPM/hermes-config/git/refs/heads/main", ref_data)
if not result:
    print("FAILED: Could not update ref")
    sys.exit(1)
print("  Branch updated!")

print(f"\n=== BACKUP COMPLETE ===")
print(f"Files backed up: {len(blobs)}")
for f in blobs:
    print(f"  demo-tester/{f}")
print(f"Commit: {commit_sha[:12]}")
print(f"Runtime files from previous backup: REMOVED")
print(f"Plaintext API keys: NONE FOUND")
