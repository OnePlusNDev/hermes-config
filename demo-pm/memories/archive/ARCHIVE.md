# ARCHIVE.md — demo-pm 记忆归档

> 记忆清理时间: 2026-08-12
> 清理工具: Hindsight v0.8.2（profile daemon :9178，HF_HUB_OFFLINE=1 启动）

---

## 归档记录

| 文件 | 原始日期 | 大小 | 说明 |
|------|---------|------|------|
| `MEMORY-20260710.snapshot.md` | 2026-07-10 | 2,826 B | 旧版 MEMORY.md.bak |
| `USER-20260710.snapshot.md` | 2026-07-10 | 1,335 B | 旧版 USER.md.bak |
| `MEMORY-20260812.snapshot.md` | 2026-07-12 | 1,578 B | 达到 30 天归档窗口的 MEMORY.md |
| `USER-20260812.snapshot.md` | 2026-07-12 | 1,215 B | 达到 30 天归档窗口的 USER.md |

## 整理摘要

- **MEMORY.md**: 3,241 → 1,578 字符（-51%），压缩表格、合并冗余行、移除格式噪音；2026-08-12 达 30 天窗口，内容仍为活跃持久配置，刷新头部日期后保留
- **USER.md**: 1,398 → 1,215 字符（-13%），精简表述；2026-08-12 达 30 天窗口，内容仍为活跃协作协议，刷新头部日期后保留
- **Hindsight 优化**: 触发 `demo-pm-memory` 银行 reflect（include_facts=True）确认 48 facts 无过期/冗余/矛盾；consolidation completed（op dc86574b，deduplicated=false）
- **30+天旧记忆**: ✅ 无（bank 内 48 facts 均为活跃持久配置；本次文件归档为 30 天窗口例行快照）

## 保留策略

- 镜像文件 (`.bak`) 归档后删除，原始内容已浓缩至当前文件
- 下次清理: 2026-09-12 或满 30 天时

---

## 清理日志

