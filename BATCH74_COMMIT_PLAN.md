# Batch 74 – Fines with Razorpay test payments and receipts; workers module

```
git add app/database/db.py app/utils/validation.py
git commit -m "feat: fines, workers and attendance tables; fine amount and worker validators"

git add app/services/razorpay_client.py app/services/fine_service.py app/services/student_portal_service.py
git commit -m "feat: fines with Razorpay Payment Link payments, cash payment, waiver and receipts"

git add app/services/worker_service.py
git commit -m "feat: worker registry, daily attendance and workload"

git add app/screens/fine_screen.py app/screens/my_fines_screen.py app/screens/worker_screen.py app/screens/complaint_screen.py app/screens/main_window.py app/theme.py
git commit -m "feat: Fines, My Fines and Workers screens; assign complaints to registered workers"

git add tests/test_fines.py tests/test_workers.py tests/test_fine_worker_screens_ui.py
git commit -m "test: cover fines, online payment verification, receipts, workers and the new screens"

git add docs/RAZORPAY_SETUP.md BATCH74_COMMIT_PLAN.md BATCH74_HANDOFF_APPEND.md
git commit -m "docs: Razorpay test-mode setup and handoff update"

git push
```

Set the Razorpay test keys as environment variables first (see `docs/RAZORPAY_SETUP.md`). Never commit keys.
After pulling, append `BATCH74_HANDOFF_APPEND.md` to `AI_CONTEXT_HANDOFF.md`.
