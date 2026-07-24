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

            CREATE TABLE IF NOT EXISTS admin_account_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_user_id INTEGER,
                actor_user_id INTEGER,
                action TEXT NOT NULL,
                description TEXT NOT NULL,
                before_values TEXT NOT NULL,
                after_values TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT NOT NULL,
                undone INTEGER NOT NULL DEFAULT 0,
                undone_at TEXT
            );

            CREATE TABLE IF NOT EXISTS prediction_settings (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS prediction_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_type TEXT NOT NULL,
                status TEXT NOT NULL,
                sample_count INTEGER NOT NULL DEFAULT 0,
                horizon_days INTEGER NOT NULL,
                metrics TEXT NOT NULL,
                predictions TEXT NOT NULL,
                created_by INTEGER,
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

            CREATE TABLE IF NOT EXISTS admin_change_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                product_name TEXT NOT NULL,
                section TEXT NOT NULL,
                description TEXT NOT NULL,
                operation TEXT NOT NULL,
                before_values TEXT NOT NULL,
                after_values TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT NOT NULL,
                undone INTEGER NOT NULL DEFAULT 0,
                undone_at TEXT,
                FOREIGN KEY (product_id) REFERENCES products(id)
            );

            CREATE INDEX IF NOT EXISTS idx_change_history_created ON admin_change_history(created_at DESC);

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
        admin_columns = {row["name"] for row in connection.execute("PRAGMA table_info(admin_users)").fetchall()}
        if "role" not in admin_columns:
            connection.execute("ALTER TABLE admin_users ADD COLUMN role TEXT NOT NULL DEFAULT 'admin'")
        if "created_by" not in admin_columns:
            connection.execute("ALTER TABLE admin_users ADD COLUMN created_by INTEGER")
        if "last_login_at" not in admin_columns:
            connection.execute("ALTER TABLE admin_users ADD COLUMN last_login_at TEXT")
        if "updated_at" not in admin_columns:
            connection.execute("ALTER TABLE admin_users ADD COLUMN updated_at TEXT")
            connection.execute("UPDATE admin_users SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL")
        connection.execute(
            "INSERT OR IGNORE INTO prediction_settings(setting_key,setting_value) VALUES('horizon_days','7')"
        )
        connection.execute(
            "INSERT OR IGNORE INTO prediction_settings(setting_key,setting_value) VALUES('minimum_training_rows','30')"
        )
        connection.execute(
            "UPDATE admin_change_history SET expires_at = datetime(created_at, '+24 hours') "
            "WHERE expires_at < datetime(created_at, '+24 hours')"
        )
