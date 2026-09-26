# Curator churn in the preflight: triage recipe for huge A/D diffs

Verified 2026-09-18 (demo-pm run). Applies whenever a backup preflight reports far more
New/Deleted entries than the profile plausibly changed.

## Symptom

```text
=== Preflight: diff + token scan ===
Local files (after excludes): 629
Remote HEAD: c1f8fb153c99  blobs: 647
Modified: 5, New: 233, Deleted: 232
  A  demo-pm/skills/.archive/airtable/SKILL.md
  ...
  D  demo-pm/skills/productivity/powerpoint/scripts/office/schemas/...  (232 files)
```

This is NOT an exclude gap in the classic sense (temp diagnostics leaking `.env`), and it
is NOT a mass local deletion. It is the curator doing its job: the **pure time-based
staleness pass** moved 36 bundled skills / 232 files / 2.7 MB from
`skills/<category>/<name>/` into `skills/.archive/`, and wrote the new
`skills/.curator_suppressed` list.

Evidence trail:

- `logs/curator/<timestamp>/REPORT.md` → `auto: 36 archived; llm: skipped (consolidation off)`
- `skills/.curator_state` → `"last_run_summary": "auto: 36 archived; llm: skipped"`, plus
  `run_count` and `last_run_at` (UTC)
- `skills/.curator_suppressed` → one line per archived skill name (marks them
  "do not re-offer")

## Triage recipe

1. **Find the dot-dir behind it.** `ls -la skills/` (the `.archive` dir's mtime is the
   curator run time) and `find . -type d -name '.archive'` (should be exactly one,
   `./skills/.archive` — if a *nested* `.archive` shows up, the global `".archive"`
   exclude is too broad and needs scoping).
2. **Confirm the curator run.** `cat skills/.curator_state` + newest
   `logs/curator/*/REPORT.md`. If there is no `auto: N archived` line, STOP — this is a
   different problem (real deletion, bad `PROFILE_DIR`, misdirected rsync DST).
3. **Classify every moved skill name** against the bundled manifest — a ~3-line Python
   loop is enough (`skills/.bundled_manifest` is `name:md5`, one per line):
   - **Bundled → EXCLUDE.** Content is re-shipped with Hermes and restorable with
     `hermes curator restore <name>`; it is not user configuration, and 2.7 MB of
     duplicates buys nothing in a config-backup repo.
   - **Agent-created → INCLUDE.** The `.archive/` copy would then be the only surviving
     copy of user-authored content; let it be uploaded (paths move, content is kept).
4. **Verify the deletions are confined AND are all archive twins of bundled skills:**
   run `python3 scripts/verify-curator-archive-churn.py <preflight.log>` and require
   **exit 0**. It does all three checks in one pass — confinement to
   `<profile>/skills/`, an `.archive/<name>/...` twin per deleted path, and
   `bundled` classification against `.bundled_manifest` (resolved via the archived
   SKILL.md `name:`, so dir-name != manifest-name cases still classify). The bare
   confinement check it subsumes is `grep '^  D  ' preflight.txt | grep -v
   'demo-pm/skills/' | wc -l` must be `0`. Any `D` outside `skills/`, any path with
   no twin, or any non-bundled/unresolved skill means the run is doing something
   else — stop and investigate.
5. **Patch the excludes, all in one pass** (they must stay in sync):
   - `scripts/preflight-backup-scan.py`, `scripts/gh-api-standalone-subtree-backup.py`,
     `scripts/gh-api-standalone-backup.py`: `EXCLUDE_DIRS += ".archive"` and
     `EXCLUDE_NAMES += ".curator_suppressed"` (next to `.curator_state`)
   - `SKILL.md`: the "Exclude" bullet list **and** the gitignore-sync list
   - `templates/gitignore-template.txt`: `**/skills/.archive/` and
     `**/skills/.curator_suppressed`
6. **Re-run the preflight** and expect the `A` entries under `.archive/` to disappear and
   `Local files (after excludes)` to drop by exactly the archive file count
   (629 → 396 here). Then run the backup as usual.
7. **Disclose the blob-count drop.** The profile's blob count falls (`demo-pm` 627 → 396
   in the excluded case). A three-digit deletion that is not explained reads as data
   loss, so the run note AND the delivered report must state: the cause (curator
   archive), the delta, that the old copies stay reachable in git history, and that
   bundled content is not user config. Also record: "do NOT hand-restore the archived
   copies."

## Recurrence log

- **2026-09-18** — 1st event: curator archived 36 bundled skills / 232 files; excludes
  (`.archive`, `.curator_suppressed`) had to be ADDED to all 3 scripts + SKILL.md x2 + gitignore.
- **2026-09-25** — 2nd event: curator's 2026-09-24T23:12:25Z pass archived 29 more bundled
  skills / 187 files (archive 36 → 65 skills; agent-created count unchanged 9 → 9). Because
  the 09-18 excludes were already in place, **no patching was needed** — the preflight simply
  reported `3 M / 0 A / 187 D`, all under `demo-pm/skills/`, every deleted path verified to have
  an `.archive/<name>/...` twin (187/187) and to classify as bundled via `.bundled_manifest`.
  Main commit `ef84bc3a8d85`, `demo-pm` blobs 410 → 223, then closing `0/0/0` after the
  follow-up. Takeaway: this recurs on the curator's time-based staleness schedule; once the
  excludes exist, the run is routine — just re-verify the twins, classify, and disclose.

## General rule this codifies

**Dot-dirs created by the curator are runtime state, not configuration.** The family:
`.archive/`, `.curator_backups/`, `.curator_state`, `.curator_suppressed`, `.hub/`,
`.bundled_manifest`. When a brand-new one appears in the diff, the default answer is
"exclude", and the burden of proof is on finding *user-authored* content inside it.

Corollary for `.archive/` specifically: excluding it makes the deleted-diff drop the
skills' old active paths from the remote tree. That is intended mirroring — the content
is a re-shippable bundled artifact, not profile configuration. Do not "fix" the shrink by
hand-restoring archived copies.
