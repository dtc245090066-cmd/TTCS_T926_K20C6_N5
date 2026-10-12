import os
import tempfile
import unittest
from unittest.mock import patch

from backend.database import Database
from backend.services import AuthService, normalize_smtp_settings


class AuthServiceProfileTests(unittest.TestCase):
    def setUp(self):
        file_descriptor, self.db_path = tempfile.mkstemp(
            prefix="lumihotel_profile_update_",
            suffix=".db",
        )
        os.close(file_descriptor)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

        self.database = Database(self.db_path)
        self.service = AuthService(self.database)

        sent_codes = []
        with patch(
            "backend.services.send_registration_verification_email",
            side_effect=lambda email, code: sent_codes.append(code) or True,
        ):
            ok, _ = self.service.request_registration_code(
                "Alice Nguyen", "alice@example.com", "Pass1234!"
            )
        self.assertTrue(ok)
        ok, _ = self.service.register("alice@example.com", sent_codes[0])
        self.assertTrue(ok)

        self.user = self.service.login("alice@example.com", "Pass1234!")
        self.assertIsNotNone(self.user)

    def test_update_profile_keeps_email_immutable(self):
        ok, message, profile = self.service.update_profile(
            self.user["id"],
            {
                "full_name": "Alice Updated",
                "birth_date": "1995-01-02",
                "email": "new@email.com",
                "phone": "0909123456",
                "avatar_url": "https://example.com/avatar.png",
            },
        )

        self.assertTrue(ok, message)
        self.assertEqual(profile["email"], "alice@example.com")
        self.assertEqual(profile["full_name"], "Alice Updated")
        self.assertEqual(profile["birth_date"], "1995-01-02")
        self.assertEqual(profile["phone"], "0909123456")
        self.assertEqual(profile["avatar_url"], "https://example.com/avatar.png")

    def test_update_profile_accepts_id_number_phone_name_and_birth_date(self):
        ok, message, profile = self.service.update_profile(
            self.user["id"],
            {
                "full_name": "Alice Nguyen",
                "birth_date": "1995-01-02",
                "id_number": "123456789012",
                "phone": "0909123456",
            },
        )

        self.assertTrue(ok, message)
        self.assertEqual(profile["full_name"], "Alice Nguyen")
        self.assertEqual(profile["birth_date"], "1995-01-02")
        self.assertEqual(profile["id_number"], "123456789012")
        self.assertEqual(profile["phone"], "0909123456")

    def test_change_password_requires_current_and_confirmation(self):
        ok, message = self.service.change_password(
            self.user["id"],
            "Pass1234!",
            "NewPass567!",
            "NewPass567!",
        )

        self.assertTrue(ok, message)
        self.assertIsNotNone(self.service.login("alice@example.com", "NewPass567!"))

        ok, message = self.service.change_password(
            self.user["id"],
            "wrong-password",
            "AnotherPass999!",
            "AnotherPass999!",
        )

        self.assertFalse(ok)
        self.assertIn("Mật khẩu hiện tại", message)

        ok, message = self.service.change_password(
            self.user["id"],
            "NewPass567!",
            "short",
            "different",
        )

        self.assertFalse(ok)
        self.assertIn("mật khẩu mới", message)

    def test_change_password_requires_email_verification_code(self):
        with patch("backend.services.send_password_verification_email", return_value=True):
            ok, message, verification_code = self.service.request_password_change_code("alice@example.com")

        self.assertTrue(ok, message)
        self.assertTrue(verification_code and verification_code.isdigit() and len(verification_code) == 6)

        ok, message = self.service.change_password(
            None,
            "Pass1234!",
            "VerifiedPass777!",
            "VerifiedPass777!",
            email="alice@example.com",
            verification_code="000000",
        )

        self.assertFalse(ok)
        self.assertIn("mã xác minh", message.lower())

        ok, message = self.service.change_password(
            None,
            "Pass1234!",
            "VerifiedPass777!",
            "VerifiedPass777!",
            email="alice@example.com",
            verification_code=verification_code,
        )

        self.assertTrue(ok, message)
        self.assertIsNotNone(self.service.login("alice@example.com", "VerifiedPass777!"))

    def test_request_password_change_code_fails_without_smtp_configuration(self):
        with patch.dict(os.environ, {
            "SMTP_EMAIL": "",
            "SMTP_USERNAME": "",
            "SMTP_PASSWORD": "",
        }):
            ok, message, verification_code = self.service.request_password_change_code("alice@example.com")

        self.assertFalse(ok)
        self.assertIsNone(verification_code)
        self.assertIn("Không thể gửi", message)

    def test_normalize_smtp_settings_removes_spaces_from_app_password(self):
        with patch.dict(os.environ, {"SMTP_EMAIL": "sender@example.com", "SMTP_PASSWORD": "jvrv vpmc jhfy qycv"}):
            settings = normalize_smtp_settings()
        self.assertEqual(settings["password"], "jvrvvpmcjhfyqycv")
        self.assertEqual(settings["username"], "sender@example.com")


if __name__ == "__main__":
    unittest.main()
