# core 配额耗尽（HTTP 403）与 GraphQL 兜底

**首次观测：2026-11-25 轮询（demo-pm cron）。**

## 症状签名

```
token_len=40                       # token 本身没问题，别去查 .env
  assignee try1 HTTP=403 bytes=535
  all      try1 HTTP=403 bytes=534
  boss / ndev 同样 403 bytes≈535
HTTP(search)=200                   # ★ Search API 独立配额，仍可用
```

`head -c 400` 看响应体：

```json
{"message": "API rate limit exceeded for user ID 295761959. ... request ID 0C97:... timestamp 2026-11-24 20:30:20 UTC"}
```

然后 `pm_parse.py` 抛：

```
PM_query_len: 3
AttributeError: 'str' object has no attribute 'get'
```

**关键误判点**：`PM_query_len: 3` 是错误对象 dict 的**键数**（`message` / `documentation_url` / `status`），
不是「3 条待分诊 issue」。看到这个数字就以为有待办 = 对着限流空转一整轮。
（`pm_parse.py` 已加 `isinstance(list)` 守卫，现在会直接打 FATAL 并提示本条。）

## 三步处置

1. **量配额**（`/rate_limit` 不消耗 core）：

   ```bash
   curl -sS --http1.1 --max-time 20 -u "OnePlusNPM:$TOK" https://api.github.com/rate_limit
   # core limit=5000 remaining=0 reset=1795552421 (epoch)
   ```

   `search` 与 `graphql` 是**按资源独立**计的：本轮 core=0，而 search=29/30、graphql=5000/5000。
   用 `time.gmtime(reset)` 算出还要等多久（本轮只差 3 分钟；窗口是滚动的，最长约 1 小时）。
   **不要对 403 反复重试**——不消耗也不推进，只是浪费轮次。

2. **等待期走 GraphQL**（`scripts/pm_gql_fallback.py`，独立 5000/h）：

   ```bash
   python3 ~/.hermes/profiles/demo-pm/skills/devops/pm-triage-cron/scripts/pm_gql_fallback.py OnePlusNPM demo-oneplusn/demo-workflow
   ```

   `issues(states:OPEN, first:50){totalCount nodes{number title labels assignees comments(last:1)}}`
   一条查询 = 「全量 open + 逐条 assignees + 最后一条 comment 作者」，
   比 REST 的 `assignee=` 过滤器更可信（该参数在本环境曾整体静默失效），
   也一次满足铁律 3 的「最后 comment 作者」检查。

3. **reset 后用 REST 复核**：`pm_fetch.sh` + `pm_parse.py <ndev>` 跑完三步判定。
   **GraphQL 与 REST 两路结论一致才回 `[SILENT]`**；只有一路时为 `SUSPECT`，不要静默。

## 本轮实证结论

- 20:30 UTC：REST 全 403；GraphQL `total_open=4`，逐条 assignees 全为 `OnePlusNBoss`，`MINE_COUNT: 0`。
- 20:31：Search API `total_count=0, incomplete=False`（与 GraphQL 一致）。
- 20:34（reset 后）：`assignee` 路返回 **5 字节真 `[ ]`**、`all`=33176 B / 5 item(4 issue+1 PR)、
  `OnePlusNDev` 过滤为空 → `VERDICT: SILENT`。三轮结论一致。

## 待办时怎么办

写 comment / 改 assignee 都要 core 配额，GraphQL 的 `addAssigneesToAssignable` /
`removeAssigneesFromAssignable` / `addComment` mutation 走的是**同一张 GraphQL 配额**，
core 耗尽期间是可用的兜底写路径；但铁律 1 的两步走（先 remove 再 add）与「恰好 1 人」验证必须照做。
