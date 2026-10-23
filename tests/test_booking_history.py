import gc
import importlib
import os
import tempfile
import unittest
import threading
from urllib.request import urlopen
from unittest.mock import patch
from werkzeug.serving import make_server

from backend.database import Database
from backend.services import AuthService, BookingService, DashboardService


class BookingHistoryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="lumi_history_")
        self.db = Database(os.path.join(self.directory.name, "test.db"))
        with self.db.connect() as conn:
            conn.execute("DELETE FROM bookings")
            room = conn.execute("SELECT id FROM rooms LIMIT 1").fetchone()[0]
            self.manager = conn.execute("SELECT id FROM users WHERE role = 'manager' LIMIT 1").fetchone()[0]
            self.staff = conn.execute("INSERT INTO users(full_name,email,password_hash,role) VALUES ('Staff','staff@test.local','unused','staff')").lastrowid
            customer = conn.execute("INSERT INTO customers(full_name,phone,email) VALUES ('Nguyễn Ánh','0901234567','anh@test.local')").lastrowid
            self.ids = []
            for code, checkout, amount, status in [
                ("NOV-A", "2026-11-01", 7050000, "checked_out"),
                ("NOV-B", "2026-11-30", 1000000, "booked"),
                ("NOV-C", "2026-11-20", 2000000, "cancelled"),
                ("OCT-A", "2026-10-31", 3000000, "checked_in"),
                ("OLD-A", "2025-11-10", 4000000, "checked_out"),
                ("DEC-A", "2026-12-01", 5000000, "checked_out"),
            ]:
                self.ids.append(conn.execute("""INSERT INTO bookings
                    (code,customer_name,customer_id,room_id,check_in,check_out,total,status)
                    VALUES (?, 'Nguyễn Ánh', ?, ?, '2026-10-30', ?, ?, ?)""",
                    (code, customer, room, checkout, amount, status)).lastrowid)
        with patch.dict(os.environ, {"DATABASE_PATH": str(self.db.path)}):
            self.module = importlib.import_module("app")
        self.patches = [patch.object(self.module, "booking_service", BookingService(self.db)),
                        patch.object(self.module, "auth_service", AuthService(self.db)),
                        patch.object(self.module, "dashboard_service", DashboardService(self.db))]
        for item in self.patches:
            item.start()
        self.client = self.module.app.test_client()
        self.sign_in(self.manager)

    def tearDown(self):
        for item in self.patches:
            item.stop()
        gc.collect()
        self.directory.cleanup()

    def sign_in(self, user_id):
        with self.client.session_transaction() as session:
            session["user"] = {"id": user_id, "role": "manager"}

    def report(self, **filters):
        return self.client.get("/api/booking-history", query_string={"year": 2026, "month": 11, **filters})

    def test_period_and_revenue_match_without_duplicates(self):
        response = self.report()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        data = response.get_json()
        self.assertEqual([b["code"] for b in data["bookings"]], ["NOV-B", "NOV-C", "NOV-A"])
        self.assertEqual(data["summary"]["booking_count"], 3)
        self.assertEqual(data["summary"]["booking_value"], 10050000)
        self.assertEqual(data["summary"]["cancelled_count"], 1)
        revenue = self.client.get("/api/revenue-statistics?year=2026").get_json()
        self.assertEqual(data["summary"]["revenue"], revenue["months"][10]["total"])
        self.assertEqual(data["summary"]["revenue"], 8050000)
        self.assertEqual(self.report(month=10).get_json()["bookings"][0]["code"], "OCT-A")
        self.assertEqual(self.report(year=2025).get_json()["bookings"][0]["code"], "OLD-A")

    def test_search_status_payment_and_empty(self):
        for search, count in [("nov-a", 1), ("NGUYỄN ÁNH", 3), ("090123", 3), ("' OR 1=1 --", 0)]:
            self.assertEqual(self.report(search=search).get_json()["count"], count)
        data = self.report(status="cancelled", payment="unknown").get_json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["summary"]["revenue"], 8050000)
        empty = self.report(month=2).get_json()
        self.assertEqual(empty["bookings"], [])
        self.assertEqual(empty["summary"]["revenue"], 0)

    def test_detail_preserves_stored_information(self):
        data = self.client.get(f"/api/booking-history/{self.ids[0]}").get_json()["booking"]
        self.assertEqual(data["code"], "NOV-A")
        self.assertEqual(data["customer_name"], "Nguyễn Ánh")
        self.assertEqual(data["customer_phone"], "0901234567")
        self.assertEqual(data["customer_email"], "anh@test.local")
        self.assertEqual(data["total"], 7050000)
        self.assertEqual(data["nights"], 2)
        self.assertTrue(data["room_code"])
        self.assertNotIn("payment_status", data)
        self.assertNotIn("customer_id_number", data)
        self.assertEqual(self.client.get("/api/booking-history/999999").status_code, 404)

    def test_permissions_and_invalid_input(self):
        for filters in ({"month":0}, {"month":13}, {"year":"abc"}, {"year":10000}, {"page":0}, {"status":"bad"}, {"payment":"paid"}, {"search":"x" * 201}):
            self.assertEqual(self.report(**filters).status_code, 400)
        self.sign_in(self.staff)
        self.assertEqual(self.report().status_code, 200)
        detail = self.client.get(f"/api/booking-history/{self.ids[0]}")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.get_json()["booking"]["total"], 7050000)
        with self.db.connect() as connection:
            connection.execute("UPDATE users SET role = 'guest' WHERE id = ?", (self.staff,))
        self.assertEqual(self.report().status_code, 403)
        self.assertEqual(self.client.get(f"/api/booking-history/{self.ids[0]}").status_code, 403)
        self.sign_in(999999)
        self.assertEqual(self.report().status_code, 403)
        self.client.post("/api/logout")
        self.assertEqual(self.report().status_code, 401)
        self.assertEqual(self.client.get(f"/api/booking-history/{self.ids[0]}").status_code, 401)

    def test_pagination_and_shell(self):
        with self.db.connect() as conn:
            for index in range(23):
                conn.execute("""INSERT INTO bookings(code,customer_name,room_id,check_in,check_out,total,status)
                    SELECT ?,customer_name,room_id,check_in,check_out,total,status FROM bookings WHERE id=?""",
                    (f"PAGE-{index}", self.ids[0]))
        first = self.report().get_json()
        second = self.report(page=2).get_json()
        self.assertEqual(len(first["bookings"]), 20)
        self.assertEqual(len(second["bookings"]), 6)
        self.assertFalse({b["id"] for b in first["bookings"]} & {b["id"] for b in second["bookings"]})
        self.assertEqual(self.report(page=99).get_json()["page"], 2)
        self.assertEqual(self.client.get("/booking-history?year=2026&month=11").status_code, 200)

    def test_application_serves_history_over_http(self):
        server = make_server("127.0.0.1", 0, self.module.app)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            with urlopen(f"http://127.0.0.1:{server.server_port}/booking-history?year=2026&month=11", timeout=5) as response:
                self.assertEqual(response.status, 200)
                self.assertIn("Lịch sử đặt phòng", response.read().decode("utf-8"))
        finally:
            server.shutdown()
            worker.join(timeout=5)
            server.server_close()


if __name__ == "__main__":
    unittest.main()
