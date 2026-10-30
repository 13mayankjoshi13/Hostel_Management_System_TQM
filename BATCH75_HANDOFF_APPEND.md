
## Update – login panels (append; do not replace the file)

`auth_service.LOGIN_PANELS` = Student → Student; Staff → Warden, Staff; Administrator → Administrator. `authenticate(username, password, panel=None)`: the panel is checked only after the password is verified, so a wrong password on any panel gives the same generic message; a correct password on the wrong panel is refused with a pointer to the right tab (audit `LoginWrongPanel`) and starts no session. `panel=None` keeps the old behaviour for scripts and tests.
`LoginScreen` has Student / Staff / Administrator tabs; sign-up link shows on Student only, the first-run admin hint on Administrator only.
Panels are a convenience: real access control remains in the services (`require_roles`, `require_own_or_staff`). Suite: 278 tests.
