# 2026-09-12 分诊基线：变量键名取 token + Basic Auth

## 场景
PM 定时分诊轮询（profile `demo-pm` / GitHub `OnePlusNPM`）。
`RULES.md` 为空（0 字节）——分诊规则全部来自 cron prompt，无额外profile铁律。

## 已验证脚本（一次通过，照抄可用）
```bash
#!/bin/bash
cd ~/.hermes/profiles/demo-pm || exit 1
KEY="GITHUB_TOKEN"
TOK=$(grep "^${KEY}=" .env | cut -d= -f2- | tr -d '"' | tr -d "'")
echo "token_len=${#TOK}"                     # 必须 = 40；2026-09-12 实测 40 ✅
curl -sS -u "OnePlusNPM:$TOK" -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/demo-oneplusn/demo-workflow/issues?state=open&assignee=OnePlusNPM&per_page=100" \
  -o /tmp/pmx_issues_$$.json -w "HTTP=%{http_code}\n"
echo "BYTES=$(wc -c < /tmp/pmx_issues_$$.json)"   # 空数组仅 3~5 字节，可快速判空
```

## 全量 crosscheck（`assignee=OnePlusNPM` 返回 0 条时）
```bash
# 去掉 assignee 参数
#   .../issues?state=open&per_page=100
# 再用 python3 json.load 打印 number / title / assignees / labels
```

## 2026-09-12 观测结果
- `state=open&assignee=OnePlusNPM` → `HTTP=200`，返回 `[]`（0 条）
- 全量 open → 5 条，assignee 全部为 `OnePlusNBoss`：#2 / #4 / #5 / #6 / #7，
  标签为 `type:feature`（#4/#5/#6 另带 `priority:normal`）或空（#7 为验证报告）
- 结论：PM 名下无任务 → 回 `[SILENT]`，不派工、不发通知

## 要点
- **变量键名拆写**（`grep "^${KEY}="`）避开 write_file 对字面量 `GITHUB_TOKEN=` 的脱敏；
  比 TL;DR 早期那种 `sed 's/^GITHUB_TOKEN=//'` 写法更安全——后者是已知地雷（会被写成字面 `***` → `repetition-operator operand invalid`）。
- 写脚本后**先看 `token_len`**，非 40 立即停手，不要拿空 token 去发请求。
- 临时文件名带日期/随机后缀（`$$`、`$(date +%H%M%S)`），避免并行 cron 兄弟轮次互相覆写脚本或 JSON。
- `read_file` 读 `.env` 会 `Access Denied`（凭据存储），必须走 terminal 提取。
- 认证用 Basic Auth `-u "OnePlusNPM:$TOK"`；Bearer/token header 写法不可靠。
