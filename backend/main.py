"""Punto de entrada del backend. Electron lo lanza y lee el puerto de la línea TIENDA_BACKEND_READY."""
import argparse
import logging
import sys

from tienda.api.server import create_server
from tienda.app import create_app


def main(argv=None):
    parser = argparse.ArgumentParser(description="Backend de la tienda en línea")
    parser.add_argument("--db", default="tienda.db", help="ruta del archivo SQLite")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=0, help="0 = puerto libre automático")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    router, _conn = create_app(args.db)
    server = create_server(router, args.host, args.port)
    print(f"TIENDA_BACKEND_READY port={server.server_address[1]}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
