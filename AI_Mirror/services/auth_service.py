import bcrypt
import json
import re
from datetime import datetime, timedelta, timezone

from database.connection import database_connection


class AuthService:
    def hash_password(self, password: str) -> str:
        password_bytes = password.encode("utf-8")

        hashed = bcrypt.hashpw(
            password_bytes,
            bcrypt.gensalt()
        )

        return hashed.decode("utf-8")

    def verify_password(
        self,
        password: str,
        password_hash: str
    ) -> bool:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8")
        )

    def create_admin(
        self,
        username: str,
        password: str
    ) -> int:
        return self.create_user(username, password, "admin")

    def create_user(self, username, password, role="admin", created_by=None):
        username = username.strip()

        if not username:
            raise ValueError(
                "Username is required."
            )

        if not re.fullmatch(r"[A-Za-z0-9_.-]{3,40}", username):
            raise ValueError("Username must be 3–40 characters using letters, numbers, dot, dash or underscore.")
        if len(password) < 10 or not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password) or not re.search(r"\d", password):
            raise ValueError("Password must be at least 10 characters with upper-case, lower-case and a number.")
        if role not in ("admin", "super_admin"):
            raise ValueError("Invalid account role.")

        password_hash = self.hash_password(password)

        with database_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO admin_users (
                    username,
                    password_hash,
                    active, role, created_by, updated_at
                )
                VALUES (?, ?, 1, ?, ?, CURRENT_TIMESTAMP)
                """,
                (
                    username,
                    password_hash, role, created_by
                )
            )
            user_id = cursor.lastrowid
            self._record_account_change(connection, user_id, created_by, "create",
                                        f"Created {role.replace('_', ' ')} account {username}",
                                        {}, {"username": username, "role": role, "active": 1})
            return user_id

    def authenticate(
        self,
        username: str,
        password: str
    ):
        with database_connection() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM admin_users
                WHERE username = ?
                  AND active = 1
                """,
                (username.strip(),)
            ).fetchone()

            if row is None:
                return None

            if not self.verify_password(
                password,
                row["password_hash"]
            ):
                return None

            connection.execute(
                "UPDATE admin_users SET last_login_at=CURRENT_TIMESTAMP WHERE id=?",
                (row["id"],),
            )

            return {
                "id": row["id"],
                "username": row["username"],
                "role": row["role"] if "role" in row.keys() else "admin",
            }

    def list_users(self):
        with database_connection() as connection:
            return [dict(row) for row in connection.execute(
                "SELECT id,username,role,active,created_at,last_login_at,updated_at "
                "FROM admin_users ORDER BY role DESC,username"
            ).fetchall()]

    def set_user_active(self, user_id, active, actor_user_id):
        if int(user_id) == int(actor_user_id):
            raise ValueError("You cannot disable your own signed-in account.")
        with database_connection() as connection:
            row = connection.execute("SELECT id,username,role,active FROM admin_users WHERE id=?", (user_id,)).fetchone()
            if row is None:
                raise ValueError("Account not found.")
            before = {"active": row["active"]}
            after = {"active": int(bool(active))}
            connection.execute("UPDATE admin_users SET active=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
                               (after["active"], user_id))
            self._record_account_change(connection, user_id, actor_user_id, "update",
                                        f'{"Enabled" if active else "Disabled"} account {row["username"]}',
                                        before, after)

    def reset_password(self, user_id, new_password, actor_user_id):
        self._validate_password(new_password)
        with database_connection() as connection:
            row = connection.execute("SELECT username,password_hash FROM admin_users WHERE id=?", (user_id,)).fetchone()
            if row is None:
                raise ValueError("Account not found.")
            new_hash = self.hash_password(new_password)
            connection.execute("UPDATE admin_users SET password_hash=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
                               (new_hash, user_id))
            self._record_account_change(connection, user_id, actor_user_id, "update",
                                        f'Reset password for {row["username"]}',
                                        {"password_hash": row["password_hash"]}, {"password_hash": new_hash})

    def _validate_password(self, password):
        if len(password) < 10 or not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password) or not re.search(r"\d", password):
            raise ValueError("Password must be at least 10 characters with upper-case, lower-case and a number.")

    def _record_account_change(self, connection, target_id, actor_id, action, description, before, after):
        expires = datetime.now(timezone.utc) + timedelta(hours=24)
        connection.execute(
            "INSERT INTO admin_account_history(target_user_id,actor_user_id,action,description,"
            "before_values,after_values,expires_at) VALUES(?,?,?,?,?,?,?)",
            (target_id, actor_id, action, description, json.dumps(before), json.dumps(after),
             expires.strftime("%Y-%m-%d %H:%M:%S")),
        )

    def account_history(self):
        with database_connection() as connection:
            rows = connection.execute(
                "SELECT h.*,u.username AS target_username FROM admin_account_history h "
                "LEFT JOIN admin_users u ON u.id=h.target_user_id ORDER BY h.id DESC LIMIT 100"
            ).fetchall()
        now = datetime.now(timezone.utc)
        result = []
        for row in rows:
            item = dict(row)
            expires = datetime.strptime(item["expires_at"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            created = datetime.strptime(item["created_at"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            item["can_undo"] = not item["undone"] and now <= expires
            item["created_display"] = created.astimezone().strftime("%d %b %Y, %H:%M")
            result.append(item)
        return result

    def undo_account_change(self, history_id, actor_user_id):
        with database_connection() as connection:
            row = connection.execute("SELECT * FROM admin_account_history WHERE id=?", (history_id,)).fetchone()
            if row is None or row["undone"]:
                return False, "This account change is unavailable."
            expires = datetime.strptime(row["expires_at"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) > expires:
                return False, "The 24-hour undo period has expired."
            target_id = row["target_user_id"]
            if int(target_id or 0) == int(actor_user_id):
                return False, "You cannot undo a change that would alter your signed-in account."
            before = json.loads(row["before_values"])
            if row["action"] == "create":
                connection.execute("UPDATE admin_users SET active=0,updated_at=CURRENT_TIMESTAMP WHERE id=?", (target_id,))
            elif before:
                allowed = {key: value for key, value in before.items() if key in ("active", "password_hash", "role")}
                assignments = ",".join(f"{key}=?" for key in allowed)
                connection.execute(f"UPDATE admin_users SET {assignments},updated_at=CURRENT_TIMESTAMP WHERE id=?",
                                   list(allowed.values()) + [target_id])
            connection.execute("UPDATE admin_account_history SET undone=1,undone_at=CURRENT_TIMESTAMP WHERE id=?",
                               (history_id,))
            return True, row["description"]
