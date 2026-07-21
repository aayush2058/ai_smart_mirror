import argparse
import csv
import json
import sqlite3
import time
from datetime import datetime

from paths import DATABASE_PATH, LOGS_DIR


HEARTBEAT_PATH = LOGS_DIR / "runtime_heartbeat.json"


def heartbeat_age():
    try:
        payload = json.loads(HEARTBEAT_PATH.read_text(encoding="utf-8"))
        return round(time.time() - float(payload["timestamp"]), 2)
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return None


def database_status():
    try:
        connection = sqlite3.connect(DATABASE_PATH, timeout=3)
        result = connection.execute("PRAGMA quick_check").fetchone()[0]
        connection.close()
        return result
    except sqlite3.Error as error:
        return f"error: {error}"


def run(hours, interval_seconds):
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    output = LOGS_DIR / f"endurance_{datetime.now():%Y%m%d_%H%M%S}.csv"
    deadline = time.time() + hours * 3600
    failures = 0

    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(("timestamp", "heartbeat_age_seconds", "database"))

        while time.time() < deadline:
            age = heartbeat_age()
            database = database_status()
            writer.writerow((datetime.now().isoformat(), age, database))
            file.flush()

            if age is None or age > 30 or database != "ok":
                failures += 1
            time.sleep(interval_seconds)

    print(f"Endurance report: {output}")
    print(f"Health failures: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor a running Smart Mirror")
    parser.add_argument("--hours", type=float, default=18)
    parser.add_argument("--interval-seconds", type=int, default=60)
    args = parser.parse_args()
    raise SystemExit(run(args.hours, args.interval_seconds))
