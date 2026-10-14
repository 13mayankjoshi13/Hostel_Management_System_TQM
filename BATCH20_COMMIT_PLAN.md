# Commit Plan — BUG-001 fix (Batch 20)

```bash
git add app/utils/validation.py app/services/room_service.py
git commit -m "fix: reject room type and capacity mismatch (BUG-001)" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -m "Claude-Session: https://claude.ai/code/session_01Y8eJDduXY7659fzRYpFPgg"
git push

git add app/database/log_bugs.py tests/test_bug_fixes.py
git commit -m "test: add bug loader and regression tests for BUG-001" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -m "Claude-Session: https://claude.ai/code/session_01Y8eJDduXY7659fzRYpFPgg"
git push

git add docs/bugs/BUG-001.md BATCH20_COMMIT_PLAN.md
git commit -m "docs: add BUG-001 find-and-fix write-up" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -m "Claude-Session: https://claude.ai/code/session_01Y8eJDduXY7659fzRYpFPgg"
git push
```
