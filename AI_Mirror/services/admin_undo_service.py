import json
import sqlite3
from datetime import datetime

from database.connection import database_connection
from paths import BACKUPS_DIR, DATABASE_PATH


class AdminUndoService:
    TRACKED_FIELDS = (
        "image_path",
        "category",
        "tryon_category",
        "tryon_enabled",
    )

    def create_database_backup(self):
        BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destination = BACKUPS_DIR / f"smart_mirror_before_change_{timestamp}.db"

        source = sqlite3.connect(DATABASE_PATH)
        backup = sqlite3.connect(destination)
        try:
            source.backup(backup)
        finally:
            backup.close()
            source.close()

        return destination

    def apply_product_corrections(self, description, corrections):
        with database_connection() as connection:
            previous_values = []

            for product_id, changes in corrections.items():
                row = connection.execute(
                    "SELECT * FROM products WHERE id = ?",
                    (product_id,),
                ).fetchone()
                if row is None:
                    continue

                old = {field: row[field] for field in self.TRACKED_FIELDS}
                previous_values.append({"id": product_id, "values": old})
                allowed = {
                    field: value for field, value in changes.items()
                    if field in self.TRACKED_FIELDS
                }
                assignments = ", ".join(f"{field} = ?" for field in allowed)
                values = list(allowed.values()) + [product_id]
                connection.execute(
                    f"UPDATE products SET {assignments}, updated_at = CURRENT_TIMESTAMP "
                    "WHERE id = ?",
                    values,
                )

            if not previous_values:
                return False

            connection.execute(
                "INSERT INTO admin_undo_actions (description, payload) VALUES (?, ?)",
                (description, json.dumps(previous_values)),
            )
            return True

    def record_created_product(self, product_id, description):
        payload = {
            "operation": "deactivate_created_products",
            "product_ids": [product_id],
        }
        with database_connection() as connection:
            connection.execute(
                "INSERT INTO admin_undo_actions (description, payload) VALUES (?, ?)",
                (description, json.dumps(payload)),
            )

    def undo_last_change(self):
        with database_connection() as connection:
            action = connection.execute(
                "SELECT * FROM admin_undo_actions WHERE undone = 0 "
                "ORDER BY id DESC LIMIT 1"
            ).fetchone()
            if action is None:
                return None

            payload = json.loads(action["payload"])

            if isinstance(payload, dict) and payload.get("operation") == "deactivate_created_products":
                for product_id in payload.get("product_ids", []):
                    connection.execute(
                        "UPDATE products SET active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                        (product_id,),
                    )
                connection.execute(
                    "UPDATE admin_undo_actions SET undone = 1, undone_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (action["id"],),
                )
                return action["description"]

            for item in payload:
                values = item["values"]
                connection.execute(
                    "UPDATE products SET image_path = ?, category = ?, "
                    "tryon_category = ?, tryon_enabled = ?, "
                    "updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (
                        values["image_path"], values["category"],
                        values["tryon_category"], values["tryon_enabled"],
                        item["id"],
                    ),
                )

            connection.execute(
                "UPDATE admin_undo_actions SET undone = 1, "
                "undone_at = CURRENT_TIMESTAMP WHERE id = ?",
                (action["id"],),
            )
            return action["description"]
