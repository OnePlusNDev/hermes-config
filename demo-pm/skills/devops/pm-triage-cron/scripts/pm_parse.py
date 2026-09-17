#!/usr/bin/env python3
"""解析 PM 分诊快照。

用法:
    python3 pm_parse.py /tmp/pm_issues_r917.json
    python3 pm_parse.py /tmp/pm_issues_r917.json /tmp/pm_all_r917.json   # 追加 crosscheck

要点（踩过的坑）:
  * 路径必须显式传入/写死，**绝不要 glob('/tmp/pm_issues_*.json')[-1]** —— 字典序会选中
    兄弟轮次的文件（如 pm_issues_x7.json），静默读到别人的空结果误判「无待办」。
  * /issues 返回的数组里**混有 PR**（条目带 pull_request 键），必须先 continue 跳过，
    否则会出现 total_open 比列出的 issue 数多、看起来像脚本丢数据。
  * 判定「无待办」以 crosscheck 的 PM_assigned 列表为空为准，而不是看 PM_query_len==0。
"""
import json
import sys


def load(path):
    with open(path) as f:
        return json.load(f)


def show(items, tag):
    for it in items:
        if "pull_request" in it:
            print("%s PR  #%s | %s" % (tag, it["number"], it["title"]))
            continue
        labels = [l["name"] for l in it.get("labels", [])]
        who = [a["login"] for a in it.get("assignees", [])]
        print("%s ISS #%s | %s | labels=%s | assignees=%s"
              % (tag, it["number"], it["title"], labels, who))
    return [it["number"] for it in items
            if "pull_request" not in it
            and any(a["login"] == "OnePlusNPM" for a in it.get("assignees", []))]


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2

    mine = load(sys.argv[1])
    print("PM_query_len:", len(mine))
    show(mine, "MINE")

    if len(sys.argv) <= 2:
        return 0

    allit = load(sys.argv[2])
    print("total_open:", len(allit))
    pm_assigned = show(allit, "ALL")
    print("crosscheck_PM_assigned:", pm_assigned)
    if not pm_assigned:
        print("VERDICT: SILENT (确认无挂在 PM 名下的 open issue)")
    else:
        print("VERDICT: TRIAGE (存在待分诊 issue)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
