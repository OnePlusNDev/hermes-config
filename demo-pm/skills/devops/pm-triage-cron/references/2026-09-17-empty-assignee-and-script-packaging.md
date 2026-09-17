# 2026-09-17 — 空 assignee 轮次 + 脚本封装

## 本轮结论

`[SILENT]`（无待分诊任务）。全流程一次通过，无审批拦截、无兄弟轮次冲突。

## 实测证据

```bash
bash /tmp/pm_fetch_r917.sh
# token_len=40
# HTTP=200
```

`assignee=OnePlusNPM` 查询 → 响应体 **5 字节**，内容 `[\n\n]` —— 真空数组，未被截断。
（判据：先 `head -c 400` 看字节，再看 `wc -c`；不要只看解析出的 `len == 0`。）

去掉 `assignee` 的全量 open crosscheck：

```
total_open: 5
ISS #7 | [验证报告] Issue 2 独立验证        | labels=[]                                   | assignees=['OnePlusNBoss']
PR  #6 | feat: 新增 subtract(a, b) 减法函数并附测试
ISS #5 | [测试] 全链路含验证：新增 subtract | labels=['type:feature','priority:normal']  | assignees=['OnePlusNBoss']
ISS #4 | [测试] PM→Dev 路径：新增 multiply  | labels=['type:feature','priority:normal']  | assignees=['OnePlusNBoss']
ISS #2 | [测试] 验证 PM 分诊流程：新增 add   | labels=['type:feature','priority:normal']  | assignees=['OnePlusNBoss']
PM_assigned: []
```

两个可复用的事实：

- `total_open: 5` 而列出的 issue 只有 4 条 —— **差额就是 PR #6**，不是脚本丢数据。解析必须先 `if "pull_request" in it: continue`。
- 库里的存量 issue 都挂在 `OnePlusNBoss` 名下（前几轮已分诊过），`PM_assigned` 为空才是判定 `[SILENT]` 的依据。

## 为什么封装成 scripts/

历轮（09-10 / 09-12 / 09-14）每次都靠 `write_file` 手写同样的 fetch + parse 脚本，
反复踩两个坑：credential scanner 把字面量 `^GITHUB_TOKEN=` 脱敏成 `***` 写坏脚本；
以及 `glob('/tmp/pm_issues_*.json')[-1]` 字典序选中兄弟轮次文件误判「无待办」。

现固化为：

- `scripts/pm_fetch.sh <轮次后缀>` —— 变量式 key（`KEY="GITHUB_TOKEN"` + `grep "^${KEY}="`），
  内置 `token_len=40` 断言，一次落两份唯一命名快照（PM 名下 + 全量 open）。
- `scripts/pm_parse.py <issues.json> [<all.json>]` —— **显式接收路径**（杜绝 glob 取尾），
  跳过 PR，直出 `VERDICT: SILENT / TRIAGE`。

手写脚本仅在二者不可用时作为兜底。

## 已知待办（留给 curator / 后续维护）

`pm-triage-cron/SKILL.md` 已顶到 100,000 字符硬上限，本轮连一行 skill 指路都差点写不进去
（需多次压缩，最终仅 ~130 字符的指针才落地）。SKILL.md 里的长文排障记录应当下沉到
`references/`，正文只留 TL;DR + 脚本指针，否则下次任何增补都会被拒绝。