| 日期 | 操作 | 结果 |
|------|------|------|
| 2026-07-12 | 初始归档 + Hindsight consolidation/dedup | MEMORY.md -51% (3,241→1,578), USER.md -13% (1,398→1,215) |
| 2026-07-13 ~ 07-27 | 15 天连续例行清理（已合并） | ✅ 期间所有日期均无 30+天文件级记忆需归档，MEMORY.md/USER.md 持续保持 < 30 天新鲜度；Hindsight bank 内 48 fact 虽创建于 06-14~06-17（41~44 天前），但均为持久活跃配置事实（Feishu/LLM/Gateway/Issue规则），非归档对象；Jul 25 后 Hindsight daemon 因 HF 模型下载被拒持续不可用，回退手动检查；session DB 会话自 06-22 起达 35d+ 但仍属历史非归档对象 |
| 2026-07-28 | Hindsight reflect + consolidation + ARCHIVE.md 压缩 | ✅ 无 30+天内存文件需归档（MEMORY.md 16d / USER.md 16d 均新鲜）；Hindsight profile daemon :9178 重新启用（HF_HUB_OFFLINE=1 绕过缓存校验），bank reflect 确认 48 facts 均为活跃配置无需归档；consolidation 全部 completed 无待处理；ARCHIVE.md 压缩 15 天冗余日志（6,192→1,634 字符，-74%）；已记忆 HF_HUB_OFFLINE=1 工作流供后续使用 |
| 2026-07-30 | 手动清理（Hindsight daemon 不可用：HF 下载超时 + tiktoken SSL） | ✅ 无 30+天内存文件需归档（MEMORY.md 18d / USER.md 18d 均新鲜）；归档 3 个 32d 旧 session dump（已移入 archive/sessions/）；Hindsight daemon 无法启动：HF 模型下载超时（中国网络限制）+ tiktoken BPE 缓存缺失 + demo-pm.env 原为模板（API key=***），已修复 env 但 daemon 仍因 HF 连通性无法启动 |
| 2026-07-31 | Hindsight reflect + consolidation + daemon 重启（清理 cron） | ✅ 无 30+天文件需归档（MEMORY.md 18d / USER.md 18d 均新鲜，字符数均低于上限）；Hindsight daemon :9178 成功重启（HF_HUB_OFFLINE=1 + hermes-agent venv binary，自 Jul 25 故障链后首次恢复）；bank reflect 确认 48 facts（44~47d 旧）均为活跃持久配置（Feishu/LLM/Gateway/Issue 规则），无需归档、无冗余/矛盾；consolidation completed（deduplicated=false，银行已最优）；0 pending / 0 failed；483 个 >30d session 按惯例保留（session_search 跨会话检索依赖） |
| 2026-08-01 | Hindsight reflect + consolidation（清理 cron） | ✅ 无 30+天文件需归档（MEMORY.md 19d / USER.md 19d 均新鲜，字符数均低于上限）；Hindsight daemon :9178 成功启动（HF_HUB_OFFLINE=1 + venv binary + `-p demo-pm`，注意：不带 -p 会用默认 profile 起 8888 并退出）；bank reflect 确认 48 facts（45d 旧）均为活跃持久配置（Feishu/LLM/Gateway/Issue 规则），无需归档、无冗余/矛盾；consolidation completed（deduplicated=false）；0 pending / 0 failed；session 保留策略不变 |
| 2026-08-02 | Hindsight reflect + consolidation（清理 cron） | ✅ 无 30+天文件需归档（MEMORY.md 20d / USER.md 20d 均新鲜，字符数均低于上限）；Hindsight daemon :9178 成功启动（HF_HUB_OFFLINE=1 + venv binary + `-p demo-pm`，idle-timeout 86400）；bank reflect（include_facts=True，hindsight_client）确认 48 facts（46-49d 旧）均为活跃持久配置（Feishu/LLM/Gateway/Issue 规则），无需归档、无冗余/矛盾；consolidation completed（deduplicated=false）；bank stats 48 nodes / 0 pending / 0 failed；session 保留策略不变 |
| 2026-08-03 | Hindsight reflect + consolidation（清理 cron） | ✅ 无 30+天文件需归档（MEMORY.md 21d / USER.md 21d 均新鲜，字符数均低于上限）；Hindsight daemon :9178 成功启动（HF_HUB_OFFLINE=1 + venv binary + `-p demo-pm`，idle-timeout 86400）；bank reflect（include_facts=True，hindsight_client）确认 48 facts 均活跃持久配置，无过期/冗余/矛盾，无需归档；consolidation completed（op 2b0782d8，deduplicated=false）；bank stats 48 nodes / 0 pending / 0 failed；session 保留策略不变 |
| 2026-08-05 | Hindsight reflect + consolidation（清理 cron） | ✅ 无 30+天文件需归档（MEMORY.md 23d / USER.md 23d 均新鲜，字符数均低于上限）；Hindsight daemon :9178 成功启动（HF_HUB_OFFLINE=1 + venv binary + `-p demo-pm`，idle-timeout 86400，~10s 后 healthy）；bank reflect（include_facts=True，hindsight_client）确认 48 facts（~50d 旧但均为活跃持久配置 Feishu/LLM/Gateway/Issue 规则）无过期/冗余/矛盾，无需归档；consolidation completed（op f7c2ee14，deduplicated=false）；bank stats 48 nodes / 1228 links / 0 pending / 0 failed；session 保留策略不变 |
| 2026-08-06 | Hindsight reflect + consolidation（清理 cron） | ✅ 无 30+天文件需归档（MEMORY.md 24d / USER.md 24d 均新鲜，字符数均低于上限）；Hindsight daemon :9178 成功启动（HF_HUB_OFFLINE=1 + venv binary + `-p demo-pm`，idle-timeout 86400，~10s 后 healthy）；bank reflect（include_facts=True，hindsight_client）确认 48 facts（~51d 旧但均为活跃持久配置 Feishu/LLM/Gateway/Issue 规则）无过期/冗余/矛盾，无需归档；consolidation completed（op 189247a3，deduplicated=false）；bank stats 48 nodes / 1228 links / 0 pending / 0 failed；session 保留策略不变 |
| 2026-08-07 | Hindsight reflect + consolidation（清理 cron） | ✅ 无 30+天文件需归档（MEMORY.md 25d / USER.md 25d 均新鲜，字符数均低于上限）；Hindsight daemon :9178 成功启动（HF_HUB_OFFLINE=1 + venv binary + `-p demo-pm`，idle-timeout 86400，~10s 后 healthy）；bank reflect（include_facts=True，hindsight_client）确认 48 facts（~52d 旧但均为活跃持久配置 Feishu/LLM/Gateway/Issue 规则）无过期/冗余/矛盾，memory health good，无需归档；consolidation completed（op 13ab10fb，deduplicated=false）；bank stats 48 nodes / 1228 links / 0 pending / 0 failed；session 保留策略不变 |
| 2026-08-08 | Hindsight reflect + consolidation（清理 cron） | ✅ 无 30+天文件需归档（MEMORY.md 26d / USER.md 26d 均新鲜，字符数均低于上限）；Hindsight daemon :9178 成功启动（HF_HUB_OFFLINE=1 + venv binary + `-p demo-pm`，idle-timeout 86400，~15s 后 healthy）；bank reflect（include_facts=True，hindsight_client）确认 48 facts（~53d 旧但均为活跃持久配置 Feishu/LLM/Gateway/Issue 规则）无过期/冗余/矛盾，memory health good，无需归档；consolidation completed（op 081fb5ea，deduplicated=false）；bank stats 48 nodes / 1228 links / 0 pending / 0 failed；session 保留策略不变 |
| 2026-08-09 | Hindsight reflect + consolidation（清理 cron） | ✅ 无 30+天文件需归档（MEMORY.md 27d / USER.md 27d 均新鲜，字符数均低于上限，均未达 30d 阈值，08-11 起将进入归档窗口）；Hindsight daemon :9178 成功启动（HF_HUB_OFFLINE=1 + venv binary + `-p demo-pm`，idle-timeout 86400，~10s 后 healthy）；bank reflect（include_facts=True，hindsight_client）确认 48 facts（~54d 旧但均为活跃持久配置 Feishu/LLM/Gateway/Issue 规则）无过期/冗余/矛盾，无需归档；consolidation completed（op 9279d004，deduplicated=false）；bank stats 48 nodes / 1228 links / 0 pending / 0 failed；session 保留策略不变 |
| 2026-08-11 | Hindsight reflect + consolidation（清理 cron） | ✅ 无 30+天文件需归档（MEMORY.md 29d / USER.md 29d 均新鲜，字符数低于上限：1220/559 chars；默认 profile USER.md 25d 亦新鲜）；Hindsight daemon :9178 成功启动（HF_HUB_OFFLINE=1 + venv binary + launcher 脚本，~5s 后 healthy）；bank reflect（hindsight_client，include_facts=True）确认 48 facts（~55d 旧但均为活跃持久配置 Feishu/LLM/Gateway/Issue 规则）无过期/冗余/矛盾，无需归档；consolidation completed（op c40e231d，deduplicated=false）；bank stats 48 nodes / 1228 links / 0 pending / 0 failed；session 保留策略不变 |
| 2026-08-12 | 30 天归档 + Hindsight reflect + consolidation（清理 cron） | ✅ MEMORY.md / USER.md 达 30 天归档窗口（均为 30d，Jul 12 修改）：已生成快照 MEMORY-20260812.snapshot.md（1,578 B）/ USER-20260812.snapshot.md（1,215 B）入 archive/，内容均为活跃持久配置故刷新头部日期后保留；字符数低于上限（1220/559 chars）；Hindsight daemon :9178 成功启动（launcher 脚本，~5s 后 healthy）；bank reflect（hindsight_client，include_facts=True）确认 48 facts（~56d 旧但均为活跃持久配置 Feishu/LLM/Gateway/Issue 规则）无过期/冗余/矛盾；consolidation completed（op dc86574b，deduplicated=false）；bank stats 48 nodes / 1228 links / 0 pending / 0 failed；session 保留策略不变 |
| 2026-08-14 | Hindsight reflect + consolidation（清理 cron） | ✅ 无 30+天文件需归档（MEMORY.md 1d / USER.md 1d 均新鲜，字符数低于上限：1625/1262 B）；Hindsight daemon :9178 成功启动（launcher 脚本，~5s 后 healthy）；bank reflect（hindsight_client，include_facts=True）确认 48 facts（~58d 旧但均为活跃持久配置 Feishu/LLM/Gateway/Issue 规则）无过期/冗余/矛盾，无需归档；consolidation completed（op e78dddfa，deduplicated=false）；bank stats 48 nodes / 1228 links / 0 pending / 0 failed；session 保留策略不变 |
| 2026-08-15 | Hindsight reflect + consolidation（清理 cron） | ✅ 无 30+天文件需归档（MEMORY.md 2d / USER.md 2d 均新鲜，字符数低于上限：1625/1262 B；默认 profile USER.md 29d 亦未达 30d 阈值）；Hindsight daemon :9178 成功启动（launcher 脚本，~5s 后 healthy；:8888 全局 daemon 不含 demo-pm-memory bank，未采用 sibling fallback）；bank reflect（hindsight_client，include_facts=True）确认 48 facts（~59d 旧但均为活跃持久配置 Feishu/LLM/Gateway/Issue 规则）无过期/冗余/矛盾；consolidation completed（op 69579f28，deduplicated=false）；bank stats 48 nodes / 1228 links / 0 pending / 0 failed；session 保留策略不变 |
| 2026-08-16 | Hindsight reflect + consolidation（清理 cron） | ✅ 无 30+天文件需归档（MEMORY.md 3d / USER.md 3d 均新鲜，字符数低于上限：1625/1262 B；默认 profile USER.md 30d 达阈值但属默认 profile 记忆，非 demo-pm 归档范围，未动）；Hindsight daemon :9178 成功启动（launcher 脚本，~5s 后 healthy）；bank reflect（hindsight_client，include_facts=True）确认 48 facts（~60d 旧但均为活跃持久配置 Feishu/LLM/Gateway/Issue 规则）无过期/冗余/矛盾；consolidation completed（op d46b5b70，deduplicated=false）；bank stats 48 nodes / 1228 links / 0 pending / 0 failed；session 保留策略不变 |
| 2026-08-18 | Hindsight reflect + consolidation（清理 cron） | ✅ 无 30+天文件需归档（MEMORY.md 5d / USER.md 5d 均新鲜，字符数低于上限：1625/1262 B；默认 profile USER.md 32d 达阈值但属默认 profile 记忆，非 demo-pm 归档范围，未动）；Hindsight daemon :9178 成功启动（launcher 脚本，~5s 后 healthy；:8888 全局 daemon 无 demo-pm-memory bank，未采用 sibling fallback）；bank reflect（hindsight_client，include_facts=True）确认 48 facts（~62d 旧但均为活跃持久配置 Feishu/LLM/Gateway/Issue 规则）无过期/冗余/矛盾；consolidation completed（op 0c9bc45e，deduplicated=false）；bank stats 48 nodes / 1228 links / 0 pending / 0 failed；session 保留策略不变 |
| 2026-08-19 | Hindsight reflect + consolidation（清理 cron） | ✅ 无 30+天文件需归档（MEMORY.md 7d / USER.md 7d 均新鲜，字符数低于上限：1625/1262 B；默认 profile USER.md 34d 达阈值但属默认 profile 记忆，非 demo-pm 归档范围，未动）；Hindsight daemon :9178 成功启动（launcher 脚本，~5s 后 healthy；:9177/:8888 均无 demo-pm-memory bank，未采用 sibling fallback）；bank reflect（hindsight_client，include_facts=True）确认 48 facts（~63d 旧但均为活跃持久配置 Feishu/LLM/Gateway/Issue 规则）无过期/冗余/矛盾，无需归档；consolidation completed（op d52c0ec5，deduplicated=false）；bank stats 48 nodes / 1228 links / 0 pending / 0 failed；session 保留策略不变 |
| 2026-08-25 | Hindsight reflect + consolidation（清理 cron） | ✅ 无 30+天文件需归档（MEMORY.md 12d / USER.md 12d 均新鲜，字符数低于上限：1625/1262 B；默认 profile USER.md 40d 达阈值但属默认 profile 记忆，非 demo-pm 归档范围，未动）；Hindsight daemon :9178 成功启动（launcher 脚本，~3s 后 healthy）；bank reflect（hindsight_client，include_facts=True）确认 48 facts（~69d 旧但均为活跃持久配置 Feishu/LLM/Gateway/Issue 规则）无过期/冗余/矛盾，无需归档；consolidation completed（op ebd4cc5e，deduplicated=false）；bank stats 48 nodes / 1228 links / 0 pending / 0 failed；session 保留策略不变 |
