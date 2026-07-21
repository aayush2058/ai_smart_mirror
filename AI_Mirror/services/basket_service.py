import json


class BasketService:
    def __init__(self):
        self.items = []

    def add(self, product, size):
        product_id = product.get("id")
        for item in self.items:
            if item["product_id"] == product_id and item["size"] == size:
                item["quantity"] += 1
                return

        self.items.append({
            "product_id": product_id,
            "product_code": product.get("product_code"),
            "name": product.get("name", "Product"),
            "size": size,
            "quantity": 1,
            "price": float(product.get("price_value", 0)),
            "location": product.get("location", ""),
        })

    def clear(self):
        self.items.clear()

    def total(self):
        return round(sum(item["price"] * item["quantity"] for item in self.items), 2)

    def qr_payload(self):
        return json.dumps({
            "type": "AI Smart Mirror Basket",
            "items": self.items,
            "total": self.total(),
        }, separators=(",", ":"))
