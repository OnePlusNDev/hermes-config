# 陷阱：SSL_CERT_FILE 被污染 → 全部 curl 路由 HTTP=000

## 症状（2026-11-15 实测）

`pm_fetch.sh` 的四路 curl **全部**返回：

```
  assignee try1 HTTP=000 bytes=0
curl: (77) error setting certificate verify locations:
  CAfile: /private/etc/declare -x TERdeclare -x TELEGRAM_ALLOdeclare -x TEdeclare -x TELEGRAM_REACTIONS=declare declare -x TERMINAL_CONTAINER_CPU=1dedeclare
  CApath: none
```

要点：`HTTP=000` 且 `bytes=0`，**不是**仓库不存在、不是 token 失效、不是 assignee 写错。
curl 连 TLS 握手都没进去，`fetch_best` 四路全 0 → 本轮完全不可判定（既不能 TRIAGE 也不能 SILENT）。

## 根因

会话 shell 里 `SSL_CERT_FILE` 被上一轮某个写坏的 `export` 污染，值里塞了一堆 `declare -x ...` 垃圾，
curl 把它当 CA 文件路径打开，直接 error 77。

## 诊断（10 秒）

```bash
env | grep -iE 'SSL_CERT|CA_BUNDLE|CURL_CA' | cut -c1-200
curl -sS -o /dev/null -w "test=%{http_code}\n" --max-time 15 https://api.github.com/rate_limit
```

## 修复

```bash
unset SSL_CERT_FILE          # 必须在本会话先执行；shell 状态在 terminal 调用间保持
curl -sS -o /dev/null -w "test=%{http_code}\n" --max-time 15 https://api.github.com/rate_limit   # 必须 200 才继续
```

再跑 `pm_fetch.sh`。macOS 上 curl 会用系统 keychain / `/etc/ssl/cert.pem`，unset 后无需再设别的变量。
（若确实需要显式指定：`export SSL_CERT_FILE=/etc/ssl/cert.pem` 或 certifi 的 `cacert.pem`。）

## 判据速查

| 现象 | 结论 |
|------|------|
| 四路全 `HTTP=000 bytes=0` + `curl: (77)` | 环境 CA 变量坏 → `unset SSL_CERT_FILE` |
| `token_len != 40` | token 取值错（KEY 拼接问题），非网络 |
| 单路 `HTTP=000` 其他路 200 | 网络抖动，`fetch_best` 已重试 4 次覆盖 |
| `HTTP=404` + `token_len=0` | token 没取到，不是仓库不存在 |
