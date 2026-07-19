# demo-pm 备份工作流 — 2026-07-17

## 概述
- **方法**: A（rsync + git push）
- **结果**: 成功推送至 `OnePlusNPM/hermes-config`，提交 `c95297a`
- **文件数**: 31 个文件变更（+2229 / -247）

## 发现

### 1. 无明文 API key
`config.yaml` 所有 `api_key` 字段均为空字符串，无 `sk-` 前缀泄露。

### 2. 需手动修复的编码令牌（3 处）
| 文件 | 问题 | 修复 |
|------|------|------|
| `pm-triage-cron/SKILL.md:523` | 完整 hex token `6768705f...` | → `***` |
| `pm-triage-cron/references/2026-07-10-xxd-hexdump-token-extraction.md` | xxd 输出含 hex encoded token + Python hex 字面量 | xxd 字节列全替换为 `2a2a...`，hex 字面量 → `***` |
| `pm-triage-cron/references/2026-07-12-session-base64-token-extraction.md:24` | base64 编码的 `GITHUB_TOKEN=*** | → `***` |

**发现过程：** `find . -name '*.md' | xargs grep -l '676870\|R0lUSFVC'` 遍历所有 `.md` 文件，发现了之前备份已追踪但未修改的文件中遗漏的令牌编码。

**关键教训：** 即使文件之前已推送成功，**修改文件的任何部分**会导致整个 blob 重新上传和扫描。必须扫描被修改文件的 **全部内容**，不能只看 diff。

### 3. 清理的遗留凭据文件（6 个）
通过 `git rm --cached` 从 git 跟踪中移除（不清除磁盘）：
- `demo-pm/home/.config/gh/hosts.yml`
- `demo-pm/home/.config/gh/config.yml`
- `demo-pm/home/.local/state/gh/device-id`
- `demo-pm/bin/tirith`
- `demo-pm/home/.gitconfig`
- `demo-pm/home/fetch_issues.py`

**根因：** 这些文件在一开始添加 rsync exclude 规则之前就被提交了。

### 4. `.gitignore` 模式合并
将 6 个独立的 `**/home/.xxx/` 子模式合并为单个 `**/home/`，简化维护。需要同时更新 rsync 的 `--exclude 'home/'`。

## 命令摘要

```bash
# 安全扫描 — 所有修改过的文件
grep -n '6768705f\|R0lUSFVC\|ghp_[A-Za-z0-9]\{10\}' \
  demo-pm/skills/devops/pm-triage-cron/SKILL.md \
  demo-pm/skills/devops/pm-triage-cron/references/2026-07-10-xxd-hexdump-token-extraction.md

# 扫描整个 diff 确认无泄漏
git diff --cached -- demo-pm/ | grep -nE '6768705f[0-9a-f]|R0lUSFVC|ghp_[A-Za-z0-9]{20}'
```
