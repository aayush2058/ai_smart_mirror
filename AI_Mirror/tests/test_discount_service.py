import unittest

from services.discount_service import DiscountService


class DiscountServiceTests(unittest.TestCase):
    def test_amount_discount(self):
        result = DiscountService.calculate(40, True, "amount", 5)
        self.assertEqual(result["final_price"], 35)
        self.assertEqual(result["discount_text"], "£5.00 OFF")

    def test_percentage_discount(self):
        result = DiscountService.calculate(40, True, "percentage", 25)
        self.assertEqual(result["final_price"], 30)
        self.assertEqual(result["discount_text"], "25% OFF")

    def test_legacy_final_price_remains_compatible(self):
        result = DiscountService.calculate(40, True, legacy_price=32)
        self.assertEqual(result["final_price"], 32)
        self.assertEqual(result["saving_amount"], 8)


if __name__ == "__main__":
    unittest.main()
