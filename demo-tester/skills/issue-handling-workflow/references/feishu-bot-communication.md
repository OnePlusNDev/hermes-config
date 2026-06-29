# Feishu Bot-to-Bot Communication — Full Diagnostic Workflow

## Two-tier Root Cause Map

When a bot doesn't respond to @mentions from another bot, there are TWO possible root causes. Diagnose in order:

```
Bot A @mentions Bot B in Feishu group → Bot B doesn't respond
  │
  ├── Tier 1: Gateway process dead (MOST COMMON — 80%+)
  │   ps aux | grep "gateway.*<profile>"
  │   If no process → hermes --profile <profile> gateway run --replace
  │
  └── Tier 2: Feishu event subscription / config (rare)
      Check FEISHU_ALLOW_BOTS=mentions in .env
      Check Feishu Developer Console event subscription
```

## Tier 1: Check Gateway Process Liveness

### Check if gateway is running

```bash
ps aux | grep "gateway" | grep -v grep
```

Expected: one process per agent profile, each with `HERMES_HOME` pointing to the correct profile.

```bash
# Detailed check with profile mapping
ps aux | grep "gateway" | grep -v grep | while read line; do
  pid=$(echo "$line" | awk '{print $2}')
  env=$(ps eww $pid 2>/dev/null | tr ' ' '\n' | grep HERMES_HOME | head -1)
  echo "PID=$pid $env"
done
```

| Profile | Expected HERMES_HOME |
|---------|---------------------|
| pm-01   | `/Users/oneplusn/.hermes/profiles/pm-01` |
| dev-01  | `/Users/oneplusn/.hermes/profiles/dev-01` |
| rev-01  | `/Users/oneplusn/.hermes/profiles/rev-01` |
| tester-01 | `/Users/oneplusn/.hermes/profiles/tester-01` |

### Start missing gateway

```bash
hermes --profile <profile> gateway run --replace
```

The gateway process runs indefinitely — verify with `ps aux` that it appears.

## Tier 2: Check Message Reception

### Check if the specific message arrived

```bash
grep "<message_id>" ~/.hermes/profiles/<profile>/logs/gateway.log
```

If you see `Inbound group message received:` with `sender=bot:<your_bot_id>`, then bot-to-bot messages ARE working.

### Check ALL inbound group messages

```bash
grep "Inbound group message" ~/.hermes/profiles/<profile>/logs/gateway.log | tail -20
```

Look at the `sender=` field:
- `sender=user:...` — human user messages (should always appear)
- `sender=bot:...` — bot messages (only appear if correctly configured)

### Key log event: bot message received ✅

```
[Feishu] Inbound group message received: id=om_x100b6c2017b438...
type=text chat_id=oc_2f222a407e... sender=bot:ou_43f3c3570...
text='收到请回复 —— tester-01 测试'
```

## Tier 3: Check Configuration

### Hermes-side: FEISHU_ALLOW_BOTS

All profiles must have in their `.env`:

```
FEISHU_ALLOW_BOTS=mentions
```

This tells the Hermes Feishu gateway to accept and process bot-sent messages.

### Feishu-side: Event Subscription

In the Feishu Developer Console (`https://open.feishu.cn/app`), each app needs:

- Subscribed event: `im.message.receive_v1` (接收消息 v2.0)
- Permission: **「获取群组中其他机器人和用户@当前机器人的消息」** — CRITICAL

The full set of recommended permissions:
| Permission | Required? |
|-----------|-----------|
| 获取群组中其他机器人和用户@当前机器人的消息 | ✅ Required |
| 获取群组中用户@机器人消息 | ✅ Required |
| 读取用户发给机器人的单聊消息 | ✅ Required |
| 获取群组中所有消息（敏感权限） | ❌ Not needed |

## Diagnostic Priority Checklist

1. ☐ Gateway process running? → Tier 1
2. ☐ Gateway logs show Inbound group messages from `sender=bot:`? → Tier 2
3. ☐ `FEISHU_ALLOW_BOTS=mentions` in .env? → Tier 3 (Hermes)
4. ☐ Feishu Developer Console has bot message permission? → Tier 3 (Feishu)

## Common Pitfalls

- **Gateway was running but crashed silently.** PM's gateway had no process but old logs existed. Always check `ps aux`, not just logs.
- **Gateway restart fixes 80% of "not responding" issues.** Start here, don't jump to Feishu config changes.
- **Different App IDs per profile.** Each agent has its own Feishu App (`FEISHU_APP_ID`). All need the same event subscription permissions.
- **After Feishu config changes, restart the gateway.** The websocket connection re-negotiates subscriptions on connect.

## Real Case: 2026-06-16 PM Not Responding

1. User reports PM doesn't respond to tester-01's @mention
2. Checked logs → PM's gateway only had `sender=user:...` entries, zero `sender=bot:...`
3. Checked processes → PM's gateway process WAS NOT RUNNING
4. Started `hermes --profile pm-01 gateway run --replace`
5. Retested @mention → PM's gateway NOW received `sender=bot:ou_43f3c3570...`
6. Conclusion: gateway process was dead, not a Feishu permission issue

## Tier 4: Bot Re-added to Chat — Websocket Subscription Reset

### The "Bot added to chat" cascade failure

**Scenario:** When ANY bot in a group chat is removed and re-added (or even just re-added), Feishu resets the websocket event subscriptions for ALL bots in that group. This causes an immediate and complete loss of bot-to-bot message delivery across every agent.

**Diagnostic signal:** You'll see this in the re-added bot's gateway log:

```
[Feishu] Bot added to chat: oc_2f222a407e7f89e272c2ef1ccf7d601a
```

After this event, every other bot will:
- ✅ Continue receiving `sender=user:...` messages (user messages)
- ❌ STOP receiving `sender=bot:...` messages from ALL other bots

