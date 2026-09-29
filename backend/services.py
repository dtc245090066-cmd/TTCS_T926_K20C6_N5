from __future__ import annotations

import re
import sqlite3
from datetime import date, datetime
from typing import Any

from werkzeug.security import check_password_hash, generate_password_hash

from backend.database import Database


class AuthService:
    def __init__(self, database: Database) -> None:
        self.database = database

    def login(self, email: str, password: str) -> dict[str, Any] | None:
        if not isinstance(email, str) or not isinstance(password, str):
            return None

        with self.database.connect() as connection:
            user = connection.execute(
                """
                SELECT id, full_name, email, password_hash, role, birth_date, phone, avatar_url
                FROM users
                WHERE email = ?
                """,
                (email.strip(),),
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


class RoomService:
    ROOM_TYPES = {"single", "double", "vip"}
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
        status = str(payload.get("status", "")).strip().lower()

        try:
            price = float(payload.get("price", 0))
            floor = int(payload.get("floor", 1))
        except (TypeError, ValueError) as exc:
            raise ValueError("Giá hoặc tầng phòng không hợp lệ.") from exc

        if not code or len(code) > 20:
            raise ValueError("Mã phòng không hợp lệ.")

        if not name or len(name) > 120:
            raise ValueError("Tên phòng không hợp lệ.")

        if room_type not in self.ROOM_TYPES:
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
            "price": round(price, 2),
            "status": status,
            "floor": floor,
        }

    def list_rooms(self) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM rooms ORDER BY floor, code"
            ).fetchall()
        return [dict(row) for row in rows]

    def create_room(self, payload: dict[str, Any]):
        try:
            data = self._normalize_room_data(payload)
            with self.database.connect() as connection:
                cursor = connection.execute(
                    """
                    INSERT INTO rooms(
                        code, name, description, image_url,
                        room_type, price, status, floor
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        data["code"], data["name"], data["description"],
                        data["image_url"], data["room_type"], data["price"],
                        data["status"], data["floor"],
                    ),
                )
                room = connection.execute(
                    "SELECT * FROM rooms WHERE id = ?",
                    (cursor.lastrowid,),
                ).fetchone()
        except sqlite3.IntegrityError:
            return False, "Mã phòng đã tồn tại.", None
        except ValueError as exc:
            return False, str(exc), None

        return True, "Thêm phòng thành công.", dict(room)

    def update_room(self, room_id: int, payload: dict[str, Any]):
        try:
            data = self._normalize_room_data(payload)
            with self.database.connect() as connection:
                result = connection.execute(
                    """
                    UPDATE rooms
                    SET code = ?, name = ?, description = ?, image_url = ?,
                        room_type = ?, price = ?, status = ?, floor = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (
                        data["code"], data["name"], data["description"],
                        data["image_url"], data["room_type"], data["price"],
                        data["status"], data["floor"], room_id,
                    ),
                )
                if result.rowcount == 0:
                    return False, "Phòng không tồn tại.", None

                room = connection.execute(
                    "SELECT * FROM rooms WHERE id = ?",
                    (room_id,),
                ).fetchone()
        except sqlite3.IntegrityError:
            return False, "Mã phòng đã tồn tại.", None
        except ValueError as exc:
            return False, str(exc), None

        return True, "Cập nhật phòng thành công.", dict(room)

    def delete_room(self, room_id: int):
        with self.database.connect() as connection:
            result = connection.execute(
                "DELETE FROM rooms WHERE id = ? AND status = 'available'",
                (room_id,),
            )
            if result.rowcount == 0:
                room = connection.execute(
                    "SELECT id FROM rooms WHERE id = ?",
                    (room_id,),
                ).fetchone()

                if room is None:
                    return False, "Phòng không tồn tại."

                return False, "Chỉ có thể xóa phòng đang trống."

        return True, "Xóa phòng thành công."


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
                    b.check_out, b.total, b.status,
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

        if not customer:
            return False, "Vui lòng nhập tên khách hàng.", None

        try:
            room_id = int(room_id)
            start = date.fromisoformat(check_in)
            end = date.fromisoformat(check_out)
        except (TypeError, ValueError):
            return False, "Thông tin đặt phòng không hợp lệ.", None

        if end <= start:
            return False, "Ngày check-out phải sau ngày check-in.", None

        with self.database.connect() as connection:
            room = connection.execute(
                "SELECT * FROM rooms WHERE id = ?",
                (room_id,),
            ).fetchone()

            if room is None:
                return False, "Không tìm thấy phòng.", None

            if room["status"] != "available":
                return False, "Phòng hiện không còn trống.", None

            nights = (end - start).days
            total = nights * float(room["price"])

            code = "BK-" + datetime.now().strftime("%m%d%H%M%S")

            try:
                cursor = connection.execute(
                    """
                    INSERT INTO bookings(
                        code, customer_name, room_id,
                        check_in, check_out, total, status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, 'booked')
                    """,
                    (code, customer, room_id, check_in, check_out, total),
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
