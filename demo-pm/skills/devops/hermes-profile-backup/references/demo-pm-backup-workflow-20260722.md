# demo-pm Backup Workflow — 2026-07-22

## Context

First-ever backup of the `demo-pm` profile to `OnePlusNPM/hermes-config` (repo already had `demo-tester/`). 534 files total.

## Key Discovery: macOS git-remote-https TLS handshake timeout

`git push origin main` failed with:
```
fatal: unable to access 'https://github.com/OnePlusNPM/hermes-config.git/':
Failed to connect to github.com port 443 after 75003 ms: Couldn't connect to server
```

But:
- `curl -sI https://github.com` returned HTTP 200 (works)
- `gh api repos/OnePlusNPM/hermes-config` returned full repo data (works)
- Python `urllib.request` SSL handshake timed out (fails)
- System git at `/usr/bin/git` (Apple Git-155) timed out (fails)

**Root cause:** `git-remote-https` (Apple Git libcurl) and Python's `ssl` module both time out on the TLS handshake to `github.com:443`, while `curl` command-line and `gh` CLI (Go net/http) succeed. This is a macOS-specific libcurl vs curl CLI discrepancy, not a network outage.

**Implication:** On this machine, `git push` to GitHub is unreliable. Always fall back to `gh api` Git Data API (Method B) when `git push` fails.

## Phase 1: Security scan - no plaintext keys

`config.yaml` had all 45 `api_key:` fields as empty strings `''`. No `sk-` prefixed values found. No `.env` or `auth.json` read (credential stores, excluded from backup).

## Phase 2: gh API blob upload — account mismatch

Uploaded 465 of 534 blobs successfully, then the remaining 69 returned `HTTP 404 — Not Found`.

**Diagnosis:** `gh api user --jq '.login'` returned `OnePlusNTester` — NOT `OnePlusNPM` who owns the repo. The collaborator account had partial write access but failed on some blobs.

**Fix:** `gh auth switch --user OnePlusNPM` → retried the 69 failed blobs → all succeeded.

## Phase 3: Tree construction with subtree

The remote already had a `demo-tester/` directory tree. Strategy:

1. Created a **subtree tree** containing all 534 `demo-pm/` blobs (with `demo-pm/` prefix stripped from paths)
2. Fetched the **base tree** via `GET /repos/OnePlusNPM/hermes-config/git/trees/{base_tree_sha}` (3 entries: `.gitignore`, `demo-tester/`, `demo-pm/`)
3. Built the top-level tree: copied all 3 base entries, replaced the `demo-pm` entry with the new subtree tree SHA
4. Created the top-level tree → commit → updated `refs/heads/main`

## Files backed up

| Path | Size |
|------|------|
| `demo-pm/config.yaml` | 17KB |
| `demo-pm/SOUL.md` | 10KB |
| `demo-pm/RULES.md` | 0B |
| `demo-pm/cron/pm_triage_script.py` | 1.4KB |
| `demo-pm/skills/` (529 files, 19 categories, 78 skills) | 7MB |

## Files excluded

`.env`, `auth.json`, `state.db*`, `sessions/`, `logs/`, `cache/`, `memories/`, `desktop/`, `sandboxes/`, `plans/`, `pairing/`, `hooks/`, `lsp/`, `bin/`, `skins/`, `home/`, `.local/`, `workspace/`, `audio_cache/`, `image_cache/`, `hindsight-maintenance-logs/`, cron runtime artifacts, `.skills_prompt_snapshot.json`, `.tmp_*`, `.hermes_history`, `*.bak.*`, `gateway.*`, `processes.json`, `context_length_cache.yaml`, `*_cache.json`, `interrupt_debug.log`.

## Result

**Success.** Commit `1d3743032fa2b420aee15e11e46e07cd0a79dacf` pushed to `OnePlusNPM/hermes-config` at 2026-07-22 12:37 UTC. No plaintext API keys exposed. No sensitive files leaked.
