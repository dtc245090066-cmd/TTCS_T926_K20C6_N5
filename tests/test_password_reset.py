import gc
import importlib
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.database import Database
from backend.services import AuthService
from backend.password_reset import PasswordResetService, send_password_reset_email


class PasswordResetTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="lumihotel_recovery_")
        self.database = Database(Path(self.directory.name) / "test.db")
        self.auth = AuthService(self.database)
        self.auth.register("Alice", "alice@example.com", "OldPass123!")
        self.service = PasswordResetService(self.database)
        with patch.dict(os.environ, {"DATABASE_PATH": str(self.database.path)}):
            self.module = importlib.import_module("app")
        self.patches = [patch.object(self.module, "auth_service", self.auth),
                        patch.object(self.module, "password_reset_service", self.service),
                        patch("backend.password_reset.send_password_reset_email", return_value=True)]
        for item in self.patches:
            item.start()
        self.sender = self.patches[-1].target.send_password_reset_email
        self.client = self.module.app.test_client()

    def tearDown(self):
        for item in reversed(self.patches):
            item.stop()
        gc.collect()
        self.directory.cleanup()

    def request_token(self):
        self.assertEqual(self.client.post("/api/password/forgot", json={"email": "alice@example.com"}).status_code, 200)
        return self.sender.call_args.args[1]

    def reset(self, token, password="NewPass123!", confirmation="NewPass123!"):
        return self.client.post("/api/password/reset", json={"token": token, "password": password, "confirmation": confirmation})

    def test_email_validation_and_identical_public_responses(self):
        self.assertEqual(self.client.post("/api/password/forgot", json={"email": "bad"}).status_code, 400)
        missing = self.client.post("/api/password/forgot", json={"email": "missing@example.com"})
        self.sender.assert_not_called()
        known = self.client.post("/api/password/forgot", json={"email": "alice@example.com"})
        self.assertEqual(missing.get_json(), known.get_json())
        self.assertEqual(missing.status_code, known.status_code)

    def test_success_hash_one_use_and_login(self):
        token = self.request_token()
        with self.database.connect() as connection:
            self.assertNotEqual(connection.execute("SELECT token_hash FROM password_resets").fetchone()[0], token)
        self.assertEqual(self.client.post("/api/password/verify", json={"token": token}).status_code, 200)
        self.assertEqual(self.reset(token).status_code, 200)
        self.assertEqual(self.reset(token).status_code, 400)
        self.assertIsNone(self.auth.login("alice@example.com", "OldPass123!"))
        self.assertEqual(self.client.post("/api/login", json={"email": "alice@example.com", "password": "NewPass123!"}).status_code, 200)

    def test_invalid_expired_link_and_email_only_cannot_reset(self):
        token = self.request_token()
        self.assertEqual(self.reset("A" * 43).status_code, 400)
        self.assertEqual(self.reset(None).status_code, 400)
        with patch("backend.password_reset.time.time", return_value=time.time() + 901):
            self.assertEqual(self.reset(token).status_code, 400)
        self.assertIsNotNone(self.auth.login("alice@example.com", "OldPass123!"))

    def test_password_validation_preserves_link(self):
        token = self.request_token()
        for password in ("short", " " * 8, "x" * 129, None):
            self.assertEqual(self.reset(token, password, password).status_code, 400)
        self.assertEqual(self.reset(token, "NewPass123!", "different").status_code, 400)
        self.assertEqual(self.reset(token).status_code, 200)

    def test_rate_limits_persist_across_service_instances(self):
        for _ in range(6):
            self.service.request_reset("alice@example.com", "one-ip")
        self.assertEqual(self.sender.call_count, 5)
        other_service = PasswordResetService(self.database)
        for _ in range(20):
            result = other_service.request_reset("missing@example.com", "one-ip")
        self.assertEqual(result[2], 429)
        for _ in range(31):
            result = other_service.reset("bad", "", "", "one-ip")
        self.assertEqual(result[2], 429)

    def test_mail_failure_does_not_leak_account_or_leave_token(self):
        self.sender.return_value = False
        known = self.client.post("/api/password/forgot", json={"email": "alice@example.com"})
        missing = self.client.post("/api/password/forgot", json={"email": "missing@example.com"})
        self.assertEqual(known.get_json(), missing.get_json())
        with self.database.connect() as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM password_resets").fetchone()[0], 0)

    def test_profile_requires_login_and_password_change_invalidates_reset(self):
        token = self.request_token()
        payload = {"current_password": "OldPass123!", "new_password": "Changed123!", "confirm_password": "Changed123!"}
        self.assertEqual(self.client.post("/api/profile/password", json=payload).status_code, 401)
        self.client.post("/api/login", json={"email": "alice@example.com", "password": "OldPass123!"})
        self.assertEqual(self.client.post("/api/profile/password", json=payload).status_code, 200)
        self.assertEqual(self.reset(token).status_code, 400)

    def test_smtp_transport_uses_tls_and_configured_origin(self):
        with patch.dict(os.environ, {"SMTP_EMAIL": "sender@example.com", "SMTP_PASSWORD": "app-password", "APP_BASE_URL": "https://hotel.example.com"}), patch("backend.password_reset.smtplib.SMTP") as smtp:
            self.assertTrue(send_password_reset_email("alice@example.com", "test-token"))
            server = smtp.return_value.__enter__.return_value
            server.starttls.assert_called_once()
            message = server.send_message.call_args.args[0]
            self.assertEqual(message["To"], "alice@example.com")
            self.assertIn("https://hotel.example.com/#reset-password=test-token", message.get_content())

    def test_recovery_form_only_asks_for_email(self):
        page = self.client.get("/").get_data(as_text=True)
        form = page.split('<form id="forgotPasswordForm">', 1)[1].split('</form>', 1)[0]
        self.assertEqual(form.count('<input '), 1)
        self.assertIn('type="email"', form)
        self.assertNotIn('password-toggle', form)
        self.assertIn('Đặt lại mật khẩu', form)
        self.assertIn('<form id="passwordForm">', page)
        self.assertIn('id="resetPasswordForm" class="hidden"', page)


if __name__ == "__main__":
    unittest.main()
