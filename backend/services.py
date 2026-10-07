from __future__ import annotations

import math
import os
import random
import re
import smtplib
import sqlite3
import threading
import time
from datetime import date, datetime
from email.message import EmailMessage
from typing import Any

from werkzeug.security import check_password_hash, generate_password_hash

from backend.database import Database


class AuthService:
    def __init__(self, database: Database) -> None:
        self.database = database

    def login(self, email: str, password: str) -> dict[str, Any] | None:
        if not isinstance(email, str) or not isinstance(password, str):
            return None

        normalized_email = email.strip().lower()
        if not normalized_email or not password.strip():
            return None

        with self.database.connect() as connection:
            user = connection.execute(
                """
                SELECT id, full_name, email, password_hash, role, birth_date, phone, avatar_url
                FROM users
                WHERE LOWER(email) = ?
                """,
                (normalized_email,),
            ).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            return None

        return {
            "id": user["id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "role": user["role"],
            "birth_date": user["birth_date"],
            "phone": user["phone"],
            "avatar_url": user["avatar_url"],
        }

    def get_profile(self, user_id: int) -> dict[str, Any] | None:
        with self.database.connect() as connection:
            user = connection.execute(
                """
                SELECT id, full_name, email, role, birth_date, phone, avatar_url
                FROM users
                WHERE id = ?
                """,
                (user_id,),
            ).fetchone()

        if user is None:
            return None

        return dict(user)

    def update_profile(self, user_id: int, payload: dict[str, Any]) -> tuple[bool, str, dict[str, Any] | None]:
        if not isinstance(payload, dict):
            return False, "Dữ liệu hồ sơ không hợp lệ.", None

        with self.database.connect() as connection:
            current = connection.execute(
                """
                SELECT id, full_name, email, role, birth_date, phone, avatar_url
                FROM users
                WHERE id = ?
                """,
                (user_id,),
            ).fetchone()

            if current is None:
                return False, "Người dùng không tồn tại.", None

            full_name = str(payload.get("full_name", current["full_name"] or "")).strip()
            birth_date = str(payload.get("birth_date", current["birth_date"] or "")).strip()
            phone = str(payload.get("phone", current["phone"] or "")).strip()
            avatar_url = str(payload.get("avatar_url", current["avatar_url"] or "")).strip()

            if not full_name or len(full_name) > 120:
                return False, "Vui lòng nhập họ tên hợp lệ.", None

            if birth_date:
                try:
                    datetime.strptime(birth_date, "%Y-%m-%d")
                except ValueError:
                    return False, "Ngày sinh không hợp lệ.", None

            if phone and len(phone) > 30:
                return False, "Số điện thoại quá dài.", None

            if avatar_url and len(avatar_url) > 500:
                return False, "Link ảnh đại diện quá dài.", None

            connection.execute(
                """
                UPDATE users
                SET full_name = ?, birth_date = ?, phone = ?, avatar_url = ?
                WHERE id = ?
                """,
                (full_name, birth_date or None, phone or None, avatar_url or None, user_id),
            )

            updated = connection.execute(
                """
                SELECT id, full_name, email, role, birth_date, phone, avatar_url
                FROM users
                WHERE id = ?
                """,
                (user_id,),
            ).fetchone()

        return True, "Cập nhật thông tin thành công.", dict(updated)

    def request_password_change_code(self, email: str) -> tuple[bool, str, str | None]:
        normalized_email = (email or "").strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", normalized_email):
            return False, "Vui lòng nhập email hợp lệ để nhận mã xác minh.", None

        with self.database.connect() as connection:
            user = connection.execute(
                "SELECT id FROM users WHERE LOWER(email) = ?",
                (normalized_email,),
            ).fetchone()

        if user is None:
            return False, "Email chưa được đăng ký trong hệ thống.", None

        code = f"{random.randint(100000, 999999)}"
        with PASSWORD_VERIFICATION_LOCK:
            PASSWORD_VERIFICATION_CODES[normalized_email] = {
                "code": code,
                "expires_at": time.time() + 300,
            }

        sent = send_password_verification_email(normalized_email, code)
        if not sent:
            return False, "Không thể gửi mã xác minh đến email. Vui lòng thử lại sau.", None

        smtp_username = os.environ.get("SMTP_USERNAME")
        smtp_password = os.environ.get("SMTP_PASSWORD")
        if not smtp_username or not smtp_password:
            return True, (
                "Đang ở chế độ phát triển: mã xác minh đã được tạo và hiển thị trong terminal/console. "
                "Vui lòng kiểm tra log để lấy mã xác minh."
            ), code

        return True, "Mã xác minh đã được gửi đến email của bạn. Vui lòng kiểm tra hộp thư.", code

    def validate_password_verification_code(self, email: str, code: str | None) -> tuple[bool, str]:
        normalized_email = (email or "").strip().lower()
        if not normalized_email:
            return False, "Vui lòng nhập email để xác thực tài khoản."
        if not code or not str(code).strip():
            return False, "Vui lòng nhập mã xác minh được gửi về email."

        with PASSWORD_VERIFICATION_LOCK:
            record = PASSWORD_VERIFICATION_CODES.get(normalized_email)
            if record is None:
                return False, "Bạn chưa yêu cầu hoặc mã xác minh đã hết hạn. Vui lòng gửi lại mã." 
            if time.time() > float(record["expires_at"]):
                PASSWORD_VERIFICATION_CODES.pop(normalized_email, None)
                return False, "Mã xác minh đã hết hạn. Vui lòng yêu cầu lại mã mới."
            if str(record["code"]) != str(code).strip():
                return False, "Mã xác minh không đúng. Vui lòng kiểm tra lại email."

        PASSWORD_VERIFICATION_CODES.pop(normalized_email, None)
        return True, "Mã xác minh hợp lệ."

    def change_password(
        self,
        user_id: int | None,
        current_password: str,
        new_password: str,
        confirm_password: str,
        email: str | None = None,
        verification_code: str | None = None,
    ) -> tuple[bool, str]:
        if not all(isinstance(value, str) for value in (current_password, new_password, confirm_password)):
            return False, "Dữ liệu mật khẩu không hợp lệ."

        current_password = current_password.strip()
        new_password = new_password.strip()
        confirm_password = confirm_password.strip()
        email = (email or "").strip().lower()
        verification_code = (verification_code or "").strip()

        if not current_password or not new_password or not confirm_password:
            return False, "Vui lòng nhập đầy đủ mật khẩu hiện tại, mật khẩu mới và xác nhận mật khẩu mới."

        if len(new_password) < 8 or len(new_password) > 128:
            return False, "mật khẩu mới phải có từ 8 đến 128 ký tự."

        if new_password != confirm_password:
            return False, "Mật khẩu xác nhận không khớp với mật khẩu mới."

        if current_password == new_password:
            return False, "Mật khẩu mới phải khác mật khẩu hiện tại."

        with self.database.connect() as connection:
            if user_id is not None:
                user = connection.execute(
                    "SELECT id, email, password_hash FROM users WHERE id = ?",
                    (user_id,),
                ).fetchone()
            else:
                if not email:
                    return False, "Vui lòng nhập email để xác thực tài khoản."
                user = connection.execute(
                    "SELECT id, email, password_hash FROM users WHERE LOWER(email) = ?",
                    (email,),
                ).fetchone()

            if user is None:
                return False, "Người dùng không tồn tại."

            if verification_code:
                email_to_verify = email or user["email"]
                valid, message = self.validate_password_verification_code(email_to_verify, verification_code)
                if not valid:
                    return False, message

            if not check_password_hash(user["password_hash"], current_password):
                return False, "Mật khẩu hiện tại không đúng."

            connection.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (generate_password_hash(new_password), user["id"]),
            )

        return True, "Cập nhật mật khẩu thành công."

    def register(self, full_name: str, email: str, password: str) -> tuple[bool, str]:
        if not all(isinstance(value, str) for value in (full_name, email, password)):
            return False, "Thông tin đăng ký không hợp lệ."

        full_name = full_name.strip()
        email = email.strip().lower()

        if not full_name or len(full_name) > 120:
            return False, "Vui lòng nhập họ tên hợp lệ."

        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            return False, "Vui lòng nhập email hợp lệ."

        if len(password) < 8 or len(password) > 128:
            return False, "Mật khẩu cần có từ 8 đến 128 ký tự."

        try:
            with self.database.connect() as connection:
                connection.execute(
                    """
                    INSERT INTO users(full_name, email, password_hash, role)
                    VALUES (?, ?, ?, 'staff')
                    """,
                    (full_name, email, generate_password_hash(password)),
                )
        except sqlite3.IntegrityError:
            return False, "Email này đã được đăng ký."

        return True, "Tạo tài khoản thành công. Bạn có thể đăng nhập ngay."


