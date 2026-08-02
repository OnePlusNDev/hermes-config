# Hindsight Memory Classification
Generated: 2026-07-22
Tool: hindsight-api reflect on bank=demo-tester

Based on the information retrieved, here is the classification of the MEMORY.md sections:

1. "对话主模型（2026-06-14）" — [STALE] - The model configuration from June 14 is older than 30 days and is not relevant to the current profile.
2. "Issue 处理规则" — [CURRENT] - The issue handling workflow is still valid and applicable.
3. "测试质量标准（Issue #9 经验）" — [CURRENT] - The testing standards are still valid and applicable.
4. "飞书 Bot 互通规则" — [STALE] - The Feishu bot configuration with App IDs is older than 30 days and the tester secret is invalid.
5. "Archived > Hindsight Daemon Config（属 tester-01 profile）" — [STALE] - This section explicitly belongs to the tester-01 profile and is not relevant to the demo-tester profile.

For the USER.md sections:

6. All user collaboration protocol rules — [CURRENT] - These are timeless operational norms and are still valid.

Additional checks:

- The DeepSeek model from June 14 still needs to be in memory as it's the current main model.
- The stale tester secret (cli_aabbef59fcb9dcc7) is still actionable.
- The cross-profile Hindsight config section does not belong here as it is for the tester-01 profile.

DRAFT consolidated MEMORY.md:

---
## 对话主模型
- 对话主模型：deepseek（model=deepseek-v4-pro, base_url=api.deepseek.com/v1）
- .env 内仍保留 GLM_API_KEY 作为回退

## Issue 处理规则
- assignee 是 demo-tester（我）就必须处理，不管 status tag
- 处理流程（task-polling cronjob）：
  1. 搜索 assignee=demo-tester 的 open issue
  2. 无任务则 [SILENT]
  3. 有任务则：a.读所有 comment → b.回复告知开始处理+概述+计划 → c.执行 → d.回复结果 → e.reassign 给下一步 → f.无法完成时 @ 相关同事

## 测试质量标准
1. 不采信自评，必须从干净源码重新执行验证
2. 留可复现的测试夹具供后续复用
3. 对照验证必须两端都实际执行，不凭推测声称差异
4. 检查源码 mtime 确保测试最新版本
5. 读完全部 comment 再动手
6. 做完必须 reassign 给下一步处理人
7. 报告里避免未经验证的假设——没跑过就说没跑过

## 飞书 Bot 互通规则
- @all 比定向 open_id 可靠（飞书 open_id 按应用隔离）
- FEISHU_ALLOW_BOTS=mentions 生效
- 群 chat_id=oc_2f222a40
- 应用 App ID: default=cli_aabbf18065e11cd3, tester=cli_aabbef59fcb9dcc7
- ⚠️ tester secret 10014 invalid（2026-06-16），需更新
- 回复规范：只发最终结果和结论，不发中间分析过程

## Archived
### 历史模型配置记录
- 2026-06-14 对话主模型切换记录：deepseek-v4-pro（provider=deepseek），保留 GLM_API_KEY 备用