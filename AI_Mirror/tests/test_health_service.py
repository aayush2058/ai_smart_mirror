import unittest

from services.health_service import HealthService


class HealthServiceTests(unittest.TestCase):
    def test_snapshot_contains_operational_metrics(self):
        service = HealthService()
        snapshot = service.snapshot({"state": "idle"})

        self.assertGreaterEqual(snapshot["uptime_seconds"], 0)
        self.assertGreater(snapshot["disk_free_gb"], 0)
        self.assertIn("memory_mb", snapshot)
        self.assertIn("cpu_percent", snapshot)
        self.assertEqual(snapshot["camera"]["state"], "idle")
        self.assertEqual(snapshot["database"], "Healthy")

    def test_uptime_is_staff_readable(self):
        self.assertEqual(HealthService.format_uptime(3661), "01:01:01")


if __name__ == "__main__":
    unittest.main()
