# Multi-Daemon Setup: Full Architecture & Incident Log

## Final Architecture (2026-06-17)

```
Profile      Daemon Port    PG Management    Health
default      9170           auto (pg0)       healthy/connected
tester-01    9177           auto (pg0)       healthy/connected
pm-01        9178           auto (pg0)       healthy/connected
dev-01       9179           auto (pg0)       healthy/connected
rev-01       9180           auto (pg0)       healthy/connected
```

- All daemons: `hindsight-api --daemon --idle-timeout 86400 --port XXXX`
- All daemons started via `execute_code` subprocess (NOT terminal, to avoid `***` cred masking)
- All use z.ai GLM key (45af10...) + `https://api.z.ai/api/paas/v4`
- Each profile has metadata.json + .env in `~/.hermes/profiles/<name>/home/.hindsight/profiles/`
- **pg0 limitation**: All daemons share ONE PostgreSQL instance (`~/.pg0`). `PG0_HOME` env var is NOT respected. True memory isolation requires unique `bank_id` per profile.

## Incident Timeline

### Problem 1: Single daemon, multiple profiles (initial state)
- pm-01 daemon occupied port 9177 → PostgreSQL 5432 (402 memories)
- tester-01 had PostgreSQL 5434 but no daemon
- Both profiles shared port 9177

### Problem 2: Shared hindsight-embed profile
- Only one profile registered: "hermes" on port 9177
- All profiles tried to connect to the same daemon

### Problem 3: Port assignment chaos
- Created profiles with `hindsight-embed profile create` but ports auto-incremented to wrong values (9259, 9485, 9324)
- Actual daemons on 9177-9180, but profiles registered different ports
- Solution: delete + recreate profiles with explicit `--port` matching actual daemon ports

### Problem 4: Database migration failures
- Setting `HINDSIGHT_API_DATABASE_URL` to manually-created PGs caused `RuntimeError: Database migration failed`
- Root cause: manually-created PGs lack pgvector extension, hindsight schema, or have incompatible versions
- Solution: DO NOT set DATABASE_URL; let daemon auto-manage via pg0

### Problem 5: Env files under wrong profile home
- All profile env files created under tester-01's home by `hindsight-embed profile create`
- Moved to each profile's own home: `~/.hermes/profiles/<name>/home/.hindsight/profiles/`
- Each needs its own metadata.json with only that profile's entry

### Problem 6: API key loss after profile recreation
- `hindsight-embed profile delete` + `profile create` regenerates .env as template (no key)
- Must restore `HINDSIGHT_API_LLM_API_KEY` value after recreation
- Read key from another profile's .env or from profile's `.env` file

### Problem 7: --idle-timeout 0 kills daemon instantly
- 0 = no idle allowed = immediate shutdown
- Fixed by using 86400 (24 hours)

### Problem 8: Foreground daemons die with parent
- Started without `--daemon`, daemons died when sandbox/shell terminated
- Fixed by using `--daemon` flag which double-forks

### Problem 9: default profile overlooked
- `~/.hermes/hindsight/config.json` exists but no daemon was created
- default profile home is `~/.hermes/home/` (not under profiles/)
- Needs its own metadata at `~/.hermes/home/.hindsight/profiles/`

### Problem 10: pg0 auto-created PG for one daemon killed by pkill
- `pkill -9 -f postgres` kills ALL PG instances including the one daemon relies on
- After kill, daemon reports "healthy" briefly then "unhealthy" as PG restart fails
- Must restart daemons after killing PG

### Problem 11: PG0_HOME env var has no effect
- pg0 binary always uses `Path.home()/.pg0` regardless of `PG0_HOME`
- Attempting per-profile PG isolation via `PG0_HOME` fails silently
- All daemons end up on the same `~/.pg0` instance

## Health Verification Commands

```bash
# Check all daemons
for port in 9170 9177 9178 9179 9180; do
  echo -n "$port: "
  curl -s --max-time 2 http://127.0.0.1:$port/health
done

# Check hindsight-embed profile registration
HERMES_HOME=~/.hermes hindsight-embed profile list

# Check running processes
ps aux | grep "hindsight-api\|hindsight_api.main" | grep -v grep

# Check PostgreSQL instances
lsof -iTCP -sTCP:LISTEN -P -n | grep postgres

# Query memory count (need psql from pg0 installation)
PGINSTALL=$(find ~/.hermes -path "*/installation/*/bin/psql" | head -1)
PGPASSWORD=hindsight $PGINSTALL -h 127.0.0.1 -p <pg_port> -U hindsight -d hindsight \
  -c "SELECT count(*) FROM memory_units;"
```

## Credential Locations

- **z.ai GLM key**: Found in `~/.hermes/profiles/dev-01/.env` as `HINDSIGHT_API_LLM_API_KEY` (len=49, prefix=45af1058)
- **DeepSeek key**: Found in `~/.hermes/profiles/tester-01/.env` as `DEEPSEEK_API_KEY` (len=35, prefix=sk-d04b1)
- **pg0 credentials**: `~/.pg0/instances/<name>/instance.json` or `<profile_home>/.pg0/instances/<name>/instance.json` — default user=hindsight, password=hindsight

## Table Detection Quirk

When querying PG directly: if `\dt` shows no tables and `SELECT count(*) FROM memory_units` fails with "relation does not exist", the database was freshly created by pg0 but the daemon hasn't run schema migrations yet. This happens when daemon was started with `--daemon` + explicit `DATABASE_URL` — the child process fails migrations silently (no pgvector). With auto-managed pg0, migrations run as part of daemon startup and succeed.
