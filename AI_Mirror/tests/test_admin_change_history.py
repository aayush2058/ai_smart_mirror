import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from database.repositories import ProductRepository
from database.schema import create_database_schema
from models.product import Product
from services.admin_undo_service import AdminUndoService


class AdminChangeHistoryTests(unittest.TestCase):
    def test_sections_can_be_undone_independently_for_24_hours(self):
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "test.db"
            with patch("database.connection.DATABASE_PATH", database_path):
                create_database_schema()
                repository = ProductRepository()
                product_id = repository.create_product(Product(
                    product_code="history-shirt", name="History shirt",
                    department="Men", category="Shirts", price=40,
                    description="Original description",
                ))
                service = AdminUndoService()
                with patch.object(service, "ensure_hourly_backup", return_value=None):
                    service.apply_product_change(product_id, "History shirt", "Price", {"price": 30})
                    service.apply_product_change(product_id, "History shirt", "Description", {"description": "New description"})
                history = service.get_change_history()
                price_change = next(item for item in history if item["section"] == "Price")
                self.assertTrue(price_change["can_undo"])
                created = datetime.strptime(price_change["created_at"], "%Y-%m-%d %H:%M:%S")
                expires = datetime.strptime(price_change["expires_at"], "%Y-%m-%d %H:%M:%S")
                self.assertEqual((expires - created).total_seconds(), 24 * 60 * 60)
                success, _ = service.undo_history_change(price_change["id"])
                product = repository.get_product_by_id(product_id)

        self.assertTrue(success)
        self.assertEqual(product["price"], 40)
        self.assertEqual(product["description"], "New description")


if __name__ == "__main__":
    unittest.main()
