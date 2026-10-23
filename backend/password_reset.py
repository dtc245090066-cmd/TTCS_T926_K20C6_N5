import hashlib
import os
import re
import secrets
import smtplib
import ssl
import time
from contextlib import closing
from email.message import EmailMessage
from urllib.parse import urlsplit

from werkzeug.security import generate_password_hash


RECOVERY_MESSAGE = "Nếu email thuộc tài khoản hợp lệ, hướng dẫn khôi phục sẽ được gửi đến email của bạn."
INVALID_LINK = "Liên kết không hợp lệ hoặc đã hết hạn. Vui lòng yêu cầu liên kết mới."


def send_password_reset_email(email, token):
    # Use a configured origin, never the untrusted request Host header.
    origin = os.environ.get("APP_BASE_URL", "http://127.0.0.1:5000").rstrip("/")
    parsed = urlsplit(origin)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False
    username = os.environ.get("SMTP_EMAIL", "").strip()
    password = os.environ.get("SMTP_PASSWORD", "").replace(" ", "")
    if not username or not password:
        return False
    message = EmailMessage()
    message["Subject"] = "Khôi phục mật khẩu LumiHotel"
    message["From"] = os.environ.get("SMTP_FROM") or username
    message["To"] = email
    message.set_content(
        f"Mở liên kết sau để đặt lại mật khẩu: {origin}/#reset-password={token}\n\n"
        "Liên kết chỉ dùng một lần và hết hạn sau 15 phút. "
        "Nếu bạn không yêu cầu khôi phục, hãy bỏ qua email này."
    )
    try:
        with smtplib.SMTP(os.environ.get("SMTP_HOST", "smtp.gmail.com"),
                          int(os.environ.get("SMTP_PORT", "587")), timeout=15) as server:
            server.starttls(context=ssl.create_default_context())
            server.login(username, password)
            server.send_message(message)
        return True
    except (OSError, ValueError, smtplib.SMTPException):
        return False


class PasswordResetService:
    def __init__(self, database):
        self.database = database

    def allow(self, action, identity, maximum):
        bucket = hashlib.sha256(f"{action}:{identity}".encode()).hexdigest()
        now = time.time()
        with closing(self.database.connect()) as connection, connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("DELETE FROM password_reset_limits WHERE started_at <= ?", (now - 3600,))
            connection.execute("INSERT OR IGNORE INTO password_reset_limits VALUES (?, ?, 0)", (bucket, now))
            row = connection.execute("SELECT attempts FROM password_reset_limits WHERE bucket = ?", (bucket,)).fetchone()
            if row["attempts"] >= maximum:
                return False
            connection.execute("UPDATE password_reset_limits SET attempts = attempts + 1 WHERE bucket = ?", (bucket,))
        return True

    def request_reset(self, email, address):
        if not self.allow("request-ip", address, 20):
            return False, "Bạn đã gửi quá nhiều yêu cầu. Vui lòng thử lại sau một giờ.", 429
        if not isinstance(email, str) or len(email) > 254 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()):
            return False, "Vui lòng nhập email hợp lệ.", 400
        email = email.strip().lower()
        if not self.allow("request-email", email, 5):
            return True, RECOVERY_MESSAGE, 200
        token = secrets.token_urlsafe(32)
        digest = hashlib.sha256(token.encode()).hexdigest()
        with closing(self.database.connect()) as connection, connection:
            connection.execute("DELETE FROM password_resets WHERE expires_at <= ?", (time.time(),))
            user = connection.execute("SELECT id, email, password_hash FROM users WHERE LOWER(email) = ?", (email,)).fetchone()
            if user is not None:
                connection.execute("INSERT INTO password_resets VALUES (?, ?, ?, ?)",
                                   (digest, user["id"], user["password_hash"], time.time() + 900))
        if user is not None and not send_password_reset_email(user["email"], token):
            with closing(self.database.connect()) as connection, connection:
                connection.execute("DELETE FROM password_resets WHERE token_hash = ?", (digest,))
        return True, RECOVERY_MESSAGE, 200

    def reset(self, token, password, confirmation, address, verify_only=False):
        if not self.allow("verify-ip", address, 30):
            return False, "Bạn đã thử quá nhiều lần. Vui lòng thử lại sau một giờ.", 429
        if not isinstance(token, str) or not re.fullmatch(r"[A-Za-z0-9_-]{43}", token):
            return False, INVALID_LINK, 400
        digest = hashlib.sha256(token.encode()).hexdigest()
        with closing(self.database.connect()) as connection, connection:
            connection.execute("BEGIN IMMEDIATE")
            record = connection.execute(
                "SELECT r.user_id FROM password_resets r JOIN users u ON u.id = r.user_id "
                "WHERE r.token_hash = ? AND r.expires_at > ? AND r.password_hash = u.password_hash",
                (digest, time.time()),
            ).fetchone()
            if record is None:
                return False, INVALID_LINK, 400
            if verify_only:
                return True, "Liên kết hợp lệ. Vui lòng nhập mật khẩu mới.", 200
            if not isinstance(password, str) or not password.strip() or not 8 <= len(password) <= 128:
                return False, "Mật khẩu mới phải có từ 8 đến 128 ký tự.", 400
            if password != confirmation:
                return False, "Mật khẩu xác nhận không khớp.", 400
            connection.execute("UPDATE users SET password_hash = ? WHERE id = ?",
                               (generate_password_hash(password), record["user_id"]))
            connection.execute("DELETE FROM password_resets WHERE user_id = ?", (record["user_id"],))
        return True, "Đặt lại mật khẩu thành công. Bạn có thể đăng nhập bằng mật khẩu mới.", 200
