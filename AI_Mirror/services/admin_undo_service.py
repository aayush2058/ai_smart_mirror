import json
import sqlite3
from datetime import datetime, timedelta, timezone

from database.connection import database_connection
from paths import BACKUPS_DIR, DATABASE_PATH


class AdminUndoService:
    TRACKED_FIELDS = (
        "product_code", "name", "department", "category", "price", "colour",
        "description", "image_path", "available", "discount", "discount_price",
        "discount_type", "discount_value", "location", "tryon_enabled",
        "tryon_category", "active",
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
                if not allowed:
                    continue
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

    def _record_history(self, connection, product_id, product_name, section, description,
                        operation, before_values, after_values):
        expires = datetime.now(timezone.utc) + timedelta(hours=24)
        connection.execute(
            "INSERT INTO admin_change_history (product_id,product_name,section,description,operation,"
            "before_values,after_values,expires_at) VALUES (?,?,?,?,?,?,?,?)",
            (product_id, product_name, section, description, operation,
             json.dumps(before_values), json.dumps(after_values),
             expires.strftime("%Y-%m-%d %H:%M:%S")),
        )

    def apply_product_change(self, product_id, product_name, section, changes, description=None):
        self.ensure_hourly_backup()
        allowed = {key: value for key, value in changes.items() if key in self.TRACKED_FIELDS}
        if not allowed:
            return False
        with database_connection() as connection:
            row = connection.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
            if row is None:
                return False
            before = {key: row[key] for key in allowed}
            assignments = ", ".join(f"{key}=?" for key in allowed)
            connection.execute(f"UPDATE products SET {assignments},updated_at=CURRENT_TIMESTAMP WHERE id=?",
                               list(allowed.values()) + [product_id])
            self._record_history(connection, product_id, product_name, section,
                                 description or f"Updated {section}", "product_fields", before, allowed)
            return True

    def apply_inventory_change(self, product_id, product_name, sizes):
        self.ensure_hourly_backup()
        after = [{"size": str(item.get("size", "")).strip(),
                  "quantity": max(0, int(item.get("quantity", 0)))} for item in sizes
                 if str(item.get("size", "")).strip()]
        with database_connection() as connection:
            before = [dict(row) for row in connection.execute(
                "SELECT size,quantity FROM product_sizes WHERE product_id=? ORDER BY id", (product_id,)).fetchall()]
            connection.execute("DELETE FROM product_sizes WHERE product_id=?", (product_id,))
            for item in after:
                connection.execute("INSERT INTO product_sizes(product_id,size,quantity) VALUES(?,?,?)",
                                   (product_id, item["size"], item["quantity"]))
            connection.execute("UPDATE products SET available=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
                               (int(sum(item["quantity"] for item in after) > 0), product_id))
            self._record_history(connection, product_id, product_name, "Inventory", "Updated sizes and stock",
                                 "inventory_sizes", before, after)
            return True

    def apply_tryon_settings_change(self, product_id, product_name, settings):
        self.ensure_hourly_backup()
        fields = ("width_scale", "height_scale", "vertical_offset", "horizontal_offset")
        after = {field: settings.get(field, 0) for field in fields}
        with database_connection() as connection:
            row = connection.execute("SELECT * FROM tryon_settings WHERE product_id=?", (product_id,)).fetchone()
            before = {field: row[field] for field in fields} if row else {
                "width_scale": 1.0, "height_scale": 1.0, "vertical_offset": 0.0, "horizontal_offset": 0}
            connection.execute("INSERT INTO tryon_settings(product_id,width_scale,height_scale,vertical_offset,horizontal_offset) "
                               "VALUES(?,?,?,?,?) ON CONFLICT(product_id) DO UPDATE SET width_scale=excluded.width_scale,"
                               "height_scale=excluded.height_scale,vertical_offset=excluded.vertical_offset,"
                               "horizontal_offset=excluded.horizontal_offset",
                               (product_id, after["width_scale"], after["height_scale"], after["vertical_offset"], after["horizontal_offset"]))
            self._record_history(connection, product_id, product_name, "Try-On Fit", "Updated fit calibration",
                                 "tryon_settings", before, after)
            return True

    def record_created_product_history(self, product_id, product_name):
        with database_connection() as connection:
            self._record_history(connection, product_id, product_name, "Product", "Created product",
                                 "created_product", {}, {"active": 1})

    def ensure_hourly_backup(self):
        BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
        backups = sorted(BACKUPS_DIR.glob("smart_mirror_hourly_*.db"), key=lambda path: path.stat().st_mtime, reverse=True)
        if backups:
            age_seconds = datetime.now().timestamp() - backups[0].stat().st_mtime
            if age_seconds < 3600:
                return backups[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destination = BACKUPS_DIR / f"smart_mirror_hourly_{timestamp}.db"
        source = sqlite3.connect(DATABASE_PATH); backup = sqlite3.connect(destination)
        try:
            source.backup(backup)
        finally:
            backup.close(); source.close()
        return destination

    def get_change_history(self, limit=200):
        with database_connection() as connection:
            rows = connection.execute("SELECT * FROM admin_change_history ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        now = datetime.now(timezone.utc); results = []
        for row in rows:
            item = dict(row)
            created = datetime.strptime(item["created_at"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            expires = datetime.strptime(item["expires_at"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            item["created_display"] = created.astimezone().strftime("%d %b %Y, %H:%M:%S")
            item["expires_display"] = expires.astimezone().strftime("%H:%M:%S")
            item["can_undo"] = not bool(item["undone"]) and now <= expires
            item["before_values"] = json.loads(item["before_values"]); item["after_values"] = json.loads(item["after_values"])
            results.append(item)
        return results

    def undo_history_change(self, history_id):
        with database_connection() as connection:
            row = connection.execute("SELECT * FROM admin_change_history WHERE id=?", (history_id,)).fetchone()
            if row is None or row["undone"]:
                return False, "This change is no longer available."
            expires = datetime.strptime(row["expires_at"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) > expires:
                return False, "The 24-hour undo period has expired."
            before = json.loads(row["before_values"]); product_id = row["product_id"]
            if row["operation"] == "product_fields":
                assignments = ", ".join(f"{key}=?" for key in before)
                connection.execute(f"UPDATE products SET {assignments},updated_at=CURRENT_TIMESTAMP WHERE id=?",
                                   list(before.values()) + [product_id])
            elif row["operation"] == "inventory_sizes":
                connection.execute("DELETE FROM product_sizes WHERE product_id=?", (product_id,))
                for item in before:
                    connection.execute("INSERT INTO product_sizes(product_id,size,quantity) VALUES(?,?,?)",
                                       (product_id, item["size"], item["quantity"]))
                connection.execute("UPDATE products SET available=? WHERE id=?",
                                   (int(sum(item["quantity"] for item in before) > 0), product_id))
            elif row["operation"] == "tryon_settings":
                connection.execute("INSERT INTO tryon_settings(product_id,width_scale,height_scale,vertical_offset,horizontal_offset) "
                                   "VALUES(?,?,?,?,?) ON CONFLICT(product_id) DO UPDATE SET width_scale=excluded.width_scale,"
                                   "height_scale=excluded.height_scale,vertical_offset=excluded.vertical_offset,horizontal_offset=excluded.horizontal_offset",
                                   (product_id, before["width_scale"], before["height_scale"], before["vertical_offset"], before["horizontal_offset"]))
            elif row["operation"] == "created_product":
                connection.execute("UPDATE products SET active=0,updated_at=CURRENT_TIMESTAMP WHERE id=?", (product_id,))
            else:
                return False, "This change type cannot be undone."
            connection.execute("UPDATE admin_change_history SET undone=1,undone_at=CURRENT_TIMESTAMP WHERE id=?", (history_id,))
            return True, row["description"]

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
                allowed = {field: value for field, value in values.items() if field in self.TRACKED_FIELDS}
                if not allowed:
                    continue
                assignments = ", ".join(f"{field} = ?" for field in allowed)
                connection.execute(
                    f"UPDATE products SET {assignments}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    list(allowed.values()) + [item["id"]],
                )

            connection.execute(
                "UPDATE admin_undo_actions SET undone = 1, "
                "undone_at = CURRENT_TIMESTAMP WHERE id = ?",
                (action["id"],),
            )
            return action["description"]
