# ARCHIVE.md — demo-pm 记忆归档

> 记忆清理时间: 2026-07-28
> 清理工具: Hindsight v0.8.2（profile daemon :9178，已通过 HF_HUB_OFFLINE=1 绕过缓存校验）

---

## 归档记录

| 文件 | 原始日期 | 大小 | 说明 |
|------|---------|------|------|
| `MEMORY-20260710.snapshot.md` | 2026-07-10 | 2,826 B | 旧版 MEMORY.md.bak |
| `USER-20260710.snapshot.md` | 2026-07-10 | 1,335 B | 旧版 USER.md.bak |

## 整理摘要

- **MEMORY.md**: 3,241 → 1,578 字符（-51%），压缩表格、合并冗余行、移除格式噪音
- **USER.md**: 1,398 → 1,215 字符（-13%），精简表述
- **Hindsight 优化**: 触发 `hermes` 银行 consolidation（dedup）和 reflection（LLM 搜索+摘要）
- **30+天旧记忆**: ✅ 无（最早条目 2026-06-14）

## 保留策略

- 镜像文件 (`.bak`) 归档后删除，原始内容已浓缩至当前文件
- 下次清理: 2026-08-12 或满 30 天时

---

## 清理日志

| 日期 | 操作 | 结果 |
|------|------|------|
| 2026-07-12 | 初始归档 + Hindsight consolidation/dedup | MEMORY.md -51% (3,241→1,578), USER.md -13% (1,398→1,215) |
| 2026-07-13 ~ 07-27 | 15 天连续例行清理（已合并） | ✅ 期间所有日期均无 30+天文件级记忆需归档，MEMORY.md/USER.md 持续保持 < 30 天新鲜度；Hindsight bank 内 48 fact 虽创建于 06-14~06-17（41~44 天前），但均为持久活跃配置事实（Feishu/LLM/Gateway/Issue规则），非归档对象；Jul 25 后 Hindsight daemon 因 HF 模型下载被拒持续不可用，回退手动检查；session DB 会话自 06-22 起达 35d+ 但仍属历史非归档对象 |
| 2026-07-28 | Hindsight reflect + consolidation + ARCHIVE.md 压缩 | ✅ 无 30+天内存文件需归档（MEMORY.md 16d / USER.md 16d 均新鲜）；Hindsight profile daemon :9178 重新启用（HF_HUB_OFFLINE=1 绕过缓存校验），bank reflect 确认 48 facts 均为活跃配置无需归档；consolidation 全部 completed 无待处理；ARCHIVE.md 压缩 15 天冗余日志（6,192→1,634 字符，-74%）；已记忆 HF_HUB_OFFLINE=1 工作流供后续使用 |
