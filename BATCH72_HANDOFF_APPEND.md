
## Update – BUG-050 and release (append; do not replace the file)

| Bug | Severity | Summary |
|---|---|---|
| 050 | Critical | Frozen (.exe) runs keep data in `%LOCALAPPDATA%\HostelManagementSystem` (`logs` subfolder for CSV logs); source runs unchanged |

Release: `.github/workflows/release-exe.yml` (tag `v*` → tests → PyInstaller one-file → GitHub Release). Replaces the misnamed `android-release.yml`.
There is no Android/APK build: the app is Tkinter and cannot run on Android.
Total: 51 bug entries. Suite: 262 tests (18 UI tests skip without a display).
