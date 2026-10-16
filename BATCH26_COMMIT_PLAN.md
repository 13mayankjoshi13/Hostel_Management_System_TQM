# Commit Plan — BUG-007 fix (Batch 26)

```bash
git add app/services/room_service.py app/services/student_service.py
git commit -m "fix: give specific messages when deleting in-use students or rooms (BUG-007)" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -m "Claude-Session: https://claude.ai/code/session_01Y8eJDduXY7659fzRYpFPgg"
git push

git add app/database/log_bugs.py tests/test_bug_fixes.py
git commit -m "test: add regression tests and tracker entry for BUG-007" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -m "Claude-Session: https://claude.ai/code/session_01Y8eJDduXY7659fzRYpFPgg"
git push

git add docs/bugs/BUG-007.md BATCH26_COMMIT_PLAN.md
git commit -m "docs: add BUG-007 find-and-fix write-up" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -m "Claude-Session: https://claude.ai/code/session_01Y8eJDduXY7659fzRYpFPgg"
git push
```
