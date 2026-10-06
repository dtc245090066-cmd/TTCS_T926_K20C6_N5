import os
import tempfile
import unittest

from backend.database import Database
from backend.services import BookingService, RoomService


class BookingServiceCheckoutTests(unittest.TestCase):
    def setUp(self):
        self.db_path = os.path.join(tempfile.gettempdir(), "lumihotel_room_checkout_test.db")
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

        self.database = Database(self.db_path)
        self.booking_service = BookingService(self.database)
        self.room_service = RoomService(self.database)

        ok, message, self.room = self.room_service.create_room({
            "code": "C101",
            "name": "Phòng đang thuê",
            "room_type": "single",
            "price": 1000000,
            "floor": 1,
        })
        self.assertTrue(ok, message)

        ok, message, _ = self.booking_service.create_booking({
            "customer_name": "Nguyễn Văn A",
            "room_id": self.room["id"],
            "check_in": "2026-10-06",
            "check_out": "2026-10-08",
        })
        self.assertTrue(ok, message)

    def test_checkout_updates_room_and_booking_and_rejects_invalid_checkout(self):
        ok, message = self.booking_service.checkout_room(self.room["id"])

        self.assertTrue(ok, message)
        room = next(
            item for item in self.room_service.list_rooms()
            if item["id"] == self.room["id"]
        )
        self.assertEqual(room["status"], "available")

        bookings = self.booking_service.list_bookings()
        booking = next(item for item in bookings if item["room_code"] == "C101")
        self.assertEqual(booking["status"], "checked_out")

        ok, message = self.booking_service.checkout_room(self.room["id"])
        self.assertFalse(ok)
        self.assertEqual(message, "Chỉ có thể trả phòng đang có khách.")

        available_room = next(
            room for room in self.room_service.list_rooms()
            if room["status"] == "available"
        )
        ok, message = self.booking_service.checkout_room(available_room["id"])
        self.assertFalse(ok)
        self.assertEqual(message, "Chỉ có thể trả phòng đang có khách.")


if __name__ == "__main__":
    unittest.main()
