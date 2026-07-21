import json
import unittest

from services.basket_service import BasketService


class BasketServiceTests(unittest.TestCase):
    def test_add_merge_total_and_qr_payload(self):
        basket = BasketService()
        product = {
            "id": 7,
            "product_code": "pants_001",
            "name": "Test Pants",
            "price_value": 20.0,
            "location": "A1",
        }
        basket.add(product, "M")
        basket.add(product, "M")

        self.assertEqual(len(basket.items), 1)
        self.assertEqual(basket.items[0]["quantity"], 2)
        self.assertEqual(basket.total(), 40.0)
        self.assertEqual(json.loads(basket.qr_payload())["total"], 40.0)

    def test_clear_removes_all_items(self):
        basket = BasketService()
        basket.add({"id": 1, "price_value": 1}, "S")
        basket.clear()
        self.assertEqual(basket.items, [])


if __name__ == "__main__":
    unittest.main()
