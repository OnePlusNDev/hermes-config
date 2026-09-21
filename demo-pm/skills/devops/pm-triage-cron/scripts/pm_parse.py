#!/usr/bin/env python3
"""解析 PM 分诊快照。

用法:
    python3 pm_parse.py /tmp/pm_issues_r917.json
    python3 pm_parse.py /tmp/pm_issues_r917.json /tmp/pm_all_r917.json   # 追加 crosscheck
    python3 pm_parse.py /tmp/pm_issues_r917.json /tmp/pm_all_r917.json \
        /tmp/pm_boss_r917.json OnePlusNBoss    # 追加「已知他人」过滤器 sanity check

三步判定「无待办」（缺一不可）:
    1. PM 过滤为空（且 head 验过响应是真 `[ ]`，非截断）。
    2. 去掉 assignee 参数做全量 open crosscheck，确认无挂在 PM 名下的条目。
    3. 拿一个**已知确有任务**的账号（如 OnePlusNBoss）再查一次：
       他人过滤非空 + PM 过滤为空 → 过滤器可信、空结果真实 → SILENT。
       他人过滤也为空（而全量明明有该人任务）→ 过滤器静默失效，改按全量自行筛 assignees。

要点（踩过的坑）:
  * 路径必须显式传入/写死，**绝不要 glob('/tmp/pm_issues_*.json')[-1]** —— 字典序会选中
    兄弟轮次的文件（如 pm_issues_x7.json），静默读到别人的空结果误判「无待办」。
  * /issues 返回的数组里**混有 PR**（条目带 pull_request 键），必须先 continue 跳过，
    否则会出现 total_open 比列出的 issue 数多、看起来像脚本丢数据。
  * 判定「无待办」以 crosscheck 的 PM_assigned 列表为空为准，而不是看 PM_query_len==0。
  * 第 3 步的「他人过滤响应与全量响应字节数完全相同」**通常不是过滤器失效**：本仓库
    的常态就是全部 open 条目都挂在 Boss 名下（2026-09-19、2026-09-21 两轮均 33096 字节、
    5 条、全为 OnePlusNBoss 独占）。正确判据是**逐条看 assignees 列表**，不是比字节数。
  * 别把整份 raw JSON 打进 stdout（全量响应约 33KB，会灌爆上下文）；摘要用 len()/sorted()。
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

    # 第 3 步：拿一个已知确有任务的账号反证过滤器没被静默忽略。
    if len(sys.argv) > 3:
        other_login = sys.argv[4] if len(sys.argv) > 4 else "?"
        other = load(sys.argv[3])
        other_assignees = sorted({a["login"]
                                  for it in other
                                  for a in it.get("assignees", [])})
        print("other_filter(%s)_len:" % other_login, len(other))
        print("other_filter_assignees:", other_assignees)

    print("---")

    if pm_assigned:
        print("VERDICT: TRIAGE (存在待分诊 issue)")
        return 0

    if len(sys.argv) <= 3:
        print("VERDICT: SILENT_PENDING_STEP3 "
              "(PM 名下无 issue；但仍需按用法补跑「已知他人」过滤器 sanity check)")
        return 0

    if len(other) > 0:
        print("VERDICT: SILENT (PM 过滤为空 + 已知他人过滤非空 → 过滤器可信、空结果真实)")
    else:
        all_logins = sorted({a["login"]
                             for it in allit
                             for a in it.get("assignees", [])})
        print("VERDICT: SUSPECT (PM 与已知他人过滤均为空，但全量有 %d 条 → "
              "过滤器可能静默失效；改按全量自行筛 assignees)" % len(allit))
        print("full_open_assignee_logins:", all_logins)
    return 0


if __name__ == "__main__":
    sys.exit(main())
