from __future__ import annotations

import math
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

        if bool(check_in_time) != bool(check_out_time):
            return False, "Vui lòng nhập đầy đủ giờ check-in và check-out.", None

        time_pattern = r"(?:[01]\d|2[0-3]):[0-5]\d"
        if check_in_time and (
            not re.fullmatch(time_pattern, check_in_time)
            or not re.fullmatch(time_pattern, check_out_time)
        ):
            return False, "Giờ check-in hoặc check-out không hợp lệ.", None

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
