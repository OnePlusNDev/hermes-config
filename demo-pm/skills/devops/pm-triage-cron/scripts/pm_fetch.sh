#!/bin/bash
# PM 分诊轮询：一次取两份快照。
#   用法: bash pm_fetch.sh <轮次后缀>    例如 bash pm_fetch.sh r917
#   产物: /tmp/pm_issues_<轮次>.json  —— assignee=OnePlusNPM 的 open issue
#         /tmp/pm_all_<轮次>.json     —— 全量 open（含 PR），用于「无待办」crosscheck
# 轮次后缀必须唯一，防止兄弟轮次互相覆盖。切勿在脚本里写 GITHUB_TOKEN= 字面量（见 SKILL.md 禁用清单）。
set -u
SUF="${1:?用法: bash pm_fetch.sh <轮次后缀>}"
cd ~/.hermes/profiles/demo-pm || exit 1
KEY="GITHUB_TOKEN"
TOK=$(grep "^${KEY}=" .env | cut -d= -f2- | tr -d '"' | tr -d "'")
echo "token_len=${#TOK}"          # 必须 = 40，否则 token 未取到
if [ "${#TOK}" -ne 40 ]; then echo "FATAL: token 长度异常，停止"; exit 1; fi
A="https://api.github.com/repos/demo-oneplusn/demo-workflow/issues?state=open&per_page=100"
curl -sS -u "OnePlusNPM:$TOK" -H "Accept: application/vnd.github+json" \
  "$A&assignee=OnePlusNPM" -o "/tmp/pm_issues_${SUF}.json" -w "HTTP(assignee)=%{http_code}\n"
curl -sS -u "OnePlusNPM:$TOK" -H "Accept: application/vnd.github+json" \
  "$A" -o "/tmp/pm_all_${SUF}.json" -w "HTTP(all)=%{http_code}\n"
echo "ISSUES=/tmp/pm_issues_${SUF}.json"
echo "ALL=/tmp/pm_all_${SUF}.json"
