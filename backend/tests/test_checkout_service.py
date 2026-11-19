import unittest

from tienda.errors import EmptyCartError, IncompleteCheckoutError, StockError, ValidationError
from tests.helpers import CUSTOMER, StoreTestCase


class CheckoutServiceTests(StoreTestCase):
    def setUp(self):
        super().setUp()
        self.checkout = self.services.checkout
        self.carts = self.services.carts

    def test_cannot_save_customer_with_empty_cart(self):
        with self.assertRaises(EmptyCartError):
            self.checkout.save_customer(self.cart_id, CUSTOMER)

    def test_invalid_customer_is_not_saved(self):
        self.carts.add_item(self.cart_id, 1, 1)
        with self.assertRaises(ValidationError):
            self.checkout.save_customer(self.cart_id, {**CUSTOMER, "email": "mal"})
        self.assertIsNone(self.checkout.get_customer(self.cart_id))

    def test_save_and_read_customer(self):
        self.carts.add_item(self.cart_id, 1, 1)
        self.checkout.save_customer(self.cart_id, CUSTOMER)
        self.assertEqual(self.checkout.get_customer(self.cart_id)["phone"], "6561234567")

    def test_summary_requires_items(self):
        with self.assertRaises(EmptyCartError):
            self.checkout.get_summary(self.cart_id)

    def test_summary_requires_customer(self):
        self.carts.add_item(self.cart_id, 1, 1)
        with self.assertRaises(IncompleteCheckoutError):
            self.checkout.get_summary(self.cart_id)

    def test_summary_contains_everything(self):
        self.carts.add_item(self.cart_id, 1, 2)
        self.carts.add_item(self.cart_id, 2, 1)
        self.checkout.save_customer(self.cart_id, CUSTOMER)
        summary = self.checkout.get_summary(self.cart_id)
        self.assertEqual(len(summary["items"]), 2)
        self.assertEqual(summary["totals"]["subtotal_cents"], 25050)
        self.assertEqual(summary["totals"]["total_cents"], 29058)
        self.assertEqual(summary["customer"]["city"], "Ciudad Juárez")
        self.assertEqual(summary["tax_rate_percent"], 16)

    def test_summary_fails_if_stock_dropped(self):
        self.carts.add_item(self.cart_id, 1, 3)
        self.checkout.save_customer(self.cart_id, CUSTOMER)
        self.set_stock(1, 1)
        with self.assertRaises(StockError) as ctx:
            self.checkout.get_summary(self.cart_id)
        self.assertEqual(ctx.exception.details["items"][0]["product_id"], 1)


if __name__ == "__main__":
    unittest.main()
