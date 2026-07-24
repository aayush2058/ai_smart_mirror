import csv
import json
import math
from collections import defaultdict
from datetime import date, datetime, timedelta

import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import TimeSeriesSplit

from database.connection import database_connection
from paths import EXPORTS_DIR


class PredictionService:
    EVENT_WEIGHTS = {"product_viewed": 0.25, "tryon_started": 1.0, "basket_added": 2.0}

    def settings(self):
        with database_connection() as connection:
            rows = connection.execute("SELECT setting_key,setting_value FROM prediction_settings").fetchall()
        values = {row["setting_key"]: row["setting_value"] for row in rows}
        return {
            "horizon_days": int(values.get("horizon_days", 7)),
            "minimum_training_rows": int(values.get("minimum_training_rows", 30)),
        }

    def save_settings(self, horizon_days, minimum_training_rows):
        horizon = max(1, min(30, int(horizon_days)))
        minimum = max(20, min(1000, int(minimum_training_rows)))
        with database_connection() as connection:
            for key, value in (("horizon_days", horizon), ("minimum_training_rows", minimum)):
                connection.execute(
                    "INSERT INTO prediction_settings(setting_key,setting_value,updated_at) VALUES(?,?,CURRENT_TIMESTAMP) "
                    "ON CONFLICT(setting_key) DO UPDATE SET setting_value=excluded.setting_value,updated_at=CURRENT_TIMESTAMP",
                    (key, str(value)),
                )

    def generate(self, created_by=None):
        settings = self.settings()
        products, events = self._load_data()
        training_rows = self._training_rows(products, events)
        model = None
        validation_mae = None
        model_type = "Statistical fallback"
        if len(training_rows) >= settings["minimum_training_rows"]:
            x = np.asarray([row[0] for row in training_rows], dtype=float)
            y = np.asarray([row[1] for row in training_rows], dtype=float)
            if np.unique(y).size > 1:
                model = HistGradientBoostingRegressor(
                    loss="poisson", learning_rate=0.06, max_iter=160,
                    max_leaf_nodes=15, min_samples_leaf=5,
                    l2_regularization=1.0, random_state=42,
                )
                splits = min(3, max(2, len(x) // 15))
                errors = []
                for train_index, test_index in TimeSeriesSplit(n_splits=splits).split(x):
                    fold = HistGradientBoostingRegressor(
                        loss="poisson", learning_rate=0.06, max_iter=120,
                        max_leaf_nodes=15, min_samples_leaf=5,
                        l2_regularization=1.0, random_state=42,
                    )
                    fold.fit(x[train_index], y[train_index])
                    errors.append(mean_absolute_error(y[test_index], fold.predict(x[test_index])))
                validation_mae = round(float(np.mean(errors)), 2)
                model.fit(x, y)
                model_type = "Histogram Gradient Boosting"

        predictions = []
        today = date.today()
        by_product = self._events_by_product_day(events)
        for product in products:
            product_events = by_product.get(product["id"], {})
            features, evidence = self._current_features(product, product_events, today)
            if model is not None:
                daily = max(0.0, float(model.predict(np.asarray([features]))[0]))
            else:
                recent = evidence["weighted_7d"]
                previous = evidence["weighted_previous_7d"]
                trend = max(0.65, min(1.6, (recent + 1.0) / (previous + 1.0)))
                daily = recent / 7.0 * trend
            demand = round(daily * settings["horizon_days"], 1)
            views = evidence["views_30d"]
            baskets = evidence["baskets_30d"]
            conversion = round((baskets + 1) / (views + 4) * 100, 1)
            stock = product["stock"]
            coverage = stock / demand if demand > 0 else 99
            if stock <= 0:
                risk = "Critical"
            elif coverage < 0.75:
                risk = "High"
            elif coverage < 1.5:
                risk = "Medium"
            else:
                risk = "Low"
            evidence_count = evidence["events_30d"]
            confidence = "High" if model is not None and evidence_count >= 50 else "Medium" if evidence_count >= 15 else "Low"
            action = self._recommendation(risk, demand, conversion, stock)
            predictions.append({
                "product_id": product["id"], "name": product["name"],
                "expected_demand": demand, "horizon_days": settings["horizon_days"],
                "conversion_probability": conversion, "stock": stock,
                "stock_risk": risk, "confidence": confidence,
                "views_30d": views, "tryons_30d": evidence["tryons_30d"],
                "baskets_30d": baskets, "recommendation": action,
            })
        risk_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        predictions.sort(key=lambda item: (risk_order[item["stock_risk"]], -item["expected_demand"]))
        metrics = {
            "validation_mae": validation_mae,
            "training_rows": len(training_rows),
            "event_count": len(events),
            "data_start": min((event["created_at"] for event in events), default=None),
            "data_end": max((event["created_at"] for event in events), default=None),
        }
        with database_connection() as connection:
            cursor = connection.execute(
                "INSERT INTO prediction_runs(model_type,status,sample_count,horizon_days,metrics,predictions,created_by) "
                "VALUES(?,?,?,?,?,?,?)",
                (model_type, "complete", len(training_rows), settings["horizon_days"],
                 json.dumps(metrics), json.dumps(predictions), created_by),
            )
            run_id = cursor.lastrowid
        return {"run_id": run_id, "model_type": model_type, "metrics": metrics,
                "settings": settings, "predictions": predictions,
                "generated_at": datetime.now().strftime("%d %b %Y, %H:%M:%S")}

    def latest(self):
        with database_connection() as connection:
            row = connection.execute("SELECT * FROM prediction_runs ORDER BY id DESC LIMIT 1").fetchone()
        if row is None:
            return None
        return {
            "run_id": row["id"], "model_type": row["model_type"],
            "metrics": json.loads(row["metrics"]), "predictions": json.loads(row["predictions"]),
            "settings": {"horizon_days": row["horizon_days"]},
            "generated_at": row["created_at"],
        }

    def export_csv(self, result):
        EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        path = EXPORTS_DIR / f"predictions_{datetime.now():%Y%m%d_%H%M%S}.csv"
        with path.open("w", newline="", encoding="utf-8-sig") as handle:
            fields = ["name", "expected_demand", "horizon_days", "conversion_probability",
                      "stock", "stock_risk", "confidence", "views_30d", "tryons_30d",
                      "baskets_30d", "recommendation"]
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for item in result["predictions"]:
                writer.writerow({key: item.get(key) for key in fields})
        return path

    def _load_data(self):
        with database_connection() as connection:
            products = [dict(row) for row in connection.execute(
                "SELECT p.id,p.name,p.price,p.discount,COALESCE(SUM(s.quantity),0) AS stock "
                "FROM products p LEFT JOIN product_sizes s ON s.product_id=p.id "
                "WHERE p.active=1 GROUP BY p.id"
            ).fetchall()]
            events = [dict(row) for row in connection.execute(
                "SELECT product_id,event_type,created_at FROM analytics_events "
                "WHERE product_id IS NOT NULL AND created_at>=datetime('now','-180 days') "
                "AND event_type IN ('product_viewed','tryon_started','basket_added') ORDER BY created_at"
            ).fetchall()]
        return products, events

    def _events_by_product_day(self, events):
        grouped = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        for event in events:
            day = datetime.fromisoformat(event["created_at"]).date()
            grouped[event["product_id"]][day][event["event_type"]] += 1
        return grouped

    def _training_rows(self, products, events):
        grouped = self._events_by_product_day(events)
        rows = []
        if not events:
            return rows
        first = min(datetime.fromisoformat(item["created_at"]).date() for item in events)
        last = max(datetime.fromisoformat(item["created_at"]).date() for item in events)
        product_map = {item["id"]: item for item in products}
        for product_id, days in grouped.items():
            product = product_map.get(product_id)
            if not product:
                continue
            current = first + timedelta(days=14)
            while current < last:
                features, _ = self._current_features(product, days, current)
                target_day = days.get(current + timedelta(days=1), {})
                target = sum(target_day.get(kind, 0) * weight for kind, weight in self.EVENT_WEIGHTS.items())
                rows.append((features, target, current))
                current += timedelta(days=1)
        rows.sort(key=lambda item: item[2])
        return [(features, target) for features, target, _ in rows]

    def _current_features(self, product, days, reference_day):
        def counts(start_days, end_days):
            result = defaultdict(int)
            for offset in range(start_days, end_days):
                for kind, value in days.get(reference_day - timedelta(days=offset), {}).items():
                    result[kind] += value
            return result
        recent = counts(0, 7)
        previous = counts(7, 14)
        month = counts(0, 30)
        weighted_recent = sum(recent[kind] * weight for kind, weight in self.EVENT_WEIGHTS.items())
        weighted_previous = sum(previous[kind] * weight for kind, weight in self.EVENT_WEIGHTS.items())
        weekday = reference_day.weekday()
        features = [
            weighted_recent, weighted_previous,
            recent["product_viewed"], recent["tryon_started"], recent["basket_added"],
            float(product.get("stock", 0)), float(product.get("price", 0)),
            int(bool(product.get("discount"))),
            math.sin(weekday * 2 * math.pi / 7), math.cos(weekday * 2 * math.pi / 7),
        ]
        evidence = {
            "weighted_7d": weighted_recent, "weighted_previous_7d": weighted_previous,
            "views_30d": month["product_viewed"], "tryons_30d": month["tryon_started"],
            "baskets_30d": month["basket_added"], "events_30d": sum(month.values()),
        }
        return features, evidence

    @staticmethod
    def _recommendation(risk, demand, conversion, stock):
        if risk == "Critical":
            return "Out of stock: replenish or hide this product from active promotion."
        if risk == "High":
            return f"Prioritise replenishment; forecast demand ({demand}) is above safe stock coverage."
        if conversion >= 20:
            return "Strong conversion: keep visible and consider matching-item promotion."
        if demand >= 5 and conversion < 8:
            return "High interest but low basket conversion: review price, fit, image and size availability."
        return "Monitor; no immediate intervention is indicated."
