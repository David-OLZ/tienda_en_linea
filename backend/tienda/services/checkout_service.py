"""Datos del cliente y resumen final de la compra."""
from ..config import CURRENCY, TAX_RATE
from ..errors import EmptyCartError, IncompleteCheckoutError, StockError
from ..validators import validate_customer


class CheckoutService:
    def __init__(self, cart_service, cart_repo):
        self._cart_service = cart_service
        self._carts = cart_repo

    def save_customer(self, cart_id, data):
        cart = self._cart_service.get_cart(cart_id)
        if not cart["items"]:
            raise EmptyCartError("Tu carrito está vacío. Agrega productos antes de continuar.")
        customer = validate_customer(data)
        self._carts.save_customer(cart_id, customer)
        return customer

    def get_customer(self, cart_id):
        self._cart_service.get_cart(cart_id)  # valida que el carrito exista
        return self._carts.get_customer(cart_id)

    def get_summary(self, cart_id):
        cart = self._cart_service.get_cart(cart_id)
        if not cart["items"]:
            raise EmptyCartError("Tu carrito está vacío. Agrega productos antes de continuar.")
        if cart["has_issues"]:
            problems = [i for i in cart["items"] if i["issue"]]
            raise StockError(
                "Algunos productos ya no tienen existencia suficiente. Revisa tu carrito.",
                details={"items": [{"product_id": i["product_id"], "message": i["issue_message"]} for i in problems]},
            )
        customer = self._carts.get_customer(cart_id)
        if customer is None:
            raise IncompleteCheckoutError("Falta capturar tus datos de contacto y entrega.")
        return {
            "cart_id": cart_id,
            "currency": CURRENCY,
            "tax_rate_percent": int(TAX_RATE * 100),
            "items": cart["items"],
            "totals": cart["totals"],
            "customer": customer,
        }
