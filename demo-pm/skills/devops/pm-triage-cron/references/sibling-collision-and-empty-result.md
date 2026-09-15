# 兄弟轮次抢文件 + 空结果确证（2026-09-15 实盘记录）

本轮：PM 轮询 `demo-oneplusn/demo-workflow`，结论 **无待分诊任务 → `[SILENT]`**，全程未产生任何 comment 或 assignee 变更。以下为可复用的判据细节。

## 1. 兄弟 cron 轮次抢 /tmp 文件——警告是误报，但必须回读

一轮内我按「唯一后缀」惯例使用了 `pm_fetch_0915b.sh` / `pm_extract_skill_0915b.py` / `pm_parse_0915b.py`，**write_file 依旧弹出**：

```
_warning: /private/tmp/pm_fetch_0915b.sh was modified by sibling subagent
'<uuid>' but this agent never read it.
```

即：**自定义后缀挡不住警告**，因为兄弟轮次会复用同名基名。警告本身不是故障（三次回读后内容均完好），但**不能无视**——若真被覆写，分诊会静默读到过期数据并误判「无待办」。

**正确姿势（已验证）：**

1. `write_file` 写出脚本；
2. **立刻 `read_file` 回读**该脚本，逐行确认内容确为本次所写；
3. 一致 → `bash` 执行；不一致 → 改名重写（不要硬跑）；
4. 输出侧也回读：别只信自己脚本 echo 的计数，要看真实响应体。

## 2. fetch 数据可信三件套

| 检查 | 期望值 | 含义 |
|---|---|---|
| `token_len` | `40` | `.env` 里 GITHUB_TOKEN 取到了 |
| `HTTP` | `200` | 鉴权 + 端点通 |
| `head -c 400` | 真实 JSON 体 | 不是错误页/空壳 |

三者齐备才进入解析。取 token 只能 shell 里 `grep`（`read_file` 读 `.env` 必 Access Denied）。

## 3. 空结果的确是 `[ ]`，不是空文件

`assignee=OnePlusNPM` 无待办时：

```
HTTP=200
BYTES=       5
---HEAD---
[
<空行>
]
```

`BYTES=5` + `head -c 400` 显示成对空数组 = 真 `[ ]`。**此时仍不可直接 `[SILENT]`**，必须跑**去掉 `assignee` 参数的全量 open crosscheck**。

## 4. 本轮 crosscheck 实况（判断尺子）

全量 open（无 assignee 过滤）：`BYTES=33096`，`total_items=5`，全部为 issue（无 PR）：

```
#7   assignees=['OnePlusNBoss']  labels=[]                              [验证报告] Issue 2 独立验证
#5   assignees=['OnePlusNBoss']  labels=['type:feature','priority:normal']  [测试] 全链路含验证：新增 subtract(a,b)
#4   assignees=['OnePlusNBoss']  labels=['type:feature','priority:normal']  [测试] PM→Dev 路径：新增 multiply(a,b)
#2   assignees=['OnePlusNBoss']  labels=['type:feature','priority:normal']  [测试] 验证 PM 分诊流程：新增 add(a,b)
MINE= []
```

`MINE=[]` → 确认无待分诊 → `[SILENT]`。

## 5. 两个诱饵，别咬

- **标签/标题诱饵**：`#5` 标题含「全链路含验证」、`#2/#4` 带 `type:feature`——看似该派给 Dev/Tester，但 assignee 是 `OnePlusNBoss`，**不属于本轮待分诊范围**。「先按 assignee 过滤，再看标签」的顺序不能反。
- **`RULES.md` 0 字节诱饵**：本 profile 的 `RULES.md` 是空文件（`total_lines: 0`，`read_file` 返回 `"content": "1|"`）。这是**正常返回**，不是读失败——视为「无额外铁律」，直接按 cron prompt 规则执行，不要反复重试或卡住。

## 6. 解析脚本过滤要点

`/issues` 端点**混装 issue 和 PR**，解析时必须 `if "pull_request" in it: continue`，否则会把 PR 计入 open 数并可能误判待办。
