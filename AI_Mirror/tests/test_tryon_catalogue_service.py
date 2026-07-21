import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from services.tryon_catalogue_service import TryOnCatalogueService


class FakeProductService:
    def __init__(self, products):
        self.products = products
        self.saved = None

    def get_products(self):
        return self.products

    def get_product(self, product_id):
        return next(
            (product for product in self.products if product["id"] == product_id),
            None,
        )

    def update_tryon_settings(self, product_id, fit):
        self.saved = (product_id, fit)
        return True


class FailingProductService:
    def get_products(self):
        raise RuntimeError("database unavailable")


class TryOnCatalogueServiceTests(unittest.TestCase):
    def test_sqlite_product_uses_image_folder_category(self):
        product = {
            "id": 3,
            "name": "Test shirt",
            "category": "Upper Fit",
            "tryon_enabled": 1,
            "tryon_category": "Pants",
            "image_path": "img/shirts/shirt1.png",
            "tryon_settings": {"width_scale": 2.25},
        }
        service = TryOnCatalogueService(FakeProductService([product]))

        with patch("services.tryon_catalogue_service.PROJECT_ROOT", Path.cwd()):
            catalogue = service.load_products()

        self.assertEqual(service.source, "sqlite")
        self.assertEqual(catalogue[0]["tryon_category"], "Shirts")
        self.assertEqual(catalogue[0]["fit"]["width_scale"], 2.25)

    def test_missing_database_images_use_json_fallback(self):
        product = {
            "id": 1,
            "tryon_enabled": 1,
            "image_path": "img/missing.png",
        }

        with tempfile.TemporaryDirectory() as directory:
            fallback = Path(directory) / "catalogue.json"
            fallback.write_text(json.dumps([{"id": "backup"}]), encoding="utf-8")
            service = TryOnCatalogueService(
                FakeProductService([product]),
                fallback,
            )
            catalogue = service.load_products()

        self.assertEqual(service.source, "json-fallback")
        self.assertEqual(catalogue, [{"id": "backup"}])

    def test_fit_updates_are_saved_to_sqlite(self):
        product_service = FakeProductService([])
        service = TryOnCatalogueService(product_service)
        fit = {"width_scale": 2.0}

        self.assertTrue(service.update_fit({"id": 7}, fit))
        self.assertEqual(product_service.saved, (7, fit))

    def test_database_error_uses_json_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            fallback = Path(directory) / "catalogue.json"
            fallback.write_text(json.dumps([{"id": "backup"}]), encoding="utf-8")
            service = TryOnCatalogueService(FailingProductService(), fallback)
            catalogue = service.load_products()

        self.assertEqual(service.source, "json-fallback")
        self.assertEqual(catalogue, [{"id": "backup"}])


if __name__ == "__main__":
    unittest.main()
