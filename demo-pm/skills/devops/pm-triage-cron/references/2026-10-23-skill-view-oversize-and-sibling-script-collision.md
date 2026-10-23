# 2026-10-23 cron 轮次：大技能读取法 + 兄弟轮抢解析脚本

本轮结果：`[SILENT]`（PM 名下 0 条）。但暴露两个与「怎么用这个技能」有关的操作细节，值得固化。

## 一、`skill_view` 返回超大结果时怎么读（本轮首次踩到）

`skill_view(name='pm-triage-cron')` 返回 ~108KB，被 Hermes 持久化到：

```
/var/folders/kb/.../hermes-results/call_00_ET_....txt
```

同时只给出 1500 字符 preview。**陷阱：**该 temp 文件是**单行 JSON**（`{"success":true,...,"content":"...\n...","linked_files":...}`），
所以——

- `read_file` 读它只会得到一整行被截断的内容（154KB/1 行），`limit/offset` 分页完全无效；
- `search_files` 在原始 JSON 上匹配，命中的是转义后的 `\n` 长行，行号定位不到章节；
- 正文里的 `\n` 全是字面量 `\\n`，直接看几乎不可读。

**正确做法：先提取 `content` 字段落成 markdown，再分页/搜索。**

```python
# /tmp/pm_dump_skill.py
import json
p = "/var/folders/kb/.../hermes-results/call_00_ET_....txt"   # 换成当轮实际路径
d = json.load(open(p))
c = d["content"]
open("/tmp/pm_skill_body.md", "w").write(c)
print("chars", len(c), "lines", c.count("\n"))
```

然后 `python3 /tmp/pm_dump_skill.py` → 得到 `/tmp/pm_skill_body.md`（本轮 100209 字符 / 2180 行）→
用 `search_files(pattern="^#{1,3} |两步|assignee|comment")` 出章节地图，用 `read_file(offset, limit)` 精读。

**不要通读 2180 行。** 分诊任务真正需要的只有四节：

| 需要什么 | 章节锚点 |
|---|---|
| 脚本/禁用清单 | `## ✅ TL;DR` |
| 标签→负责人映射 | `## 分诊映射表` |
| 评论 + 两步法变更 | `### 第四步：分类与派工` |
| 中文 comment 被 tirith 拦时的写法 | 搜 `confusable_text` |

（本轮正文 100k 已顶到上限，新增内容继续落 `references/`。）

## 二、兄弟轮抢文件：这次抢的是**解析脚本**，不只是数据 JSON

`write_file` 写入 `/tmp/pm_parse_1023.py` 后返回：

```
_warning: /tmp/pm_parse_1023.py was modified by sibling subagent '13bf1c82-...' but this agent never read it.
```

但 `read_file` 回读发现**内容确实就是自己刚写的那份**（14 行，完全一致）。
说明该 `_warning` 是「同名文件曾被别的 session 写过」的历史提示，**不等于内容被篡改**。

处置规则（本轮验证有效）：

1. 收到 `_warning` **先 `read_file` 回读比对**，内容一致就照跑；不一致才改名重写。
2. **数据 JSON 与解析脚本都要带本轮唯一后缀**，不要只给 JSON 加：
   - `pm_all_pm1023_k9x.json`
   - `pm_parse_pm1023_k9x.py`（脚本里把上面这个绝对路径**写死**）
3. fetch 完立刻 `wc -c` + 解析，把「抓到」和「读到」之间的窗口压到最短。
4. 别用 `rm -f /tmp/pm_*.json` 批量清（tirith「mass file deletion」会卡死无人值守 cron）——逐个 `rm` 或干脆不清。

## 三、本轮实证数据点（供下次判断「真无任务」对照）

- `gh auth status` 活跃账号 = `OnePlusNDev`；**未做 `gh auth switch`**，只读查询照常可用 → 再次确认「assignee 过滤与活跃账号无关」，纯查询不必切账号（只有 comment/edit 写操作才需要 PM 身份）。
- `issues?state=open&assignee=OnePlusNPM` → `[]`（**2 字节**）。
- 全量 `issues?state=open` → 5 条：ISSUE #2 / #4 / #5 / #7 + PR #6，**全部** assign `OnePlusNBoss`，**无游离（0 assignee）issue**。
- 抽查 #2/#4/#5/#6/#7 评论历史：均有 `OnePlusNPM` 的 PM 分诊记录（#5、#6 还有 Tester 的流程异常标记）→ 确属「已分诊过、停在 Boss 终审」，不是漏派。
- 结论：0 条 + 全量无游离 + 评论证实已分诊 → `[SILENT]`，零副作用（未评论、未改 assignee、未切账号）。

**注意：** 仓库里的 `type:feature` issue 停在 `OnePlusNBoss` 名下**不是**待办——它们的历史 comment 已记录 PM 判给 Dev、Dev 交付、Tester 验证、最后交 Boss 终审。分诊职责只覆盖 `assignee=自己` 的 issue，不要去「顺手纠正」Boss 名下的 issue。
