import json, subprocess, sys

def gh_api(method, path, data=None):
    cmd = ["gh", "api", path, "--method", method]
    if data:
        cmd.extend(["--input", "-"])
        proc = subprocess.run(cmd, input=json.dumps(data).encode(), capture_output=True, timeout=30)
    else:
        proc = subprocess.run(cmd, capture_output=True, timeout=30)
    if proc.returncode != 0:
        err = proc.stderr.decode().strip()[:200]
        if err:
            print(f"  WARN: {err}", file=sys.stderr)
        return None
    if proc.stdout:
        return json.loads(proc.stdout)
    return {}

def list_recursive(path):
    """Recursively list all files in a directory via API."""
    result = gh_api("GET", f"repos/OnePlusNPM/hermes-config/contents/{path}")
    files = []
    if not result:
        return files
    for item in result:
        if item["type"] == "file":
            files.append(item["path"])
        elif item["type"] == "dir":
            files.extend(list_recursive(item["path"]))
    return files

print("Listing runtime files to delete...")
runtime_patterns = [
    "demo-tester/gateway.",
    "demo-tester/sessions/",
    "demo-tester/desktop/",
    "demo-tester/hindsight/",
    "demo-tester/home/",
    "demo-tester/logs/",
    "demo-tester/memories/",
    "demo-tester/sessions.db",
    "demo-tester/ticker_",
    "demo-tester/provider_models_cache",
    "demo-tester/ollama_cloud_models_cache",
    "demo-tester/models_dev_cache",
    "demo-tester/processes.json",
    "demo-tester/fetch_issues.py",
    "demo-tester/check_issues.py",
]

all_files = list_recursive("demo-tester")
print(f"Total files in demo-tester: {len(all_files)}")

to_delete = []
for f in all_files:
    for pattern in runtime_patterns:
        if pattern in f:
            to_delete.append(f)
            break

print(f"Runtime files to delete: {len(to_delete)}")
for f in to_delete:
    print(f"  {f}")

if not to_delete:
    print("Nothing to delete.")
    sys.exit(0)

# Get latest commit SHA for parent commit
ref = gh_api("GET", "repos/OnePlusNPM/hermes-config/git/refs/heads/main")
latest_sha = ref["object"]["sha"]
print(f"\nUsing parent commit: {latest_sha}")

# Create blobs for empty state to delete files
import base64
for f in to_delete:
    # Get the file's SHA first
    info = gh_api("GET", f"repos/OnePlusNPM/hermes-config/contents/{f}")
    if not info or "sha" not in info:
        print(f"  SKIP (no info): {f}")
        continue
    
    del_data = {
        "message": f"cleanup: remove {f} (runtime file)",
        "sha": info["sha"],
        "branch": "main"
    }
    result = gh_api("DELETE", f"repos/OnePlusNPM/hermes-config/contents/{f}", del_data)
    if result:
        print(f"  DELETED: {f}")
    else:
        print(f"  FAILED: {f}")

print("\nDone!")
