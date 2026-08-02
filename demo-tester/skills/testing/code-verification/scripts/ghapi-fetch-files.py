#!/usr/bin/env python3
"""Fetch all files from a GitHub repo branch via gh API (no git clone needed).

Usage:
  ghapi-fetch-files.py OWNER/REPO main hello.py test_hello.py
  
If no filenames are given, lists all files in the branch.
Given filenames, fetches and writes them to /tmp/<path>/filename.ext.
"""
import subprocess
import json
import sys
import os

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: {cmd}")
        print(result.stderr, file=sys.stderr)
        sys.exit(1)
    return result.stdout

def get_tree_sha(owner_repo, ref):
    """Get the root tree SHA for a given ref."""
    out = run(f'gh api repos/{owner_repo}/git/refs/heads/{ref}')
    commit_sha = json.loads(out)['object']['sha']
    out2 = run(f'gh api repos/{owner_repo}/git/trees/{commit_sha}?recursive=true')
    data = json.loads(out2)
    return data['tree'], commit_sha

def fetch_blob(owner_repo, blob_sha):
    """Fetch and decode a blob."""
    out = run(f'gh api repos/{owner_repo}/git/blobs/{blob_sha}')
    d = json.loads(out)
    import base64
    content = base64.b64decode(d['content']).decode('utf-8')
    return content

def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} OWNER/REPO ref [file1 file2 ...]")
        sys.exit(1)
    
    owner_repo = sys.argv[1]
    ref = sys.argv[2]
    target_files = sys.argv[3:] if len(sys.argv) > 3 else None
    
    tree, commit_sha = get_tree_sha(owner_repo, ref)
    
    # Build path -> sha mapping
    sha_map = {f['path']: f['sha'] for f in tree}
    
    if not target_files:
        print(f"Branch: main (commit: {commit_sha})")
        print(f"\nFiles ({len(tree)} total):")
        for p in sorted(sha_map.keys()):
            print(f"  {p}")
        return
    
    missed = []
    for target in target_files:
        if target not in sha_map:
            missed.append(target)
            continue
        
        content = fetch_blob(owner_repo, sha_map[target])
        outdir = os.path.join('/tmp', os.path.dirname(target))
        os.makedirs(outdir, exist_ok=True)
        path = os.path.join('/tmp', target)
        
        with open(path, 'w') as f:
            f.write(content)
        print(f"OK     {target} -> {path}")
    
    if missed:
        print(f"\nMISSING (not found in tree):")
        for m in missed:
            print(f"  ???? {m}")

if __name__ == '__main__':
    main()