PASSWORD_VERIFICATION_CODES: dict[str, dict[str, float | str]] = {}
PASSWORD_VERIFICATION_LOCK = threading.Lock()


def normalize_smtp_settings() -> dict[str, str]:
    smtp_username = (os.environ.get("SMTP_USERNAME") or "").strip()
    smtp_password = (os.environ.get("SMTP_PASSWORD") or "").replace(" ", "").strip()
    smtp_from = (os.environ.get("SMTP_FROM") or smtp_username or "no-reply@lumihotel.local").strip()
    return {
        "host": (os.environ.get("SMTP_HOST") or "smtp.gmail.com").strip(),
        "port": str(os.environ.get("SMTP_PORT") or "587").strip(),
        "username": smtp_username,
        "password": smtp_password,
        "from": smtp_from,
    }


def send_password_verification_email(email: str, code: str) -> bool:
    settings = normalize_smtp_settings()
    smtp_host = settings["host"]
    smtp_port = int(settings["port"])
    smtp_username = settings["username"]
    smtp_password = settings["password"]
    smtp_from = settings["from"]

    if not smtp_username or not smtp_password:
        print(f"[DEV_EMAIL_CODE] Gửi mã xác minh đến {email}: {code}")
        return True

    try:
        message = EmailMessage()
        message["Subject"] = "Mã xác minh đổi mật khẩu LumiHotel"
        message["From"] = smtp_from
        message["To"] = email
        message.set_content(
            "Mã xác minh đổi mật khẩu của bạn là: "
            f"{code}\n\nMã này có hiệu lực trong 5 phút."
        )

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(message)
        print(f"[EMAIL_SENT] Đã gửi mã xác minh tới {email}")
        return True
    except Exception as exc:
        print(f"[EMAIL_ERROR] {exc}")
        return False


