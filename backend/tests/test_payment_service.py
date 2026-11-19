import unittest

from tienda.errors import EmptyCartError, IncompleteCheckoutError, PaymentUnavailableError
from tienda.services.payment_service import UNAVAILABLE_MESSAGE
from tests.helpers import CUSTOMER, StoreTestCase


class PaymentServiceTests(StoreTestCase):
    def test_payment_never_succeeds(self):
        self.services.carts.add_item(self.cart_id, 1, 1)
        self.services.checkout.save_customer(self.cart_id, CUSTOMER)
        with self.assertRaises(PaymentUnavailableError) as ctx:
            self.services.payments.attempt_payment(self.cart_id)
        self.assertEqual(ctx.exception.message, UNAVAILABLE_MESSAGE)

    def test_payment_does_not_change_stock_or_cart(self):
        self.services.carts.add_item(self.cart_id, 1, 2)
        self.services.checkout.save_customer(self.cart_id, CUSTOMER)
        with self.assertRaises(PaymentUnavailableError):
            self.services.payments.attempt_payment(self.cart_id)
        self.assertEqual(self.catalog_repo.get_product(1)["stock"], 5)
        self.assertEqual(self.services.carts.get_cart(self.cart_id)["items"][0]["quantity"], 2)

    def test_empty_cart_is_reported_before_payment(self):
        with self.assertRaises(EmptyCartError):
            self.services.payments.attempt_payment(self.cart_id)

    def test_missing_customer_is_reported_before_payment(self):
        self.services.carts.add_item(self.cart_id, 1, 1)
        with self.assertRaises(IncompleteCheckoutError):
            self.services.payments.attempt_payment(self.cart_id)


if __name__ == "__main__":
    unittest.main()
