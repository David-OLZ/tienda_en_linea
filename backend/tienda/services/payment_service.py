"""Módulo de pago: todavía no hay proveedor contratado, por lo que nunca cobra.

No recibe ni almacena datos de tarjeta y no se conecta a ningún servicio externo.
"""
from ..errors import PaymentUnavailableError

UNAVAILABLE_MESSAGE = (
    "El pago en línea todavía no está disponible. "
    "No se realizó ningún cargo y tu compra no fue procesada."
)


class PaymentService:
    def __init__(self, checkout_service):
        self._checkout = checkout_service

    def attempt_payment(self, cart_id):
        # Primero se exige que la compra esté completa; después se informa que no se puede cobrar.
        self._checkout.get_summary(cart_id)
        raise PaymentUnavailableError(UNAVAILABLE_MESSAGE)
