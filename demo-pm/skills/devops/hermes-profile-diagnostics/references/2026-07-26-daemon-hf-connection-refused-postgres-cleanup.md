# 2026-07-26 — Hindsight Daemon HF Connection Refused + Postgres Cleanup

## 场景

Cron 内存清理任务尝试启动 `hindsight-embed -p demo-pm daemon start`，失败。

## 错误链

### 1. Embedding 模型下载被拒

```
HEAD https://huggingface.co/BAAI/bge-small-en-v1.5/resolve/main/adapter_config.json
→ '[Errno 61] Connection refused'

WARNING - huggingface_hub.utils._http - Retrying in 1s [Retry 1/5].
```

### 2. 客户端关闭导致 Application startup failed

```
File "httpx/_client.py", line 901, in send
    raise RuntimeError("Cannot send a request, as the client has been closed.")
RuntimeError: Cannot send a request, as the client has been closed.

ERROR:    Application startup failed. Exiting.
```

### 3. PG 清理时产生无害错误

```
Error stopping pg0: Failed to stop PostgreSQL: cannot schedule new futures after interpreter shutdown
```

## 与已知 HF 超时模式的区别

| 特征 | 本模式 | 已记载的 HF 超时模式 |
|------|--------|-------------------|
| 错误类型 | `Connection refused` (Errno 61) | `Model/connection initialization did not complete within 300s` |
| 阶段 | 模型元数据 HEAD 请求 | 完整模型下载/加载 |
| 根因 | HF.co 完全不可达（网络/防火墙） | SSL 握手超时或下载速度过低 |
| 解决 | `HF_HUB_OFFLINE=1` 通用 | `HF_HUB_OFFLINE=1` 或 `HF_ENDPOINT=https://hf-mirror.com` |

## 残留进程清理

Hindsight daemon 启动失败后，嵌入式 PostgreSQL (`pg0`) 的子进程可能残留：

```bash
# 检查残留
ps aux | grep pg0

# 清理（使用 `kill` 而非 `kill -9` 以让 PG 完成安全关闭）
ps aux | grep pg0 | grep -v grep | awk '{print $2}' | xargs kill

# 验证清理
ps aux | grep pg0 | grep -v grep || echo "cleaned"
```

**不要用 `kill -9`** — 强制终止 PG 可能导致锁文件残留，影响下次启动。

## 正确启动命令

```bash
# hindsight-embed 是正确入口（非 hindsight CLI）
hindsight-embed -p <profile> daemon start
```

`hindsight` CLI 没有 `daemon` 子命令。`hindsight-embed` 是嵌入式 daemon 管理的专用工具。
