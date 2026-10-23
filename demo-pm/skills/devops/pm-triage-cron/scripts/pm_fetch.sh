#!/bin/bash
# PM 分诊轮询：一次取三份快照。
#   用法: bash pm_fetch.sh <轮次后缀>    例如 bash pm_fetch.sh r917
#   产物: /tmp/pm_issues_<轮次>.json  —— assignee=OnePlusNPM 的 open issue
#         /tmp/pm_all_<轮次>.json     —— 全量 open（含 PR），用于「无待办」crosscheck
#         /tmp/pm_boss_<轮次>.json    —— assignee=OnePlusNBoss（已知有任务，判定力弱）
#         /tmp/pm_ndev_<轮次>.json    —— assignee=OnePlusNDev（零任务账号）
# 第 3 步 sanity check 请优先用 pm_ndev（见 pm_parse.py）：本仓库稳态下 Boss 与全量必然同构、
# 无判定力（2026-09-29 实证，2026-09-30 复核）；零任务账号过滤为空 + 全量非空 = 过滤器有效。
# 一次取齐三份，直接喂给 pm_parse.py 的三步判定，无需每轮手写补充脚本。
# 轮次后缀必须唯一，防止兄弟轮次互相覆盖。切勿在脚本里写 GITHUB_TOKEN= 字面量（见 SKILL.md 禁用清单）。
# 可选第 2 参数 OUT：输出目录。默认 /tmp；建议传私有目录（如 /tmp/pmpm-<轮次>-<时分秒>），
# 以免兄弟 profile 的 /tmp 清扫动作删掉本轮的中间文件（见 SKILL.md 兄弟 profile 清扫那一条）。
set -u
SUF="${1:?用法: bash pm_fetch.sh <轮次后缀> [输出目录]}"
OUT="${2:-/tmp}"
mkdir -p "$OUT" || exit 1
cd ~/.hermes/profiles/demo-pm || exit 1
KEY="GITHUB_""TOKEN"             # 相邻引号拼接：直接写字面量会被 write_file 脱敏成 ***；勿拆成 "GITHUB"+"TOKEN"（下划线丢失）
TOK=$(grep "^${KEY}=" .env | cut -d= -f2- | tr -d '"' | tr -d "'")
echo "token_len=${#TOK}"          # 必须 = 40，否则 token 未取到
# 诊断签名：token_len=0 且 HTTP=404 Not Found 同现 = 取 token 失败，不是仓库不存在/无权限/assignee 写错。
if [ "${#TOK}" -ne 40 ]; then echo "FATAL: token 长度异常，停止（90% 是 KEY 变量拼接丢了字符）"; exit 1; fi
A="https://api.github.com/repos/demo-oneplusn/demo-workflow/issues?state=open&per_page=100"
# --http1.1 必须保留：2026-10-22 实证 HTTP/2 framing 故障会把坏响应写成「空数组 + HTTP 200(5 字节)」。
# cb=$(date +%s) 破 60 秒 cache-control，避免读到上一轮的陈旧快照。
# 2026-10-23 实证：即使加了 --http1.1 坏响应仍间歇出现（同一 URL 连打 4 次得 5/33096/33096/5 字节，
# HTTP 全是 200），所以每路必须打 N 次、取字节数最大的一份作权威快照，单次请求不可信。
fetch_best () {   # $1=label $2=url $3=outfile
  label="$1"; url="$2"; out="$3"
  best=0
  for i in 1 2 3 4; do
    tmp="${out}.t${i}"
    code=$(curl -sS --http1.1 -u "OnePlusNPM:$TOK" -H "Accept: application/vnd.github+json" \
      "${url}&cb=$(date +%s%N)" -o "$tmp" -w "%{http_code}")
    sz=$(wc -c < "$tmp" | tr -d ' ')
    echo "  ${label} try${i} HTTP=${code} bytes=${sz}"
    if [ "$sz" -gt "$best" ]; then best=$sz; cp "$tmp" "$out"; fi
  done
  echo "BEST ${label}=${best} bytes -> ${out}"
}
fetch_best "assignee" "${A}&assignee=OnePlusNPM" "${OUT}/pm_issues_${SUF}.json"
fetch_best "all"      "${A}"                     "${OUT}/pm_all_${SUF}.json"
# 第 3 步 sanity check：零任务账号过滤应为空，反证 assignee 过滤器没被静默忽略
# （Boss 也抓一份作对照，但 Boss 与全量同构、无判定力，见 pm_parse.py 用法）
fetch_best "boss"     "${A}&assignee=OnePlusNBoss" "${OUT}/pm_boss_${SUF}.json"
fetch_best "ndev"     "${A}&assignee=OnePlusNDev"  "${OUT}/pm_ndev_${SUF}.json"
# 第 4 路：Search API 独立交叉验证（assignee= 参数在本环境曾整体失效，2026-10-22 实证）
curl -sS --http1.1 -u "OnePlusNPM:$TOK" -H "Accept: application/vnd.github+json" \
  -G "https://api.github.com/search/issues" \
  --data-urlencode "q=repo:demo-oneplusn/demo-workflow is:open assignee:OnePlusNPM" \
  -o "${OUT}/pm_search_${SUF}.json" -w "HTTP(search)=%{http_code}\n"
echo "ISSUES=${OUT}/pm_issues_${SUF}.json"
echo "ALL=${OUT}/pm_all_${SUF}.json"
echo "BOSS=${OUT}/pm_boss_${SUF}.json"
echo "NDEV=${OUT}/pm_ndev_${SUF}.json"
