"""Servidor HTTP local (solo stdlib) que expone el enrutador."""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qsl, urlsplit

from ..errors import BadRequestError
from .router import error_response

MAX_BODY_BYTES = 1_000_000


def make_handler(router):
    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def _send(self, response):
            data = json.dumps(response.payload, ensure_ascii=False).encode("utf-8")
            self.send_response(response.status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _handle(self):
            parts = urlsplit(self.path)
            length = int(self.headers.get("Content-Length") or 0)
            if length > MAX_BODY_BYTES:
                return self._send(error_response(BadRequestError("La petición es demasiado grande.")))
            body = None
            if length:
                raw = self.rfile.read(length)
                try:
                    body = json.loads(raw.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    return self._send(error_response(BadRequestError("El cuerpo no es un JSON válido.")))
            query = dict(parse_qsl(parts.query))
            self._send(router.dispatch(self.command, parts.path, query, body))

        do_GET = do_POST = do_PUT = do_DELETE = _handle

        def log_message(self, fmt, *args):  # silencia el log por defecto
            pass

    return Handler


def create_server(router, host="127.0.0.1", port=0):
    return HTTPServer((host, port), make_handler(router))
