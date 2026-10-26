# Network flakiness, retry discipline, and verify-tooling gotchas

Companion to `scripts/preflight-backup-scan.py` (pre-push) and
`scripts/post-push-verify.py` (post-push). Verified 2026-09-16 on a run that
required three attempts and produced one false FAIL from the verifier itself.

## 1. A mid-phase `i/o timeout` is NOT a partial failure — plain re-run

2026-09-16: attempts 1 and 2 aborted with
`dial tcp 20.205.243.168:443: i/o timeout` — the first on the LAST blob POST,
the second on the initial `git/trees/<sha>?recursive=1` GET. Attempt 3 uploaded
all 8 blobs and pushed first-try, no intervention.

Rules:
- Blob SHAs are idempotent. A re-run re-uploads only what is missing and
  re-parents the same commit on the current HEAD. Re-running is the whole fix.
- Do NOT treat it as a partial backup: no rebase, no tree surgery, no manual
  re-parent, no "recovery" commit.
- Do NOT abandon the run and report failure — the first attempts already
  uploaded blobs successfully.
- A `FATAL ... i/o timeout` line can appear BEFORE the successful step lines in
  the captured output (stderr/stdout interleaving). Read the whole tail before
  concluding which phase died.

## 2. `curl https://api.github.com` returning `000` is not evidence of failure

Same moment as the timeouts above, `curl` returned `000` three times in a row
while `gh api repos/<owner>/<repo>/git/refs/heads/main` answered 5/5 retries
immediately afterwards. `curl`'s TLS/transport path in cron mode is simply less
reliable than `gh`'s here.

Use this as the go/no-go probe before deciding the network is down:

```
for i in 1 2 3 4 5; do gh api repos/<owner>/<repo>/git/refs/heads/main --jq '.object.sha[:12]'; done
```

5/5 answers means connectivity is fine — re-run the backup script. Only if `gh`
also fails repeatedly is it a real outage.

## 3. Verify-probe bug: `/contents/` needs `--jq .content`, not `--jq .`

`scripts/post-push-verify.py` false-FAILed on its first execution with
`[FAIL] config.yaml decodes: Incorrect padding`. Root cause: its `gh()` helper
hardcoded `--jq "."`, so the `/repos/{o}/{r}/contents/{path}` call returned the
whole JSON envelope (`{"content": ..., "encoding": "base64", ...}`) and the
script base64-decoded THAT instead of the `content` field.

Fix applied: `gh()` takes a `jq="."` parameter; the config.yaml call passes
`jq=".content"`.

Triage rule for any `Incorrect padding` / garbage-decode in a verify probe:
check the `--jq` filter BEFORE believing the leak claim. Confirm by hand —
`gh api repos/{o}/{r}/contents/{path} --jq '.content'` — then base64-decode and
compare byte-for-byte against the local file. A real leak and a decode bug look
identical from the probe's exit code.

## 4a. Attributing a ref-PATCH 422: list recent commits, and get the endpoint right

After `FATAL ref update: ... (HTTP 422 Update is not a fast forward)`, the plain
re-run fix is documented — but the **run note / practice-notes row** also needs the
cause. List the last few commits and name the sibling run that advanced HEAD:

```bash
gh api "repos/$OWNER/$REPO/commits?per_page=4" \
  --jq '.[] | "\(.sha[0:12]) \(.commit.author.date) \(.commit.message | split("\n")[0])"'
```

Endpoint gotcha (hit 2026-10-21): **`/git/commits?per_page=4` returns HTTP 404
`{"message":"Not Found"}`** — the list endpoint is `/commits`, not `/git/commits`
(`/git/commits/<sha>`, singular with an explicit SHA, IS valid). A 404 here looks
like a missing repo or an auth/account problem; it is neither, just the wrong path.

Verified 2026-10-21: preflight saw HEAD `68d5da9921bc`, the first commit `e69fffb3c243`
was rejected 422, and `/commits` showed `e2edf5ebcbf3 backup: demo-dev profile config
(2026-10-21)` at 12:00:55Z — i.e. a sibling profile's cron landed ~2 min before our
ref PATCH. That is the fastest and only authoritative way to say *which* run beat us
(and it confirms the loss is a race, not a bad tree).

## 5. Size numbers: characters vs bytes

Run notes have quoted remote `config.yaml` as `16835` since ~09-15. That is a
**character** count from `len(str)`, not bytes — the file holds CJK comments.
True byte length is **17021**. The 186-char gap is the multi-byte savings.

Rule: when reporting or comparing file sizes, use `len(bytes)`. A `len(str)`
figure derived from `decode("utf-8", "replace")` will silently under-report and
make two identical files look different in size while their blob SHA matches.
Blob SHA equality is the authoritative identity check — trust it over any
size arithmetic.

## 6. A mid-script `unexpected EOF` leaves partial-looking output — re-run, never report FAIL

Verified 2026-10-25, on the **closing** probes (after a clean follow-up push), both
scripts died mid-run with a transport EOF while auth was demonstrably fine:

- `preflight-backup-scan.py` exited **1** having printed only
  `Local files (after excludes): 264` — the fatal line was
  `GH API error: Get ".../git/trees/<sha>?recursive=1": unexpected EOF`
- `post-push-verify.py` exited **1** after its structural checks had already
  **PASSed** (`demo-pm blobs: 264`, siblings intact), dying on
  `GH API FAIL .../contents/demo-pm/config.yaml: ... EOF`

At that moment `gh api user` → `OnePlusNDev`, `permissions.push=true`, and a 3×
`git/refs/heads/main` probe answered 3/3. Plain re-runs of both scripts: preflight
`Modified: 0, New: 0, Deleted: 0`; verify **ALL CHECKS PASS**.

Rules:
- `EOF` / `unexpected EOF` / `connection reset` = **transport**, not a verification
  verdict. A non-zero exit from either probe is not by itself evidence of anything.
- A **truncated preflight** (only `Local files…` printed) must never be read as
  "no changes" *or* as a diff failure — it never reached the diff.
- A **partial verify** that PASSed structure and then EOF'd is not a leak/FAIL:
  do not push a correction commit and do not start tree surgery. Re-run the probe.
- Keep the go/no-go probe from §2 (3–5× `git/refs/heads/main`) as the gate; only a
  repeated `gh` failure means a real outage. `curl` remains the wrong probe.
- Same remedy as §1 and the Step-5 hang: ONE plain re-run. Probing is cheap; a
  speculative "recovery" commit is not.
