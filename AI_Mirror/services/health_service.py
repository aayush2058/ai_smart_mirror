import os
import shutil
import sqlite3
import time

try:
    import psutil
except ImportError:
    psutil = None

from paths import DATABASE_PATH, PROJECT_ROOT


class HealthService:
    def __init__(self):
        self.started_at = time.time()
        self.process = psutil.Process(os.getpid()) if psutil else None

    def snapshot(self, camera_status=None):
        disk = shutil.disk_usage(PROJECT_ROOT)
        return {
            "uptime_seconds": int(time.time() - self.started_at),
            "memory_mb": round(self.process.memory_info().rss / 1_048_576, 1) if self.process else None,
            "cpu_percent": round(self.process.cpu_percent(interval=None), 1) if self.process else None,
            "disk_free_gb": round(disk.free / 1_073_741_824, 1),
            "database": self._database_status(),
            "camera": camera_status or {"state": "idle"},
        }

    def _database_status(self):
        try:
            connection = sqlite3.connect(DATABASE_PATH, timeout=2)
            result = connection.execute("PRAGMA quick_check").fetchone()
            connection.close()
            return "Healthy" if result and result[0] == "ok" else f"Integrity warning: {result[0] if result else 'unknown'}"
        except sqlite3.Error as error:
            return f"Error: {error}"

    @staticmethod
    def format_uptime(seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
