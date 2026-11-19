"""Reglas del carrito: cantidades válidas y existencias."""
import uuid

from ..errors import NotFoundError, StockError
from ..pricing import calculate_totals, line_total
from ..text import plural_units
from ..validators import parse_quantity


class CartService:
    def __init__(self, cart_repo, catalog_repo):
        self._carts = cart_repo
        self._catalog = catalog_repo

    # --- ciclo de vida -------------------------------------------------
    def create_cart(self):
        cart_id = uuid.uuid4().hex
        self._carts.create(cart_id)
        return cart_id

    def _require_cart(self, cart_id):
        if not self._carts.exists(cart_id):
            raise NotFoundError("El carrito no existe.")

    def _require_product(self, product_id):
        product = self._catalog.get_product(product_id)
        if product is None:
            raise NotFoundError("El producto no existe.")
        return product

    # --- consulta ------------------------------------------------------
    def get_cart(self, cart_id):
        self._require_cart(cart_id)
        items = [self._build_line(i) for i in self._carts.get_items(cart_id)]
        totals = calculate_totals((i["unit_price_cents"], i["quantity"]) for i in items)
        return {
            "cart_id": cart_id,
            "items": items,
            "totals": totals.to_dict(),
            "has_issues": any(i["issue"] for i in items),
        }

    @staticmethod
    def _build_line(item):
        stock, qty, name = item["stock"], item["quantity"], item["name"]
        issue = message = None
        if stock == 0:
            issue, message = "out_of_stock", f"«{name}» ya no está disponible. Quítalo del carrito para continuar."
        elif qty > stock:
            issue, message = "exceeds_stock", f"Solo hay {plural_units(stock)} de «{name}». Ajusta la cantidad."
        return {
            "product_id": item["product_id"],
            "sku": item["sku"],
            "name": name,
            "emoji": item["emoji"],
            "unit_price_cents": item["price_cents"],
            "quantity": qty,
            "line_total_cents": line_total(item["price_cents"], qty),
            "stock": stock,
            "issue": issue,
            "issue_message": message,
        }

    # --- modificación --------------------------------------------------
    def add_item(self, cart_id, product_id, quantity=1):
        self._require_cart(cart_id)
        qty = parse_quantity(quantity)
        product = self._require_product(product_id)
        in_cart = self._carts.get_quantity(cart_id, product_id)
        self._ensure_stock(product, in_cart + qty, in_cart)
        self._carts.set_quantity(cart_id, product_id, in_cart + qty)
        return self.get_cart(cart_id)

    def set_quantity(self, cart_id, product_id, quantity):
        self._require_cart(cart_id)
        qty = parse_quantity(quantity)
        product = self._require_product(product_id)
        if self._carts.get_quantity(cart_id, product_id) == 0:
            raise NotFoundError("Ese producto no está en tu carrito.")
        self._ensure_stock(product, qty)
        self._carts.set_quantity(cart_id, product_id, qty)
        return self.get_cart(cart_id)

    def remove_item(self, cart_id, product_id):
        self._require_cart(cart_id)
        if not self._carts.delete_item(cart_id, product_id):
            raise NotFoundError("Ese producto no está en tu carrito.")
        return self.get_cart(cart_id)

    def clear(self, cart_id):
        self._require_cart(cart_id)
        self._carts.clear(cart_id)
        return self.get_cart(cart_id)

    # --- reglas de existencia -----------------------------------------
    @staticmethod
    def _ensure_stock(product, requested_total, already_in_cart=0):
        stock, name = product["stock"], product["name"]
        details = {"product_id": product["id"], "stock": stock, "in_cart": already_in_cart}
        if stock == 0:
            raise StockError(f"«{name}» está agotado.", details=details)
        if requested_total <= stock:
            return
        remaining = stock - already_in_cart
        if already_in_cart and remaining <= 0:
            msg = f"Ya tienes en tu carrito todas las unidades disponibles de «{name}» ({stock})."
        elif already_in_cart:
            msg = (f"Solo puedes agregar {plural_units(remaining)} más de «{name}» "
                   f"(hay {stock} en existencia y ya tienes {already_in_cart}).")
        else:
            msg = f"Solo hay {plural_units(stock)} disponible{'s' if stock != 1 else ''} de «{name}»."
        raise StockError(msg, details=details)
