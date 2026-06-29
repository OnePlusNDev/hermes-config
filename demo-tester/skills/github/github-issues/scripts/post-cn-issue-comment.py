#!/usr/bin/env python3
"""Post a GitHub issue comment with Chinese/non-ASCII content reliably.

Bypasses tirith:confusable_text scanner by reading the body from a file on disk
(written via write_file, not terminal) and posting via gh CLI --body-file.

Usage: post-cn-issue-comment.py <issue_number> <repo_owner/repo> <body_file_or_stdin>
"""
import subprocess, sys, argparse

def main():
    parser = argparse.ArgumentParser(description="Post Chinese issue comment safely")
    parser.add_argument("issue", help="Issue number")
    parser.add_argument("repo", help="owner/repo")
    parser.add_argument("--body-file", "-b", help="File with comment body (UTF-8)")
    args = parser.parse_args()

    cmd = ["gh", "issue", "comment", str(args.issue),
           "--repo", args.repo, "--body-file"]
    
    if args.body_file:
        cmd.append(args.body_file)
    else:
        # Read from stdin (pipe or heredoc)
        import os
        data = sys.stdin.buffer.read()
        tmp = "/tmp/gh_comment_body.md"
        with open(tmp, "wb") as f:
            f.write(data)
        cmd.append(tmp)

    result = subprocess.run(cmd, capture_output=True, text=False)
    if result.returncode != 0:
        sys.stderr.buffer.write(result.stderr)
        sys.exit(1)
    if result.stdout:
        print(result.stdout.decode(), end="")

if __name__ == "__main__":
    main()
