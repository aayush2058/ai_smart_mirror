import json
from pathlib import Path

from paths import CATALOGUE_PATH, PROJECT_ROOT
from services.product_service import ProductService


class TryOnCatalogueService:
    """Builds the try-on catalogue from SQLite with a JSON safety fallback."""

    def __init__(self, product_service=None, fallback_path=None):
        self.product_service = product_service or ProductService()
        self.fallback_path = Path(fallback_path or CATALOGUE_PATH)
        self.source = "sqlite"

    def load_products(self):
        products = []

        try:
            summaries = self.product_service.get_products()

            for summary in summaries:
                if not summary.get("tryon_enabled"):
                    continue

                product = self.product_service.get_product(summary.get("id"))
                converted = self._convert_product(product)

                if converted is not None:
                    products.append(converted)
        except Exception as error:
            print(f"SQLite try-on catalogue unavailable: {error}")

        if products:
            self.source = "sqlite"
            return products

        self.source = "json-fallback"
        return self._load_fallback()

    def update_fit(self, product, fit):
        product_id = product.get("id")
        if not isinstance(product_id, int):
            return False
        return self.product_service.update_tryon_settings(product_id, fit)

    def _convert_product(self, product):
        if not product:
            return None

        image = product.get("image_path") or product.get("image") or ""
        if not image or not (PROJECT_ROOT / image).is_file():
            return None

        tryon_category = self._category_from_image(image)
        if tryon_category is None:
            tryon_category = self._category_from_product(product)
        if tryon_category is None:
            return None

        settings = product.get("tryon_settings") or {}
        converted = dict(product)
        converted["image"] = image
        converted["tryon_category"] = tryon_category
        converted["fit"] = {
            "width_scale": settings.get("width_scale", 1.0),
            "height_scale": settings.get("height_scale", 1.0),
            "vertical_offset": settings.get("vertical_offset", 0.0),
            "horizontal_offset": settings.get("horizontal_offset", 0),
        }
        return converted

    @staticmethod
    def _category_from_image(image):
        parts = {part.lower() for part in Path(image).parts}
        if "shirts" in parts:
            return "Shirts"
        if "pants" in parts:
            return "Pants"
        return None

    @staticmethod
    def _category_from_product(product):
        category = product.get("category")
        if category == "Upper Fit":
            return "Shirts"
        if category == "Lower Fit":
            return "Pants"

        tryon_category = product.get("tryon_category")
        if tryon_category in {"Shirts", "Pants"}:
            return tryon_category
        return None

    def _load_fallback(self):
        try:
            with self.fallback_path.open("r", encoding="utf-8") as file:
                products = json.load(file)
            return products if isinstance(products, list) else []
        except (OSError, json.JSONDecodeError):
            return []
