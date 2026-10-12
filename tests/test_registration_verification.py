import io
import gc
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from backend.database import Database
from backend.services import (
    AuthService,
    REGISTRATION_VERIFICATION_CODES,
    send_registration_verification_email,
)


class RegistrationVerificationTests(unittest.TestCase):
    def setUp(self):
        file_descriptor, self.db_path = tempfile.mkstemp(
            prefix="lumihotel_registration_verification_",
            suffix=".db",
        )
        os.close(file_descriptor)
        os.remove(self.db_path)
        self.database = Database(self.db_path)
        self.service = AuthService(self.database)
        self.sent = []
        self.sender_patch = patch(
            "backend.services.send_registration_verification_email",
            side_effect=lambda recipient, code: self.sent.append((recipient, code)) or True,
        )
        self.sender_patch.start()
        self.addCleanup(self.sender_patch.stop)
        self.addCleanup(self._remove_database)

    def _remove_database(self):
        self.service = None
        self.database = None
        gc.collect()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_codes_are_sent_to_and_bound_to_each_registration_email(self):
        self.assertTrue(self.service.request_registration_code("Alice", "alice@example.com", "Pass1234!")[0])
        self.assertTrue(self.service.request_registration_code("Bob", "bob@example.com", "Pass5678!")[0])
        self.assertEqual([recipient for recipient, _ in self.sent], [
            "alice@example.com",
            "bob@example.com",
        ])

        alice_code = self.sent[0][1]
        bob_code = self.sent[1][1]
        self.assertFalse(self.service.register("bob@example.com", alice_code)[0])
        self.assertTrue(self.service.register("alice@example.com", alice_code)[0])
        self.assertFalse(self.service.register("alice@example.com", alice_code)[0])
        self.assertTrue(self.service.register("bob@example.com", bob_code)[0])
        self.assertIsNotNone(self.service.login("alice@example.com", "Pass1234!"))
        self.assertIsNotNone(self.service.login("bob@example.com", "Pass5678!"))

    def test_registration_code_expires_after_five_minutes(self):
        self.assertTrue(self.service.request_registration_code("Alice", "alice@example.com", "Pass1234!")[0])
        expires_at = REGISTRATION_VERIFICATION_CODES["alice@example.com"]["expires_at"]
        with patch("backend.services.time.time", return_value=expires_at + 1):
            ok, message = self.service.register("alice@example.com", self.sent[0][1])

        self.assertFalse(ok)
        self.assertIn("hết hạn", message.lower())
        self.assertIsNone(self.service.login("alice@example.com", "Pass1234!"))

    def test_smtp_uses_configured_sender_and_registration_recipient_without_logging_secrets(self):
        output = io.StringIO()
        with patch.dict(os.environ, {
            "SMTP_EMAIL": "sender@example.com",
            "SMTP_PASSWORD": "smtp-secret-value",
            "SMTP_HOST": "smtp.example.com",
            "SMTP_PORT": "587",
        }), patch("backend.services.smtplib.SMTP") as smtp_class, redirect_stdout(output):
            sent = send_registration_verification_email("recipient@example.com", "123456")

        message = smtp_class.return_value.__enter__.return_value.send_message.call_args.args[0]
        self.assertTrue(sent)
        self.assertEqual(message["To"], "recipient@example.com")
        self.assertEqual(smtp_class.return_value.__enter__.return_value.login.call_args.args[0], "sender@example.com")
        self.assertNotIn("smtp-secret-value", output.getvalue())
        self.assertNotIn("123456", output.getvalue())

    def test_failed_smtp_send_does_not_print_code_or_password(self):
        self.sender_patch.stop()
        output = io.StringIO()
        with patch.dict(os.environ, {
            "SMTP_EMAIL": "sender@example.com",
            "SMTP_PASSWORD": "smtp-secret-value",
            "SMTP_HOST": "smtp.example.com",
            "SMTP_PORT": "587",
        }), patch("backend.services.smtplib.SMTP", side_effect=RuntimeError("send failed")), redirect_stdout(output):
            ok, _ = self.service.request_registration_code("Alice", "alice@example.com", "Pass1234!")

        self.assertFalse(ok)
        self.assertEqual(output.getvalue(), "")


if __name__ == "__main__":
    unittest.main()