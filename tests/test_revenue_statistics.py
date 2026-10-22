import gc
import importlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.database import Database
from backend.services import DashboardService


class RevenueStatisticsTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="lumihotel_revenue_")
        self.database = Database(Path(self.directory.name) / "test.db")
        self.service = DashboardService(self.database)
        with self.database.connect() as connection:
            connection.execute("DELETE FROM bookings")
            room = connection.execute("SELECT id FROM rooms LIMIT 1").fetchone()[0]
            for index, (checkout, amount, status) in enumerate([
                ("2026-01-12", 7050000, "checked_out"),
                ("2026-01-20", 1000000, "booked"),
                ("2026-03-12", 2000000, "checked_in"),
                ("2026-03-13", 9990000, "cancelled"),
                ("2025-12-12", 3000000, "checked_out"),
            ]):
                connection.execute("INSERT INTO bookings(code, customer_name, room_id, check_in, check_out, total, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                   (f"TEST-{index}", "Test Guest", room, checkout, checkout, amount, status))
        with patch.dict(os.environ, {"DATABASE_PATH": str(self.database.path)}):
            self.module = importlib.import_module("app")
        self.service_patch = patch.object(self.module, "dashboard_service", self.service)
        self.service_patch.start()
        self.client = self.module.app.test_client()
        with self.client.session_transaction() as session:
            session["user"] = {"id": 1, "full_name": "Test Report"}

    def tearDown(self):
        self.service_patch.stop()
        gc.collect()
        self.directory.cleanup()

    def test_api_matches_database_rules_and_has_twelve_months(self):
        report = self.client.get("/api/revenue-statistics?year=2026").get_json()
        self.assertEqual([row["month"] for row in report["months"]], list(range(1, 13)))
        self.assertEqual(report["months"][0]["total"], 8050000)
        self.assertEqual(report["months"][1]["total"], 0)
        self.assertEqual(report["months"][2]["total"], 2000000)
        self.assertEqual(report["total"], 10050000)
        self.assertEqual(report["total"], sum(row["total"] for row in report["months"]))
        other = self.client.get("/api/revenue-statistics?year=2025").get_json()
        self.assertEqual(other["total"], 3000000)
        empty = self.client.get("/api/revenue-statistics?year=2024").get_json()
        self.assertEqual([row["total"] for row in empty["months"]], [0] * 12)

    def test_pdf_exports_with_and_without_revenue(self):
        for year in (2026, 2024):
            response = self.client.get(f"/api/revenue-statistics/export?year={year}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.mimetype, "application/pdf")
            self.assertTrue(response.data.startswith(b"%PDF-"))
            self.assertIn(str(year), response.headers["Content-Disposition"])

    def test_invalid_year_and_authentication(self):
        for endpoint in ("/api/revenue-statistics", "/api/revenue-statistics/export"):
            for year in ("abc", "0", "-1", "10000"):
                self.assertEqual(self.client.get(f"{endpoint}?year={year}").status_code, 400)
        self.client.post("/api/logout")
        self.assertEqual(self.client.get("/api/revenue-statistics").status_code, 401)
        self.assertEqual(self.client.get("/api/revenue-statistics/export").status_code, 401)


if __name__ == "__main__":
    unittest.main()
