# Assignee 查询自检 & 空结果取证（实测踩坑记录）

分诊脚本「跑通了但结论是错的」比报错更危险。本文件记录圆 2026-11 轮次实际踩到的四个坑，
以及 `[SILENT]` 之前必须走完的取证清单。

## 坑 1：token 取成了 `GITHUB_USERNAME` → curl 静默 404

```bash
# 错：取第一个 GITHUB_ 开头的键
K=$(grep -E '^GITHUB_' ~/.hermes/profiles/demo-pm/.env | head -1 | cut -d= -f1)
# → key=GITHUB_USERNAME, token_len=10, HTTP=404
```

`.env` 里 `GITHUB_USERNAME` 排在 `GITHUB_TOKEN` 前面。用短密码做 Basic Auth 时
GitHub 返回 **404 而不是 401**（对私有/测试仓库一律隐藏存在性），极易被误读成「仓库没了」。

正确写法 + 强制自检：

```bash
K="GITHUB_""TOKEN"
TOK=$(grep "^${K}=" .env | cut -d= -f2- | tr -d '"' | tr -d "'")
echo "token_len=${#TOK}"   # 必须 = 40；不是 40 就停，别往下跑
```

**推论：遇到 404 先怀疑凭据，再怀疑仓库名/权限。** 若 token_len 正确仍 404，才去看仓库是否存在、token 是否有 repo scope。

## 坑 2：一条 terminal 命令里串多个 curl + 嵌套引号 → `unexpected EOF`

现象：

```
/bin/bash: eval: line 13: unexpected EOF while looking for matching `''
/bin/bash: eval: line 15: syntax error: unexpected end of file
```

成因是命令文本里的凭据键名/参数在传递时被脱敏重写成 `***`，把引号配对打断了。
`grep -E '^GITHUB_TOKEN=' .env` 这种内联写法尤其容易中招。

对策（固定套路）：

1. `write_file` 把脚本落盘（`/tmp/pm_xxx.sh`），再 `bash /tmp/pm_xxx.sh`；
2. **一个脚本一个 curl**，不要 `curl ... && curl ... && python3 -c "..."`；
3. 脚本内取 key 用相邻引号拼接 `K="GITHUB_""TOKEN"`，不写字面量；
4. 需要多接口时写多个小脚本，或写一个脚本内用 `for` 循环 + 独立 `-o` 文件。

## 坑 3：用 sed/python 改写旧脚本换 assignee → 计数自相矛盾

本轮事故：把已存在的 `state=all&assignee=OnePlusNPM` 脚本用 `sed`+`str.replace` 改成 Boss 查询。
因为 `sed` 先把 `OnePlusNPM&per_page=100` 替换掉了，后面 python 的
`replace('state=all&assignee=OnePlusNPM', ...)` 没能命中 → `state=all` 残留，
结果返回 **7 条（含 2 条已关闭）**，而全量 open 查询是 **5 条**，看起来像仓库数据自相矛盾。

**铁律：每换一次查询条件，写一个全新的脚本**，URL 里把
`state=` / `assignee=` / `per_page=` 全部显式写全，并 `echo "URL=$URL"`。
解析时逐条打印 `number | state | title | assignees | PR/ISSUE`，
两处计数不一致时**先怀疑查询 URL，不要怀疑仓库数据**。

## 坑 4：`/issues` 端点会混进 PR

`GET /repos/{owner}/{repo}/issues?state=open` 同时返回 open 的 pull request。
判别依据：JSON 条目里有 `pull_request` 字段（本轮 #6 就是 PR，标题带 `feat:` 前缀）。

- 统计「待分诊 issue 数」且要排除 PR：`if 'pull_request' not in item`
- 但**分诊判断本身不需要排除 PR**：PR 也可以被 assign、也可以写 comment 做分诊说明；
  只是报告里别说成「5 个 issue」，说「5 条 open（4 issue + 1 PR）」。

## `[SILENT]` 前的四步取证（顺序固定，全过才静默）

```bash
# 1) 响应体确认是真空数组
head -c 200 /tmp/pm_issues_<uniq>.json      # 期望 "[\n\n]"

# 2) 同条件换 state=all，确认不是「只有已关闭的曾在我名下」
GET /issues?state=all&assignee=OnePlusNPM   # 仍 0 才继续

# 3) 确认 token 身份就是自己（防止拿到别人的 token → 永远查不到自己的 issue）
GET /user                                    # login 必须 == OnePlusNPM

# 4) 可选反查：assignee=OnePlusNBoss 是否返回非空
#    非空 ⇒ assignee 参数确实生效；参数生效 + 自己名下为空 ⇒ 真无待办
```

四步全绿 → 回 `[SILENT]`，**不写任何 comment、不改任何 assignee**。

## 本轮实测结果（可作为基线参照）

`demo-oneplusn/demo-workflow` open 共 5 条（#2 #4 #5 #7 issue + #6 PR），
全部 `assignee=OnePlusNBoss`，`OnePlusNPM` 名下 0 条（state=all 也是 0）→ `[SILENT]`。

同一批 issue 历史上有 PM 反复分诊刷屏的记录（#2 被重复分诊三次），
所以「没有自己名下的任务就绝对不发言」既是规则也是正确行为，不要为了"有产出"去碰老板名下的 issue。
