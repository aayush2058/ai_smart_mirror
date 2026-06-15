from database.connection import database_connection


def create_database_schema():
    with database_connection() as connection:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                colour TEXT,
                description TEXT,
                image_path TEXT,
                available INTEGER NOT NULL DEFAULT 1,
                discount INTEGER NOT NULL DEFAULT 0,
                discount_price REAL,
                location TEXT,
                tryon_enabled INTEGER NOT NULL DEFAULT 0,
                tryon_category TEXT,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS product_sizes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                size TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (product_id)
                    REFERENCES products(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS tryon_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL UNIQUE,
                width_scale REAL NOT NULL DEFAULT 1.0,
                height_scale REAL NOT NULL DEFAULT 1.0,
                vertical_offset REAL NOT NULL DEFAULT 0.0,
                horizontal_offset INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (product_id)
                    REFERENCES products(id)
                    ON DELETE CASCADE
            );
        """)