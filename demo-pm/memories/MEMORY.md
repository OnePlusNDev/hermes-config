# MEMORY.md — demo-pm（项目牧羊人）

> 最后更新: 2026-07-12 | 经 Hindsight v0.8.2 整理

---

## 1. GitHub Issue 处理

**规则**: 只看 assignees（唯一），不看 status tag。读完所有 comment 再动手。

**流程**: 搜索 open issue → [SILENT]若无任务 → 若有时: 回复概述+计划 → 执行 → 更新 comment → reassign 下一步人。交付走飞书 Home channel。

**测试标准 (#9)**: 不采信自评；从干净源码独立验证；留可复现 harness；检查 mtime 确保最新版；两端都执行对照；做完 reassign；避免未验证假设。

## 2. 飞书/Feishu

**Bot**: FEISHU_ALLOW_BOTS=mentions ✅; FEISHU_ALLOW_ALL_USERS ❌。
**群 chat_id**: `oc_2f222a40`。Cron 用 @all（缺 `im:chat:readonly` 99991672）。

**App ID**:

| 环境 | App ID |
|------|--------|
| default | `cli_aabbf18065e11cd3` |
| dev | `cli_aabbeea5c379dcb6` |
| pm | `cli_aabbe8b5f479dce6` |
| rev | `cli_aabbefb068781ce4` |
| tester | `cli_aabbef59fcb9dcc7` |

**⚠️ 4 profile secret 10014 invalid（2026-06-16）**—需去飞书后台更新。
**Gateway**: `hermes --profile X gateway run --replace`

## 3. Hindsight

**全局 API**: :8888（daemon since Jun 19, bank=hermes, 20 facts）。
**Port 分配**: tester=9177, pm=9178, dev=9179, rev=9180。启动: `HINDSIGHT_API_LLM_API_KEY=<key> hindsight-embed -p <profile> daemon start`
**Key**: z.ai GLM + `https://api.z.ai/api/paas/v4`

## 4. LLM/模型

tester-01 主模型: deepseek-v4-pro（since 2026-06-14），端点为 `api.deepseek.com/v1`。回退: GLM_API_KEY。
