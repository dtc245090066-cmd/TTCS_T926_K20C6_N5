import os
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta

from backend.database import Database
from backend.services import BookingService


class BookingServiceTimeTests(unittest.TestCase):
    def setUp(self):
        file_descriptor, self.db_path = tempfile.mkstemp(prefix="lumihotel_booking_time_", suffix=".db")
        os.close(file_descriptor)

        self.database = Database(self.db_path)
        self.service = BookingService(self.database)

    def test_booking_times_are_saved_and_returned(self):
        connection = self.database.connect()
        try:
            room = connection.execute(
                "SELECT * FROM rooms WHERE status = 'available'"
            ).fetchone()
        finally:
            connection.close()

        ok, message, booking = self.service.create_booking({
            "customer_name": "Test Guest",
            "room_id": room["id"],
            "check_in": "2026-10-10",
            "check_out": "2026-10-12",
            "check_in_time": "14:30",
            "check_out_time": "11:15",
        })

        self.assertTrue(ok, message)
        self.assertEqual(booking["check_in_time"], "14:30")
        self.assertEqual(booking["check_out_time"], "11:15")
        listed = self.service.list_bookings()[0]
        self.assertEqual(listed["check_in_time"], "14:30")
        self.assertEqual(listed["check_out_time"], "11:15")

    def test_invalid_booking_time_is_rejected(self):
        ok, message, booking = self.service.create_booking({
            "customer_name": "Test Guest",
            "room_id": 2,
            "check_in": "2026-10-10",
            "check_out": "2026-10-12",
            "check_in_time": "25:00",
            "check_out_time": "11:00",
        })

        self.assertFalse(ok)
        self.assertIn("Giờ", message)
        self.assertIsNone(booking)

    def test_hourly_rental_total_is_validated(self):
        room = self.database.connect().execute("SELECT * FROM rooms WHERE status = 'available' LIMIT 1").fetchone()
        self.database.connect().close()

        ok, message, booking = self.service.create_booking({
            "customer_name": "Hourly Guest",
            "room_id": room["id"],
            "check_in": "2026-10-10",
            "check_out": "2026-10-10",
            "check_in_time": "09:00",
            "check_out_time": "12:00",
            "total": 1000000,
        })

        self.assertTrue(ok, message)
        self.assertAlmostEqual(float(booking["total"]), float(room["price"]) * 0.125, places=2)

    def test_past_checkout_is_rejected(self):
        with self.database.connect() as connection:
            room = connection.execute(
                "SELECT id FROM rooms WHERE status = 'available' LIMIT 1"
            ).fetchone()

        start = datetime.now() - timedelta(hours=4)
        end = datetime.now() - timedelta(hours=2)
        ok, message, booking = self.service.create_booking({
            "customer_name": "Past Guest",
            "room_id": room["id"],
            "check_in": start.date().isoformat(),
            "check_out": end.date().isoformat(),
            "check_in_time": start.strftime("%H:%M"),
            "check_out_time": end.strftime("%H:%M"),
        })

        self.assertFalse(ok)
        self.assertEqual(message, "Thời gian trả phòng không được trong quá khứ.")
        self.assertIsNone(booking)

    def test_non_positive_room_price_is_rejected(self):
        with self.database.connect() as connection:
            room = connection.execute(
                "SELECT id FROM rooms WHERE status = 'available' LIMIT 1"
            ).fetchone()
            connection.execute(
                "UPDATE rooms SET price = 0 WHERE id = ?",
                (room["id"],),
            )

        start = datetime.now() + timedelta(minutes=5)
        end = start + timedelta(hours=3)
        ok, message, booking = self.service.create_booking({
            "customer_name": "Free Guest",
            "room_id": room["id"],
            "check_in": start.date().isoformat(),
            "check_out": end.date().isoformat(),
            "check_in_time": start.strftime("%H:%M"),
            "check_out_time": end.strftime("%H:%M"),
        })

        self.assertFalse(ok)
        self.assertEqual(message, "Giá phòng không hợp lệ.")
        self.assertIsNone(booking)

    def test_existing_booking_table_gets_time_columns(self):
        file_descriptor, legacy_path = tempfile.mkstemp(prefix="lumihotel_legacy_booking_time_", suffix=".db")
        os.close(file_descriptor)

        with sqlite3.connect(legacy_path) as connection:
            connection.execute("""
                CREATE TABLE bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT NOT NULL UNIQUE,
                    customer_name TEXT NOT NULL,
                    room_id INTEGER NOT NULL,
                    check_in TEXT NOT NULL,
                    check_out TEXT NOT NULL,
                    total REAL NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'booked',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

        Database(legacy_path)
        with sqlite3.connect(legacy_path) as connection:
            columns = {row[1] for row in connection.execute("PRAGMA table_info(bookings)")}

        self.assertIn("check_in_time", columns)
        self.assertIn("check_out_time", columns)


if __name__ == "__main__":
    unittest.main()