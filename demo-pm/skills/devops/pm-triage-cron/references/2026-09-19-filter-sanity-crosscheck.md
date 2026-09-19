# 2026-09-19 空结果「过滤器完整性」crosscheck

## 场景

轮询 `assignee=OnePlusNPM&state=open` 返回 5 字节 `[\n\n]`（真空白数组）。按既有两步法：
1. `head -c 400` 确认是真 `[ ]`（非截断的空响应体）✅
2. 去掉 `assignee` 做全量 open crosscheck ✅ —— 33096 字节，5 条（4 issue + 1 PR）。

全量结果里 4 条 open issue **全部** assign 给 `OnePlusNBoss`，**没有一条**在 PM 名下，也**没有无 assignee 的游离 issue**。

## 新增的第三步：用「已知他人」反向证明过滤器没坏

只做无 `assignee` 全量 crosscheck 有个盲区：万一 API 的 assignee 过滤参数被静默忽略/失效，
空结果和「真无待办」长得一模一样，无法区分。

**低成本鉴别法：拿一个已知确有任务的账号再查一次，看过滤是否真的生效。**

```bash
# assignee=OnePlusNBoss → 33096 字节（=全量同尺寸），count 与全量一致
curl -sS -u "OnePlusNPM:$TOK" -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/demo-oneplusn/demo-workflow/issues?state=open&assignee=OnePlusNBoss&per_page=100" \
  -o /tmp/pm_boss_sanity.json -w "HTTP=%{http_code}\n"
# assignee=OnePlusNPM → 5 字节 [ ]

# 判定：
#   他人过滤返回非空、且 PM 过滤返回空  → 过滤器工作正常 → 空结果是真 → [SILENT]
#   他人过滤也返回空（而全量明明有该人的任务）→ 过滤器坏了 → 不可信 → 改用全量结果自行筛 assignees
```

判据总结：**他人过滤非空 + PM 过滤为空 = 过滤器可信，空结果真实**。这是比单纯
「去掉 assignee 全量 crosscheck」更强的证据——后者只能证明「PM 名下无任务」，
前者额外证明了「过滤机制本身没坏」。两条都跑一遍成本极低（各一次 curl），建议都做。

## 本轮结论

过滤可信 → PM 名下确实 0 条 → 无待分诊任务 → 返回 `[SILENT]`。

## 顺带踩到（已被禁用清单覆盖，再次确认）

写 sanity 脚本时一度写成 `curl ... | python3 -c "..."` 内联管道 —— 这正是
`pm-triage-cron` TL;DR 禁用清单里的 `curl | python3（tirith 拦截）`。**当场改写为
`curl -o 文件` + 单独 `python3 解析.py`** 即通过。教训：sanity/解析脚本一律 file-based，
不要图省事内联管道给解释器。

## 本轮脚本命名（防兄弟轮覆盖）

`/tmp/pm_fetch_0919_1800.sh`、`/tmp/pm_cross_0919_1800.sh`、`/tmp/pm_sanity_0919_1800.sh`、
`/tmp/pm_parse_0919_1800.py` —— 轮次+时分后缀，互不覆盖，`token_len=40` / `HTTP=200` 一次通过。
收尾不 `rm`（避免 `mass_file_deletion` 审批拦截）。
