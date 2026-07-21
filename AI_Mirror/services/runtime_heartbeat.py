import json
import os
import time
from pathlib import Path

from PySide6.QtCore import QTimer

from paths import LOGS_DIR


class RuntimeHeartbeat:
    def __init__(self, parent=None, interval_ms=10_000):
        self.path = LOGS_DIR / "runtime_heartbeat.json"
        self.timer = QTimer(parent)
        self.timer.setInterval(interval_ms)
        self.timer.timeout.connect(self.write)

    def start(self):
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        self.write()
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def write(self):
        payload = {
            "pid": os.getpid(),
            "timestamp": time.time(),
        }
        temporary = Path(f"{self.path}.tmp")
        temporary.write_text(json.dumps(payload), encoding="utf-8")
        temporary.replace(self.path)
