import json
import threading
import unittest
from urllib import request, error

from tienda.api.router import Router
from tienda.api.server import create_server
from tienda.app import create_app
from tests.helpers import CUSTOMER, make_connection
from tienda.api.routes import register_routes
from tienda.app import build_services


def build_router():
    conn = make_connection()
    router = Router()
    register_routes(router, build_services(conn))
    return router


class RouterTests(unittest.TestCase):
    def setUp(self):
        self.router = build_router()
        self.cart_id = self.call("POST", "/api/cart").payload["cart_id"]

    def call(self, method, path, query=None, body=None):
        return self.router.dispatch(method, path, query, body)

    def test_full_purchase_flow_until_payment(self):
        r = self.call("POST", f"/api/cart/{self.cart_id}/items", body={"product_id": 1, "quantity": 2})
        self.assertEqual(r.status, 201)
        r = self.call("PUT", f"/api/cart/{self.cart_id}/customer", body=CUSTOMER)
        self.assertEqual(r.status, 200)
        r = self.call("GET", f"/api/cart/{self.cart_id}/summary")
        self.assertEqual(r.status, 200)
        self.assertEqual(r.payload["totals"]["total_cents"], 23200)
        r = self.call("POST", f"/api/cart/{self.cart_id}/payment")
        self.assertEqual(r.status, 501)
        self.assertEqual(r.payload["error"]["code"], "payment_unavailable")

    def test_catalog_endpoints(self):
        self.assertEqual(len(self.call("GET", "/api/categories").payload["categories"]), 2)
        r = self.call("GET", "/api/products", query={"q": "cafe", "available": "1"})
        self.assertEqual([p["id"] for p in r.payload["products"]], [1])
        self.assertEqual(self.call("GET", "/api/products/1").payload["product"]["name"], "Café molido")
        self.assertEqual(self.call("GET", "/api/products/999").status, 404)
        self.assertEqual(self.call("GET", "/api/products/abc").status, 400)
        self.assertEqual(self.call("GET", "/api/products", query={"category": "x"}).status, 400)
        self.assertEqual(self.call("GET", "/api/products", query={"sort": "x"}).status, 422)

    def test_stock_error_maps_to_409(self):
        r = self.call("POST", f"/api/cart/{self.cart_id}/items", body={"product_id": 2, "quantity": 5})
        self.assertEqual(r.status, 409)
        self.assertEqual(r.payload["error"]["code"], "insufficient_stock")

    def test_quantity_defaults_to_one(self):
        r = self.call("POST", f"/api/cart/{self.cart_id}/items", body={"product_id": 1})
        self.assertEqual(r.payload["items"][0]["quantity"], 1)

    def test_validation_errors_include_fields(self):
        self.call("POST", f"/api/cart/{self.cart_id}/items", body={"product_id": 1})
        r = self.call("PUT", f"/api/cart/{self.cart_id}/customer", body={**CUSTOMER, "postal_code": "1"})
        self.assertEqual(r.status, 422)
        self.assertIn("postal_code", r.payload["error"]["fields"])

    def test_bad_bodies(self):
        self.assertEqual(self.call("POST", f"/api/cart/{self.cart_id}/items", body=None).status, 400)
        self.assertEqual(self.call("POST", f"/api/cart/{self.cart_id}/items", body={"quantity": 1}).status, 400)

    def test_update_and_remove_item(self):
        self.call("POST", f"/api/cart/{self.cart_id}/items", body={"product_id": 1})
        r = self.call("PUT", f"/api/cart/{self.cart_id}/items/1", body={"quantity": 3})
        self.assertEqual(r.payload["items"][0]["quantity"], 3)
        r = self.call("DELETE", f"/api/cart/{self.cart_id}/items/1")
        self.assertEqual(r.payload["items"], [])
        self.assertEqual(self.call("DELETE", f"/api/cart/{self.cart_id}/items/1").status, 404)

    def test_clear_cart(self):
        self.call("POST", f"/api/cart/{self.cart_id}/items", body={"product_id": 1})
        self.assertEqual(self.call("DELETE", f"/api/cart/{self.cart_id}/items").payload["items"], [])

    def test_unknown_route_and_method(self):
        self.assertEqual(self.call("GET", "/api/nada").status, 404)
        self.assertEqual(self.call("PATCH", "/api/categories").status, 405)

    def test_unknown_cart(self):
        self.assertEqual(self.call("GET", "/api/cart/zzz").status, 404)

    def test_empty_cart_cannot_reach_summary_or_payment(self):
        self.assertEqual(self.call("GET", f"/api/cart/{self.cart_id}/summary").status, 409)
        self.assertEqual(self.call("POST", f"/api/cart/{self.cart_id}/payment").status, 409)

    def test_config_exposes_tax_and_states(self):
        cfg = self.call("GET", "/api/config").payload
        self.assertEqual(cfg["tax_rate_percent"], 16)
        self.assertEqual(len(cfg["states"]), 32)

    def test_unexpected_errors_return_500(self):
        self.router.add("GET", "/api/boom", lambda p, q, b: 1 / 0)
        with self.assertLogs("tienda.api", level="ERROR"):
            self.assertEqual(self.call("GET", "/api/boom").status, 500)


class HttpServerTests(unittest.TestCase):
    """Prueba de humo con un servidor real en un puerto libre."""

    def setUp(self):
        router, conn = create_app(":memory:", seed=True)
        self.server = create_server(router, "127.0.0.1", 0)
        self.base = f"http://127.0.0.1:{self.server.server_address[1]}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self._stop, conn)

    def _stop(self, conn):
        self.server.shutdown()
        self.server.server_close()
        conn.close()

    def req(self, method, path, body=None, raw=None):
        data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
        r = request.Request(self.base + path, data=data, method=method, headers={"Content-Type": "application/json"})
        try:
            with request.urlopen(r) as resp:
                return resp.status, json.loads(resp.read())
        except error.HTTPError as e:
            return e.code, json.loads(e.read())

    def test_seeded_catalog_over_http(self):
        status, data = self.req("GET", "/api/products")
        self.assertEqual(status, 200)
        self.assertGreaterEqual(len(data["products"]), 30)

    def test_flow_over_http(self):
        _, cart = self.req("POST", "/api/cart")
        cid = cart["cart_id"]
        status, _ = self.req("POST", f"/api/cart/{cid}/items", {"product_id": 1, "quantity": 1})
        self.assertEqual(status, 201)
        status, data = self.req("POST", f"/api/cart/{cid}/payment")
        self.assertEqual(status, 409)  # falta capturar datos del cliente

    def test_invalid_json(self):
        status, data = self.req("POST", "/api/cart/x/items", raw=b"{no es json")
        self.assertEqual(status, 400)
        self.assertEqual(data["error"]["code"], "bad_request")


if __name__ == "__main__":
    unittest.main()
