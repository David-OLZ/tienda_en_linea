import unittest

from tienda.errors import NotFoundError, StockError, ValidationError
from tests.helpers import StoreTestCase


class CartServiceTests(StoreTestCase):
    def setUp(self):
        super().setUp()
        self.carts = self.services.carts

    def test_new_cart_is_empty(self):
        cart = self.carts.get_cart(self.cart_id)
        self.assertEqual(cart["items"], [])
        self.assertEqual(cart["totals"]["total_cents"], 0)
        self.assertFalse(cart["has_issues"])

    def test_unknown_cart(self):
        with self.assertRaises(NotFoundError):
            self.carts.get_cart("no-existe")

    def test_add_item_and_totals(self):
        cart = self.carts.add_item(self.cart_id, 1, 2)
        self.assertEqual(cart["items"][0]["quantity"], 2)
        self.assertEqual(cart["totals"]["subtotal_cents"], 20000)
        self.assertEqual(cart["totals"]["tax_cents"], 3200)
        self.assertEqual(cart["totals"]["total_cents"], 23200)

    def test_adding_same_product_accumulates(self):
        self.carts.add_item(self.cart_id, 1, 2)
        cart = self.carts.add_item(self.cart_id, 1, 1)
        self.assertEqual(cart["items"][0]["quantity"], 3)

    def test_cannot_exceed_stock(self):
        with self.assertRaises(StockError) as ctx:
            self.carts.add_item(self.cart_id, 2, 3)  # hay 2
        self.assertIn("2 unidades", ctx.exception.message)

    def test_cannot_exceed_stock_with_items_already_in_cart(self):
        self.carts.add_item(self.cart_id, 1, 4)  # hay 5
        with self.assertRaises(StockError) as ctx:
            self.carts.add_item(self.cart_id, 1, 2)
        self.assertIn("1 unidad", ctx.exception.message)
        self.assertEqual(self.carts.get_cart(self.cart_id)["items"][0]["quantity"], 4)

    def test_cart_already_has_all_units(self):
        self.carts.add_item(self.cart_id, 2, 2)
        with self.assertRaises(StockError) as ctx:
            self.carts.add_item(self.cart_id, 2, 1)
        self.assertIn("todas las unidades", ctx.exception.message)

    def test_out_of_stock_product(self):
        with self.assertRaises(StockError) as ctx:
            self.carts.add_item(self.cart_id, 3, 1)
        self.assertIn("agotado", ctx.exception.message)

    def test_invalid_quantities(self):
        for bad in (0, -2, "x", 1.5, None):
            with self.subTest(quantity=bad):
                with self.assertRaises(ValidationError):
                    self.carts.add_item(self.cart_id, 1, bad)

    def test_unknown_product(self):
        with self.assertRaises(NotFoundError):
            self.carts.add_item(self.cart_id, 999, 1)

    def test_set_quantity(self):
        self.carts.add_item(self.cart_id, 1, 1)
        cart = self.carts.set_quantity(self.cart_id, 1, 4)
        self.assertEqual(cart["items"][0]["quantity"], 4)

    def test_set_quantity_respects_stock(self):
        self.carts.add_item(self.cart_id, 1, 1)
        with self.assertRaises(StockError):
            self.carts.set_quantity(self.cart_id, 1, 6)

    def test_set_quantity_requires_item_in_cart(self):
        with self.assertRaises(NotFoundError):
            self.carts.set_quantity(self.cart_id, 1, 2)

    def test_set_quantity_rejects_zero(self):
        self.carts.add_item(self.cart_id, 1, 1)
        with self.assertRaises(ValidationError):
            self.carts.set_quantity(self.cart_id, 1, 0)

    def test_remove_item(self):
        self.carts.add_item(self.cart_id, 1, 1)
        self.assertEqual(self.carts.remove_item(self.cart_id, 1)["items"], [])

    def test_remove_missing_item(self):
        with self.assertRaises(NotFoundError):
            self.carts.remove_item(self.cart_id, 1)

    def test_clear(self):
        self.carts.add_item(self.cart_id, 1, 1)
        self.carts.add_item(self.cart_id, 4, 1)
        self.assertEqual(self.carts.clear(self.cart_id)["items"], [])

    def test_carts_are_independent(self):
        other = self.carts.create_cart()
        self.carts.add_item(self.cart_id, 1, 1)
        self.assertEqual(self.carts.get_cart(other)["items"], [])

    def test_stock_drop_marks_line_with_issue(self):
        self.carts.add_item(self.cart_id, 1, 4)
        self.set_stock(1, 2)
        cart = self.carts.get_cart(self.cart_id)
        self.assertTrue(cart["has_issues"])
        self.assertEqual(cart["items"][0]["issue"], "exceeds_stock")

    def test_product_sold_out_marks_line_with_issue(self):
        self.carts.add_item(self.cart_id, 1, 1)
        self.set_stock(1, 0)
        self.assertEqual(self.carts.get_cart(self.cart_id)["items"][0]["issue"], "out_of_stock")


if __name__ == "__main__":
    unittest.main()
