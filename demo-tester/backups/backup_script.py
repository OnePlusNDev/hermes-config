import base64, json, subprocess, os

profile_dir = os.path.expanduser("~/.hermes/profiles/demo-tester")
backup_prefix = "demo-tester"

def gh_api(method, path, data=None):
    cmd = ["gh", "api", path, "--method", method]
    if data:
        cmd.extend(["--input", "-"])
        proc = subprocess.run(cmd, input=json.dumps(data).encode(), capture_output=True, timeout=30)
    else:
        proc = subprocess.run(cmd, capture_output=True, timeout=30)
    if proc.returncode != 0:
        print(f"ERROR: {proc.stderr.decode()[:200]}")
        return None
    return json.loads(proc.stdout) if proc.stdout else {}

def file_list():
    """List files to back up, excluding sensitive/runtime files."""
    exclude_dirs = {
        ".git", "__pycache__", "node_modules", "audio_cache", "cache",
        "cron/output", "workspace", "skins", "backups"
    }
    exclude_files = {
        ".env", ".hermes_history", ".skills_prompt_snapshot.json", ".update_check",
        "auth.json", "auth.lock", "state.db", "state.db-shm", "state.db-wal",
        ".jobs.lock", ".tick.lock", ".DS_Store"
    }
    exclude_suffixes = {".bak"}
    results = []
    for root, dirs, files in os.walk(profile_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        rel_root = os.path.relpath(root, profile_dir)
        if rel_root == ".":
            rel_root = ""
        for f in files:
            rel_path = os.path.join(rel_root, f) if rel_root else f
            if f in exclude_files or any(rel_path.startswith(d) for d in exclude_dirs):
                continue
            if any(f.endswith(s) for s in exclude_suffixes):
                continue
            # Skip binary files
            fp = os.path.join(root, f)
            if f == "tirith":  # binary file
                continue
            try:
                with open(fp, "rb") as fh:
                    chunk = fh.read(8192)
                if b"\x00" in chunk:
                    continue
            except:
                continue
            results.append(rel_path)
    return sorted(results)

def upload_file(file_rel_path):
    """Upload a single file via GitHub Content API."""
    full_path = os.path.join(profile_dir, file_rel_path)
    api_path = f"{backup_prefix}/{file_rel_path}"
    
    # Read and encode content
    with open(full_path, "rb") as fh:
        content = fh.read()
    
    # Check if file already exists (need the SHA for update)
    check = gh_api("GET", f"repos/OnePlusNPM/hermes-config/contents/{api_path}")
    sha = check.get("sha") if check and "sha" in check else None
    
    data = {
        "message": f"backup: {api_path}",
        "content": base64.b64encode(content).decode(),
        "branch": "main"
    }
    if sha:
        data["sha"] = sha
    
    result = gh_api("PUT", f"repos/OnePlusNPM/hermes-config/contents/{api_path}", data)
    if result and "content" in result:
        return True
    return False

# Main
files = file_list()
success = []
failed = []
for f in files:
    if upload_file(f):
        success.append(f)
        print(f"OK: {f}")
    else:
        failed.append(f)
        print(f"FAIL: {f}")

print(f"\n=== Summary ===")
print(f"Total: {len(files)}, Success: {len(success)}, Failed: {len(failed)}")
