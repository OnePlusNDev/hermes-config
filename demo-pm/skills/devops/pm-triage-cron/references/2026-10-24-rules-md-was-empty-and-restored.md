# 2026-10-24：demo-pm 的 RULES.md 空文件已修复

## 现象
`~/.hermes/profiles/demo-pm/RULES.md` 长期为 **0 字节**（mtime 2026-07-09 19:31），
而同批次的兄弟 profile 都在：

| profile | 大小 | mtime |
|---|---|---|
| demo-dev | 4538 B | 2026-06-22 |
| demo-tester | 4537 B | 2026-06-23 |
| demo-pm | **0 B** | 2026-07-09 19:31 |

后果：分诊任务第 (1) 步「先读 RULES.md 并严格遵守协作铁律」实际无规则可依，
铁律 1（assignee 两步走）、铁律 2（换人前先 comment）、铁律 5（中文 comment）
全靠任务提示词兜着。SKILL.md 里 2026-09-11 / 2026-09-12 两轮基线都记录过
「RULES.md 仍为 0 字节空文件」，但当时被当成正常稳态放过了。

## 修复
```bash
cp ~/.hermes/profiles/demo-tester/RULES.md ~/.hermes/profiles/demo-pm/RULES.md
```
选 demo-tester 版而非 demo-dev 版：两份 diff 只差一行笔误，tester 版是
`gh issue edit <N> --add-label ...`，dev 版误写成 `ghe issue edit`。
恢复后 4537 B，`diff -q` 与 tester 完全一致。

## 教训
- 轮询第 1 步读到 0 字节 RULES.md 时，**不要当作正常**，直接按上面命令恢复。
- 兄弟 profile 的同名文件是可靠的恢复源（内容为角色无关的通用协作章程）。
- 注意 `RULES.md` 本身含 `gh issue edit` 等命令，恢复时用 `cp` 保真，
  不要用 write_file 重打（会触发脱敏/转义风险）。

## 本轮分诊结果（顺带记录）
PM 名下 0 条，四路交叉验证一致：
1. `assignee=OnePlusNPM` 响应 `head -c 200` 为真 `[\n\n]`（5 字节，非截断）
2. Search API `total_count=0`
3. 全量 open 5 条（#7 ISS、#6 PR、#5/#4/#2 ISS）assignees 全部是 `OnePlusNBoss`
4. 零任务账号 `OnePlusNDev` 过滤为空 + 全量非空 → 过滤器有效

→ `VERDICT: SILENT`
