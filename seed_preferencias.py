"""Carga preferencias y compras demo coherentes con los géneros para usuarios existentes."""

import logging
import random
import sys
from typing import Dict, List, Set

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
    """Genera perfiles de compra con clusters colaborativos fuertes para la tabla Usuario."""
    usuarios = client.select("Usuario", "select=idUsuario,nombre,email&order=idUsuario.asc")
    libros = client.select("Libro", "select=idLibro")
    generos = client.select("Genero", "select=idGenero")
    genero_libro = client.select("GeneroLibro", "select=idGenero,idLibro")

    if not usuarios or not libros or not generos:
        raise ValueError("Faltan usuarios, libros o géneros en Supabase. Ejecuta primero py seed.py.")

    ids_libros = sorted([int(libro["idLibro"]) for libro in libros])
    ids_generos = sorted([int(genero["idGenero"]) for genero in generos])

    # Mapear qué libros pertenecen a cada género (ordenados para consistencia)
    libros_por_genero: Dict[int, List[int]] = {gid: [] for gid in ids_generos}
    for rel in genero_libro:
        gid = int(rel["idGenero"])
        bid = int(rel["idLibro"])
        libros_por_genero.setdefault(gid, []).append(bid)
    for gid in libros_por_genero:
        libros_por_genero[gid].sort()

    # Definir 4 arquetipos (clusters) de lectores sobre los primeros géneros con suficientes libros
    generos_con_libros = [gid for gid in ids_generos if len(libros_por_genero.get(gid, [])) >= 6]
    if len(generos_con_libros) < 3:
        generos_con_libros = ids_generos

    # Bestsellers globales de la plataforma (los primeros 2 libros de los 3 géneros principales)
    bestsellers_globales: List[int] = []
    for gid in generos_con_libros[:3]:
        bestsellers_globales.extend(libros_por_genero[gid][:3])
    bestsellers_globales = list(dict.fromkeys(bestsellers_globales))[:6]

    rng = random.Random(semilla)
    total_insertadas = 0

    for idx_u, usuario in enumerate(usuarios):
        usuario_id = int(usuario["idUsuario"])

        if reemplazar:
            client.delete("UsuarioGenero", f"idUsuario=eq.{usuario_id}")
            client.delete("Preferencia", f"idUsuario=eq.{usuario_id}")

        # Asignar a cada usuario uno de los 3 arquetipos principales para concentrar la matriz 100x100
        genero_principal = generos_con_libros[idx_u % min(3, len(generos_con_libros))]
        genero_secundario = generos_con_libros[(idx_u + 1) % min(3, len(generos_con_libros))]

        generos_actuales = client.select("UsuarioGenero", f"select=idGenero&idUsuario=eq.{usuario_id}")
        if not generos_actuales:
            elegidos = [genero_principal]
            if rng.random() < 0.5 and genero_secundario != genero_principal:
                elegidos.append(genero_secundario)
            client.insert(
                "UsuarioGenero",
                [{"idUsuario": usuario_id, "idGenero": g} for g in elegidos],
            )
            generos_usuario = elegidos
        else:
            generos_usuario = [int(g["idGenero"]) for g in generos_actuales]

        # Este usuario queda siempre sin compras para probar Cold Start
        if usuario["email"].strip().lower() == USUARIO_COLD_START.lower():
            client.delete("Preferencia", f"idUsuario=eq.{usuario_id}")
            logger.info("Usuario %s (%s) queda sin compras para probar Cold Start.", usuario_id, usuario["email"])
            continue

        preferencias_actuales = client.select("Preferencia", f"select=idLibro&idUsuario=eq.{usuario_id}")
        if preferencias_actuales and not reemplazar:
            continue

        cantidad = rng.choice([7, 8]) if rng.random() < 0.90 else 10

        # Pool nuclear del cluster del usuario (los primeros 7 libros de su género principal)
        pool_cluster = list(libros_por_genero.get(generos_usuario[0], [])[:7])
        # Agregar bestsellers globales para fortalecer Popularidad Global y co-ocurrencias
        pool_popular = [b for b in bestsellers_globales if b not in pool_cluster]

        libros_comprados: List[int] = []

        # 1. El usuario compra entre 5 y 6 libros del núcleo de su cluster (alta co-ocurrencia ítem-ítem)
        cant_cluster = min(len(pool_cluster), cantidad - 2)
        if cant_cluster > 0:
            libros_comprados.extend(rng.sample(pool_cluster, cant_cluster))

        # 2. Compra 1 o 2 bestsellers globales de la tienda
        faltan = cantidad - len(libros_comprados)
        if faltan > 0 and pool_popular:
            libros_comprados.extend(rng.sample(pool_popular, min(faltan, len(pool_popular))))

        # 3. Completa si aún falta alguno
        faltan = cantidad - len(libros_comprados)
        if faltan > 0:
            resto = [b for b in ids_libros if b not in libros_comprados]
            libros_comprados.extend(rng.sample(resto, min(faltan, len(resto))))

        preferencias = []
        for id_libro in libros_comprados:
            # 60% de probabilidad de dejar rating explícito (4 o 5 en su cluster), 40% implícito (None)
            if rng.random() < 0.60:
                rating_val = rng.choice([4, 5]) if id_libro in pool_cluster else rng.choice([3, 4, 5])
            else:
                rating_val = None

            preferencias.append({
                "idUsuario": usuario_id,
                "idLibro": id_libro,
                "rating": rating_val,
            })

        if preferencias:
            client.insert("Preferencia", preferencias)
            total_insertadas += len(preferencias)

    logger.info("Se procesaron %s usuarios y se insertaron %s preferencias.", len(usuarios), total_insertadas)

def main() -> None:
    config = AppConfig.load()
    client = SupabaseClient(config.supabase_url, config.supabase_key)
    reemplazar = "--reset-preferencias" in sys.argv
    cargar_preferencias_usuarios_existentes(client, reemplazar=reemplazar)


if __name__ == "__main__":
    main()