import json
import sqlite3
import uuid

from database.connection import database_connection


class EventTracker:
    def __init__(self):
        self.session_id = uuid.uuid4().hex

    def track(self, event_type, product_id=None, metadata=None):
        try:
            with database_connection() as connection:
                connection.execute(
                    "INSERT INTO analytics_events (session_id, event_type, product_id, metadata) VALUES (?, ?, ?, ?)",
                    (self.session_id, event_type, product_id, json.dumps(metadata or {}, separators=(",", ":"))),
                )
            return True
        except sqlite3.Error:
            return False
