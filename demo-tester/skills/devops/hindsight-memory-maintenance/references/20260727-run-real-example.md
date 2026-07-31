# 记忆维护实况示例 — 2026-07-27

## 场景

cron 定时任务执行记忆维护，hindsight daemon 不可用（PG 迁移失败），退化为纯文件级维护。

## 前置状态

- MEMORY.md: 29 行, 1.5KB（含一个 `## Archived` 区段，内有 2026-06-14/16 两条条目）
- USER.md: 27 行, 1.5KB（内容当前有效，但 mtime 停留在 Jun 17 — 40 天前）
- archive/ 目录: 31 松散 MD + 5 tarball, ~140KB

## 执行过程

### 1. 检查 hindsight → 不可用

```bash
hindsight-embed -p hermes daemon status
# → "Daemon is not running"

hindsight-embed -p hermes daemon start
# → timed out after 30s (exit 124)

tail -40 ~/.hindsight/daemon.log
# → "RuntimeError: Database migration failed"
```

### 2. 快照活跃记忆

```bash
cp MEMORY.md archive/MEMORY-20260727.md
cp USER.md   archive/USER-20260727.md
```

### 3. 识别过期内容

```bash
# archive 文件按 mtime 检查: USER-20260722.md 的 mtime 异常（Jun 17），其余均为 7 天内
# 活跃 MEMORY.md 的 ## Archived 区段:
#   - ⚠️ tester secret 10014 invalid（2026-06-16）→ 41 天
#   - 2026-06-14 对话主模型切换记录 → 43 天
```

### 4. 清理 MEMORY.md —— 移出 Archived 条目

将 June 条目写入冷存储档案 `archive/archived-from-active-20260727.md`，再将活跃 MEMORY.md 的 Archived 区段替换为注释：

```markdown
## Archived
<!-- 30天前的旧内容已于 2026-07-27 移入 archive/archived-from-active-20260727.md -->
```

### 5. 修复 USER.md mtime

```bash
touch USER.md  # mtime 从 Jun 17 → Jul 27
```

### 6. 打包陈旧归档文件（July 14-20 的松散文件）

```bash
tar czf hindsight-reports-old-20260727.tar.gz \
  12 个 hindsight/memory-maintenance 报告 .md
rm 已打包的源文件
```

## 结果

| 指标 | 之前 | 之后 | Δ |
|------|------|------|----|
| 松散 MD | 31 | 19 | -12 |
| tarball | 5 | 6 | +1 |
| 磁盘 | ~140K | 116K | -17% |

## 关键决策点

- **hindsight 不可用时**：跳过 LLM reflect/consolidate，继续执行文件级操作，报告中标注"LLM 离线，reflect 跳过"
- **USER.md mtime 修复**：虽然不是严格必要的，但防止后续维护按 mtime 误判该文件为过期
- **已位于 Archived 的条目**：仍需移出到冷存储——`## Archived` 不是冷存储，应只留注释
