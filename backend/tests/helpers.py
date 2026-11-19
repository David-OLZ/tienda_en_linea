"""Base de datos en memoria con un catálogo mínimo y predecible para las pruebas."""
import unittest

from tienda.app import build_services
from tienda.database import connect, init_schema
from tienda.repositories.cart_repository import CartRepository
from tienda.repositories.catalog_repository import CatalogRepository

# ids fijos: 1 Café (5 pzs, $100.00), 2 Taza (2 pzs, $50.50), 3 Agotado (0 pzs), 4 Libro (10 pzs, $200.00)
CUSTOMER = {
    "full_name": "María López Pérez",
    "email": "maria@example.com",
    "phone": "656 123 4567",
    "street": "Av. de las Torres",
    "ext_number": "123",
    "int_number": "",
    "neighborhood": "Centro",
    "city": "Ciudad Juárez",
    "state": "Chihuahua",
    "postal_code": "32000",
    "references": "Portón negro",
}


def make_connection():
    conn = connect(":memory:")
    init_schema(conn)
    conn.execute("INSERT INTO categories(id, name) VALUES (1, 'Cocina'), (2, 'Libros')")
    conn.executemany(
        "INSERT INTO products(id, sku, name, description, price_cents, stock, emoji, category_id) VALUES (?,?,?,?,?,?,?,?)",
        [
            (1, "COC-1", "Café molido", "Café de altura tostado medio", 10000, 5, "☕", 1),
            (2, "COC-2", "Taza de cerámica", "Taza blanca de 300 ml", 5050, 2, "🍵", 1),
            (3, "COC-3", "Jarra agotada", "Jarra de vidrio", 8000, 0, "🫗", 1),
            (4, "LIB-1", "Libro de recetas", "Recetas fáciles", 20000, 10, "📖", 2),
        ],
    )
    conn.commit()
    return conn


class StoreTestCase(unittest.TestCase):
    def setUp(self):
        self.conn = make_connection()
        self.addCleanup(self.conn.close)
        self.services = build_services(self.conn)
        self.cart_repo = CartRepository(self.conn)
        self.catalog_repo = CatalogRepository(self.conn)
        self.cart_id = self.services.carts.create_cart()

    def set_stock(self, product_id, stock):
        self.conn.execute("UPDATE products SET stock = ? WHERE id = ?", (stock, product_id))
        self.conn.commit()
