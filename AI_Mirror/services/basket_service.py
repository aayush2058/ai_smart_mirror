import json


class BasketService:
    def __init__(self):
        self.items = []

    def add(self, product, size, quantity=1):
        quantity = max(1, min(10, int(quantity)))
        product_id = product.get("id")
        for item in self.items:
            if item["product_id"] == product_id and item["size"] == size:
                item["quantity"] += quantity
                return

        self.items.append({
            "product_id": product_id,
            "product_code": product.get("product_code"),
            "name": product.get("name", "Product"),
            "size": size,
            "quantity": quantity,
            "price": float(product.get("price_value", 0)),
            "original_price": float(product.get("original_price", product.get("price_value", 0))),
            "location": product.get("location", ""),
        })

    def clear(self):
        self.items.clear()

    def total(self):
        return round(sum(item["price"] * item["quantity"] for item in self.items), 2)

    def original_total(self):
        return round(sum(item["original_price"] * item["quantity"] for item in self.items), 2)

    def savings_total(self):
        return round(self.original_total() - self.total(), 2)

    def remove(self, product_id, size):
        self.items = [item for item in self.items
                      if not (item["product_id"] == product_id and item["size"] == size)]

    def qr_payload(self):
        return json.dumps({
            "type": "AI Smart Mirror Basket",
            "items": self.items,
            "total": self.total(),
            "original_total": self.original_total(),
            "savings": self.savings_total(),
        }, separators=(",", ":"))
