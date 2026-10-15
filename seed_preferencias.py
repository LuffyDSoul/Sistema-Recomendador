"""Carga preferencias y compras demo para usuarios ya existentes."""

import logging
import random
import sys

from src.infrastructure.config import AppConfig
from src.infrastructure.supabase.client import SupabaseClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

USUARIO_COLD_START = "emilianolanaro@gmail.com"


def cargar_preferencias_usuarios_existentes(
    client: SupabaseClient,
    semilla: int = 100,
    reemplazar: bool = False,
) -> None:
    """Genera onboarding y compras para los usuarios de la tabla Usuario."""
    usuarios = client.select(
        "Usuario",
        "select=idUsuario,nombre,email&order=idUsuario.asc",
    )
    libros = client.select("Libro", "select=idLibro")
    generos = client.select("Genero", "select=idGenero")

    if not usuarios:
        raise ValueError("No hay usuarios cargados en Supabase.")
    if not libros:
        raise ValueError("No hay libros cargados. Ejecuta primero py seed.py.")
    if not generos:
        raise ValueError("No hay generos cargados. Ejecuta primero py seed.py.")

    ids_libros = [libro["idLibro"] for libro in libros]
    ids_generos = [genero["idGenero"] for genero in generos]
    rng = random.Random(semilla)
    total_insertadas = 0

    for usuario in usuarios:
        usuario_id = usuario["idUsuario"]

        if reemplazar:
            client.delete("UsuarioGenero", f"idUsuario=eq.{usuario_id}")
            client.delete("Preferencia", f"idUsuario=eq.{usuario_id}")

        generos_actuales = client.select(
            "UsuarioGenero",
            f"select=idGenero&idUsuario=eq.{usuario_id}",
        )
        if not generos_actuales:
            cantidad_generos = rng.randint(1, min(3, len(ids_generos)))
            client.insert(
                "UsuarioGenero",
                [{"idUsuario": usuario_id, "idGenero": id_genero}
                 for id_genero in rng.sample(ids_generos, cantidad_generos)],
            )

        # Este usuario queda siempre sin compras para probar Cold Start.
        if usuario["email"] == USUARIO_COLD_START:
            if not reemplazar:
                client.delete("Preferencia", f"idUsuario=eq.{usuario_id}")
            logger.info(
                "Usuario %s (%s) queda sin compras para probar Cold Start.",
                usuario_id,
                usuario["email"],
            )
            continue

        preferencias_actuales = client.select(
            "Preferencia",
            f"select=idLibro&idUsuario=eq.{usuario_id}",
        )
        ids_preferidos = {preferencia["idLibro"] for preferencia in preferencias_actuales}
        cantidad = rng.choice([7, 8]) if rng.random() < 0.95 else 10
        disponibles = [id_libro for id_libro in ids_libros if id_libro not in ids_preferidos]
        libros_comprados = rng.sample(disponibles, min(cantidad, len(disponibles)))
        preferencias = [{
            "idUsuario": usuario_id,
            "idLibro": id_libro,
            "rating": rng.randint(1, 5) if rng.random() < 0.6 else None,
        } for id_libro in libros_comprados]

        if preferencias:
            client.insert("Preferencia", preferencias)
            total_insertadas += len(preferencias)

    logger.info(
        "Se procesaron %s usuarios existentes y se insertaron %s preferencias.",
        len(usuarios),
        total_insertadas,
    )


def main() -> None:
    config = AppConfig.load()
    client = SupabaseClient(config.supabase_url, config.supabase_key)
    reemplazar = "--reset-preferencias" in sys.argv
    cargar_preferencias_usuarios_existentes(client, reemplazar=reemplazar)


if __name__ == "__main__":
    main()