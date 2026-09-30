import os
import tempfile
import unittest

from backend.database import Database
from backend.services import AuthService


class AuthServiceProfileTests(unittest.TestCase):
    def setUp(self):
        self.db_path = os.path.join(tempfile.gettempdir(), "lumihotel_profile_update_test.db")
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


if __name__ == "__main__":
    unittest.main()
