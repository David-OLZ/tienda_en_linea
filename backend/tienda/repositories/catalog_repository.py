"""Acceso a datos de categorías y productos."""

_PRODUCT_SELECT = (
    "SELECT p.id, p.sku, p.name, p.description, p.price_cents, p.stock, p.emoji, "
    "p.category_id, c.name AS category_name "
    "FROM products p JOIN categories c ON c.id = p.category_id"
)


class CatalogRepository:
    def __init__(self, conn):
        self._conn = conn

    def list_categories(self):
        rows = self._conn.execute(
            "SELECT c.id, c.name, COUNT(p.id) AS product_count "
            "FROM categories c LEFT JOIN products p ON p.category_id = c.id "
            "GROUP BY c.id ORDER BY c.name COLLATE NOCASE"
        )
        return [dict(r) for r in rows]

    def list_products(self, category_id=None):
        sql, params = _PRODUCT_SELECT, []
        if category_id is not None:
            sql += " WHERE p.category_id = ?"
            params.append(category_id)
        sql += " ORDER BY p.name COLLATE NOCASE"
        return [dict(r) for r in self._conn.execute(sql, params)]

    def get_product(self, product_id):
        row = self._conn.execute(_PRODUCT_SELECT + " WHERE p.id = ?", (product_id,)).fetchone()
        return dict(row) if row else None
