# MEMORY.md — demo-pm（项目牧羊人）

> 最后更新: 2026-07-10

---

## 1. 项目管理工具

### 1.1 GitHub Issue 处理流程

**基本规则**
- **只看 assignees，不看 status tag** — assignee 是 tester-01 就必须处理
- status tag 是给 boss 看的，非执行判断依据
- assignees 不会是多人

**Task-Polling CronJob 流程**
1. 搜索 assignee=tester-01 的 open issue
2. 无任务 → [SILENT]（不发送任何消息）
3. 有任务 → a. 读全部 comment → b. 回复告知开始处理+概述+计划 → c. 实际执行 → d. 更新 comment 说明结果 → e. 流转 assignee → f. 无法独立完成时 @ 相关同事
4. deliver 改为 feishu（Home channel），有任务时发私信通知

**Issue #9 测试质量标准**
1. 不采信自评，必须独立从干净源码重新执行验证
2. 留可复现的测试夹具（harness 脚本）
3. 对照验证必须两端都实际执行
4. 检查源码 mtime 确保测试的是最新版本
5. 读完全部 comment 再动手
6. 做完必须 reassign 给下一步处理人
7. 报告里避免未经验证的假设

---

## 2. 基础设施与工具配置

### 2.1 飞书/Feishu

**Bot 互通规则**
- **用 @all 比定向 open_id 可靠**（飞书 open_id 按应用隔离）
- FEISHU_ALLOW_BOTS=mentions ✅ 生效；FEISHU_ALLOW_ALL_USERS / FEISHU_GROUP_POLICY ❌ 无效

**群组与 App ID**

| 环境 | App ID |
|------|--------|
| default | `cli_aabbf18065e11cd3` |
| dev | `cli_aabbeea5c379dcb6` |
| pm | `cli_aabbe8b5f479dce6` |
| rev | `cli_aabbefb068781ce4` |
| tester | `cli_aabbef59fcb9dcc7` |

**OpenID 映射**（按应用隔离）

| 角色 | Rev App | Tester/PM App |
|------|---------|---------------|
| Boss | `ou_1a0460d0...2739` | `ou_88737568...fbcf` |
| PM | `ou_f0c8c556...d092` | `ou_18cd0f78...3c7a` |
| Tester | `ou_50e6f0cb...2b04` | `ou_fb8a1b18...5334` |

**Scheduler 权限**
- 缺少 `im:chat:readonly`（ID: 99991672），开通前 cron 用 @all
- ⚠️ **archive: dev/pm/rev/tester 四 profile secret 均 10014 invalid（2026-06-16）** — 问题持续 24 天未解决，已归档为已知阻塞项。需尽快去飞书后台更新。

**Gateway**
- 查看：`ps aux | grep gateway`
- 重启：`hermes --profile X gateway run --replace`

### 2.2 Hindsight 部署

**Daemon 端口分配**

| Profile | Port |
|---------|------|
| tester-01 | 9177 |
| pm-01 | 9178 |
| dev-01 | 9179 |
| rev-01 | 9180 |

所有 daemon 用 `--daemon --idle-timeout 86400` 启动，自管 PG。
LLM key 用 z.ai GLM + `https://api.z.ai/api/paas/v4`。
每个 profile 的 `home/.hindsight/profiles/` 下有独立 metadata.json + env。
不设 DATABASE_URL 让 daemon 自管 PG。
env 中的 `HINDSIGHT_API_LLM_API_KEY` 必须写实际 key 值。

**当前状态（2026-07-07 快照）**
- profile=demo-pm, port=9178, daemon=❌ 未运行（检查确认 daemon_running=false）
- 全局 hindsight-api 运行在 :8888（bank=hermes, 20 facts）
- 如需启动：`HINDSIGHT_API_LLM_API_KEY=<key> hindsight-embed -p demo-pm daemon start`

### 2.3 LLM/模型配置

- tester-01 主模型：deepseek-v4-pro（自 2026-06-14），端点 `api.deepseek.com/v1`，key_env=`DEEPSEEK_API_KEY`
- 回退：GLM_API_KEY + z.ai 端点（注释待清理）
