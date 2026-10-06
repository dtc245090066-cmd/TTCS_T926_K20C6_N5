import os
import tempfile
import unittest

from backend.database import Database
from backend.services import AuthService


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

        ok, _ = self.service.register("Alice Nguyen", "alice@example.com", "Pass1234!")
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


if __name__ == "__main__":
    unittest.main()
