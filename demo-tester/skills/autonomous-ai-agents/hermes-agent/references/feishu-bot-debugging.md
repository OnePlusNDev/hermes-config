# Feishu Bot Debugging

Systematic diagnosis of Feishu bot problems in a multi-profile Hermes environment. Covers the full diagnostic chain: config audit → token verification → gateway log triage → root-cause identification → fix application.

## Trigger Conditions

- A bot is not receiving or responding to messages in a Feishu group
- `@bot-name` mentions are not triggering responses
- You suspect bot-to-bot communication is broken
- Feishu gateway logs show errors or unexpected behavior
- You need to verify app credentials are valid

## Prerequisites

- Access to `.env` files
- Ability to `curl` the Feishu API
- Access to gateway logs
- Multiple profile gateways may need to be running for cross-comparison

## Diagnostic Workflow

### Phase 1: Config Audit

1. Read each profile's `.env` to extract `FEISHU_APP_ID` and verify `FEISHU_ALLOW_BOTS`:
   ```bash
   cat ~/.hermes/.env                        # default/Scheduler
   cat ~/.hermes/profiles/dev-01/.env
   cat ~/.hermes/profiles/pm-01/.env
   # ... etc
   ```
2. Build an App ID mapping table. Check for **shared App IDs** — RED FLAG.
3. Verify `FEISHU_ALLOW_BOTS=mentions` is present in all profiles.

### Phase 2: App Secret Verification

Test each app's secret by requesting a tenant access token. **Do not trust cached gateway tokens**:

```bash
curl -s -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d '{"app_id":"<APP_ID>","app_secret":"<APP_SECRET>"}'
```

Expected: `"code":0` with `tenant_access_token` starting with `t-`.
Failure: `"code":10014, "msg":"app secret invalid"` — secret was rotated but not updated.

**⚠ Warning**: A gateway may continue to work with a stale secret while its cached token is still valid (~2 hour TTL).

### Phase 3: Gateway Log Triage

If a bot isn't responding to `@mentions`, check gateway logs:
- `"sender":"bot:..."` — confirms receiving from other bots
- `Sending response ... to <chat_id>` — confirms generating/sending replies
- No response log but receiving = bot received but chose not to reply (likely `mentions` filtering)
- No mention log at all = message filtered before processing

### Phase 4: Root Cause — open_id Per-App Isolation 🔑

**Most common and least obvious root cause for bot-to-bot @mention failures.**

Feishu `open_id` is **per-app isolated**: the same user/bot has a DIFFERENT `open_id` in each app's view.

Why @mentions fail: When Bot-A uses `@<open_id_from_BotA_view>`, Bot-B's app cannot match that open_id → Bot-B does not consider itself mentioned → `FEISHU_ALLOW_BOTS=mentions` does not trigger.

### Phase 5: Solutions

**Immediate fix (always works):** Use `@all` / `@所有人` — does not depend on any specific open_id.

**Long-term fix:** Build a union_id → per-app open_id mapping table.

## Verified Best Practices

- **Group broadcast to all agents**: always use `@all`
- **Directed mention to one agent**: only possible with union_id mapping table
- **Gateways that lose websocket**: after moving a bot out and back into a group, ALL gateways need restart
- **Secret rotation**: update `.env` IMMEDIATELY and restart gateways

## Common Pitfalls

1. **"It was working before"**: Likely cached token was still valid. Check secret freshness.
2. **"I used the open_id from the gateway log"**: That's the sender app's view. Not valid for receiver's @mention matching.
3. **"FEISHU_ALLOW_BOTS isn't working"**: Check spelling `mentions` (not `mention`), verify gateways restarted.
4. **Cross-profile .env confusion**: Default/Scheduler uses `~/.hermes/.env`. Profile-specific uses `~/.hermes/profiles/<name>/.env`.

## Reference

- `references/feishu-app-id-mapping.md` — Empirical App ID mapping, secret verification, open_id isolation proof from a real multi-profile debugging session.
