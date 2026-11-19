"""Ensamblado de dependencias (composition root)."""
from .api.router import Router
from .api.routes import Services, register_routes
from .database import connect, init_schema
from .repositories.cart_repository import CartRepository
from .repositories.catalog_repository import CatalogRepository
from .seed import seed_database
from .services.cart_service import CartService
from .services.catalog_service import CatalogService
from .services.checkout_service import CheckoutService
from .services.payment_service import PaymentService


def build_services(conn):
    catalog_repo = CatalogRepository(conn)
    cart_repo = CartRepository(conn)
    carts = CartService(cart_repo, catalog_repo)
    checkout = CheckoutService(carts, cart_repo)
    return Services(
        catalog=CatalogService(catalog_repo),
        carts=carts,
        checkout=checkout,
        payments=PaymentService(checkout),
    )


def create_app(db_path=":memory:", seed=True):
    conn = connect(db_path)
    init_schema(conn)
    if seed:
        seed_database(conn)
    router = Router()
    register_routes(router, build_services(conn))
    return router, conn
