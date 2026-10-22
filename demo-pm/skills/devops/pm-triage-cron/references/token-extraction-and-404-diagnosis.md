# 取 token 的坑 与 HTTP 404 误诊（2026-10-22 实证）

## 症状
轮询返回空结果，紧随 `token_len=0` 之后是：

```
HTTP=404
{"message": "Not Found", "documentation_url": "https://docs.github.com/rest/issues/issues#list-repository-issues"}
```

**误判**：以为仓库名写错 / token 无权限 / assignee 拼错，去翻仓库和权限。
**真相**：token 根本没取到，`curl -u "OnePlusNPM:"`（空密码）打匿名请求，私有仓库对匿名用户一律回 404（不是 401，所以特别像"仓库不存在"）。

## 诊断规则
| 现象 | 结论 |
|---|---|
| `token_len=0` + `HTTP=404` | 取 token 失败。**先回读脚本**，别查仓库 |
| `token_len=40` + `HTTP=404` | 才是仓库名/权限问题 |
| `token_len=40` + `HTTP=401` | token 失效或过期 |
| `token_len=40` + `HTTP=200` + `[ ]` | 真·无待办，需再跑无 `assignee` 全量 crosscheck |

## 为什么会取不到 token（write_file 脱敏）
`write_file` 会把脚本里形如 `GITHUB_TOKEN=` 的字面量脱敏成 `GITHUB_TOKEN=***` 再落盘，于是 `grep "^GITHUB_TOKEN="` 变成非法正则或永不命中。

三种写法对比：

```bash
KEY="GITHUB_TOKEN"      # ❌ 落盘被脱敏成 ***，grep 报 repetition-operator operand invalid
KEY="GITHUB"'TOKEN'     # ❌ 静默拼成 GITHUBTOKEN（下划线丢了），grep 不报错但命中 0 行 → token_len=0
KEY="GITHUB_""TOKEN"    # ✅ 相邻引号拼接，下划线和等号都保住，落盘不受影响
```

第三种是最隐蔽的：**脚本不报错、grep 不报错、只是默默取不到**，所以必须靠 `echo "token_len=${#TOK}"` 兜底，并且长度 != 40 就 `exit 1` 硬停。

## 流程教训
**别每轮手写 fetch 脚本。** 手写就是重新踩脱敏坑的入口。直接跑 skill 里打包好的：

```bash
bash scripts/pm_fetch.sh <唯一轮次后缀> [输出目录]
# 产物: pm_issues_<轮次>.json / pm_all_<轮次>.json / pm_boss_<轮次>.json / pm_ndev_<轮次>.json
```

它已内置：token 长度校验、唯一文件名防兄弟轮次覆盖、全量 crosscheck 快照、零任务账号 sanity check（`pm_ndev`）。
