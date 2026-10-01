import os
import tempfile
import unittest

from backend.database import Database
from backend.services import RoomService


class RoomServiceCreateRoomTests(unittest.TestCase):
    def setUp(self):
        self.db_path = os.path.join(tempfile.gettempdir(), "lumihotel_room_creation_test.db")
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

        self.database = Database(self.db_path)
        self.service = RoomService(self.database)

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


if __name__ == "__main__":
    unittest.main()
