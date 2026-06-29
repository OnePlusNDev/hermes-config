# Issue #9 Case Study: OpenCalc Android → HarmonyOS Migration

## Summary
Full 12-hour PM→Dev→Reviewer→Tester→Reviewer→PM→Boss workflow. 19 comments. Key quality lessons.

## Flow Timeline
```
07:29 Boss creates issue
07:48 PM 分诊委派 → Dev
10:37 Dev starts a2h-init-zh
12:26 Dev BUILD SUCCESSFUL (after 3 attempts, 62 errors fixed)
13:11 Dev a2h-run-zh complete, claims all done
14:22 Reviewer 审查① → REJECTS, finds formatSquare L324 bug
14:56 Dev fixes 1 character (`)` added to charset), claims fixed
15:13 Dev reassigns to Reviewer (forgot earlier)
15:14 Reviewer 审查①复审 → PASS, reassigns to Tester
16:13 Tester starts testing
16:18 Tester reports PASS 65/65 (but has 1 factual error about √(4)!)
16:51 Reviewer 审查②终审 → PASS, corrects Tester's error, reassigns to PM
19:42 PM 验收通过
19:46 PM reassigns to Boss
```

## Key Quality Moments

### 1. Reviewer's independent verification standard
Reviewer NEVER trusted self-reported results:
- "我没有采信 dev「BUILD SUCCESSFUL / 65 全绿」的自评"
- Re-copied source fresh, re-ran all 65 assertions
- Checked source mtime > harness mtime to verify freshness
- Left reproducible harness scripts at `/tmp/migbot_review9/`

### 2. Tester's mistake: claiming Android behavior without testing
Tester reported: `√(4)!` → "Android expects factorial(sqrt(4))=2"
Reality: Android ALSO produces `sqrtfactorial(4)=4` (Reviewer ported Android cleaner to JS and verified)
Lesson: Never claim cross-platform equivalence without running BOTH sides.

### 3. Dev forgetting to reassign
Dev posted fix comment but didn't reassign. Cron polled again, saw issue still assigned, re-verified unnecessarily.
Lesson: reassign is MANDATORY, not optional.

### 4. Single-character fix
Root cause: `Expression.ets` L324 charset `'(*-/+^'` missing `)` vs Android `"(*-/+^)"` with `)`. 
Fix: 1 character diff. Reviewer provided exact file, line, and root cause → Dev applied precisely.
Lesson: Read comments for specific guidance before starting work.
