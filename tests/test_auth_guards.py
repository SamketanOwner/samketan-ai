"""Regression checks for the two previously removed fail-open login paths.

These are static source checks, not an end-to-end authentication audit.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AuthenticationGuardTests(unittest.TestCase):
    def test_no_import_error_auth_bypass(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertNotIn("class _FallbackAuth:", app)
        self.assertIn("import auth  # Fail closed", app)

    def test_no_cookie_based_automatic_authentication(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertNotIn('saved_user = cookie_manager.get("samketan_user")', app)
        self.assertIn("if not auth.login_screen():", app)


if __name__ == "__main__":
    unittest.main()
