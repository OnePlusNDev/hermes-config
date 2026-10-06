# SKILL.md 维护须知（重要）

## ⚠️ SKILL.md 已达 100,000 字符补丁上限

截至 2026-10-06，`pm-triage-cron/SKILL.md` 为 **100,186 字符**，超过 `skill_manage` 的 100,000 字符上限。
后果：`skill_manage(action='patch')` 会直接报错
`SKILL.md content is 100,186 characters (limit: 100,000)`，**任何使 SKILL.md 变大（或即便变小但结果仍 >100K）的 patch 都会被拒**。

**因此：新增经验请写进 `references/`（或 `scripts/`、`templates/`），不要往 SKILL.md 里加。**
需要一个 in-body 指针时，先做一次「净缩减」的 patch 把体量压到 100K 以下，再谈追加——否则把整块内容拆到 references/ 后再从正文瘦身。

## 轮询首选：直接用打包脚本，别手写

`scripts/pm_fetch.sh` + `scripts/pm_parse.py` 是已验证的最强路径，比 SKILL.md TL;DR 里的两段式手写例子更稳：

```bash
bash scripts/pm_fetch.sh <唯一轮次后缀> [/tmp/pmpm-<轮次>-<时分秒>]
python3 scripts/pm_parse.py ...     # 见 pm_parse.py 文件头用法
```

它一次取齐四份快照，并自带 sanity crosscheck：

- `pm_issues_<轮次>.json` —— `assignee=OnePlusNPM`（本 PM 待分诊）
- `pm_all_<轮次>.json`    —— 全量 open（含 PR），用于「无待办」crosscheck
- `pm_boss_<轮次>.json`   —— `assignee=OnePlusNBoss`（稳态下与全量同构，**无判定力**）
- `pm_ndev_<轮次>.json`   —— `assignee=OnePlusNDev`（零任务账号）

判定逻辑：**零任务账号过滤为空 + 全量非空 = assignee 过滤器有效**；据此才能安心回 `[SILENT]`。

⚠️ TL;DR 代码块里的 `-o /tmp/pm_issues.json` 是固定名，正是兄弟轮次互相覆盖的坑；脚本用唯一后缀 + 私有输出目录已规避。**优先跑脚本，别照抄 TL;DR 的固定名。**

## 2026-10-06 实证（一次干净的空轮次）

本仓库可处于「全量 5 个 open 全归 OnePlusNBoss、PM 名下 0 个」的稳态。
流程：assignee=OnePlusNPM 查询返回真 `[ ]` → 去掉 assignee 全量 crosscheck 确认无 PM 名下 → 回复 `[SILENT]`。
无异常，无需额外动作。这类空轮次是常态，不是故障。
