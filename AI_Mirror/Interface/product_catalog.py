import json
from pathlib import Path


class ProductCatalog:
    def __init__(self):
        self.project_root = Path(__file__).resolve().parent
        self.catalogue_path = self.project_root / "data" / "catalogue.json"
        self.products = self.load_products()

    def load_products(self):
        try:
            print("PROJECT ROOT:", self.project_root)
            print("CATALOGUE PATH:", self.catalogue_path)
            print("CATALOGUE EXISTS:", self.catalogue_path.exists())

            if not self.catalogue_path.exists():
                print("Catalogue file not found.")
                return []

            with open(self.catalogue_path, "r", encoding="utf-8") as file:
                return json.load(file)

        except json.JSONDecodeError as error:
            print("Catalogue JSON is broken.")
            print("JSON error:", error)
            return []

        except Exception as error:
            print(f"Unexpected catalogue error: {error}")
            return []

    def get_products(self, department=None, category=None):
        results = self.products

        if department:
            results = [
                product for product in results
                if product.get("department") == department
            ]

        if category:
            results = [
                product for product in results
                if product.get("category") == category
            ]

        return results

    def get_product_by_id(self, product_id):
        for product in self.products:
            if product.get("id") == product_id:
                return product

        return None

    def get_discounted_products(self):
        return [
            product for product in self.products
            if product.get("discount") is True
        ]