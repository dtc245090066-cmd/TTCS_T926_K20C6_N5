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


if __name__ == "__main__":
    unittest.main()
