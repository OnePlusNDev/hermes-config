# Example: tester-01 daemon verification session

## Context
Multi-profile setup on single macOS machine. pm-01 and tester-01 both have Hindsight local_embedded configured. The question was: "does tester-01 have its own daemon or is it sharing pm-01's?"

## Command transcript

### Step 1: Raw process listing (MISLEADING)

```
$ ps aux | grep hindsight-api | grep -v grep
oneplusn  58148  ... /venv/bin/python3 /venv/bin/hindsight-api --daemon --idle-timeout 300 --port 9177
```

This shows ONE daemon on port 9177. Alone, this tells you nothing about which profile it serves.

### Step 2: Find all PostgreSQL instances

```
$ ps aux | grep postgres | grep hindsight
oneplusn  34873  ... postgres -D ~/.hermes/profiles/tester-01/home/.pg0/instances/hindsight-embed-hermes/data -p 5434 ...
oneplusn  23191  ... postgres -D ~/.pg0/instances/hindsight-embed-hermes/data -p 5432 ...
```

Two PostgreSQL instances:
- Port 5434 → tester-01's home
- Port 5432 → default/global home (pm-01's)

### Step 3: Authoritative profile mapping

```
$ HERMES_HOME=~/.hermes hindsight-embed profile list
Profiles:
  hermes ● running
    Port: 9177
    Config: /Users/oneplusn/.hermes/profiles/tester-01/home/.hindsight/profiles/hermes.env
```

The "hermes" profile runs on port 9177 and uses tester-01's config path. This is the ground truth.

### Step 4: Daemon status confirms database

```
$ HERMES_HOME=~/.hermes hindsight-embed -p hermes daemon status
Daemon is running
  URL: http://127.0.0.1:9177
  Database: ~/.hermes/profiles/tester-01/home/.pg0/instances/hindsight-embed-hermes
```

The database path matches tester-01's PostgreSQL (port 5434). Confirmed.

### Step 5: Read/write test

Retain → stored successfully. Recall → retrieved. Reflect → synthesized answer with the new data. All pass.

## Key lesson
The daemon on 9177 IS tester-01's. The initial assumption that it belonged to pm-01 was wrong — corrected by `hindsight-embed profile list`.
