"""Enrutador HTTP independiente del servidor: recibe (método, ruta, query, cuerpo) y devuelve una respuesta."""
import logging
import re
from dataclasses import dataclass

from ..errors import StoreError

log = logging.getLogger("tienda.api")


@dataclass
class Response:
    status: int
    payload: dict


def error_response(err):
    return Response(err.http_status, {"error": err.to_dict()})


class Router:
    def __init__(self):
        self._routes = []

    def add(self, method, pattern, handler, status=200):
        regex = re.compile(re.sub(r"\{(\w+)\}", r"(?P<\1>[^/]+)", pattern))
        self._routes.append((method.upper(), regex, handler, status))

    def dispatch(self, method, path, query=None, body=None):
        method = method.upper()
        path_matched = False
        for route_method, regex, handler, status in self._routes:
            match = regex.fullmatch(path)
            if not match:
                continue
            path_matched = True
            if route_method != method:
                continue
            try:
                return Response(status, handler(match.groupdict(), query or {}, body))
            except StoreError as err:
                return error_response(err)
            except Exception:  # noqa: BLE001 - último recurso para no tumbar el servidor
                log.exception("Error inesperado en %s %s", method, path)
                return Response(500, {"error": {
                    "code": "internal_error", "message": "Ocurrió un error inesperado.",
                    "fields": {}, "details": {}}})
        if path_matched:
            return Response(405, {"error": {"code": "method_not_allowed", "message": "Método no permitido.",
                                            "fields": {}, "details": {}}})
        return Response(404, {"error": {"code": "not_found", "message": "Ruta no encontrada.",
                                        "fields": {}, "details": {}}})
