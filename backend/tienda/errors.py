"""Errores de dominio. Cada uno sabe qué código HTTP le corresponde."""


class StoreError(Exception):
    code = "store_error"
    http_status = 400

    def __init__(self, message, fields=None, details=None):
        super().__init__(message)
        self.message = message
        self.fields = fields or {}
        self.details = details or {}

    def to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "fields": self.fields,
            "details": self.details,
        }


class BadRequestError(StoreError):
    code = "bad_request"
    http_status = 400


class NotFoundError(StoreError):
    code = "not_found"
    http_status = 404


class ValidationError(StoreError):
    code = "validation_error"
    http_status = 422


class StockError(StoreError):
    code = "insufficient_stock"
    http_status = 409


class EmptyCartError(StoreError):
    code = "empty_cart"
    http_status = 409


class IncompleteCheckoutError(StoreError):
    code = "incomplete_checkout"
    http_status = 409


class PaymentUnavailableError(StoreError):
    code = "payment_unavailable"
    http_status = 501
