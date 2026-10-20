# Batch 70 – clean .gitignore

The current `.gitignore` begins with `@"` and ends with `"@ | Out-File -Encoding utf8 .gitignore` (a PowerShell command was saved into the file). Its patterns still work by accident, but those two lines and the trailing spaces are junk. Replace the file with the one in this zip.

```
git add .gitignore
git commit -m "chore: clean .gitignore and ignore restore leftovers"
git push
```

Check afterwards: `git status` shows no `hostel.db`, `backups/` or `*.pending` files. None of them are in the repository at the moment.
