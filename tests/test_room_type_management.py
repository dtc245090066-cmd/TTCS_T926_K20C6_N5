import os
import sqlite3
import tempfile
import unittest
import uuid

from backend.database import Database
from backend.services import RoomService, RoomTypeService


class RoomTypeManagementTests(unittest.TestCase):
    def setUp(self):
        self.db_path = os.path.join(
            tempfile.gettempdir(), f"lumihotel_room_types_{uuid.uuid4().hex}.db"
        )

        self.database = Database(self.db_path)
        self.room_types = RoomTypeService(self.database)
        self.rooms = RoomService(self.database)

    def test_create_room_type_and_assign_it_to_a_room(self):
        ok, message, room_type = self.room_types.create_room_type({
            "code": "family",
            "name": "Phòng gia đình",
            "description": "Phòng dành cho gia đình",
            "price": 1800000,
            "max_guests": 4,
            "status": "active",
        })

        self.assertTrue(ok, message)
        self.assertEqual(room_type["code"], "family")

        ok, message, room = self.rooms.create_room({
            "code": "F101",
            "name": "Family 101",
            "room_type": "family",
            "price": 1800000,
            "floor": 1,
        })

        self.assertTrue(ok, message)
        self.assertEqual(room["room_type"], "family")
        self.assertEqual(room["room_type_name"], "Phòng gia đình")

        ok, message, updated_room = self.rooms.update_room(room["id"], {
            "code": "F101",
            "name": "Family 101 Updated",
            "room_type": "family",
            "price": 1900000,
            "floor": 1,
        })

        self.assertTrue(ok, message)
        self.assertEqual(updated_room["room_type"], "family")
        self.assertEqual(updated_room["room_type_name"], "Phòng gia đình")

    def test_cannot_delete_room_type_in_use(self):
        _, _, room_type = self.room_types.create_room_type({
            "code": "family",
            "name": "Phòng gia đình",
            "price": 1800000,
            "max_guests": 4,
        })
        self.rooms.create_room({
            "code": "F101",
            "name": "Family 101",
            "room_type": "family",
            "price": 1800000,
            "floor": 1,
        })

        ok, message = self.room_types.delete_room_type(room_type["id"])

        self.assertFalse(ok)
        self.assertIn("đang được sử dụng", message)

    def test_rejects_invalid_room_type_code(self):
        ok, message, room_type = self.room_types.create_room_type({
            "code": "bad code",
            "name": "Không hợp lệ",
            "price": 1000000,
            "max_guests": 2,
        })

        self.assertFalse(ok)
        self.assertIsNone(room_type)
        self.assertIn("Mã loại phòng", message)

    def test_migrates_existing_rooms_to_seeded_room_types(self):
        legacy_path = os.path.join(
            tempfile.gettempdir(), f"lumihotel_legacy_rooms_{uuid.uuid4().hex}.db"
        )
        with sqlite3.connect(legacy_path) as connection:
            connection.execute("""
                CREATE TABLE rooms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    description TEXT,
                    image_url TEXT,
                    room_type TEXT NOT NULL CHECK(room_type IN ('single', 'double', 'vip')),
                    price REAL NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'available',
                    floor INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            connection.execute(
                "INSERT INTO rooms(code, name, room_type, price, floor) VALUES ('OLD101', 'Legacy room', 'vip', 2000000, 1)"
            )

        legacy_database = Database(legacy_path)
        migrated_room = next(
            room for room in RoomService(legacy_database).list_rooms()
            if room["code"] == "OLD101"
        )

        self.assertEqual(migrated_room["room_type"], "vip")
        self.assertEqual(migrated_room["room_type_name"], "Phòng VIP")


if __name__ == "__main__":
    unittest.main()