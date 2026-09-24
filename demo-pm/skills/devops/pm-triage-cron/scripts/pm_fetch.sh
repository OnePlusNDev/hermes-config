#!/bin/bash
# PM 分诊轮询：一次取三份快照。
#   用法: bash pm_fetch.sh <轮次后缀>    例如 bash pm_fetch.sh r917
#   产物: /tmp/pm_issues_<轮次>.json  —— assignee=OnePlusNPM 的 open issue
#         /tmp/pm_all_<轮次>.json     —— 全量 open（含 PR），用于「无待办」crosscheck
#         /tmp/pm_boss_<轮次>.json    —— assignee=OnePlusNBoss，用于第 3 步「已知他人」过滤器 sanity check
# 一次取齐三份，直接喂给 pm_parse.py 的三步判定，无需每轮手写补充脚本。
# 轮次后缀必须唯一，防止兄弟轮次互相覆盖。切勿在脚本里写 GITHUB_TOKEN= 字面量（见 SKILL.md 禁用清单）。
# 可选第 2 参数 OUT：输出目录。默认 /tmp；建议传私有目录（如 /tmp/pmpm-<轮次>-<时分秒>），
# 以免兄弟 profile 的 /tmp 清扫动作删掉本轮的中间文件（见 SKILL.md 兄弟 profile 清扫那一条）。
set -u
SUF="${1:?用法: bash pm_fetch.sh <轮次后缀> [输出目录]}"
OUT="${2:-/tmp}"
mkdir -p "$OUT" || exit 1
cd ~/.hermes/profiles/demo-pm || exit 1
KEY="GITHUB_TOKEN"
TOK=$(grep "^${KEY}=" .env | cut -d= -f2- | tr -d '"' | tr -d "'")
echo "token_len=${#TOK}"          # 必须 = 40，否则 token 未取到
if [ "${#TOK}" -ne 40 ]; then echo "FATAL: token 长度异常，停止"; exit 1; fi
A="https://api.github.com/repos/demo-oneplusn/demo-workflow/issues?state=open&per_page=100"
curl -sS -u "OnePlusNPM:$TOK" -H "Accept: application/vnd.github+json" \
  "$A&assignee=OnePlusNPM" -o "${OUT}/pm_issues_${SUF}.json" -w "HTTP(assignee)=%{http_code}\n"
curl -sS -u "OnePlusNPM:$TOK" -H "Accept: application/vnd.github+json" \
  "$A" -o "${OUT}/pm_all_${SUF}.json" -w "HTTP(all)=%{http_code}\n"
# 第 3 步 sanity check：已知确有任务的账号，反证 assignee 过滤器没被静默忽略
curl -sS -u "OnePlusNPM:$TOK" -H "Accept: application/vnd.github+json" \
  "$A&assignee=OnePlusNBoss" -o "${OUT}/pm_boss_${SUF}.json" -w "HTTP(boss)=%{http_code}\n"
echo "ISSUES=${OUT}/pm_issues_${SUF}.json"
echo "ALL=${OUT}/pm_all_${SUF}.json"
echo "BOSS=${OUT}/pm_boss_${SUF}.json"
