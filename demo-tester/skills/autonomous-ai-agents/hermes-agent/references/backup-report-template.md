# Backup Report Template

Use this structure when outputting the backup summary at the end of a backup run.

```
## 🔌 <profile-name> 配置备份完成

**仓库**: `<owner>/<repo>` (private)
**时间**: <UTC timestamp>
**认证**: gh CLI (user: `<github-user>`)

---

### 备份内容

| 文件 | 大小 | SHA | 变更 |
|------|------|-----|------|
| `SOUL.md` | N bytes | `sha8` | 未变/已更新 — <brief description> |
| `cron/jobs.json` | N bytes | `sha8` | 未变/已更新 — <brief description> |
| `memories/MEMORY.md` | N bytes | `sha8` | 未变/已更新 — <brief description> |
| `skills/skills_index.txt` | N bytes | `sha8` | 未变/已更新 — N个技能 |

---

### Cron 任务状态

| 任务 | 调度 | 完成次数 |
|------|------|----------|
| `<name>` | `<schedule>` | N 次 |

---

### 本次变更说明

- List significant changes detected between current and previous backup
- Note skill count changes, cron config modifications, memory additions
- Flag files that remained unchanged (same SHA)
```

## Verification Checklist

After pushing, confirm:

- [ ] All 4 files exist in repo via `gh api repos/$REPO/contents/`
- [ ] Latest commit message has correct timestamp
- [ ] SHAs match expected values (compare with local files)
- [ ] Skills count in skills_index.txt matches `find ... -name 'SKILL.md' | wc -l`
- [ ] No files are 0 bytes (empty push)
- [ ] Cron jobs.json is valid JSON
