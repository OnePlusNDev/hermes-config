# Hindsight Consolidation Report
Generated: 2026-07-14
Source: MEMORY.md (2026-06-17) + USER.md (2026-06-17)

```markdown
# Consolidated Knowledge Summary

## 1. Model & Provider Config
- 对话主模型已切换为 deepseek（model=deepseek-v4-flash, provider=deepseek, base_url=api.deepseek.com/v1）
- .env 内仍保留 GLM_API_KEY 作为回退

## 2. Issue Handling Workflow
- assignee 是 demo-tester（我）就必须处理，不管 status tag
- 处理流程（task-polling cronjob）：
  1. 搜索 assignee=demo-tester 的 open issue
  2. 无任务则 [SILENT]
  3. 有任务则：a.读所有 comment → b.回复告知开始处理+概述+计划 → c.执行 → d.回复结果 → e.reassign 给下一步 → f.无法完成时 @ 相关同事

## 3. Testing Quality Standards
1. 不采信自评，必须从干净源码重新执行验证
2. 留可复现的测试夹具供后续复用
3. 对照验证必须两端都实际执行，不凭推测声称差异
4. 检查源码 mtime 确保测试最新版本
5. 读完全部 comment 再动手
6. 做完必须 reassign 给下一步处理人
7. 报告里避免未经验证的假设——没跑过就说没跑过

## 4. Hindsight / Daemon Config
- 需要更新的 tester secret 10014（2026-06-16）

## 5. Feishu Bot Config
- @all 比定向 open_id 可靠（飞书 open_id 按应用隔离）
- FEISHU_ALLOW_BOTS=mentions 生效
- 群 chat_id=oc_2f222a40
- 应用 App ID: default=cli_aabbf18065e11cd3, tester=cli_aabbef59fcb9dcc7
- ⚠️ tester secret 10014 invalid（2026-06-16），需更新
- 回复规范：只发最终结果和结论，不发中间分析过程

## 6. User Collaboration Protocol
- **核心铁律 (零容忍)**:
  1. 绝对自主：遇阻自行解决。严禁以“无法做到”、“未收到消息”为由推诿。
  2. 直击根因：出问题只报核心原因，禁止绕圈子找技术借口。
  3. 杜绝复犯：利用 `memory` 记录教训。同类问题复现即违规。
  4. 端到端验证：改完配置必须测试生效，未经证实视为未完成。
  5. PM 权责：你是协调中枢。跨 Agent 调度自己解决，**严禁**将协调难题抛给 Boss。
- **飞书沟通规范**:
  - 内容：**仅发最终结果**。禁止发送“正在处理”、日志详情或中间过程。
  - 格式：极简、数据化、条目清晰。
  - 频率：任务完成或重大阻断时，一次性同步。
- **交互逻辑**:
  - Boss: “处理 X。”
  - Agent: [执行] -> [自查/测试] -> [飞书同步最终结果]。
  - 遇阻: 启动 Plan B/C，直至解决后再汇报。
- **禁止事项 (Anti-Patterns)**:
  - 请示“是否继续？”或“可否执行？”
  - 只报错不修复，或只描述现象不分析原因。
  - 飞书刷屏发送调试日志。
  - 未经测试就标记任务完成。
- **用户（PM 要求）偏好**：Bot 回复只发结果和结论，不发中间推理过程。所有 Bot 必须遵守此规则，保持消息简洁。
```