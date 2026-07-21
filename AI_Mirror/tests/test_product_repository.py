import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from database.repositories import ProductRepository
from database.schema import create_database_schema
from models.product import Product


class ProductRepositoryTests(unittest.TestCase):
    def test_saving_fit_does_not_enable_disabled_tryon(self):
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "test.db"
            with patch("database.connection.DATABASE_PATH", database_path):
                create_database_schema()
                repository = ProductRepository()
                product_id = repository.create_product(Product(
                    product_code="disabled-shirt",
                    name="Disabled shirt",
                    department="Men",
                    category="Upper Fit",
                    price=10.0,
                    image_path="img/shirts/shirt5.png",
                    tryon_enabled=False,
                    tryon_category="Shirts",
                ))

                repository.update_tryon_settings(
                    product_id,
                    {"width_scale": 2.0},
                )
                product = repository.get_product_by_id(product_id)

        self.assertEqual(product["tryon_enabled"], 0)
        self.assertEqual(product["tryon_settings"]["width_scale"], 2.0)


if __name__ == "__main__":
    unittest.main()
