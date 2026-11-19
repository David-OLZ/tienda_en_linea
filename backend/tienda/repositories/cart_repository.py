"""Acceso a datos de carritos y datos del cliente."""
import json


class CartRepository:
    def __init__(self, conn):
        self._conn = conn

    def create(self, cart_id):
        self._conn.execute("INSERT INTO carts(id) VALUES (?)", (cart_id,))
        self._conn.commit()

    def exists(self, cart_id):
        return self._conn.execute("SELECT 1 FROM carts WHERE id = ?", (cart_id,)).fetchone() is not None

    def get_items(self, cart_id):
        rows = self._conn.execute(
            "SELECT ci.product_id, ci.quantity, p.sku, p.name, p.emoji, p.price_cents, p.stock "
            "FROM cart_items ci JOIN products p ON p.id = ci.product_id "
            "WHERE ci.cart_id = ? ORDER BY ci.rowid",
            (cart_id,),
        )
        return [dict(r) for r in rows]

    def get_quantity(self, cart_id, product_id):
        row = self._conn.execute(
            "SELECT quantity FROM cart_items WHERE cart_id = ? AND product_id = ?",
            (cart_id, product_id),
        ).fetchone()
        return row["quantity"] if row else 0

    def set_quantity(self, cart_id, product_id, quantity):
        self._conn.execute(
            "INSERT INTO cart_items(cart_id, product_id, quantity) VALUES (?,?,?) "
            "ON CONFLICT(cart_id, product_id) DO UPDATE SET quantity = excluded.quantity",
            (cart_id, product_id, quantity),
        )
        self._conn.commit()

    def delete_item(self, cart_id, product_id):
        cur = self._conn.execute(
            "DELETE FROM cart_items WHERE cart_id = ? AND product_id = ?", (cart_id, product_id)
        )
        self._conn.commit()
        return cur.rowcount > 0

    def clear(self, cart_id):
        self._conn.execute("DELETE FROM cart_items WHERE cart_id = ?", (cart_id,))
        self._conn.commit()

    def save_customer(self, cart_id, customer):
        self._conn.execute(
            "UPDATE carts SET customer_json = ? WHERE id = ?",
            (json.dumps(customer, ensure_ascii=False), cart_id),
        )
        self._conn.commit()

    def get_customer(self, cart_id):
        row = self._conn.execute("SELECT customer_json FROM carts WHERE id = ?", (cart_id,)).fetchone()
        return json.loads(row["customer_json"]) if row and row["customer_json"] else None
