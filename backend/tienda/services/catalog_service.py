"""Consulta de catálogo: categorías, búsqueda, filtros y orden."""
from ..errors import NotFoundError, ValidationError
from ..text import normalize

SORT_OPTIONS = ("name", "price_asc", "price_desc")
LOW_STOCK_THRESHOLD = 5


def present_product(product):
    p = dict(product)
    p["available"] = p["stock"] > 0
    p["low_stock"] = 0 < p["stock"] <= LOW_STOCK_THRESHOLD
    return p


class CatalogService:
    def __init__(self, catalog_repo):
        self._repo = catalog_repo

    def list_categories(self):
        return self._repo.list_categories()

    def list_products(self, query="", category_id=None, sort="name", only_available=False):
        if sort not in SORT_OPTIONS:
            raise ValidationError("Orden no válido.", fields={"sort": f"Usa uno de: {', '.join(SORT_OPTIONS)}."})
        products = [present_product(p) for p in self._repo.list_products(category_id)]

        terms = normalize(query or "").split()
        if terms:
            def matches(p):
                haystack = normalize(f"{p['name']} {p['description']} {p['category_name']} {p['sku']}")
                return all(t in haystack for t in terms)
            products = [p for p in products if matches(p)]
        if only_available:
            products = [p for p in products if p["available"]]

        if sort == "price_asc":
            products.sort(key=lambda p: (p["price_cents"], normalize(p["name"])))
        elif sort == "price_desc":
            products.sort(key=lambda p: (-p["price_cents"], normalize(p["name"])))
        else:
            products.sort(key=lambda p: normalize(p["name"]))
        return products

    def get_product(self, product_id):
        product = self._repo.get_product(product_id)
        if product is None:
            raise NotFoundError("El producto no existe.")
        return present_product(product)
