"""
Script de Inyección Inicial de Datos (Data Seeding)
Arquitectura: Domain-Driven Design (DDD)
Carga los 12 géneros, 9 editoriales, 18 autores, 100 libros exactos, 20 usuarios y sus preferencias.
"""

import sys
import logging
from src.infrastructure.config import AppConfig
from src.infrastructure.supabase.client import SupabaseClient
from src.infrastructure.repositories.supabase_repositories import (
    SupabaseGeneroRepository,
    SupabaseEditorialRepository,
    SupabaseAutorRepository,
    SupabaseLibroRepository,
    SupabaseUsuarioRepository
)
from src.application.use_cases.seed_data_use_case import SeedDataUseCase

# Configuración de Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def limpiar_base_de_datos(client: SupabaseClient) -> None:
    """Elimina datos previos para asegurar una recarga limpia."""
    logger.info("Vaciando tablas para reinyección limpia...")
    tablas_ordenadas = [
        ("UsuarioGenero", "idUsuario=gte.0"),
        ("Preferencia", "idPreferencia=gte.0"),
        ("GeneroLibro", "idLibro=gte.0"),
        ("Libro", "idLibro=gte.0"),
        ("Usuario", "idUsuario=gte.0"),
        ("Autor", "idAutor=gte.0"),
        ("Editorial", "idEditorial=gte.0"),
        ("Genero", "idGenero=gte.0")
    ]
    for tabla, param in tablas_ordenadas:
        try:
            client.delete(tabla, param)
        except Exception as e:
            logger.debug(f"Aviso al limpiar {tabla}: {e}")
    logger.info("Tablas preparadas para la inyección.")


def main():
    force_reload = "--reset" in sys.argv or "-r" in sys.argv

    logger.info("================================================================")
    logger.info("  INICIANDO INYECCIÓN INICIAL DE DATOS EN SUPABASE (DDD)        ")
    logger.info("================================================================")

    # 1. Configuración y Cliente
    config = AppConfig.load()
    client = SupabaseClient(config.supabase_url, config.supabase_key)

    # Si se pasa --reset o si no hay datos, limpiar primero
    if force_reload:
        limpiar_base_de_datos(client)

    # 2. Instanciación de Repositorios (Infrastructure)
    genero_repo = SupabaseGeneroRepository(client)
    editorial_repo = SupabaseEditorialRepository(client)
    autor_repo = SupabaseAutorRepository(client)
    libro_repo = SupabaseLibroRepository(client)
    usuario_repo = SupabaseUsuarioRepository(client)

    # 3. Caso de Uso (Application)
    seed_use_case = SeedDataUseCase(
        genero_repo=genero_repo,
        editorial_repo=editorial_repo,
        autor_repo=autor_repo,
        libro_repo=libro_repo,
        usuario_repo=usuario_repo
    )

    # 4. Ejecución
    seed_use_case.execute(force_reload=force_reload)

    # 5. Verificación Final de Estado
    logger.info("\n--- [RESUMEN DE REGISTROS EN SUPABASE] ---")
    tablas = ["Genero", "Editorial", "Autor", "Libro", "GeneroLibro", "Usuario", "UsuarioGenero"]
    for t in tablas:
        data = client.select(t, "select=*")
        print(f"  * Tabla '{t}': {len(data)} registros cargados.")

    logger.info("\n================================================================")
    logger.info("  INYECCIÓN INICIAL FINALIZADA CON ÉXITO                         ")
    logger.info("================================================================")


if __name__ == "__main__":
    main()
