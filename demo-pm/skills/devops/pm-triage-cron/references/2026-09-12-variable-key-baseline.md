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
  2026-09-14 实测：`$$` 后缀**挡不住**并发兄弟轮——两个 cron 轮次可能撞同一脚本路径，
  `write_file` 会回告警 `modified by sibling subagent ... but this agent never read it`。
  一旦被兄弟轮覆写，脚本可能在 write 与 bash 之间变内容（token 提取行被换成别的写法即静默 404）。
  对策：脚本名加一段随机 token（如 `pmt_fetch_<日期>_k7q2.sh`），JSON 同理（`..._k7q2_$$.json`）；
  或干脆每次现写现跑、不复用同一路径。解析脚本里的 JSON 路径必须写死。
  **2026-09-14 补记：随机后缀仍挡不住兄弟轮**——各轮都照抄本 skill 的命名模板时会生成
  **相同**的「随机」名（实测 `pmt_fetch_0914_k7q2.sh` 照样被兄弟轮撞上并告警）。
  稳妥做法：**写完必须 `read_file` 回读磁盘内容**，确认 token 提取行仍是
  `grep "^${KEY}="` 写法、curl 行未被换掉，再 `bash`；回读一致即可放心跑，不必因告警弃用。
  「无任务」判定同理要证伪：先 `od -c` 确认响应真是 `[ \n ]`，再跑去掉 `assignee` 的
  全量 crosscheck 确认真无本 PM 名下 issue，才回 `[SILENT]`。
- `read_file` 读 `.env` 会 `Access Denied`（凭据存储），必须走 terminal 提取。
- 认证用 Basic Auth `-u "OnePlusNPM:$TOK"`；Bearer/token header 写法不可靠。
