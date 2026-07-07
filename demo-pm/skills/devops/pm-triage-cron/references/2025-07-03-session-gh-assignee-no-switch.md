# 2025-07-03：`gh issue list --assignee` 无需账号切换也可工作

## 背景

cron 分诊任务轮询 `demo-oneplusn/demo-workflow` 仓库时，发现 `gh auth status --active` 显示的活跃账号是 `OnePlusNDev`（非 PM 账号 OnePlusNPM）。按照 skill 的旧指引，认为必须先 `gh auth switch` 再查询。

## 实际发现

直接使用活跃账号 `OnePlusNDev` 执行：

```bash
gh issue list --repo demo-oneplusn/demo-workflow --assignee OnePlusNPM --state open --json number,title,state,labels,assignees,body
```

成功返回正确结果（空数组 `[]`，因为确实无 issue 指派给 PM）。

## 原因分析

GitHub Issues API 的 `assignee` 过滤器作用于**被查询的仓库中的 issue**，而非查询者本身。只要当前活跃账号的 OAuth token 拥有该仓库的 `repo` scope（读取仓库权限），就可以正确指定**任何用户**作为过滤器值。

`gh issue list --assignee <USER>` 底层调用的是 `GET /repos/{owner}/{repo}/issues?assignee=<USER>`，这是一个仓库级别的 API，不依赖「以谁的身份」查看——它只是告诉 API「帮我过滤出 assignee 为 X 的 issue」。

## 旧认知修正

旧认知说「未切换时 `gh issue list --assignee OnePlusNPM` 返回 `[]`，不代表仓库无 issue，只代表当前活跃账号视角下没有」——这个说法不准确。正确的理解是：

- `--assignee` 过滤器返回的结果取决于 **token 的 scope**，而非活跃账号的身份
- 如果活跃账号（如 OnePlusNDev）持有 `repo` scope 的 token，它能正确查询到 OnePlusNPM 的 assignee
- 假阴性只会在 token 权限不足（无 `repo` scope）时出现

## 真实假阴性场景

真正的`gh issue list --assignee` 返回 `[]` 但实际有 issue 的情况：

1. Token 缺少必要的 scope（如只给了 `public_repo` 但仓库是 private）
2. 仓库在另一个 org 下，当前 token 无该 org 的权限
3. API rate limit 导致结果为空（HTTP 403）
4. 网络断连导致的空响应

## 鉴别流程

参见 SKILL.md 中的「鉴别真无任务 vs 假阴性」一节。
