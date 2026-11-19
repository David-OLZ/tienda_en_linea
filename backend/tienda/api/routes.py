"""Definición de endpoints. Cada handler solo traduce la petición a llamadas de servicio."""
from dataclasses import dataclass

from ..config import CURRENCY, TAX_RATE
from ..errors import BadRequestError
from ..validators import MEXICAN_STATES


@dataclass
class Services:
    catalog: object
    carts: object
    checkout: object
    payments: object


def _int(value, name):
    try:
        if isinstance(value, bool):
            raise ValueError
        return int(value)
    except (TypeError, ValueError):
        raise BadRequestError(f"El parámetro «{name}» debe ser un número entero.") from None


def _body(body):
    if not isinstance(body, dict):
        raise BadRequestError("El cuerpo de la petición debe ser un objeto JSON.")
    return body


def register_routes(router, s):
    r = router.add

    r("GET", "/api/health", lambda p, q, b: {"status": "ok"})
    r("GET", "/api/config", lambda p, q, b: {
        "currency": CURRENCY, "tax_rate_percent": int(TAX_RATE * 100), "states": MEXICAN_STATES})

    # --- catálogo ---
    r("GET", "/api/categories", lambda p, q, b: {"categories": s.catalog.list_categories()})

    def list_products(p, q, b):
        category = q.get("category")
        return {"products": s.catalog.list_products(
            query=q.get("q", ""),
            category_id=_int(category, "category") if category else None,
            sort=q.get("sort", "name"),
            only_available=q.get("available") in ("1", "true"),
        )}
    r("GET", "/api/products", list_products)
    r("GET", "/api/products/{product_id}",
      lambda p, q, b: {"product": s.catalog.get_product(_int(p["product_id"], "product_id"))})

    # --- carrito ---
    r("POST", "/api/cart", lambda p, q, b: {"cart_id": s.carts.create_cart()}, status=201)
    r("GET", "/api/cart/{cart_id}", lambda p, q, b: s.carts.get_cart(p["cart_id"]))

    def add_item(p, q, b):
        data = _body(b)
        return s.carts.add_item(p["cart_id"], _int(data.get("product_id"), "product_id"), data.get("quantity", 1))
    r("POST", "/api/cart/{cart_id}/items", add_item, status=201)

    def set_quantity(p, q, b):
        data = _body(b)
        return s.carts.set_quantity(p["cart_id"], _int(p["product_id"], "product_id"), data.get("quantity"))
    r("PUT", "/api/cart/{cart_id}/items/{product_id}", set_quantity)
    r("DELETE", "/api/cart/{cart_id}/items/{product_id}",
      lambda p, q, b: s.carts.remove_item(p["cart_id"], _int(p["product_id"], "product_id")))
    r("DELETE", "/api/cart/{cart_id}/items", lambda p, q, b: s.carts.clear(p["cart_id"]))

    # --- compra ---
    r("GET", "/api/cart/{cart_id}/customer", lambda p, q, b: {"customer": s.checkout.get_customer(p["cart_id"])})
    r("PUT", "/api/cart/{cart_id}/customer",
      lambda p, q, b: {"customer": s.checkout.save_customer(p["cart_id"], _body(b))})
    r("GET", "/api/cart/{cart_id}/summary", lambda p, q, b: s.checkout.get_summary(p["cart_id"]))
    r("POST", "/api/cart/{cart_id}/payment", lambda p, q, b: s.payments.attempt_payment(p["cart_id"]))
