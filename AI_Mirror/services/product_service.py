import json

from paths import CATALOGUE_PATH
from database.repositories import ProductRepository
from models.product import Product


class ProductCatalog:
    """
    Customer catalogue reader.

    Now reads products from SQLite first.
    If database is empty, it falls back to catalogue.json.
    """

    def __init__(self):
        self.repository = ProductRepository()
        self.catalogue_path = CATALOGUE_PATH
        self.products = self.load_products()

    def load_products(self):
        database_products = self.repository.get_all_products()

        if database_products:
            return self.convert_database_products(database_products)

        return self.load_json_products()

    def load_json_products(self):
        if not self.catalogue_path.exists():
            print(f"Catalogue file not found: {self.catalogue_path}")
            return []

        try:
            with self.catalogue_path.open("r", encoding="utf-8") as file:
                products = json.load(file)

            if not isinstance(products, list):
                print("Catalogue must contain a JSON list.")
                return []

            return products

        except json.JSONDecodeError as error:
            print(f"Catalogue JSON error: {error}")
            return []

        except OSError as error:
            print(f"Could not read catalogue: {error}")
            return []

    def convert_database_products(self, products):
        converted = []

        for product in products:
            converted.append({
                "id": product.get("id"),
                "name": product.get("name"),
                "department": product.get("department"),
                "category": product.get("category"),
                "price": f"£{product.get('price')}",
                "colour": product.get("colour"),
                "description": product.get("description"),
                "image": product.get("image_path"),
                "image_path": product.get("image_path"),
                "available": bool(product.get("available")),
                "discount": bool(product.get("discount")),
                "discount_price": product.get("discount_price"),
                "location": product.get("location"),
                "tryon_category": product.get("tryon_category"),
            })

        return converted

    def reload(self):
        self.products = self.load_products()
        return self.products

    def get_products(self, department=None, category=None):
        self.reload()

        results = self.products

        if department:
            results = [
                product
                for product in results
                if product.get("department") == department
            ]

        if category:
            results = [
                product
                for product in results
                if product.get("category") == category
            ]

        return results

    def get_product_by_id(self, product_id):
        self.reload()

        for product in self.products:
            if product.get("id") == product_id:
                return product

        return None

    def get_discounted_products(self):
        self.reload()

        return [
            product
            for product in self.products
            if product.get("discount", False)
        ]
    
    
class ProductService:
    def __init__(self):
        self.repository = ProductRepository()

    def add_product(self, product_data: dict) -> int:
        required_fields = [
            "product_code",
            "name",
            "department",
            "category",
            "price",
        ]

        missing_fields = [
            field
            for field in required_fields
            if product_data.get(field) in (None, "")
        ]

        if missing_fields:
            raise ValueError(
                "Missing required fields: "
                + ", ".join(missing_fields)
            )

        price = float(product_data["price"])

        if price < 0:
            raise ValueError("Product price cannot be negative.")

        product = Product(
            product_code=product_data["product_code"],
            name=product_data["name"],
            department=product_data["department"],
            category=product_data["category"],
            price=price,
            colour=product_data.get("colour", ""),
            description=product_data.get("description", ""),
            image_path=product_data.get("image_path", ""),
            available=product_data.get("available", True),
            discount=product_data.get("discount", False),
            discount_price=product_data.get("discount_price"),
            location=product_data.get("location", ""),
            tryon_enabled=product_data.get("tryon_enabled", False),
            tryon_category=product_data.get("tryon_category"),
            active=True,
            sizes=product_data.get("sizes", []),
            width_scale=product_data.get("width_scale", 1.0),
            height_scale=product_data.get("height_scale", 1.0),
            vertical_offset=product_data.get("vertical_offset", 0.0),
            horizontal_offset=product_data.get("horizontal_offset", 0),
        )

        return self.repository.create_product(product)

    def get_products(self):
        return self.repository.get_all_products()

    def get_product(self, product_id: int):
        return self.repository.get_product_by_id(product_id)

    def update_product(self, product_id: int, changes: dict):
        return self.repository.update_product(
            product_id,
            changes
        )

    def delete_product(self, product_id: int):
        return self.repository.soft_delete_product(
            product_id
        )

    def restore_product(self, product_id: int):
        return self.repository.restore_product(
            product_id
        )
    
    def update_tryon_settings(self, product_id: int, settings: dict):
        return self.repository.update_tryon_settings(product_id, settings)
    
    def get_deleted_products(self):
        return self.repository.get_deleted_products()
    
    def get_product_for_tryon(self, product_id: int):
        return self.repository.get_product_by_id(product_id)