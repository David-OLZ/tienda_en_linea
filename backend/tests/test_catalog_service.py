import unittest

from tienda.errors import NotFoundError, ValidationError
from tests.helpers import StoreTestCase


class CatalogServiceTests(StoreTestCase):
    def setUp(self):
        super().setUp()
        self.catalog = self.services.catalog

    def names(self, **kwargs):
        return [p["name"] for p in self.catalog.list_products(**kwargs)]

    def test_categories_with_counts(self):
        cats = {c["name"]: c["product_count"] for c in self.catalog.list_categories()}
        self.assertEqual(cats, {"Cocina": 3, "Libros": 1})

    def test_list_all_sorted_by_name(self):
        self.assertEqual(self.names(), ["Café molido", "Jarra agotada", "Libro de recetas", "Taza de cerámica"])

    def test_filter_by_category(self):
        self.assertEqual(self.names(category_id=2), ["Libro de recetas"])

    def test_search_ignores_accents_and_case(self):
        self.assertEqual(self.names(query="CAFE"), ["Café molido"])
        self.assertEqual(self.names(query="ceramica taza"), ["Taza de cerámica"])

    def test_search_looks_in_description_and_category(self):
        self.assertEqual(self.names(query="altura"), ["Café molido"])
        self.assertEqual(self.names(query="libros"), ["Libro de recetas"])

    def test_search_without_results(self):
        self.assertEqual(self.names(query="zzz"), [])

    def test_only_available_hides_out_of_stock(self):
        self.assertNotIn("Jarra agotada", self.names(only_available=True))

    def test_sort_by_price(self):
        asc = self.catalog.list_products(sort="price_asc")
        self.assertEqual([p["price_cents"] for p in asc], [5050, 8000, 10000, 20000])
        desc = self.catalog.list_products(sort="price_desc")
        self.assertEqual(desc[0]["price_cents"], 20000)

    def test_invalid_sort(self):
        with self.assertRaises(ValidationError):
            self.catalog.list_products(sort="random")

    def test_product_flags(self):
        self.assertTrue(self.catalog.get_product(2)["low_stock"])
        self.assertFalse(self.catalog.get_product(3)["available"])
        self.assertTrue(self.catalog.get_product(4)["available"])

    def test_missing_product(self):
        with self.assertRaises(NotFoundError):
            self.catalog.get_product(999)


if __name__ == "__main__":
    unittest.main()
