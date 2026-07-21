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
                discount_type TEXT,
                discount_value REAL,
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

            CREATE TABLE IF NOT EXISTS admin_undo_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                payload TEXT NOT NULL,
                undone INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                undone_at TEXT
            );

            CREATE TABLE IF NOT EXISTS analytics_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                product_id INTEGER,
                metadata TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_analytics_event_type ON analytics_events(event_type);
            CREATE INDEX IF NOT EXISTS idx_analytics_product ON analytics_events(product_id);
        """)
        product_columns = {row["name"] for row in connection.execute("PRAGMA table_info(products)").fetchall()}
        if "discount_type" not in product_columns:
            connection.execute("ALTER TABLE products ADD COLUMN discount_type TEXT")
        if "discount_value" not in product_columns:
            connection.execute("ALTER TABLE products ADD COLUMN discount_value REAL")
