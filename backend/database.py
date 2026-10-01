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
                    birth_date TEXT,
                    phone TEXT,
                    avatar_url TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            user_columns = {
                row["name"] for row in connection.execute("PRAGMA table_info(users)").fetchall()
            }
            for column_name in ("birth_date", "phone", "avatar_url"):
                if column_name not in user_columns:
                    connection.execute(
                        f"ALTER TABLE users ADD COLUMN {column_name} TEXT"
                    )

            connection.execute("""
                CREATE TABLE IF NOT EXISTS rooms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    description TEXT,
                    image_url TEXT,
                    room_type TEXT NOT NULL,
                    price REAL NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'available'
                        CHECK(status IN ('available', 'occupied', 'cleaning', 'maintenance')),
                    floor INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            room_table_sql = connection.execute(
                "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'rooms'"
            ).fetchone()["sql"]
            normalized_room_sql = " ".join(room_table_sql.lower().split())
            if "check(room_type in ('single', 'double', 'vip'))" in normalized_room_sql:
                connection.execute("PRAGMA foreign_keys = OFF")
                connection.execute("""
                    CREATE TABLE rooms_migrated (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        code TEXT NOT NULL UNIQUE,
                        name TEXT NOT NULL,
                        description TEXT,
                        image_url TEXT,
                        room_type TEXT NOT NULL,
                        price REAL NOT NULL DEFAULT 0,
                        status TEXT NOT NULL DEFAULT 'available'
                            CHECK(status IN ('available', 'occupied', 'cleaning', 'maintenance')),
                        floor INTEGER NOT NULL DEFAULT 1,
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                connection.execute("""
                    INSERT INTO rooms_migrated(
                        id, code, name, description, image_url, room_type,
                        price, status, floor, created_at, updated_at
                    )
                    SELECT id, code, name, description, image_url, room_type,
                           price, status, floor, created_at, updated_at
                    FROM rooms
                """)
                connection.execute("DROP TABLE rooms")
                connection.execute("ALTER TABLE rooms_migrated RENAME TO rooms")
                connection.execute("PRAGMA foreign_keys = ON")

            room_types_table_exists = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'room_types'"
            ).fetchone() is not None
            connection.execute("""
                CREATE TABLE IF NOT EXISTS room_types (
                    code TEXT PRIMARY KEY COLLATE NOCASE,
                    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            if not room_types_table_exists:
                connection.executemany(
                    "INSERT INTO room_types(code, name) VALUES (?, ?)",
                    [("single", "Phòng đơn"), ("double", "Phòng đôi"), ("vip", "Phòng VIP")],
                )

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
                    check_in_time TEXT,
                    check_out_time TEXT,
                    total REAL NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'booked'
                        CHECK(status IN ('booked', 'checked_in', 'checked_out', 'cancelled')),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(room_id) REFERENCES rooms(id)
                )
            """)

            booking_columns = {
                row["name"] for row in connection.execute("PRAGMA table_info(bookings)").fetchall()
            }
            for column_name in ("check_in_time", "check_out_time"):
                if column_name not in booking_columns:
                    connection.execute(
                        f"ALTER TABLE bookings ADD COLUMN {column_name} TEXT"
                    )

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

            rooms = [
                ("101", "Deluxe Ocean View", "Phòng đôi rộng rãi, view đẹp.", "https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&w=900&q=85", "double", 1850000, "occupied", 1),
                ("102", "Deluxe Garden View", "Phòng đôi hướng vườn thoáng mát.", "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=900&q=85", "double", 1950000, "available", 1),
                ("103", "Superior Double", "Phòng đôi tiện nghi, thiết kế hiện đại.", "https://images.unsplash.com/photo-1611892440504-42a792e24d32?auto=format&fit=crop&w=900&q=85", "double", 1550000, "available", 1),
                ("104", "Family Twin", "Phòng hai giường phù hợp gia đình.", "https://images.unsplash.com/photo-1591088398332-8a7791972843?auto=format&fit=crop&w=900&q=85", "double", 2100000, "cleaning", 1),
                ("105", "Standard Queen", "Phòng giường Queen ấm cúng.", "https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&w=900&q=85", "double", 1450000, "available", 1),
                ("205", "Premium King", "Phòng cao cấp với giường King.", "https://images.unsplash.com/photo-1611892440504-42a792e24d32?auto=format&fit=crop&w=900&q=85", "double", 2350000, "available", 2),
                ("206", "Deluxe King", "Phòng King rộng rãi với khu vực nghỉ ngơi riêng.", "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=900&q=85", "double", 2500000, "available", 2),
                ("207", "Premium Twin", "Phòng hai giường đơn cao cấp.", "https://images.unsplash.com/photo-1591088398332-8a7791972843?auto=format&fit=crop&w=900&q=85", "double", 2200000, "maintenance", 2),
                ("208", "Executive Double", "Phòng đôi có bàn làm việc và khu vực tiếp khách.", "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=900&q=85", "double", 2800000, "available", 2),
                ("308", "Executive Suite", "Suite rộng, có khu vực tiếp khách.", "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=900&q=85", "vip", 3200000, "available", 3),
                ("309", "Junior Suite", "Suite tiện nghi với tầm nhìn thoáng.", "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=900&q=85", "vip", 3500000, "available", 3),
                ("310", "Grand Suite", "Suite rộng với nội thất sang trọng.", "https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&w=900&q=85", "vip", 4200000, "available", 3),
                ("311", "Royal Suite", "Suite cao cấp với không gian riêng tư.", "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=900&q=85", "vip", 5000000, "available", 3),
                ("412", "Standard Twin", "Hai giường đơn, phù hợp bạn bè.", "https://images.unsplash.com/photo-1591088398332-8a7791972843?auto=format&fit=crop&w=900&q=85", "double", 1250000, "cleaning", 4),
                ("413", "Premium Twin", "Phòng hai giường với tiện nghi cao cấp.", "https://images.unsplash.com/photo-1611892440504-42a792e24d32?auto=format&fit=crop&w=900&q=85", "double", 1950000, "available", 4),
                ("414", "Family Suite", "Suite rộng dành cho gia đình.", "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=900&q=85", "vip", 3800000, "available", 4),
                ("509", "Luxury Suite", "Suite sang trọng, không gian riêng tư.", "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=900&q=85", "vip", 4500000, "occupied", 5),
                ("510", "Honeymoon Suite", "Suite lãng mạn với thiết kế tinh tế.", "https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&w=900&q=85", "vip", 5200000, "available", 5),
                ("511", "Skyline Deluxe", "Phòng cao cấp với tầm nhìn thành phố.", "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=900&q=85", "double", 2650000, "available", 5),
                ("601", "Garden Deluxe", "Phòng yên tĩnh hướng vườn.", "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=900&q=85", "double", 2100000, "available", 6),
            ]
            existing_room_codes = {
                row["code"] for row in connection.execute("SELECT code FROM rooms").fetchall()
            }
            rooms_to_add = [
                room for room in rooms if room[0] not in existing_room_codes
            ][:max(0, 20 - room_count)]
            if rooms_to_add:
                connection.executemany(
                    """
                    INSERT INTO rooms(
                        code, name, description, image_url,
                        room_type, price, status, floor
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    rooms_to_add,
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
        connection.close()
