## 对话主模型（2026-06-14）
- tester-01 对话主模型已从 glm-5.1 切换为 deepseek（model=deepseek-v4-pro, base_url=api.deepseek.com/v1, key_env=DEEPSEEK_API_KEY）；handoff.yaml 与 README.md 已同步至 GitHub。
- .env 内仍保留 GLM_API_KEY 与 REV01 yibuapi 端点作为回退（注释待清理）。
§
Issue 处理规则：只看 assignees，不看 status tag。assignees 是我（tester-01）就必须处理，不管 status 是什么标签（Todo/In Progress/Done 等）。status tag 是给 boss 看的，我自己只认 assignees。assignees 不会是多人的情况。
§
Issue 处理流程（task-polling cronjob）：1) 搜索 assignee=tester-01 的 open issue；2) 无任务则 [SILENT]；3) 有任务则：a.先读所有 comment 了解上下文 → b.回复告知开始处理+概述+计划 → c.实际执行任务 → d.完成后更新 comment 说明结果 → e.将 assignee 流转给下一步处理人 → f.无法独立完成时 @ 相关同事协调。deliver 改为 feishu（Home channel），有任务时发私信通知。
§
Issue #9 学到的测试质量标准：1) 不采信自评，必须独立从干净源码重新执行验证；2) 留可复现的测试夹具（harness脚本）供后续复用；3) 对照验证必须两端都实际执行，不能凭推测声称差异；4) 检查源码mtime确保测试的是最新版本；5) 读完全部comment再动手，前人可能已给出精确修复指引；6) 做完必须reassign给下一步处理人；7) 报告里避免"Android期望X"这类未经验证的假设——如果没跑过Android就说没跑过。
§
Hindsight 2026-06-17 终态: 4 daemon 均以 --daemon --idle-timeout 86400 启动，自管 PG。端口: tester-01=9177, pm-01=9178, dev-01=9179, rev-01=9180。key 用 z.ai GLM (45af10...) + https://api.z.ai/api/paas/v4。每个 profile 的 home/.hindsight/profiles/ 下有独立 metadata.json + env。不设 DATABASE_URL 让 daemon 自管 PG。env 文件中的 HINDSIGHT_API_LLM_API_KEY 必须写实际 key 值否则 daemon 无法启动。
§
飞书 Bot 互通规则：
- 用 @all 比定向 open_id 可靠（飞书 open_id 按应用隔离，跨 app 时接收方匹配不到自己）
- FEISHU_ALLOW_BOTS=mentions 生效；FEISHU_ALLOW_ALL_USERS/FEISHU_GROUP_POLICY 无效
- Gateway：`ps aux|grep gateway`；重启：`hermes --profile X gateway run --replace`
- 群 chat_id=oc_2f222a40
- App ID: default=cli_aabbf18065e11cd3, dev=cli_aabbeea5c379dcb6, pm=cli_aabbe8b5f479dce6, rev=cli_aabbefb068781ce4, tester=cli_aabbef59fcb9dcc7

OpenID 映射（按应用隔离）：Boss=ou_1a0460d0...2739(Rev)/ou_88737568...fbcf, PM=ou_f0c8c556...d092(Rev)/ou_18cd0f78...3c7a(Tester), Tester=ou_50e6f0cb...2b04(Rev)/ou_fb8a1b18...5334(PM)

Scheduler 缺 im:chat:readonly（99991672），开通前 cron 用 @all。⚠️ dev/pm/rev/tester 四 profile secret 均 10014 invalid（2026-06-16），需尽快去飞书后台更新
§
群内输出规范：每次回复只发最终结果和结论，不发中间分析过程。用户要求「只发结果，不发中间过程」。这条规则也适用于所有 Bot。