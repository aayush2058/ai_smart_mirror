import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
HEARTBEAT_PATH = PROJECT_ROOT / "logs" / "runtime_heartbeat.json"
WATCHDOG_LOG = PROJECT_ROOT / "logs" / "watchdog.log"
STOP_FILE = PROJECT_ROOT / "storage" / "STOP_WATCHDOG"


def log(message):
    WATCHDOG_LOG.parent.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with WATCHDOG_LOG.open("a", encoding="utf-8") as file:
        file.write(f"{timestamp} | {message}\n")


def heartbeat_age():
    try:
        payload = json.loads(HEARTBEAT_PATH.read_text(encoding="utf-8"))
        return time.time() - float(payload["timestamp"])
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return None


def run(stale_seconds, restart_delay):
    log("Watchdog started")
    while not STOP_FILE.exists():
        process = subprocess.Popen(
            [sys.executable, str(PROJECT_ROOT / "main.py")],
            cwd=PROJECT_ROOT,
        )
        log(f"Application started with PID {process.pid}")
        started_at = time.time()

        while process.poll() is None and not STOP_FILE.exists():
            age = heartbeat_age()
            startup_grace = time.time() - started_at < stale_seconds
            if age is not None and age > stale_seconds and not startup_grace:
                log(f"Heartbeat stale for {age:.1f}s; restarting application")
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                break
            time.sleep(5)

        if STOP_FILE.exists():
            if process.poll() is None:
                process.terminate()
            log("Watchdog stopped by STOP_WATCHDOG file")
            return

        log(f"Application exited with code {process.poll()}; restart pending")
        time.sleep(restart_delay)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Smart Mirror application watchdog")
    parser.add_argument("--stale-seconds", type=int, default=60)
    parser.add_argument("--restart-delay", type=int, default=5)
    arguments = parser.parse_args()
    run(arguments.stale_seconds, arguments.restart_delay)
