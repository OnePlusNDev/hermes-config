---
name: demo-pm-triage
description: "PM triage workflow: query GitHub issues, classify, reassign via gh CLI"
---

# demo-pm-triage: PM 定时分诊 cron 任务

## 触发条件

demo-pm profile cron job 轮询时触发。

## 工作流程

### 第一步：检查 gh CLI 认证

```bash
gh auth status
```

### 第二步：查询待分诊 issue

```bash
gh issue list --repo demo-oneplusn/demo-workflow --assignee OnePlusNPM --state open --json number,title,labels,body,assignees,id
```

### 第三步：按类型分诊

| 标签 | 派给 |
|---|---|
| type:feature / type:bug | OnePlusNDev |
| type:verification | OnePlusNTester |
| type:research / type:docs / 其他不明 | OnePlusNBoss |

### 第四步：加 comment + 两步法 reassign

1. 写中文 comment
2. 先 remove 旧人再 add 新人

### 第五步：无任务则静默

输出 [SILENT]
