from database.connection import database_connection


class InventoryService:
    def get_sizes(self, product_id: int):
        with database_connection() as connection:
            rows = connection.execute(
                """
                SELECT id, size, quantity
                FROM product_sizes
                WHERE product_id = ?
                ORDER BY id
                """,
                (product_id,)
            ).fetchall()

            return [dict(row) for row in rows]

    def replace_sizes(
        self,
        product_id: int,
        sizes: list[dict]
    ):
        with database_connection() as connection:
            connection.execute(
                """
                DELETE FROM product_sizes
                WHERE product_id = ?
                """,
                (product_id,)
            )

            for item in sizes:
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
                        item.get("size"),
                        item.get("quantity", 0),
                    )
                )

    def update_quantity(
        self,
        size_id: int,
        quantity: int
    ):
        quantity = max(0, int(quantity))

        with database_connection() as connection:
            connection.execute(
                """
                UPDATE product_sizes
                SET quantity = ?
                WHERE id = ?
                """,
                (
                    quantity,
                    size_id
                )
            )