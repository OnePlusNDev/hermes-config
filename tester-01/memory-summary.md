# tester-01 Memory Summary (2026-08-02)

## Model Configuration
- Main model: deepseek-v4-pro (api.deepseek.com/v1)
- API key env: DEEPSEEK_API_KEY

## Issue Handling Rules
- Only check assignees field, ignore status tag
- If assignee=tester-01 then process regardless of status
- Full workflow: search, read comments, reply, execute, update, reassign
- Deliver via feishu (Home channel)

## Testing Quality Standards (from Issue #9)
1. Independent verification from clean source -- no self-assessment
2. Leave reproducible test harness scripts
3. Cross-platform comparison must execute both sides
4. Check source mtime for latest version
5. Read all comments before acting
6. Always reassign after completion
7. Never assert "Android expects X" without running Android

## Feishu Bot Interop
- Use @all over direct open_id (app-isolated)
- FEISHU_ALLOW_BOTS=mentions active
- Group chat_id: oc_2f222a40
- 5 App IDs: default/dev/pm/rev/tester

## Profile Secrets Status
- WARNING: dev/pm/rev/tester all 10014 invalid (2026-06-16)
- Needs renewal via Feishu console

## Output Rules
- Reply only with final results, no intermediate process
- Keep messages concise and data-driven

## OpenID Mapping (App-Isolated)
- Boss: ou_1a0460d0...2739 (Rev) / ou_88737568...fbcf
- PM: ou_f0c8c556...d092 (Rev) / ou_18cd0f78...3c7a (Tester)
- Tester: ou_50e6f0cb...2b04 (Rev) / ou_fb8a1b18...5334 (PM)

