from __future__ import annotations

import sqlite3
from pathlib import Path

from werkzeug.security import generate_password_hash


DEMO_EMAIL = "admin@lumihotel.local"
DEMO_PASSWORD = "Hotel2026@"


class Database:
    """Lớp quản lý kết nối và khởi tạo SQLite.

    Đây là tầng database theo cấu trúc TTCS:
        app.py -> services.py -> database.py -> hotel_management.db
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'manager',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS rooms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    description TEXT,
                    image_url TEXT,
                    room_type TEXT NOT NULL
                        CHECK(room_type IN ('single', 'double', 'vip')),
                    price REAL NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'available'
                        CHECK(status IN ('available', 'occupied', 'cleaning', 'maintenance')),
                    floor INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    phone TEXT,
                    email TEXT,
                    id_number TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT NOT NULL UNIQUE,
                    customer_name TEXT NOT NULL,
                    room_id INTEGER NOT NULL,
                    check_in TEXT NOT NULL,
                    check_out TEXT NOT NULL,
                    total REAL NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'booked'
                        CHECK(status IN ('booked', 'checked_in', 'checked_out', 'cancelled')),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(room_id) REFERENCES rooms(id)
                )
            """)

            existing_user = connection.execute(
                "SELECT id FROM users WHERE email = ?",
                (DEMO_EMAIL,),
            ).fetchone()

            if existing_user is None:
                connection.execute(
                    """
                    INSERT INTO users(full_name, email, password_hash, role)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        "Quản trị viên LumiHotel",
                        DEMO_EMAIL,
                        generate_password_hash(DEMO_PASSWORD),
                        "manager",
                    ),
                )
            else:
                connection.execute(
                    "UPDATE users SET password_hash = ? WHERE id = ?",
                    (generate_password_hash(DEMO_PASSWORD), existing_user["id"]),
                )

            room_count = connection.execute(
                "SELECT COUNT(*) AS total FROM rooms"
            ).fetchone()["total"]

            if room_count == 0:
                rooms = [
                    ("101", "Deluxe Ocean View", "Phòng đôi rộng rãi, view đẹp.", "https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&w=900&q=85", "double", 1850000, "occupied", 1),
                    ("205", "Premium King", "Phòng cao cấp với giường King.", "https://images.unsplash.com/photo-1611892440504-42a792e24d32?auto=format&fit=crop&w=900&q=85", "double", 2350000, "available", 2),
                    ("308", "Executive Suite", "Suite rộng, có khu vực tiếp khách.", "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=900&q=85", "vip", 3200000, "available", 3),
                    ("412", "Standard Twin", "Hai giường đơn, phù hợp bạn bè.", "https://images.unsplash.com/photo-1591088398332-8a7791972843?auto=format&fit=crop&w=900&q=85", "double", 1250000, "cleaning", 4),
                    ("509", "Luxury Suite", "Suite sang trọng, không gian riêng tư.", "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=900&q=85", "vip", 4500000, "occupied", 5),
                    ("601", "Garden Deluxe", "Phòng yên tĩnh hướng vườn.", "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=900&q=85", "double", 2100000, "available", 6),
                ]
                connection.executemany(
                    """
                    INSERT INTO rooms(
                        code, name, description, image_url,
                        room_type, price, status, floor
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    rooms,
                )

            booking_count = connection.execute(
                "SELECT COUNT(*) AS total FROM bookings"
            ).fetchone()["total"]

            if booking_count == 0:
                connection.executemany(
                    """
                    INSERT INTO bookings(
                        code, customer_name, room_id,
                        check_in, check_out, total, status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        ("BK-2058", "Nguyễn Minh Anh", 1, "2026-09-29", "2026-10-02", 5550000, "checked_in"),
                        ("BK-2057", "Trần Hoàng Nam", 2, "2026-09-29", "2026-10-01", 4700000, "booked"),
                        ("BK-2056", "Lê Thu Hà", 5, "2026-09-28", "2026-09-30", 9000000, "checked_in"),
                    ],
                )
