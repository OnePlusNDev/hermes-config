# Hindsight Memory Classification
Generated: 2026-07-16
Tool: hindsight-api reflect on bank=demo-tester

### MEMORY.md Sections Classification

1. **对话主模型（2026-06-14）** - [STALE] - References a date older than 30 days and is not relevant to the current profile.
2. **Issue 处理规则** - [CURRENT] - No explicit date, and the issue handling workflow is still valid.
3. **测试质量标准（Issue #9 经验）** - [CURRENT] - No explicit date, and the testing standards are still relevant.
4. **飞书 Bot 互通规则** - [STALE] - Contains a tester secret marked invalid on 2026-06-16, making it outdated.
5. **Archived > Hindsight Daemon Config（属 tester-01 profile）** - [STALE] - Explicitly labeled for tester-01, not demo-tester.

### USER.md Sections Classification

6. **All user collaboration protocol rules** - [CURRENT] - These are timeless operational norms.

### Additional Checks

- The DeepSeek model from Jun 14 still needs to be in memory as it's the current main model. - [CURRENT]
- The stale tester secret (cli_aabbef59fcb9dcc7) is not actionable and should be updated. - [STALE]
- The cross-profile Hindsight config section does not belong here and should be removed. - [REMOVED]

### Draft Consolidated MEMORY.md

```markdown
---
## Current Workflow
- Issue 处理规则
  - assignee 是 demo-tester（我）就必须处理，不管 status tag
  - 处理流程（task-polling cronjob）：
    1. 搜索 assignee=demo-tester 的 open issue
    2. 无任务则 [SILENT]
    3. 有任务则：a.读所有 comment → b.回复告知开始处理+概述+计划 → c.执行 → d.回复结果 → e.reassign 给下一步 → f.无法完成时 @ 相关同事
- 测试质量标准（Issue #9 经验）
  1. 不采信自评，必须从干净源码重新执行验证
  2. 留可复现的测试夹具供后续复用
  3. 对照验证必须两端都实际执行，不凭推测声称差异
  4. 检查源码 mtime 确保测试最新版本
  5. 读完全部 comment 再动手
  6. 做完必须 reassign 给下一步处理人
  7. 报告里避免未经验证的假设——没跑过就说没跑过

## Configuration
- 飞书 Bot 互通规则
  - @all 比定向 open_id 可靠（飞书 open_id 按应用隔离）
  - FEISHU_ALLOW_BOTS=mentions 生效
  - 群 chat_id=oc_2f222a40
  - 应用 App ID: default=cli_aabbf18065e11cd3, tester=cli_aabbef59fcb9dcc7
  - ⚠️ tester secret 10014 invalid（2026-06-16），需更新

## Historical
- 对话主模型（2026-06-14）
```

This draft removes redundancy, moves stale items to the "## Historical" section, and removes items that belong to other profiles.