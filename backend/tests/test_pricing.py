import unittest

from tienda.pricing import calculate_tax, calculate_totals, line_total


class PricingTests(unittest.TestCase):
    def test_line_total(self):
        self.assertEqual(line_total(1999, 3), 5997)

    def test_totals_with_iva(self):
        t = calculate_totals([(10000, 2), (5050, 1)])
        self.assertEqual(t.items_count, 3)
        self.assertEqual(t.subtotal_cents, 25050)
        self.assertEqual(t.tax_cents, 4008)  # 250.50 * 0.16 = 40.08
        self.assertEqual(t.total_cents, 29058)

    def test_tax_rounds_half_up(self):
        self.assertEqual(calculate_tax(1005), 161)  # 160.8 -> 161
        self.assertEqual(calculate_tax(103), 16)    # 16.48 -> 16
        self.assertEqual(calculate_tax(125), 20)    # 20.0 exacto

    def test_empty_cart_is_zero(self):
        t = calculate_totals([])
        self.assertEqual((t.items_count, t.subtotal_cents, t.tax_cents, t.total_cents), (0, 0, 0, 0))

    def test_negative_values_rejected(self):
        with self.assertRaises(ValueError):
            line_total(-1, 1)
        with self.assertRaises(ValueError):
            calculate_totals([(100, -2)])


if __name__ == "__main__":
    unittest.main()
