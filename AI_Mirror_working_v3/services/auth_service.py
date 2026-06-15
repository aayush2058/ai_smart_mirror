import bcrypt

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
        username = username.strip()

        if not username:
            raise ValueError(
                "Username is required."
            )

        if len(password) < 8:
            raise ValueError(
                "Password must contain at least 8 characters."
            )

        password_hash = self.hash_password(password)

        with database_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO admin_users (
                    username,
                    password_hash,
                    active
                )
                VALUES (?, ?, 1)
                """,
                (
                    username,
                    password_hash
                )
            )

            return cursor.lastrowid

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

            return {
                "id": row["id"],
                "username": row["username"],
            }