The user may have changed NOTHING in the Feishu Developer Console — the add-to-chat event alone is sufficient to break bot messaging.

### Fix: Pan-profile gateway restart

After a "Bot added to chat" event, **ALL** gateway processes must be restarted (not just the re-added bot's):

```bash
# Step 1: Kill old processes (watch for duplicates)
ps aux | grep "gateway run" | grep -v grep | awk '{print $2}' | xargs kill 2>/dev/null

# Step 2: Wait for cleanup
sleep 5

# Step 3: Kill any stubborn duplicates with -9
ps aux | grep "gateway run" | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null

# Step 4: Verify no lingering processes
ps aux | grep "gateway run" | grep -v grep  # should be empty

# Step 5: Restart ALL profiles
for profile in pm-01 dev-01 rev-01 tester-01; do
  hermes --profile $profile gateway run --replace &
done

# Step 6: Wait for websocket handshake (~30s)
sleep 30

# Step 7: Verify each profile has ONE gateway process
ps aux | grep "gateway run" | grep -v grep
```

### Duplicate gateway processes

A common side effect of restarting gateways is duplicate processes. Old processes may not die cleanly on `kill`, resulting in 2+ gateway instances per profile. This causes undefined behavior.

**Check for duplicates:**
```bash
ps aux | grep "gateway run" | grep -v grep | awk '{print $2, $11, $12, $13, $14, $15, $16}'
```

If any profile shows more than one `gateway run` process, kill the older PID (identified by earlier start time in `ps` output):
```bash
kill -9 <older_pid>
```

**Better approach:** Kill ALL gateway processes and restart clean (Steps 1-5 above).

## Tier 5: Intermittent/Recurring Failure — "Works After Restart, Then Breaks Again"

### Symptom

After a pan-profile restart, bot messages work for a few minutes, then ALL bots stop receiving `sender=bot:` messages again. User messages continue to be received normally.

### Diagnostic Pattern

Timeline from real case (2026-06-16):
```
20:46-20:49  Bot messages delivered to ALL gateways ✅
20:50-21:54  All gateways restarted (multiple cycles)
21:46        "Bot added to chat: oc_2f222a4..." in tester-01 log
21:54        User message (type=post) received by ALL gateways ✅
21:55+       Bot messages → NONE received by any gateway ❌
22:11        User messages still received by PM's gateway ✅
22:30+       Bot messages still not received ❌
```

The pattern: bot-to-bot delivery dies at some point after restart, while user message delivery works flawlessly throughout.

### Likely Causes

1. **Feishu platform silently drops bot→bot messages after initial delivery.** Some Feishu tenants/apps have undocumented rate limits or filtering on bot-sent messages in group chats.
2. **Websocket heartbeat/session expiry.** If the Feishu long-connection websocket's session token expires without graceful reconnection, bot message subscriptions may be dropped while user message subscriptions persist (because user messages use a different dispatch path).
3. **App-level throttling.** Feishu may throttle bot message delivery if a bot sends too many messages in a short window.

### Diagnostic: Feishu API App Status Check

Use the Feishu Open API to verify each app is active and has correct permissions. This bypasses the websocket entirely and checks server-side state:

```bash
# Step 1: Get tenant_access_token for the app
curl -s -X POST \
  'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d '{"app_id":"<APP_ID>","app_secret":"<APP_SECRET>"}'

# Step 2: Check app status
curl -s \
  'https://open.feishu.cn/open-apis/application/v6/applications/<APP_ID>' \
  -H 'Authorization: Bearer ***
```

Expected response: `"status": 2` (published/active). If status is not 2, the app needs to be published in the Developer Console.

### Fix Attempt Order

1. **Pan-profile restart** (Tier 4 Steps 1-5) — works in ~50% of cases
2. **Re-invite ALL bots to the group** — remove each bot and re-add. This forces fresh websocket subscriptions for every bot.
3. **Check Feishu Developer Console** — ensure all 4 apps are "已发布" (published), not just saved as drafts
4. **Wait and retest** — some Feishu subscription changes take 5-15 minutes to propagate

### When All Fixes Fail

If bot→bot messages persistently fail after restart + re-invite + publish, the Feishu platform itself may not support reliable bot-to-bot event delivery in the current tenant configuration. **Fallback to GitHub Issue comments as the inter-agent communication channel.** This is reliable and independent of Feishu's bot message routing.

## Batch Fix: All-Agent Gateway Health Check

When one agent's gateway is found dead, **check ALL agents** — the same root cause (crashed/stale process) often affects multiple profiles. Follow this pattern:

```bash
# 1. Kill ALL gateway processes (clean slate)
ps aux | grep "gateway run" | grep -v grep | awk '{print $2}' | xargs kill 2>/dev/null
sleep 5

# 2. Restart each profile
for profile in pm-01 dev-01 rev-01 tester-01; do
  hermes --profile $profile gateway run --replace &
done

# 3. Wait for websocket reconnection (~30s)
sleep 30

# 4. Send test @mention from one bot to each other bot
send_message(target='feishu:用户216043', 
  message='<at user_id="<target_open_id>">Agent</at> restart test')

# 5. Verify each gateway log has the bot message
grep "sender=bot:" ~/.hermes/profiles/<profile>/logs/gateway.log | tail -1
```

### Priority order when fixing

```
1. Kill stuck processes FIRST (use `kill <pid>`)
2. Start gateway with --replace flag
3. Verify with test @mention
4. Move to next agent
```

**Common trap:** `ps eww $pid` sometimes shows wrong `HERMES_HOME` for child Python processes. To identify which profile a gateway serves, read the command line instead:
```bash
ps aux | grep "hermes.*profile\|gateway run" | grep -v grep
```
