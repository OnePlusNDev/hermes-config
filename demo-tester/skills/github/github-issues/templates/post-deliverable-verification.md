# Post-Deliverable Verification Template

When verifying a developer claim that "code has been delivered", **do NOT trust comments or reports alone**. Always verify against actual repository state before issuing any verdict.

## The Claim-Verification Gap

The most common delivery discrepancy scenario: developer comment says "merged to main" but repository shows otherwise. This is not theoretical — it happens in real workflows and must be explicitly checked.

### Verification Order (Strict)

1. **Check main branch HEAD** via API:
   ```bash
   gh api repos/OWNER/REPO/contents/TARGET_FILE --jq '.download_url'
   curl -s <url> | base64 -d  # decode content
   ```
   If the claimed function is not present in `main`, it has NOT been merged — regardless of what any comment says.

2. **Check for linked PR** (if claim says "PR submitted"):
   ```bash
   gh pr list --repo OWNER/REPO --search "<issue-number-or-keyword>" --state open
   gh issue view N --repo OWNER/REPO --json pullRequests --jq '.pullRequests[0].url'
   ```

3. **Check git log on main** for commits:
   ```bash
   gh api repos/OWNER/REPO/commits/heads/main --jq '.commit.message'
   ```

4. **Verify tests actually run** by pulling the claimed code and executing them (if available via diff/PR).

5. **Cross-check**: Does `hello.py` exist? Does it contain `add()` or whatever was supposed to be delivered? This is THE decisive check.

## When Claim ≠ Reality

If verification reveals a gap:
- Document precisely what main contains vs what was claimed
- Reference the specific commit SHA or API URL that proves your finding
- Do NOT assume it was "a delay in pushing" — state the fact objectively  
- Include the developer's original claim (ID and content) as evidence

## Verification Checklist per AC Item

```
AC#: [Acceptance Criteria Text]
  ✓ Delivered to main? (Y/N - SHA: XXX)
  ✓ Function/feature exists with correct signature?
  ✓ Tests exist and pass when run? (run: command used)
  ✓ PR open and linked? (PR# if applicable)
  
Result: PASS / FAIL (with evidence)
```

## Comment Template (Chinese for tester role)

Write the comment body to /tmp/ via write_file, then post using `python3 scripts/post-cn-issue-comment.py` from the skills repo. Use this structure:

- 结论：PASS 或 FAIL（明确标注）
- AC对照表（每行对应一个AC，含验证方式和结果证据）
- main分支代码检查（实际内容 vs 声称内容）
- PR关联检查（PR号是否存在且状态正确）
- 测试运行记录（命令+输出摘要）
- 边界/异常补充测试
- 明确判决交回谁

Do NOT write: "已完成" or "看起来没问题". Write exact API query results.
