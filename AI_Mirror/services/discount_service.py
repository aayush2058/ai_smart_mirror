class DiscountService:
    @staticmethod
    def calculate(original_price, enabled=False, discount_type=None, discount_value=None, legacy_price=None):
        original = max(0.0, float(original_price or 0))
        final = original
        dtype = discount_type if discount_type in ("amount", "percentage") else None
        value = float(discount_value or 0)
        if enabled and dtype == "amount" and value > 0:
            final = max(0.0, original - value)
        elif enabled and dtype == "percentage" and value > 0:
            value = min(value, 100.0)
            final = original * (1.0 - value / 100.0)
        elif enabled and legacy_price is not None:
            final = max(0.0, min(original, float(legacy_price)))
            dtype, value = "amount", original - final
        saving = max(0.0, original - final)
        percentage = (saving / original * 100.0) if original else 0.0
        active = bool(enabled and saving > 0)
        label = f"{value:g}% OFF" if active and dtype == "percentage" else f"£{saving:.2f} OFF" if active else ""
        return {"active": active, "discount_type": dtype, "discount_value": value if active else None, "original_price": original, "final_price": round(final, 2), "saving_amount": round(saving, 2), "saving_percentage": round(percentage, 1), "discount_text": label}
