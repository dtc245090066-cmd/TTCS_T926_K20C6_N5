import os
import sqlite3
import tempfile
import unittest

from backend.database import Database
from backend.services import RoomService


class RoomServiceCreateRoomTests(unittest.TestCase):
    def setUp(self):
        test_name = self._testMethodName
        self.db_path = os.path.join(tempfile.gettempdir(), f"lumihotel_room_creation_{test_name}.db")
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

        self.database = Database(self.db_path)
        self.service = RoomService(self.database)

    def test_custom_room_type_can_be_created_and_assigned_to_room(self):
        ok, message, room_type = self.service.create_room_type({
            "code": "suite",
            "name": "Phòng Suite",
        })

        self.assertTrue(ok, message)
        self.assertEqual(room_type["name"], "Phòng Suite")

        ok, message, room = self.service.create_room({
            "code": "S101",
            "name": "Suite hướng vườn",
            "room_type": "suite",
            "price": 3200000,
            "floor": 2,
        })

        self.assertTrue(ok, message)
        self.assertEqual(room["room_type"], "suite")

        ok, message, updated_type = self.service.update_room_type("suite", {
            "code": "family_suite",
            "name": "Suite gia đình",
        })

        self.assertTrue(ok, message)
        self.assertEqual(updated_type["name"], "Suite gia đình")
        self.assertEqual(updated_type["code"], "family_suite")

        connection = self.database.connect()
        try:
            updated_room_type = connection.execute(
                "SELECT room_type FROM rooms WHERE id = ?",
                (room["id"],),
            ).fetchone()[0]
        finally:
            connection.close()
        self.assertEqual(updated_room_type, "family_suite")

        ok, message = self.service.delete_room_type("family_suite")
        self.assertFalse(ok)
        self.assertIn("đang được phòng sử dụng", message)

        self.service.delete_room(room["id"])
        ok, message = self.service.delete_room_type("family_suite")
        self.assertTrue(ok, message)

        self.database.initialize()
        connection = self.database.connect()
        try:
            deleted_type = connection.execute(
                "SELECT 1 FROM room_types WHERE code = 'family_suite'"
            ).fetchone()
        finally:
            connection.close()
        self.assertIsNone(deleted_type)

    def test_create_room_defaults_status_to_available(self):
        self.database.initialize()

        connection = self.database.connect()
        try:
            room_count = connection.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]
        finally:
            connection.close()

        self.assertEqual(room_count, 20)

        ok, message, room = self.service.create_room({
            "code": "A101",
            "name": "Phòng đơn deluxe",
            "description": "Phòng mới cho thuê",
            "image_url": "https://example.com/room.jpg",
            "room_type": "single",
            "price": 1200000,
            "floor": 1,
        })

        self.assertTrue(ok, message)
        self.assertIsNotNone(room)
        self.assertEqual(room["status"], "available")

        connection = self.database.connect()
        try:
            occupied_room_id = connection.execute(
                "SELECT id FROM rooms WHERE code = '101'"
            ).fetchone()[0]
        finally:
            connection.close()

        ok, message = self.service.delete_room(occupied_room_id)

        self.assertTrue(ok, message)

        connection = self.database.connect()
        try:
            room_count_after_delete = connection.execute(
                "SELECT COUNT(*) FROM rooms"
            ).fetchone()[0]
            booking_count_for_deleted_room = connection.execute(
                "SELECT COUNT(*) FROM bookings WHERE room_id = ?",
                (occupied_room_id,),
            ).fetchone()[0]
        finally:
            connection.close()

        self.assertEqual(room_count_after_delete, 20)
        self.assertEqual(booking_count_for_deleted_room, 0)

    def test_initialize_migrates_room_types_and_preserves_bookings(self):
        legacy_path = os.path.join(tempfile.gettempdir(), "lumihotel_legacy_room_types.db")
        if os.path.exists(legacy_path):
            os.remove(legacy_path)

        connection = sqlite3.connect(legacy_path)
        connection.executescript("""
            CREATE TABLE rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                description TEXT,
                image_url TEXT,
                room_type TEXT NOT NULL CHECK(room_type IN ('single', 'double', 'vip')),
                price REAL NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'available'
                    CHECK(status IN ('available', 'occupied', 'cleaning', 'maintenance')),
                floor INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                customer_name TEXT NOT NULL,
                room_id INTEGER NOT NULL,
                check_in TEXT NOT NULL,
                check_out TEXT NOT NULL,
                total REAL NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'booked',
                FOREIGN KEY(room_id) REFERENCES rooms(id)
            );
            INSERT INTO rooms(code, name, room_type) VALUES ('101', 'Deluxe', 'double');
            INSERT INTO bookings(code, customer_name, room_id, check_in, check_out)
            VALUES ('BK-1', 'Khách mẫu', 1, '2026-10-01', '2026-10-02');
        """)
        connection.close()

        Database(legacy_path)
        connection = sqlite3.connect(legacy_path)
        try:
            connection.execute("INSERT INTO rooms(code, name, room_type) VALUES (?, ?, ?)",
                               ("S101", "Suite", "suite"))
            booking_count = connection.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
            foreign_key_errors = connection.execute("PRAGMA foreign_key_check").fetchall()
        finally:
            connection.close()
            os.remove(legacy_path)

        self.assertEqual(booking_count, 1)
        self.assertEqual(foreign_key_errors, [])


if __name__ == "__main__":
    unittest.main()
