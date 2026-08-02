# Hindsight 记忆分类报告
生成时间: 2026-07-21
银行: demo-tester

### Memory Classification

#### 对话主模型
- **[CURRENT]** - This section is relevant and up-to-date with the current model and API key information.

#### Issue 处理规则
- **[CURRENT]** - This section outlines the current process for handling issues, which is essential for the team's workflow.

#### 测试质量标准
- **[CURRENT]** - These standards are critical for maintaining high-quality testing practices.

#### 飞书 Bot 互通规则
- **[CURRENT]** - This section contains important rules for communication using the Feishu platform.

#### Archived
### 历史模型配置记录
- **[ARCHIVE]** - This section is historical and contains information about past model configurations.

### Stale Memory Identification
- **[STALE]** - There is no direct indication of a stale memory in the provided content. However, the '飞书 Bot 互通规则' section mentions that the tester secret 10014 is invalid (2026-06-16), which suggests that the information might be outdated and requires an update.

### Draft Consolidated MEMORY.md

```markdown
## 对话主模型
- 当前模型 deepseek (deepseek-v4-flash, provider=deepseek, base_url=api.deepseek.com/v1)
- 回退 GLM_API_KEY 保留于 .env

## Issue 处理规则
- assignee=demo-tester 的 open issue 必须处理 (不论 status tag)
- 流程: ①搜索 open issue → ②无则 [SILENT] → ③读全部 comment → ④通知开始+计划 → ⑤执行 → ⑥回复结果 → ⑦reassign 下一步 → ⑧遇阻 @ 相关同事

## 测试质量标准
1. 不采信自评 — 从干净源码重新执行
2. 留可复现的测试夹具
3. 对照验证两端实际执行，不凭推测声称差异
4. 检查源码 mtime 确保最新版本
5. 读完全部 comment 再动手
6. 完成后 reassign 给下一步处理人
7. 报告避免未经验证的假设

## 飞书 Bot 互通规则
- @all 比定向 open_id 可靠 (飞书 open_id 按应用隔离)
- FEISHU_ALLOW_BOTS=mentions 生效
- 群 chat_id=oc_2f222a40
- 应用 App ID: default=cli_aabbf18065e11cd3, tester=cli_aabbef59fcb9dcc7
- ⚠️ tester secret 10014 invalid (2026-06-16), 需更新
- 回复规范: 只发最终结果和结论
```

This draft aims to be 20-30% shorter than the current MEMORY.md by removing unnecessary details and focusing on the essential information.

## Token 消耗
{
  "input_tokens": 2768,
  "output_tokens": 615,
  "total_tokens": 3383,
  "cached_tokens": 0
}