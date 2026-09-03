# 2026-09-03 cron 会话：full_triage.py → list 端点交叉验证 → [SILENT] 闭环确认

## 结果
- `python3 scripts/full_triage.py`（search API）→ `No issues to triage. Silent exit.` / `SILENT`
- 随后用 list 端点交叉验证（同一命令内完成）：`issues?state=open&assignee=OnePlusNPM` → 0 个；全量健康检查 5 个 open issue #2/#4/#5/#6/#7 全部 assign 给 `OnePlusNBoss`，无游离 issue → 确认真无任务 → `[SILENT]`。
- 与 2026-08-31 参考（`2026-08-31-session-user-401-transient-crosscheck.md`）闭环：**search API 可能索引延迟，full_triage.py 报 SILENT 后不要直接结束**，先用权威 list 端点交叉验证一次再定论，避免假阴性漏掉刚 assign 给自己的 issue。

## 交叉验证单命令模板（读 .env 用 open()，token 动态拼接，无 Authorization 字面量）
```python
python3 -c "
import json, os, urllib.request
env={}
with open(os.path.expanduser('~/.hermes/profiles/demo-pm/.env')) as f:
    for line in f:
        line=line.strip()
        if line.startswith('GITHUB_TOKEN='): env['TOKEN']=line.split('=',1)[1].strip()
def gh(url):
    req=urllib.request.Request(url)
    req.add_header('Authorization','token '+env['TOKEN'])
    req.add_header('Accept','application/vnd.github.v3+json')
    req.add_header('User-Agent','PM-Triage-Cron/1.1')
    with urllib.request.urlopen(req, timeout=30) as r: return json.loads(r.read())
# 1) assignee 过滤（权威端点，无索引延迟）
mine=gh('https://api.github.com/repos/demo-oneplusn/demo-workflow/issues?state=open&assignee=OnePlusNPM&per_page=50')
# 2) 全量健康检查（所有 open issue 及其 assignee，确认无游离 issue）
all_issues=gh('https://api.github.com/repos/demo-oneplusn/demo-workflow/issues?state=open&per_page=50')
"
```

## 新数据点：多行内联 python3 -c 并非必然被打散
- 本轮一段**多行** inline `python3 -c "..."`（双引号包裹、内含多行与单引号字符串、无 `$()`、无 Authorization 字面量、token 用变量动态拼接）**成功执行**，与 2026-08-03 记录的「多行内联必被打散」不完全一致。
- 收敛结论：仍以写脚本文件为首选；但简单、无嵌套 `$()`/引号、无敏感字面量的多行 `-c` 可先行尝试，失败再落盘脚本文件，不必默认必坏。

## 其他备忘
- `~/.hermes/profiles/demo-pm/RULES.md` 当前为**空文件**（0 行）——步骤 (1) 读取后无铁律可执行，属正常；不要因空而跳过读取，内容可能随时被写入。
- `cron/jobs.json` 结构：`{'jobs': [...], 'updated_at': ...}`，jobs 为 list。分诊 job = `demo-pm-task-polling`（id `1a8d81813395`，schedule `0,30 * * * *`），历史输出在 `cron/output/1a8d81813395/`；勿与 `020650fcf9e2`（memory-cleanup）、`db397164dfb6`（config-backup）输出目录混淆。
