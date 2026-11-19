"""Carga del catálogo inicial."""
from .seed_data import CATEGORIES, PRODUCTS


def seed_database(conn, categories=CATEGORIES, products=PRODUCTS):
    """Inserta el catálogo solo si la base está vacía. Devuelve True si cargó datos."""
    if conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] > 0:
        return False
    for name in categories:
        conn.execute("INSERT OR IGNORE INTO categories(name) VALUES (?)", (name,))
    ids = {row["name"]: row["id"] for row in conn.execute("SELECT id, name FROM categories")}
    for sku, name, description, price, stock, emoji, category in products:
        conn.execute(
            "INSERT INTO products(sku, name, description, price_cents, stock, emoji, category_id) "
            "VALUES (?,?,?,?,?,?,?)",
            (sku, name, description, int(round(price * 100)), stock, emoji, ids[category]),
        )
    conn.commit()
    return True
