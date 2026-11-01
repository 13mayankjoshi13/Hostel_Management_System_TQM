"""Settings screen and live theme switching. Skipped when no display is available."""
import os
import tempfile
import unittest
import tkinter as tk


class TestSettingsUI(unittest.TestCase):

    def setUp(self):
        self.ready = False
        try:
            tk.Tk().destroy()
        except tk.TclError:
            self.skipTest("no display available")
        self.tmp = tempfile.mkdtemp()
        import app.config as config
        import app.database.db as db_module
        import app.utils.logging_service as ls

        self._original = (config.DATABASE_PATH, db_module.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV)
        config.DATABASE_PATH = db_module.DATABASE_PATH = os.path.join(self.tmp, "t.db")
        ls.ERROR_LOG_CSV = os.path.join(self.tmp, "e.csv")
        ls.AUDIT_LOG_CSV = os.path.join(self.tmp, "a.csv")
        db_module.initialize_database(config.DATABASE_PATH)
        from app.screens.main_window import MainWindow

        self.window = MainWindow(show_splash=False)
        for child in self.window.winfo_children():
            if child.winfo_class() == "Toplevel":
                child.destroy()
        self.ready = True

    def tearDown(self):
        if not self.ready:
            return
        import app.config as config
        import app.database.db as db_module
        import app.utils.logging_service as ls
        from app import theme
        from app.utils import session

        session.clear_session()
        self.window.destroy()
        theme.set_appearance("Light", theme.DEFAULT_ACCENT)
        config.DATABASE_PATH, db_module.DATABASE_PATH, ls.ERROR_LOG_CSV, ls.AUDIT_LOG_CSV = self._original

    def _log_in(self, username, role):
        from app.utils import session

        session.set_session(username, role)
        self.window._user = {"username": username, "role": role}
        self.window._enter_user_ui(self.window._user)

    def test_admin_sees_all_tabs_and_staff_only_appearance(self):
        self._log_in("boss", "Administrator")
        self.assertEqual(set(self.window.screens["Settings"].pages), {"appearance", "audit", "data", "quality"})
        self.assertNotIn("Quality", self.window.screens)
        self._log_in("sam", "Staff")
        self.assertEqual(set(self.window.screens["Settings"].pages), {"appearance"})

    def test_applying_dark_theme_rebuilds_the_window_and_persists(self):
        from app import theme
        from app.services import settings_service

        self._log_in("boss", "Administrator")
        settings = self.window.screens["Settings"]
        settings.mode_var.set("Dark")
        settings.accent_var.set("#D6336C")
        settings.on_apply()
        self.assertEqual(theme.current_appearance(), ("Dark", "#D6336C"))
        self.assertEqual(theme.COLORS["background"], "#12141C")
        self.assertEqual(self.window.screens["Settings"].mode_var.get(), "Dark")
        self.assertEqual(settings_service.get_appearance("boss"), ("Dark", "#D6336C"))
        for key in ("Dashboard", "Students", "Settings"):
            self.window.show_screen(key)
        self.window.screens["Settings"].show_tab("audit")
        self.window.screens["Settings"].show_tab("quality")

    def test_bad_colour_is_rejected_and_theme_unchanged(self):
        from unittest import mock
        from app import theme

        self._log_in("boss", "Administrator")
        settings = self.window.screens["Settings"]
        settings.accent_var.set("#FFFFCC")
        with mock.patch("app.screens.settings_screen.messagebox.showerror") as shown:
            settings.on_apply()
        shown.assert_called_once()
        self.assertEqual(theme.current_appearance(), ("Light", theme.DEFAULT_ACCENT))


if __name__ == "__main__":
    unittest.main()
