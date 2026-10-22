import gc
import importlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from werkzeug.security import check_password_hash

from backend.database import Database
from backend.services import AuthService


class RegistrationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="lumihotel_registration_")
        self.database = Database(Path(self.directory.name) / "test.db")
        self.service = AuthService(self.database)
        # Import the Flask application against an isolated database, never real data.
        with patch.dict(os.environ, {"DATABASE_PATH": str(self.database.path)}):
            self.module = importlib.import_module("app")
        self.service_patch = patch.object(self.module, "auth_service", self.service)
        self.service_patch.start()
        self.client = self.module.app.test_client()
        self.payload = {"full_name": "Alice Nguyen", "email": "alice@example.com", "password": "Pass1234!"}

    def tearDown(self):
        self.service_patch.stop()
        gc.collect()
        self.directory.cleanup()

    def test_direct_registration_hash_login_profile_and_logout_without_email(self):
        with patch("smtplib.SMTP", side_effect=AssertionError("Registration must not send email")) as smtp:
            response = self.client.post("/api/register", json=self.payload)
        smtp.assert_not_called()
        self.assertEqual(response.status_code, 201)
        with self.database.connect() as connection:
            user = connection.execute("SELECT * FROM users WHERE email = ?", (self.payload["email"],)).fetchone()
        self.assertNotEqual(user["password_hash"], self.payload["password"])
        self.assertTrue(check_password_hash(user["password_hash"], self.payload["password"]))
        self.assertEqual(user["role"], "staff")
        response = self.client.post("/api/login", json=self.payload)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("password_hash", response.get_json()["user"])
        self.assertEqual(self.client.get("/api/profile").status_code, 200)
        self.assertEqual(self.client.post("/api/logout").status_code, 200)
        self.assertIsNone(self.client.get("/api/session").get_json()["user"])

    def test_duplicate_email_is_case_insensitive(self):
        self.assertEqual(self.client.post("/api/register", json=self.payload).status_code, 201)
        response = self.client.post("/api/register", json={**self.payload, "email": " ALICE@EXAMPLE.COM "})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["message"], "Email này đã được đăng ký.")

    def test_invalid_fields_do_not_create_users(self):
        cases = [(field, value) for field in self.payload for value in ("", "   ", None, [])]
        cases += [("email", "invalid"), ("email", "a@b"), ("password", "short"), ("password", "x" * 129), ("full_name", "x" * 121)]
        with self.database.connect() as connection:
            before = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        for field, value in cases:
            with self.subTest(field=field, value=value):
                response = self.client.post("/api/register", json={**self.payload, field: value})
                self.assertEqual(response.status_code, 400)
                self.assertTrue(response.get_json()["message"])
        for field in self.payload:
            self.assertEqual(self.client.post("/api/register", json={k: v for k, v in self.payload.items() if k != field}).status_code, 400)
        self.assertEqual(self.client.post("/api/register", json=["invalid"]).status_code, 400)
        with self.database.connect() as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM users").fetchone()[0], before)

    def test_logged_in_password_change_still_works(self):
        self.client.post("/api/register", json=self.payload)
        self.client.post("/api/login", json=self.payload)
        response = self.client.post("/api/profile/password", json={
            "email": self.payload["email"], "current_password": self.payload["password"],
            "new_password": "NewPass123!", "confirm_password": "NewPass123!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.post("/api/login", json={**self.payload, "password": "NewPass123!"}).status_code, 200)

    def test_registration_page_has_no_otp_and_keeps_password_toggle(self):
        page = self.client.get("/").get_data(as_text=True)
        self.assertIn('id="registerSubmitBtn" type="submit">Tạo tài khoản</button>', page)
        self.assertIn('data-target="registerPassword"', page)
        for removed in ("registerVerification", "registerResend", "Gửi mã xác minh"):
            self.assertNotIn(removed, page)


if __name__ == "__main__":
    unittest.main()