class RoomTypeService:
    def __init__(self, database: Database) -> None:
        self.database = database

    def _normalize(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("Dữ liệu loại phòng không hợp lệ.")

        code = str(payload.get("code", "")).strip().lower()
        name = str(payload.get("name", "")).strip()
        description = str(payload.get("description", "")).strip()
        status = str(payload.get("status", "active")).strip().lower()

        try:
            price = float(payload.get("price", 0))
            max_guests = int(payload.get("max_guests", 2))
        except (TypeError, ValueError) as exc:
            raise ValueError("Giá hoặc số khách tối đa không hợp lệ.") from exc

        if not re.fullmatch(r"[a-z0-9_-]{2,30}", code):
            raise ValueError("Mã loại phòng chỉ gồm chữ thường, số, '-' hoặc '_'.")
        if not name or len(name) > 100:
            raise ValueError("Tên loại phòng không hợp lệ.")
        if not math.isfinite(price) or price < 0:
            raise ValueError("Giá mặc định phải lớn hơn hoặc bằng 0.")
        if max_guests < 1 or max_guests > 50:
            raise ValueError("Số khách tối đa phải từ 1 đến 50.")
        if status not in {"active", "inactive"}:
            raise ValueError("Trạng thái loại phòng không hợp lệ.")

        return {
            "code": code,
            "name": name,
            "description": description or "Loại phòng tại LumiHotel.",
            "price": round(price, 2),
            "max_guests": max_guests,
            "status": status,
        }

    def list_room_types(self, active_only: bool = False) -> list[dict[str, Any]]:
        sql = "SELECT * FROM room_types"
        if active_only:
            sql += " WHERE status = 'active'"
        sql += " ORDER BY name"
        with self.database.connect() as connection:
            rows = connection.execute(sql).fetchall()
        return [dict(row) for row in rows]

    def create_room_type(self, payload: dict[str, Any]):
        try:
            data = self._normalize(payload)
            with self.database.connect() as connection:
                cursor = connection.execute(
                    """
                    INSERT INTO room_types(code, name, description, price, max_guests, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        data["code"], data["name"], data["description"],
                        data["price"], data["max_guests"], data["status"],
                    ),
                )
                row = connection.execute(
                    "SELECT * FROM room_types WHERE id = ?", (cursor.lastrowid,)
                ).fetchone()
        except sqlite3.IntegrityError:
            return False, "Mã hoặc tên loại phòng đã tồn tại.", None
        except ValueError as exc:
            return False, str(exc), None
        return True, "Thêm loại phòng thành công.", dict(row)

    def update_room_type(self, room_type_id: int, payload: dict[str, Any]):
        try:
            data = self._normalize(payload)
            with self.database.connect() as connection:
                result = connection.execute(
                    """
                    UPDATE room_types
                    SET code = ?, name = ?, description = ?, price = ?,
                        max_guests = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (
                        data["code"], data["name"], data["description"],
                        data["price"], data["max_guests"], data["status"], room_type_id,
                    ),
                )
                if result.rowcount == 0:
                    return False, "Loại phòng không tồn tại.", None
                row = connection.execute(
                    "SELECT * FROM room_types WHERE id = ?", (room_type_id,)
                ).fetchone()
        except sqlite3.IntegrityError:
            return False, "Mã hoặc tên loại phòng đã tồn tại.", None
        except ValueError as exc:
            return False, str(exc), None
        return True, "Cập nhật loại phòng thành công.", dict(row)

    def delete_room_type(self, room_type_id: int):
        with self.database.connect() as connection:
            room_type = connection.execute(
                "SELECT id FROM room_types WHERE id = ?", (room_type_id,)
            ).fetchone()
            if room_type is None:
                return False, "Loại phòng không tồn tại."

            in_use = connection.execute(
                "SELECT 1 FROM rooms WHERE room_type_id = ? LIMIT 1",
                (room_type_id,),
            ).fetchone()
            if in_use:
                return False, "Không thể xóa loại phòng đang được sử dụng."

            connection.execute("DELETE FROM room_types WHERE id = ?", (room_type_id,))
        return True, "Xóa loại phòng thành công."


class RoomService:
    ROOM_STATUSES = {"available", "occupied", "cleaning", "maintenance"}

    def __init__(self, database: Database) -> None:
        self.database = database

    def _normalize_room_data(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("Dữ liệu phòng không hợp lệ.")

        code = str(payload.get("code", "")).strip().upper()
        name = str(payload.get("name", "")).strip()
        description = str(payload.get("description", "")).strip()
        image_url = str(payload.get("image_url", "")).strip()
        room_type = str(payload.get("room_type", "")).strip().lower()
        status = str(payload.get("status", "available")).strip().lower() or "available"

        try:
            price = float(payload.get("price", 0))
            floor = int(payload.get("floor", 1))
        except (TypeError, ValueError) as exc:
            raise ValueError("Giá hoặc tầng phòng không hợp lệ.") from exc

        if not code or len(code) > 20:
            raise ValueError("Mã phòng không hợp lệ.")

        if not name or len(name) > 120:
            raise ValueError("Tên phòng không hợp lệ.")

        with self.database.connect() as connection:
            room_type_row = connection.execute(
                "SELECT id, code FROM room_types WHERE code = ? COLLATE NOCASE",
                (room_type,),
            ).fetchone()
        if room_type_row is None:
            raise ValueError("Loại phòng không hợp lệ.")

        if status not in self.ROOM_STATUSES:
            raise ValueError("Trạng thái phòng không hợp lệ.")

        if price < 0:
            raise ValueError("Giá phòng phải lớn hơn hoặc bằng 0.")

        if floor < 1 or floor > 50:
            raise ValueError("Tầng phòng phải từ 1 đến 50.")

        return {
            "code": code,
            "name": name,
            "description": description or "Phòng tại LumiHotel.",
            "image_url": image_url,
            "room_type": room_type,
            "room_type_id": room_type_row["id"],
            "legacy_room_type": room_type if room_type in {"single", "double", "vip"} else "single",
            "price": round(price, 2),
            "status": status,
            "floor": floor,
        }

    def list_rooms(self) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT rooms.*, room_types.code AS assigned_type_code,
                    room_types.name AS room_type_name
                FROM rooms
                LEFT JOIN room_types ON room_types.id = rooms.room_type_id
                ORDER BY rooms.floor, rooms.code
                """
            ).fetchall()
        return [self._serialize_room(row) for row in rows]

    @staticmethod
    def _serialize_room(row: sqlite3.Row) -> dict[str, Any]:
        room = dict(row)
        room["room_type"] = room.pop("assigned_type_code", None) or room["room_type"]
        return room

    def create_room(self, payload: dict[str, Any]):
        try:
            data = self._normalize_room_data(payload)
            with self.database.connect() as connection:
                cursor = connection.execute(
                    """
                    INSERT INTO rooms(
                        code, name, description, image_url, room_type, room_type_id,
                        price, status, floor
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        data["code"], data["name"], data["description"],
                        data["image_url"], data["legacy_room_type"], data["room_type_id"], data["price"],
                        data["status"], data["floor"],
                    ),
                )
                room = connection.execute(
                    """
                    SELECT rooms.*, room_types.code AS assigned_type_code,
                        room_types.name AS room_type_name
                    FROM rooms
                    LEFT JOIN room_types ON room_types.id = rooms.room_type_id
                    WHERE rooms.id = ?
                    """,
                    (cursor.lastrowid,),
                ).fetchone()
        except sqlite3.IntegrityError:
            return False, "Mã phòng đã tồn tại.", None
        except ValueError as exc:
            return False, str(exc), None

        return True, "Thêm phòng thành công.", self._serialize_room(room)

    def update_room(self, room_id: int, payload: dict[str, Any]):
        try:
            data = self._normalize_room_data(payload)
            with self.database.connect() as connection:
                result = connection.execute(
                    """
                    UPDATE rooms
                    SET code = ?, name = ?, description = ?, image_url = ?,
                        room_type = ?, room_type_id = ?, price = ?, status = ?, floor = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (
                        data["code"], data["name"], data["description"],
                        data["image_url"], data["legacy_room_type"], data["room_type_id"], data["price"],
                        data["status"], data["floor"], room_id,
                    ),
                )
                if result.rowcount == 0:
                    return False, "Phòng không tồn tại.", None

                room = connection.execute(
                    """
                    SELECT rooms.*, room_types.code AS assigned_type_code,
                        room_types.name AS room_type_name
                    FROM rooms
                    LEFT JOIN room_types ON room_types.id = rooms.room_type_id
                    WHERE rooms.id = ?
                    """,
                    (room_id,),
                ).fetchone()
        except sqlite3.IntegrityError:
            return False, "Mã phòng đã tồn tại.", None
        except ValueError as exc:
            return False, str(exc), None

        return True, "Cập nhật phòng thành công.", self._serialize_room(room)

    def checkout_room(self, room_id: int):
        with self.database.connect() as connection:
            result = connection.execute(
                """
                UPDATE rooms
                SET status = 'available', updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND status = 'occupied'
                """,
                (room_id,),
            )
            if result.rowcount:
                room = connection.execute(
                    """
                    SELECT rooms.*, room_types.code AS assigned_type_code,
                        room_types.name AS room_type_name
                    FROM rooms
                    LEFT JOIN room_types ON room_types.id = rooms.room_type_id
                    WHERE rooms.id = ?
                    """,
                    (room_id,),
                ).fetchone()
                return True, "Trả phòng thành công!", self._serialize_room(room)

            room = connection.execute(
                "SELECT id FROM rooms WHERE id = ?",
                (room_id,),
            ).fetchone()
            if room is None:
                return False, "Phòng không tồn tại.", None

        return False, "Phòng này không thể trả phòng.", None

    def delete_room(self, room_id: int):
        with self.database.connect() as connection:
            room = connection.execute(
                "SELECT id FROM rooms WHERE id = ?",
                (room_id,),
            ).fetchone()
            if room is None:
                return False, "Phòng không tồn tại."

            connection.execute(
                "DELETE FROM bookings WHERE room_id = ?",
                (room_id,),
            )
            connection.execute(
                "DELETE FROM rooms WHERE id = ?",
                (room_id,),
            )

        return True, "Xóa phòng thành công."

    def list_room_types(self) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT code, name FROM room_types ORDER BY name COLLATE NOCASE"
            ).fetchall()
        return [dict(row) for row in rows]

    def create_room_type(self, payload: dict[str, Any]):
        if not isinstance(payload, dict):
            return False, "Dữ liệu thể loại không hợp lệ.", None

        code = str(payload.get("code", "")).strip().lower()
        name = str(payload.get("name", "")).strip()
        if not re.fullmatch(r"[a-z][a-z0-9_-]{1,19}", code):
            return False, "Mã thể loại phải gồm 2-20 ký tự chữ thường, số, _ hoặc -.", None
        if not name or len(name) > 60:
            return False, "Tên thể loại phải có từ 1 đến 60 ký tự.", None

        try:
            with self.database.connect() as connection:
                connection.execute(
                    "INSERT INTO room_types(code, name) VALUES (?, ?)",
                    (code, name),
                )
                room_type = connection.execute(
                    "SELECT code, name FROM room_types WHERE code = ?",
                    (code,),
                ).fetchone()
        except sqlite3.IntegrityError:
            return False, "Mã hoặc tên thể loại đã tồn tại.", None

        return True, "Thêm thể loại phòng thành công.", dict(room_type)

    def update_room_type(self, code: str, payload: dict[str, Any]):
        if not isinstance(payload, dict):
            return False, "Dữ liệu thể loại không hợp lệ.", None

        old_code = code.strip().lower()
        new_code = str(payload.get("code", old_code)).strip().lower()
        name = str(payload.get("name", "")).strip()
        if not re.fullmatch(r"[a-z][a-z0-9_-]{1,19}", new_code):
            return False, "Mã thể loại phải gồm 2-20 ký tự chữ thường, số, _ hoặc -.", None
        if not name or len(name) > 60:
            return False, "Tên thể loại phải có từ 1 đến 60 ký tự.", None

        try:
            with self.database.connect() as connection:
                room_type_exists = connection.execute(
                    "SELECT 1 FROM room_types WHERE code = ?",
                    (old_code,),
                ).fetchone()
                if room_type_exists is None:
                    return False, "Thể loại phòng không tồn tại.", None

                connection.execute(
                    "UPDATE rooms SET room_type = ? WHERE room_type = ?",
                    (new_code, old_code),
                )
                result = connection.execute(
                    "UPDATE room_types SET code = ?, name = ? WHERE code = ?",
                    (new_code, name, old_code),
                )
                if result.rowcount == 0:
                    return False, "Thể loại phòng không tồn tại.", None
                room_type = connection.execute(
                    "SELECT code, name FROM room_types WHERE code = ?",
                    (new_code,),
                ).fetchone()
        except sqlite3.IntegrityError:
            return False, "Mã hoặc tên thể loại đã tồn tại.", None

        return True, "Cập nhật thể loại phòng thành công.", dict(room_type)

    def delete_room_type(self, code: str):
        normalized_code = code.strip().lower()
        with self.database.connect() as connection:
            room_type = connection.execute(
                "SELECT code FROM room_types WHERE code = ?",
                (normalized_code,),
            ).fetchone()
            if room_type is None:
                return False, "Thể loại phòng không tồn tại."

            room_count = connection.execute(
                "SELECT COUNT(*) FROM rooms WHERE room_type = ?",
                (normalized_code,),
            ).fetchone()[0]
            if room_count:
                return False, "Không thể xóa thể loại đang được phòng sử dụng."

            connection.execute(
                "DELETE FROM room_types WHERE code = ?",
                (normalized_code,),
            )

        return True, "Xóa thể loại phòng thành công."


class BookingService:
    """Nghiệp vụ đặt phòng, tách khỏi app.py giống mô hình Service của TTCS."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def list_bookings(self) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    b.id, b.code, b.customer_name, b.check_in,
                    b.check_out, b.check_in_time, b.check_out_time,
                    b.total, b.status,
                    r.code AS room_code, r.name AS room_name
                FROM bookings b
                JOIN rooms r ON r.id = b.room_id
                ORDER BY b.id DESC
                """
            ).fetchall()

        return [dict(row) for row in rows]

    def create_booking(self, payload: dict[str, Any]):
        customer = str(payload.get("customer_name", "")).strip()
        room_id = payload.get("room_id")
        check_in = str(payload.get("check_in", "")).strip()
        check_out = str(payload.get("check_out", "")).strip()
        check_in_time = str(payload.get("check_in_time", "")).strip() or None
        check_out_time = str(payload.get("check_out_time", "")).strip() or None
        requested_total = payload.get("total")

        if not customer:
            return False, "Vui lòng nhập tên khách hàng.", None

        try:
            room_id = int(room_id)
            start = date.fromisoformat(check_in)
            end = date.fromisoformat(check_out)
        except (TypeError, ValueError):
            return False, "Thông tin đặt phòng không hợp lệ.", None

        if end < start:
            return False, "Ngày trả phòng phải sau hoặc bằng ngày nhận phòng.", None

        if bool(check_in_time) != bool(check_out_time):
            return False, "Vui lòng nhập đầy đủ giờ nhận phòng và giờ trả phòng.", None

        time_pattern = r"(?:[01]\d|2[0-3]):[0-5]\d"
        if check_in_time and (
            not re.fullmatch(time_pattern, check_in_time)
            or not re.fullmatch(time_pattern, check_out_time)
        ):
            return False, "Giờ nhận phòng hoặc giờ trả phòng không hợp lệ.", None

        if end == start and (check_in_time is None or check_out_time is None):
            return False, "Vui lòng chọn đầy đủ giờ thuê phòng.", None

        if check_in_time and check_out_time:
            start_dt = datetime.strptime(f"{check_in} {check_in_time}", "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(f"{check_out} {check_out_time}", "%Y-%m-%d %H:%M")
            if end_dt <= start_dt:
                return False, "Giờ trả phòng phải sau giờ nhận phòng.", None
            if end_dt <= datetime.now():
                return False, "Thời gian trả phòng không được trong quá khứ.", None
        elif datetime.combine(end, datetime.min.time()) <= datetime.now():
            return False, "Thời gian trả phòng không được trong quá khứ.", None

        with self.database.connect() as connection:
            room = connection.execute(
                "SELECT * FROM rooms WHERE id = ?",
                (room_id,),
            ).fetchone()

            if room is None:
                return False, "Không tìm thấy phòng.", None

            if room["status"] != "available":
                return False, "Phòng hiện không còn trống.", None

            room_price = float(room["price"])
            if not math.isfinite(room_price) or room_price <= 0:
                return False, "Giá phòng không hợp lệ.", None

            if check_in_time and check_out_time:
                delta_hours = (datetime.strptime(f"{check_out} {check_out_time}", "%Y-%m-%d %H:%M") - datetime.strptime(f"{check_in} {check_in_time}", "%Y-%m-%d %H:%M")).total_seconds() / 3600
                if delta_hours <= 0:
                    return False, "Thời gian thuê phải lớn hơn 0 giờ.", None
                computed_total = room_price * (delta_hours / 24)
            else:
                nights = (end - start).days
                if nights <= 0:
                    return False, "Thời gian thuê phải lớn hơn 0 ngày.", None
                computed_total = nights * room_price

            if not math.isfinite(computed_total) or computed_total <= 0:
                return False, "Tổng tiền phải lớn hơn 0.", None

            if requested_total is not None:
                try:
                    requested_total = float(requested_total)
                    if not math.isfinite(requested_total):
                        return False, "Giá thuê không hợp lệ.", None
                    if requested_total < 0:
                        return False, "Giá thuê phải lớn hơn 0.", None
                except (TypeError, ValueError):
                    return False, "Giá thuê không hợp lệ.", None

            total = computed_total

            code = "BK-" + datetime.now().strftime("%m%d%H%M%S")

            try:
                cursor = connection.execute(
                    """
                    INSERT INTO bookings(
                        code, customer_name, room_id,
                        check_in, check_out, check_in_time, check_out_time,
                        total, status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'booked')
                    """,
                    (
                        code, customer, room_id, check_in, check_out,
                        check_in_time, check_out_time, total,
                    ),
                )
                connection.execute(
                    "UPDATE rooms SET status = 'occupied', updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (room_id,),
                )
                booking = connection.execute(
                    """
                    SELECT b.*, r.code AS room_code, r.name AS room_name
                    FROM bookings b
                    JOIN rooms r ON r.id = b.room_id
                    WHERE b.id = ?
                    """,
                    (cursor.lastrowid,),
                ).fetchone()
            except sqlite3.IntegrityError:
                return False, "Không thể tạo mã đặt phòng.", None

        return True, "Đặt phòng thành công.", dict(booking)


class DashboardService:
    def __init__(self, database: Database) -> None:
        self.database = database

    def get_summary(self) -> dict[str, Any]:
        with self.database.connect() as connection:
            rooms = connection.execute(
                "SELECT COUNT(*) AS total FROM rooms"
            ).fetchone()["total"]

            available = connection.execute(
                "SELECT COUNT(*) AS total FROM rooms WHERE status = 'available'"
            ).fetchone()["total"]

            occupied = connection.execute(
                "SELECT COUNT(*) AS total FROM rooms WHERE status = 'occupied'"
            ).fetchone()["total"]

            cleaning = connection.execute(
                "SELECT COUNT(*) AS total FROM rooms WHERE status = 'cleaning'"
            ).fetchone()["total"]

            maintenance = connection.execute(
                "SELECT COUNT(*) AS total FROM rooms WHERE status = 'maintenance'"
            ).fetchone()["total"]

            bookings = connection.execute(
                "SELECT COUNT(*) AS total FROM bookings"
            ).fetchone()["total"]

            revenue = connection.execute(
                """
                SELECT COALESCE(SUM(total), 0) AS total
                FROM bookings
                WHERE status IN ('booked', 'checked_in', 'checked_out')
                """
            ).fetchone()["total"]

        occupancy = round((occupied / rooms) * 100, 1) if rooms else 0

        return {
            "rooms": rooms,
            "available_rooms": available,
            "occupied_rooms": occupied,
            "cleaning_rooms": cleaning,
            "maintenance_rooms": maintenance,
            "bookings": bookings,
            "revenue": revenue,
            "occupancy": occupancy,
        }
