"""Punto de entrada para iniciar el servidor de la API REST (Fase 4: Modelado)."""

import logging
import os
import sys

from src.api.server import run_server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main() -> None:
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8000"))

    for idx, arg in enumerate(sys.argv[1:], start=1):
        if arg in ("--port", "-p") and idx < len(sys.argv) - 1:
            port = int(sys.argv[idx + 1])
        elif arg.startswith("--port="):
            port = int(arg.split("=", 1)[1])
        elif arg in ("--host", "-h") and idx < len(sys.argv) - 1:
            host = sys.argv[idx + 1]
        elif arg.startswith("--host="):
            host = arg.split("=", 1)[1]

    run_server(host=host, port=port)


if __name__ == "__main__":
    main()
