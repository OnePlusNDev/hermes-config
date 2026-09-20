# Pre-backup plaintext-key scan — patterns, steady state, false positives

Cron backup jobs mandate: BEFORE any upload, check `config.yaml` for a plaintext
`api_key` (incl. an `sk-` prefix). If a real one is found, replace it with a
`key_env` reference BEFORE backing up. This note is the concrete recipe behind
the "Pre-Backup Security Check" section of SKILL.md.

## Scan command set (run all five, in order)
```bash
cd ~/.hermes/profiles/demo-pm
grep -nE 'sk-[A-Za-z0-9_-]{16,}' config.yaml || echo "NO sk- matches"             # task-mandated
grep -nE 'api_key' config.yaml                                                     # list every api_key line
grep -nE "api_key: *['\"]?[^'\"]{4,}" config.yaml || echo "NO non-empty api_key"   # non-empty values
grep -nE 'key_env' config.yaml                                                     # env-var refs
grep -niE '(token|secret|password) *:' config.yaml || echo NONE                    # other secret fields
```

## Steady state for demo-pm (verified 2026-09-19)
- `sk-` matches: **0**
- `api_key:` lines: **15**, ALL `''` (empty) → only a NON-EMPTY match is a finding
- `password: ''` / `secret: ''`: empty, not findings
- `key_env`: the ONLY hit is a **doc comment** (config.yaml ~line 695:
  `# For custom OpenAI-compatible endpoints, add base_url and key_env.`) — it is NOT an
  active config field. ⚠️ Do not report it as a "key_env reference" and do not treat it as a
  migration target. (Earlier run notes that counted "1 × `key_env` reference" were counting
  this same comment — the count is a false positive, not a finding.)

## If a REAL plaintext key is found (the mandated replacement)
1. Move the secret into the profile's `.env` (e.g. `DEEPSEEK_API_KEY=sk-...`). `.env` is
   always excluded from the backup, so it is the correct home for the secret.
2. Clear the config field: set `api_key: ''` in config.yaml.
3. Point the provider at the env var via the provider block's `key_env:` field (the same
   field the line-695 comment names). Confirm the exact placement against the live provider
   block before editing — do not guess top-level vs provider-nested.
4. Re-run the scan to confirm 0 non-empty `api_key` values, then proceed with the backup.

## Why this is a manual gate
GitHub push protection does NOT reliably catch a plaintext key in `config.yaml`, and the
backup uploads `config.yaml` verbatim — so this scan is the real gate for the mandated check.
