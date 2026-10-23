# 2026-10-22：HTTP/2 framing 故障导致「假空」+ assignee 参数失灵

## 现象（本轮实测）

1. `issues?state=open&assignee=OnePlusNPM` → `HTTP=200`，body 仅 5 字节 `[\n\n]`。
2. 按常规做 crosscheck 时，`state=open&per_page=100` 全量也返回 5 字节 —— 但同一秒
   `labels=type%3Afeature&state=open` 返回 4 条。**自相矛盾 = 传输层坏了，不是真的没任务。**
3. 期间出现 `curl: (16) Error in the HTTP2 framing layer` 与 `HTTP=000`。
4. `assignee=<任何人>` 全部返回 0 条，包括明明有 5 条 open 的 `OnePlusNBoss` ——
   该参数在本机环境下已不可信。
5. `HTTP: cache-control: private, max-age=60, s-maxage=60` 会放大问题：坏响应可能被缓存 60 秒。

## 正确做法

```bash
# 1) 一律显式 --http1.1，并加缓存破坏参数
curl -sS --http1.1 -u "OnePlusNPM:$TOK" \
  "https://api.github.com/repos/demo-oneplusn/demo-workflow/issues?state=open&per_page=100&cb=$(date +%s)" \
  -o /tmp/pm_all.json -w "HTTP=%{http_code}\n"

# 2) 字节数自检：本仓库 open 全量稳态约 33096 字节；<1KB 一律当坏响应重试
wc -c /tmp/pm_all.json

# 3) 独立交叉验证：Search API 读 total_count
curl -sS --http1.1 -u "OnePlusNPM:$TOK" -G "https://api.github.com/search/issues" \
  --data-urlencode "q=repo:demo-oneplusn/demo-workflow is:open assignee:OnePlusNPM" \
  -o /tmp/pm_search.json -w "HTTP=%{http_code}\n"
```

结论判定：**无过滤全量（自行筛 `assignees`）与 Search API 同时为 0** → 才能 `[SILENT]`。

## 本轮结论（留档）

- open 共 5 条（4 issue + 1 PR），**全部 assignee = OnePlusNBoss**，无一条在 OnePlusNPM 名下。
- Search API `total_count: 0`（issue 与含 PR 两种查询均为 0）。
- 因此本轮无待分诊任务 → `[SILENT]`，未发任何 comment、未改任何 assignee。
- `/repos/demo-oneplusn/demo-workflow/assignees` 返回 6 个合法登录名：
  OnePlusNBoss, OnePlusNDev, OnePlusNPM, OnePlusNTester, peter-202, zhangtbj。
