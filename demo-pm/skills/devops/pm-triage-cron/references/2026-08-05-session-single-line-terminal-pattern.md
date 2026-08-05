# 2026-08-05 cron 会话：单行 terminal 零文件路径 + 未加载技能的失败成本

## 会话结果

- `assignee=OnePlusNPM&state=open` → `[]`（真无任务）
- 全量健康检查：5 个 open issue（#2、#4、#5、#6、#7），全部 assign 给 `OnePlusNBoss`，无 unassigned issue → 输出 `[SILENT]`
- RULES.md 为空（0 字节，无额外协作铁律）
- `.env` 的 GITHUB_TOKEN 有效（curl HTTP 200，非 401）

## 成功的最简路径（零 write_file、零 gh CLI）

单行 terminal 命令，分两次调用（不要把「抓取」和「多行解析」放同一条命令）：

```bash
# 1) 抓取（单行；`***` 仅为显示层脱敏，执行的是真实 token）
set -a; source ~/.hermes/profiles/demo-pm/.env; set +a; curl -s -H "Authorization: token $GITHUB_TOKEN" -H "Accept: application/vnd.github+json" "https://api.github.com/repos/demo-oneplusn/demo-workflow/issues?state=open&assignee=OnePlusNPM&per_page=100" -o /tmp/demo_pm_issues.json; echo "curl exit: $?"; wc -c /tmp/demo_pm_issues.json

# 2) 解析（必须单行；多行 python3 -c 会被 bash eval 打散）
python3 -c "import json; data=json.load(open('/tmp/demo_pm_issues.json')); print('total:', len(data) if isinstance(data,list) else data.get('message')); [print('#'+str(i['number']), i['title'], '| assignees:', [a['login'] for a in i.get('assignees',[])], '| labels:', [l['name'] for l in i['labels']]) for i in data] if isinstance(data,list) else None"
```

## 失败成本链（未先加载技能 → 重踩全部已记录陷阱）

| # | 尝试 | 失败 | 已记录于 |
|---|------|------|---------|
| 1 | `curl ... \| python3 -c "..."` | tirith `curl_pipe_shell` 拦截（pending approval） | 技能「不推荐的方法」 |
| 2 | write_file 写 bash 脚本含 `Authorization: token $GITHUB_TOKEN` | 文件被脱敏破坏为 `token ***`（无闭合引号）→ bash `unexpected EOF while looking for matching quote` | 2026-08-03 条目 |
| 3 | 同一条 terminal 命令内嵌多行 `python3 -c "..."` | bash eval 打散 → `import: command not found` / `syntax error near unexpected token '('`；且整条命令失败导致前面 curl 未执行（随后 FileNotFoundError） | 2026-08-03 条目 |
| 4 | `/tmp/check_issues.py`、`/tmp/fetch_issues.sh` | 兄弟 subagent 覆盖警告（`_warning: modified by sibling subagent`） | 2026-07-11 条目 |

## 教训

- **先 `skill_view(name='pm-triage-cron')` 再动手。** 本会话未加载技能，白白重踩 4 个已记录陷阱（4-5 次无效 tool call）。
- 加载后优先 `scripts/full_triage.py`（快捷路径），或直接用上面的单行 terminal 路径。
- 不要把「curl 抓取」和「多行 python 解析」放在同一条 terminal 命令里——整条失败时 curl 的结果文件也不会生成。
- `.env` token 是否过期是间歇性的；本轮有效（200），但 2026-07-13 曾过期（401）。先跑一次再决定是否降级到 gh CLI。
