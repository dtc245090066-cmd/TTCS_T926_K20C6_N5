from contextlib import closing
import os
import tempfile
import unittest

from backend.database import Database
from backend.services import RoomService


class TrackingDatabase(Database):
    def __init__(self, path):
        self.connections = []
        super().__init__(path)

    def connect(self):
        connection = super().connect()
        self.connections.append(connection)
        return connection

    def close_connections(self):
        for connection in self.connections:
            connection.close()
        self.connections.clear()


class RoomServiceCheckoutTests(unittest.TestCase):
    def setUp(self):
        file_descriptor, self.db_path = tempfile.mkstemp(
            prefix="lumihotel_room_checkout_",
            suffix=".db",
        )
        os.close(file_descriptor)
        self.database = TrackingDatabase(self.db_path)
        self.service = RoomService(self.database)
        with closing(self.database.connect()) as connection, connection:
            room = connection.execute(
                "SELECT * FROM rooms WHERE status = 'available' LIMIT 1"
            ).fetchone()
            self.room_id = room["id"]
            connection.execute(
                "UPDATE rooms SET status = 'occupied' WHERE id = ?",
                (self.room_id,),
            )

    def tearDown(self):
        self.database.close_connections()
        os.remove(self.db_path)

    def test_checkout_changes_occupied_room_to_available_and_preserves_details(self):
        with closing(self.database.connect()) as connection, connection:
            before = connection.execute(
                "SELECT * FROM rooms WHERE id = ?",
                (self.room_id,),
            ).fetchone()

        ok, message, room = self.service.checkout_room(self.room_id)

        self.assertTrue(ok, message)
        self.assertEqual(message, "Trả phòng thành công!")
        self.assertEqual(room["status"], "available")
        for field in ("id", "code", "name", "description", "image_url", "price", "floor"):
            self.assertEqual(room[field], before[field])

    def test_checkout_rejects_rooms_not_occupied(self):
        for status in ("available", "cleaning", "maintenance"):
            with self.subTest(status=status):
                with closing(self.database.connect()) as connection, connection:
                    connection.execute(
                        "UPDATE rooms SET status = ? WHERE id = ?",
                        (status, self.room_id),
                    )

                ok, message, room = self.service.checkout_room(self.room_id)

                self.assertFalse(ok)
                self.assertEqual(message, "Phòng này không thể trả phòng.")
                self.assertIsNone(room)
                with closing(self.database.connect()) as connection, connection:
                    current_status = connection.execute(
                        "SELECT status FROM rooms WHERE id = ?",
                        (self.room_id,),
                    ).fetchone()["status"]
                self.assertEqual(current_status, status)

    def test_checkout_reports_missing_room(self):
        ok, message, room = self.service.checkout_room(-1)

        self.assertFalse(ok)
        self.assertEqual(message, "Phòng không tồn tại.")
        self.assertIsNone(room)


if __name__ == "__main__":
    unittest.main()
