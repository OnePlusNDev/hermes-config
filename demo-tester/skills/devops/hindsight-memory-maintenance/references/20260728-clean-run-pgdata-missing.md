# 记忆维护实况示例 — 2026-07-28（清扫轮）

## 场景

cron 定时任务二次执行。前一次（2026-07-27）已完成主要清理，这次是"清扫轮"——验证无积压，归档跨月的单文件。

## 前置状态

- **MEMORY.md**: 29 行, 1.4KB；`## Archived` 区段已在上次维护替换为注释指针
- **USER.md**: 27 行, 1.5KB；mtime Jul 27（已上次修复）
- **archive/**: 21 松散 MD + 6 tarball, ~116KB

执行前活跃记忆已干净，无待处理条目。

## 维护执行

### 1. Hindsight 检查 → 不可用

```bash
hindsight-embed -p hermes daemon status
# → "Daemon is not running"

hindsight-embed -p hermes daemon start
# → timed out after 30s (exit 124)
```

**关键诊断**（新发现）:

```bash
# 检查 pgdata → 不存在
ls -la ~/.hindsight/pgdata/
# → "No pgdata dir found"

# 对比 daemon.log 确认匹配模式：
tail -5 ~/.hindsight/daemon.log | grep -i "refused\|connection\|migration"
# → "OperationalError: (psycopg2.OperationalError) connection to server at
#      \"127.0.0.1\", port 5434 failed: Connection refused"
# → "RuntimeError: Database migration failed"
```

**结论**: 嵌入 PG 的 pgdata 目录完全不存在 → 不是迁移版本问题，是 PG 从未初始化成功或被清空。需要清除 daemon.lock  → 重新 start 让 hindsight 走首次初始化路径（或重建 profile）。

### 2. 快照（Standard Practice）

```bash
cp MEMORY.md archive/MEMORY-20260728.md
cp USER.md   archive/USER-20260728.md
```

### 3. 30+天文件检查

```bash
find archive/ -maxdepth 1 -name "*.md" -mtime +28 -ls
# → 仅 1 个文件: USER-20260722.md (mtime Jun 17, >40 天前)
```

### 4. 压缩陈旧文件

```bash
tar czf old-loosely-pre-july-20260728.tar.gz USER-20260722.md
rm USER-20260722.md
# rm 成功（Tirith 未拦截）；新 tarball: 1.3KB
```

注意: `USER-20260722.md` 的 filename 日期是 Jul 22 但 mtime 是 Jun 17。归档时以 mtime 为准（文件的实际存在时间）。

### 5. 活跃记忆内容检查

```bash
# MEMORY.md：已干净，## Archived 区段只有注释
# USER.md：当前规则仍然有效，无过期条目
```
→ 无需清理。

### 6. mtime 检查

- MEMORY.md: Jul 27（24h 内）
- USER.md: Jul 27（24h 内）
→ 无需 touch。

## 结果

| 指标 | 之前 | 之后 | Δ |
|------|------|------|----|
| 松散 MD | 21 | 20 | -1 |
| tarball | 6 | 7 | +1 |
| 磁盘 | ~116K | ~117K | +1K（补偿快照+新 tarball）|

## 关键决策点

- **pgdata/ 缺失** 是一个比 "migration failed" 更根本的故障：不是升级或修复就能解决的，需要重建整个 PG 环境。如果在 cron 环境中反复看到这个模式，应考虑重建 hindsight profile。
- **清扫轮无收获是正常的**：前一次维护做得多，后续轮次就无事可做。这证明维护策略有效。区分"初扫轮"（7 月 27 日）和"清扫轮"（7 月 28 日）两种模式。
- **Tirith 不总是拦截 rm**：本次 rm 成功执行，没有出现上轮提到的 "Tirith 质量文件删除保护"。安全系统可能只在特定文件类型或路径模式触发。
