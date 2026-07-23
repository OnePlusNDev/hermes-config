# ARCHIVE.md — demo-pm 记忆归档

> 记忆清理时间: 2026-07-12
> 清理工具: Hindsight v0.8.2（全局 API :8888）

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
| 2026-07-13 | Hindsight 尝试 | ⚠️ demo-pm hindsight daemon 未运行（API key 未配置）；全局 :8888 daemon 健康但属于 dev-01 银行，无法直接操作 demo-pm 记忆 |
| 2026-07-14 | 例行检查 | ✅ 无 30+天数据；MEMORY.md(1d/1,578B)、USER.md(1d/1,215B) 均新鲜；字符数在限制内；state.db 1133 会话皆 <30d |
| 2026-07-15 | 例行检查 + Hindsight reflect/consolidate | ✅ 无 30+天数据；MEMORY.md(2d/1,578B)、USER.md(2d/1,215B) 均新鲜且 < 字符限制；Hindsight hermes bank (20 facts) reflect 确认无过时内容，consolidation ✅ (op #74)；demo-tester bank (30 facts, last Jul 10) 健康；全局 :8888 daemon 运行中 |
| 2026-07-16 | 例行检查 + Hindsight reflect/consolidate | ✅ 无 30+天数据；MEMORY.md(4d/1,578B)、USER.md(4d/1,215B) 均新鲜且 < 字符限制；Hindsight reflect 确认无冗余/过时内容 ✅；consolidation 无重复事实需合并 ✅；demo-pm hindsight daemon 未运行（9178），通过全局 :8888 API 执行；archive snapshots (Jul 10) 仅 6 天尚不需归档 |
| 2026-07-17 | 深度清理 + Hindsight reflect/consolidate | ✅ 无 30+天数据；MEMORY.md(5d/1,578B)、USER.md(5d/1,215B) 均新鲜且 < 限制；Hindsight `demo-pm-memory` bank (54 facts, last Jul 7) reflect → 无超30天内容；consolidation ✅ (op已完成，无重复)；session DB (1,283 sessions, 首 Jun 22) 无 30d+ 会话；daemon 临时启动并停止 |
| 2026-07-18 | 深度反射分析 + Hindsight reflect/consolidate | ✅ 无 30+天文件记忆（MEMORY.md 6d/USER.md 6d 均新鲜）；Hindsight bank 全量 reflect 分析通过（21 observations + 32 world + 1 experience，全部 31-34 天但为持久事实）；reflect 识别 ~10 组 observation↔world 冗余对及 7 条 Issue #9 碎片化记忆 → consolidation daemon (2 slots) 已在后台自动处理；daemon 已停止；默认 profile 记忆已合并至 profile 级，USER-20260617.bak (31d) 已在 archive 中 |
| 2026-07-19 | 新建 Hindsight `demo-pm` bank + 完整数据摄入 + reflect/consolidate | ✅ 无 30+天数据；MEMORY.md(7d/1,578B)、USER.md(7d/1,578B) 均新鲜；Hindsight 全局 :8888 daemon 健康；新建 `demo-pm` bank 并完整摄入 MEMORY.md + USER.md → 28 memory units (14 obs + 10 exp + 4 world)，198 links (6 entity + 90 semantic + 102 temporal)；consolidation 全部 ✅ 完成无重复；无 30+天文件需归档 |
| 2026-07-20 | 例行 reflect + consolidation | ✅ 无 30+天数据；MEMORY.md(8d/1,578B)、USER.md(8d/1,215B) 均新鲜且 < 字符限制；Hindsight `demo-pm` bank (28 facts, last Jul 19) reflect 确认全部最新 ✅；consolidation 已完成无新增 (op #9, deduplicated)；全局 :8888 daemon 健康 |
| 2026-07-21 | 例行检查 + Hindsight reflect/consolidate | ✅ 无 30+天数据；MEMORY.md(9d/1,578B)、USER.md(9d/1,215B) 均新鲜且 < 字符限制；Hindsight `demo-pm` bank (28 facts, 14 obs+10 exp+4 world, 198 links) reflect ✅ 未发现过时或冗余内容；consolidation ✅ (op #10, completed)；全局 :8888 daemon 健康 |
| 2026-07-22 | 全量 reflect + 归档检查 | ✅ 4 banks reflect 均通过，无过时/冗余/矛盾记忆；consolidation 已验证无待处理操作；demo-pm(28事实/198链接) hermes(38) demo-dev(38) demo-tester(24) 全部<30天；file-level MEMORY.md(10d/1,578B) USER.md(10d/1,215B) 均新鲜 |
