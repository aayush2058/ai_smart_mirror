from database.connection import database_connection
from models.product import Product


class ProductRepository:
    def create_product(self, product: Product) -> int:
        with database_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO products (
                    product_code,
                    name,
                    department,
                    category,
                    price,
                    colour,
                    description,
                    image_path,
                    available,
                    discount,
                    discount_price,
                    location,
                    tryon_enabled,
                    tryon_category,
                    active
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    product.product_code,
                    product.name,
                    product.department,
                    product.category,
                    product.price,
                    product.colour,
                    product.description,
                    product.image_path,
                    int(product.available),
                    int(product.discount),
                    product.discount_price,
                    product.location,
                    int(product.tryon_enabled),
                    product.tryon_category,
                    int(product.active),
                )
            )

            product_id = cursor.lastrowid

            for size_data in product.sizes:
                connection.execute(
                    """
                    INSERT INTO product_sizes (
                        product_id,
                        size,
                        quantity
                    )
                    VALUES (?, ?, ?)
                    """,
                    (
                        product_id,
                        size_data.get("size"),
                        size_data.get("quantity", 0),
                    )
                )

            if product.tryon_enabled:
                connection.execute(
                    """
                    INSERT INTO tryon_settings (
                        product_id,
                        width_scale,
                        height_scale,
                        vertical_offset,
                        horizontal_offset
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        product_id,
                        product.width_scale,
                        product.height_scale,
                        product.vertical_offset,
                        product.horizontal_offset,
                    )
                )

            return product_id
        
    def update_tryon_settings(self, product_id: int, settings: dict):
        with database_connection() as connection:
            existing = connection.execute(
                """
                SELECT id
                FROM tryon_settings
                WHERE product_id = ?
                """,
                (product_id,)
            ).fetchone()

            if existing:
                connection.execute(
                    """
                    UPDATE tryon_settings
                    SET width_scale = ?,
                        height_scale = ?,
                        vertical_offset = ?,
                        horizontal_offset = ?
                    WHERE product_id = ?
                    """,
                    (
                        settings.get("width_scale", 1.0),
                        settings.get("height_scale", 1.0),
                        settings.get("vertical_offset", 0.0),
                        settings.get("horizontal_offset", 0),
                        product_id,
                    )
                )
            else:
                connection.execute(
                    """
                    INSERT INTO tryon_settings (
                        product_id,
                        width_scale,
                        height_scale,
                        vertical_offset,
                        horizontal_offset
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        product_id,
                        settings.get("width_scale", 1.0),
                        settings.get("height_scale", 1.0),
                        settings.get("vertical_offset", 0.0),
                        settings.get("horizontal_offset", 0),
                    )
                )

            connection.execute(
                """
                UPDATE products
                SET tryon_enabled = 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (product_id,)
            )

            return True

    def get_all_products(self):
        with database_connection() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM products
                WHERE active = 1
                ORDER BY created_at DESC
                """
            ).fetchall()

            return [dict(row) for row in rows]

    def get_product_by_id(self, product_id: int):
        with database_connection() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM products
                WHERE id = ?
                """,
                (product_id,)
            ).fetchone()

            if row is None:
                return None

            product = dict(row)

            sizes = connection.execute(
                """
                SELECT size, quantity
                FROM product_sizes
                WHERE product_id = ?
                """,
                (product_id,)
            ).fetchall()

            product["sizes"] = [dict(size) for size in sizes]

            tryon = connection.execute(
                """
                SELECT *
                FROM tryon_settings
                WHERE product_id = ?
                """,
                (product_id,)
            ).fetchone()

            product["tryon_settings"] = (
                dict(tryon) if tryon else None
            )

            return product

    def update_product(self, product_id: int, changes: dict):
        allowed_fields = {
            "product_code",
            "name",
            "department",
            "category",
            "price",
            "colour",
            "description",
            "image_path",
            "available",
            "discount",
            "discount_price",
            "location",
            "tryon_enabled",
            "tryon_category",
            "active",
        }

        updates = []
        values = []

        for field, value in changes.items():
            if field in allowed_fields:
                updates.append(f"{field} = ?")
                values.append(value)

        if not updates:
            return False

        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(product_id)

        query = f"""
            UPDATE products
            SET {", ".join(updates)}
            WHERE id = ?
        """

        with database_connection() as connection:
            cursor = connection.execute(query, values)
            return cursor.rowcount > 0

    def soft_delete_product(self, product_id: int):
        with database_connection() as connection:
            cursor = connection.execute(
                """
                UPDATE products
                SET active = 0,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (product_id,)
            )

            return cursor.rowcount > 0

    def restore_product(self, product_id: int):
        with database_connection() as connection:
            cursor = connection.execute(
                """
                UPDATE products
                SET active = 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (product_id,)
            )

            return cursor.rowcount > 0
        
    def get_deleted_products(self):
        with database_connection() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM products
                WHERE active = 0
                ORDER BY updated_at DESC
                """
            ).fetchall()

            return [dict(row) for row in rows]