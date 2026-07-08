import json

from paths import CATALOGUE_PATH, ensure_directories
from database.schema import create_database_schema
from services.product_service import ProductService


def convert_price(price_value):
    if isinstance(price_value, (int, float)):
        return float(price_value)

    return float(
        str(price_value)
        .replace("£", "")
        .replace(",", "")
        .strip()
    )


def main():
    ensure_directories()
    create_database_schema()

    service = ProductService()

    with CATALOGUE_PATH.open("r", encoding="utf-8") as file:
        products = json.load(file)

    imported = 0

    for product in products:
        product_data = {
            "product_code": product.get("id"),
            "name": product.get("name"),
            "department": product.get("department", "Men"),
            "category": product.get("category"),
            "price": convert_price(product.get("price", 0)),
            "colour": product.get("colour", ""),
            "description": product.get("description", ""),
            "image_path": product.get("image", ""),
            "available": product.get("available", True),
            "discount": product.get("discount", False),
            "discount_price": product.get("discount_price"),
            "location": product.get("location", ""),
            "tryon_enabled": bool(product.get("tryon_category")),
            "tryon_category": product.get("tryon_category"),
            "sizes": [
                {"size": size, "quantity": 5}
                for size in product.get("sizes", [])
            ],
            "width_scale": product.get("fit", {}).get("width_scale", 1.0),
            "height_scale": product.get("fit", {}).get("height_scale", 1.0),
            "vertical_offset": product.get("fit", {}).get("vertical_offset", 0.0),
            "horizontal_offset": product.get("fit", {}).get("horizontal_offset", 0),
        }

        try:
            service.add_product(product_data)
            imported += 1
            print("Imported:", product.get("name"))

        except Exception as error:
            print("Skipped:", product.get("name"), "|", error)

    print(f"\nDone. Imported {imported} products.")


if __name__ == "__main__":
    main()