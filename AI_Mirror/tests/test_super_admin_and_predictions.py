import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from database.repositories import ProductRepository
from database.schema import create_database_schema
from models.product import Product
from services.auth_service import AuthService
from services.prediction_service import PredictionService


class SuperAdminAndPredictionTests(unittest.TestCase):
    def test_role_login_and_account_change_undo(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.db"
            with patch("database.connection.DATABASE_PATH", path):
                create_database_schema()
                auth = AuthService()
                root_id = auth.create_user("root.manager", "StrongPass123", "super_admin")
                admin_id = auth.create_user("shop.admin", "AnotherPass123", "admin", root_id)
                self.assertEqual(auth.authenticate("root.manager", "StrongPass123")["role"], "super_admin")
                auth.set_user_active(admin_id, False, root_id)
                change = auth.account_history()[0]
                success, _ = auth.undo_account_change(change["id"], root_id)
                restored = next(user for user in auth.list_users() if user["id"] == admin_id)
        self.assertTrue(success)
        self.assertEqual(restored["active"], 1)

    def test_prediction_fallback_is_transparent_and_persisted(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.db"
            with patch("database.connection.DATABASE_PATH", path):
                create_database_schema()
                repository = ProductRepository()
                product_id = repository.create_product(Product(
                    product_code="forecast-shirt", name="Forecast Shirt",
                    department="Men", category="Shirts", price=30,
                    sizes=[{"size": "M", "quantity": 2}],
                ))
                from database.connection import database_connection
                with database_connection() as connection:
                    for event_type in ("product_viewed", "tryon_started", "basket_added"):
                        connection.execute(
                            "INSERT INTO analytics_events(session_id,event_type,product_id) VALUES('test',?,?)",
                            (event_type, product_id),
                        )
                service = PredictionService()
                result = service.generate()
                latest = service.latest()
        self.assertEqual(result["model_type"], "Statistical fallback")
        self.assertEqual(latest["run_id"], result["run_id"])
        self.assertEqual(result["predictions"][0]["stock"], 2)
        self.assertIn(result["predictions"][0]["confidence"], ("Low", "Medium", "High"))


if __name__ == "__main__":
    unittest.main()
