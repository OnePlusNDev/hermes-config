# 2026-09-13 分诊基线：无待办静默（兄弟轮次 /tmp 脚本撞名）

## 场景
PM 定时分诊轮询（profile `demo-pm` / GitHub `OnePlusNPM`）。`RULES.md` 仍为空（0 字节），
规则全部来自 cron prompt。

## 结果：无需派工 → 回 `[SILENT]`
- `token_len=40` ✅，`HTTP=200`
- `state=open&assignee=OnePlusNPM` → `[\n\n]\n`（5 字节，真·空数组）
- 全量 open crosscheck → 5 条，assignee **全部**为 `OnePlusNBoss`：
  #2 / #4 / #5（`type:feature` + `priority:normal`）、#6（PR，`type:feature`）、#7（验证报告，无标签）
- 结论：PM 名下无任务 → 静默退出，不派工、不发通知

## 本轮新细节
1. **空数组判别用 `od -c` 比只看字节数更硬**：
   `head -c 200 <file> | od -c` 输出 `[  \n  \n   ]  \n`（BYTES=5）即确认真空数组，
   排除「有内容但被截断/报错 JSON」的可能。TL;DR 里提的 `head -c 400` 复核可用此法落实。
2. **write_file 写 /tmp 通用文件名会与兄弟 cron 轮次撞车**：本轮写 `/tmp/pm_parse_all.py`
   时工具返回 `_warning: ... was modified by sibling subagent ... but this agent never read it`。
   → 解析脚本的文件名同样必须带日期/唯一后缀（改名为 `/tmp/pm_parse_0913_pm.py` 后告警消失）。
   即：**凡落 `/tmp` 的产物（fetch 脚本、JSON、解析脚本）一律唯一命名**，不止 JSON 一处。
3. 取 token 沿用变量键名写法，一次通过：
   `KEY="GITHUB_TOKEN"; TOK=$(grep "^${KEY}=" .env | cut -d= -f2- | tr -d '"' | tr -d "'")`

## 要点速记
- 并发/兄弟 cron 轮次是常态：三类 `/tmp` 产物都要唯一命名，避免静默读到别人的结果。
- 一切正常时回答**严格只输出 `[SILENT]`**，不带任何附加内容。

## 2026-09-13 第二轮复跑（同日再确认，零摩擦）
- TL;DR 路径首次即通：`/tmp/pm_fetch_0913c.sh`（`KEY="GITHUB_TOKEN"` 变量键名 + `cut` 提 token）一次抓 mine+all，
  `token_len=40` / `HTTP_MINE=200` / `HTTP_ALL=200`；mine=5 字节、all=33096 字节。
- 全量 open = 5 条，**全部 **`OnePlusNBoss`： #2/#4/#5（`type:feature`+`priority:normal`）、#6（PR，`type:feature`）、#7（验证报告，无标签）。
  PM 名下 0 条 → `[SILENT]`。
- 复现「解析脚本撞名」：`/tmp/pm_parse_all.py` 又被兄弟轮次覆盖告警，改唯一名 `/tmp/pm_parse_pm_0913_final_z9.py` 后消失。
- `RULES.md` 仍为 0 字节空文件。
- 备注：SKILL.md 已达 100,000 字符上限，新基线只能写入 references/（本次如此处理）。

## 2026-09-13 第三轮复跑（零摩擦，路径已稳定）
- 脚本 `/tmp/pm_fetch_0913_d1.sh`：`KEY="GITHUB_TOKEN"` 变量键名 + `cut` 提 token，
  一次抓 mine+all → `token_len=40` / `HTTP_MINE=200` / `HTTP_ALL=200`；
  mine=5 字节（`od -c` 确认 `[ \n \n ] \n`），all=33096 字节。
- 全量 open = 5 条，assignee 全部 `OnePlusNBoss`：#2/#4/#5（`type:feature`+`priority:normal`）、
  #6（PR，`type:feature`）、#7（验证报告，无标签）。PM 名下 0 条 → `[SILENT]`。
- 唯一命名用 shell `$$`（PID）最省事：`/tmp/pmx_{mine,all}_$$.json`、解析脚本 `/tmp/pm_parse_pm_0913_d1.py`，无撞名告警。
- `RULES.md` 仍为 0 字节空文件。
