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
