from database.connection import database_connection


class MetricsService:
    def summary(self):
        with database_connection() as connection:
            counts = {row["event_type"]: row["count"] for row in connection.execute(
                "SELECT event_type, COUNT(*) AS count FROM analytics_events GROUP BY event_type"
            ).fetchall()}
            top_products = connection.execute(
                "SELECT p.name, COUNT(*) AS interactions FROM analytics_events e "
                "JOIN products p ON p.id = e.product_id "
                "WHERE e.event_type IN ('product_viewed', 'tryon_started', 'basket_added') "
                "GROUP BY p.id, p.name ORDER BY interactions DESC LIMIT 5"
            ).fetchall()

        views = counts.get("product_viewed", 0)
        tryons = counts.get("tryon_started", 0)
        baskets = counts.get("basket_added", 0)
        return {
            "sessions": counts.get("session_started", 0), "views": views,
            "tryons": tryons, "baskets": baskets,
            "tryon_rate": round(tryons / views * 100, 1) if views else 0,
            "basket_rate": round(baskets / views * 100, 1) if views else 0,
            "top_products": [dict(row) for row in top_products],
        }
