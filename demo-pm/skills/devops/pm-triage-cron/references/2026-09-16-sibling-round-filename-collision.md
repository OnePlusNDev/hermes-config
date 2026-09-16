# 2026-09-16：同日兄弟轮的临时文件名冲突

## 现象

用日期后缀命名临时脚本（`/tmp/pm_fetch_0916.sh`），`write_file` 返回：

```
_warning: "/private/tmp/pm_fetch_0916.sh was modified by sibling subagent
'997b4a29-...' but this agent never read it. Read the file before writing
to avoid overwriting the sibling's changes."
```

即同日另一个 cron 轮次（或子代理）已经写过同一路径。风险：直接 `bash` 该路径，可能执行的是**别人那一轮**的脚本（token 变量、仓库、输出路径都可能不同），静默拿到错误结果。

## 处置

1. 收到 sibling 覆盖警告 → 先 `read_file` 回读，确认磁盘字节是本轮预期内容（本轮实测回读无误，`file_size: 443`，脚本完好）。
2. 真正执行时**改用带随机后缀的唯一路径**：

```bash
sed 's/pm_issues_0916/pm_issues_pm0916_a7f3/g' /tmp/pm_fetch_0916.sh \
  > /tmp/pm_fetch_pm0916_a7f3.sh && bash /tmp/pm_fetch_pm0916_a7f3.sh
```

3. 解析脚本里 JSON 路径**写死**这个唯一名，勿 `glob(...)[-1]`。

## 结论

**日期后缀不保证唯一性**——同日多轮/多子代理会撞名。所有临时文件（fetch 脚本、输出 JSON、parse 脚本）一律带短随机串后缀。回读验证仍是发现「脚本被写坏或被别人覆盖」的唯一可靠手段。
