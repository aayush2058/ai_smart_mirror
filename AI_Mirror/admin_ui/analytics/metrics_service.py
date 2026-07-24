import csv
from datetime import datetime, timedelta

from database.connection import database_connection
from paths import EXPORTS_DIR


class MetricsService:
    def dashboard_data(self, days=14):
        days = max(7, min(30, int(days)))
        start = (datetime.now() - timedelta(days=days - 1)).strftime("%Y-%m-%d")
        with database_connection() as connection:
            activity = connection.execute(
                "SELECT date(created_at) AS day,event_type,COUNT(*) AS count FROM analytics_events "
                "WHERE date(created_at)>=? GROUP BY date(created_at),event_type ORDER BY day",
                (start,),
            ).fetchall()
            stock = connection.execute(
                "SELECT SUM(CASE WHEN total=0 THEN 1 ELSE 0 END) AS out_stock,"
                "SUM(CASE WHEN total BETWEEN 1 AND 3 THEN 1 ELSE 0 END) AS low_stock,"
                "SUM(CASE WHEN total>3 THEN 1 ELSE 0 END) AS healthy FROM ("
                "SELECT p.id,COALESCE(SUM(s.quantity),0) AS total FROM products p "
                "LEFT JOIN product_sizes s ON s.product_id=p.id WHERE p.active=1 GROUP BY p.id)"
            ).fetchone()
        date_values = [(datetime.now() - timedelta(days=offset)).date()
                       for offset in range(days - 1, -1, -1)]
        index = {(row["day"], row["event_type"]): row["count"] for row in activity}
        labels = [value.strftime("%d %b") for value in date_values]
        key_dates = [value.isoformat() for value in date_values]
        return {
            "labels": labels,
            "views": [index.get((day, "product_viewed"), 0) for day in key_dates],
            "tryons": [index.get((day, "tryon_started"), 0) for day in key_dates],
            "baskets": [index.get((day, "basket_added"), 0) for day in key_dates],
            "stock": [stock["healthy"] or 0, stock["low_stock"] or 0, stock["out_stock"] or 0],
        }
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

    def export_summary_csv(self):
        EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        summary = self.summary()
        destination = EXPORTS_DIR / f"retail_insights_{datetime.now():%Y%m%d_%H%M%S}.csv"
        with destination.open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.writer(handle)
            writer.writerow(("Retail Insights Export", datetime.now().strftime("%d %b %Y %H:%M:%S")))
            writer.writerow(("Metric", "Value"))
            for key in ("sessions", "views", "tryons", "baskets", "tryon_rate", "basket_rate"):
                writer.writerow((key.replace("_", " ").title(), summary[key]))
            writer.writerow(())
            writer.writerow(("Top Product", "Interactions"))
            for item in summary["top_products"]:
                writer.writerow((item["name"], item["interactions"]))
        return destination
