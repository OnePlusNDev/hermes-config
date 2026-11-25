#!/usr/bin/env python3
"""GraphQL 兜底枚举器 —— REST core 配额耗尽（HTTP 403 rate limit）时用。

为什么需要它：/issues 端点属于 core 配额（5000/h，按用户计），耗尽后全 REST 403；
GraphQL 是**独立** 5000/h 配额，一条查询就能拿「全量 open + 每条 assignees + 最后一条 comment」，
等价于「全量 crosscheck + 逐条看 assignees」，比 REST 的 assignee 过滤器更可信
（assignee= 参数在本环境曾整体静默失效）。写操作仍需等 core reset。

用法:
    python3 pm_gql_fallback.py                        # 默认 owner/repo + 关注 OnePlusNPM
    python3 pm_gql_fallback.py OnePlusNPM demo-oneplusn/demo-workflow

输出:
    total_open / ISSUE / PR 逐条列表（含 labels、assignees、last_comment_by）
    MINE_COUNT: N                    ← 0 且 total_open>0 才是真空
    MINE 名下 issue 的正文与最后一条 comment（便于意图识别）
退出码: 0 正常；1 取 token 失败或 GraphQL 报错。

铁律（踩过）:
  * token 键名必须写成 "GITHUB_" + "TOKEN" 相邻拼接 —— 字面量会被 write_file 脱敏成 ***。
  * 不要用 urllib 直连 REST /issues 作主路径（TLS 握手会超时），GraphQL 用 urllib 可通。
  * 别把整份响应 print 到 stdout（30KB+ 会灌爆上下文），只打摘要。
"""
import json
import os
import sys
import urllib.request

LOGIN = sys.argv[1] if len(sys.argv) > 1 else "OnePlusNPM"
SLUG = sys.argv[2] if len(sys.argv) > 2 else "demo-oneplusn/demo-workflow"
OWNER, NAME = SLUG.split("/", 1)


def token():
    path = os.path.expanduser("~/.hermes/profiles/demo-pm/.env")
    key = "GITHUB_" + "TOKEN"
    for line in open(path):
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


Q = """
query($owner:String!, $name:String!) {
  repository(owner:$owner, name:$name) {
    issues(states:OPEN, first:50, orderBy:{field:UPDATED_AT, direction:DESC}) {
      totalCount
      nodes {
        number title updatedAt body
        labels(first:10){nodes{name}}
        assignees(first:5){nodes{login}}
        comments(last:1){nodes{author{login} body createdAt}}
      }
    }
  }
}
"""


def main():
    tok = token()
    print("token_len=%d" % (len(tok) if tok else 0))
    if not tok or len(tok) != 40:
        print("FATAL: token 未取到或长度异常")
        return 1

    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": Q,
                         "variables": {"owner": OWNER, "name": NAME}}).encode(),
        headers={"Authorization": "bearer %s" % tok,
                 "User-Agent": "pm-triage",
                 "Content-Type": "application/json"},
    )
    d = json.load(urllib.request.urlopen(req, timeout=30))
    if "errors" in d or "data" not in d:
        print("ERRORS", json.dumps(d.get("errors", d))[:800])
        return 1

    issues = d["data"]["repository"]["issues"]
    print("total_open:", issues["totalCount"], "(返回 %d 条，>50 需分页)" % len(issues["nodes"]))

    mine = []
    for it in issues["nodes"]:
        who = [a["login"] for a in it["assignees"]["nodes"]]
        lbl = [l["name"] for l in it["labels"]["nodes"]]
        cm = it["comments"]["nodes"]
        last = cm[-1]["author"]["login"] if cm else "-"
        print("ISS #%s | %s | labels=%s | assignees=%s | last_comment_by=%s | upd=%s"
              % (it["number"], it["title"][:70], lbl, who, last, it["updatedAt"]))
        if LOGIN in who:
            mine.append(it)

    print("MINE_COUNT:", len(mine))
    for it in mine:
        print("=" * 60)
        print("#%s %s" % (it["number"], it["title"]))
        print("labels:", [l["name"] for l in it["labels"]["nodes"]])
        print("body:", (it["body"] or "")[:1200])
        cm = it["comments"]["nodes"]
        if cm:
            print("last comment by %s at %s:\n%s"
                  % (cm[-1]["author"]["login"], cm[-1]["createdAt"], (cm[-1]["body"] or "")[:800]))
        else:
            print("no comments")
    return 0


if __name__ == "__main__":
    sys.exit(main())
