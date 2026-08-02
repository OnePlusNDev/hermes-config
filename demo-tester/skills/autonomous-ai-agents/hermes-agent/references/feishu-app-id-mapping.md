# App ID & Secret Verification Results (2026-06-16)

## Current App ID Mapping

| Profile | App ID | Secret Status |
|---------|--------|--------------|
| default (Scheduler) | `cli_aabbf18065e11cd3` | ✅ Token OK |
| dev-01 | `cli_aabbeea5c379dcb6` | ❌ 10014 (2026-06-16 实测) |
| pm-01 | `cli_aabbe8b5f479dce6` | ❌ 10014 (2026-06-16 实测) |
| rev-01 | `cli_aabbefb068781ce4` | ❌ 10014 (2026-06-16 实测) |
| tester-01 | `cli_aabbef59fcb9dcc7` | ❌ 10014 (2026-06-16 实测) |

## Shared App ID History

The App ID `cli_aabbf18065e11cd3` was previously shared by pm-01 AND tester-01 (both used it with different secrets, both returned 10014). As of 2026-06-16:
- pm-01 moved to `cli_aabbe8b5f479dce6`
- tester-01 moved to `cli_aabbef59fcb9dcc7`
- default (Scheduler) is the sole remaining user of `cli_aabbf18065e11cd3`, with a NEW secret that works

## open_id Isolation Proof

Same Tester bot, different apps' views (from cross-gateway log comparison):
- Reviewer app view: `ou_50e6f0cb...`
- PM app view: `ou_fb8a1b18...`
- Tester app's own view: third distinct value

## Gateway Log Evidence (2026-06-16 22:18-22:22)

Bot-to-bot communication confirmed working via @all:
- PM gateway: `Sending response (451 chars)` and `(163 chars)` to `oc_2f22...` at 22:20, 22:22
- Tester gateway: `Sending response (977 chars)` to `oc_2f22...` at 22:18
- Dev gateway: successfully sent cross-profile verification report
- Reviewer gateway: successfully received all bot messages and confirmed

## Config Checklist (all four profiles verified)

| Setting | Value | Status |
|---------|-------|--------|
| FEISHU_ALLOW_BOTS | mentions | ✅ All 4 |
| FEISHU_CONNECTION_MODE | websocket | ✅ All 4 |
| FEISHU_ALLOW_ALL_USERS | true | ✅ All 4 |
| FEISHU_GROUP_POLICY | open | ✅ All 4 |
| FEISHU_HOME_CHANNEL | oc_2f222a... | ✅ All 4 |
| FEISHU_REQUIRE_MENTION | false | ✅ All 4 |

## .env File Locations

- default/Scheduler: `/Users/oneplusn/.hermes/.env`
- dev-01: `/Users/oneplusn/.hermes/profiles/dev-01/.env`
- pm-01: `/Users/oneplusn/.hermes/profiles/pm-01/.env`
- rev-01: `/Users/oneplusn/.hermes/profiles/rev-01/.env`
- tester-01: `/Users/oneplusn/.hermes/profiles/tester-01/.env`
