# Commit Plan — User Management (Batch 10)

```bash
git add app/services/auth_service.py
git commit -m "feat: add list_users, change_password and delete_user with last-admin and self-delete guards" -m "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -m "Claude-Session: https://claude.ai/code/session_01Y8eJDduXY7659fzRYpFPgg"
git push

git add app/screens/user_screen.py
git commit -m "feat: add User Management screen"
git push

git add app/screens/main_window.py
git commit -m "feat: add admin-only User Management navigation"
git push

git add tests/test_auth.py
git commit -m "test: add module tests for user management (Q09)"
git push

git add BATCH10_README.md BATCH10_COMMIT_PLAN.md AI_CONTEXT_HANDOFF.md
git commit -m "docs: add Batch 10 docs and update AI handoff"
git push
```
