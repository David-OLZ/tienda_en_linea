import unittest

from tienda.database import connect, init_schema
from tienda.seed import seed_database
from tienda.seed_data import CATEGORIES, PRODUCTS


class SeedTests(unittest.TestCase):
    def setUp(self):
        self.conn = connect(":memory:")
        init_schema(self.conn)

    def test_seed_loads_realistic_catalog(self):
        self.assertTrue(seed_database(self.conn))
        count = self.conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        self.assertEqual(count, len(PRODUCTS))
        self.assertGreaterEqual(count, 30)
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0], len(CATEGORIES))

    def test_seed_is_idempotent(self):
        seed_database(self.conn)
        self.assertFalse(seed_database(self.conn))
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM products").fetchone()[0], len(PRODUCTS))

    def test_catalog_has_unavailable_and_low_stock_items(self):
        seed_database(self.conn)
        stocks = [r[0] for r in self.conn.execute("SELECT stock FROM products")]
        self.assertIn(0, stocks)
        self.assertTrue(any(0 < s <= 5 for s in stocks))

    def test_skus_are_unique_and_prices_positive(self):
        self.assertEqual(len({p[0] for p in PRODUCTS}), len(PRODUCTS))
        self.assertTrue(all(p[3] > 0 for p in PRODUCTS))


if __name__ == "__main__":
    unittest.main()
