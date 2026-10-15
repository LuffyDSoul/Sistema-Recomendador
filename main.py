"""Punto de entrada del sistema recomendador conectado a Supabase."""

import logging
from src.infrastructure.config import AppConfig
from src.infrastructure.supabase.client import SupabaseClient
from src.supabase_operations import cargar_datos, recomendar, registrar_preferencia

# Configuración de Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def main():
    logger.info("================================================================")
    logger.info("  INICIANDO SISTEMA RECOMENDADOR HÍBRIDO                       ")
    logger.info("================================================================")

    # 1. Carga de Configuración (Infrastructure)
    config = AppConfig.load()
    client = SupabaseClient(config.supabase_url, config.supabase_key)

    # Carga de datos directamente en Supabase.
    logger.info("\n--- [PASO 1: Verificación / Carga de Catálogo y Datos Semilla] ---")
    cargar_datos(client)

    logger.info("\n--- [PASO 2: Demostración de Recomendación Cold Start] ---")
    test_user_email = "pabloleal@gmail.com"
    recomendaciones = recomendar(client, test_user_email, limit=5)

    print(f"\n=== [RECOMENDACIONES COLD START] Para '{test_user_email}' ===")
    for idx, libro in enumerate(recomendaciones, start=1):
        print(f"  {idx}. [{libro['id_libro']}] {libro['titulo']}")
        print(f"     Páginas: {libro['nro_paginas']} | Precio: ${libro['precio']:.2f}")
        print(f"     Descripción: {libro['descripcion']}")
        print()

    logger.info("--- [PASO 3: Demostración de Registro de Preferencia (Rating / Click)] ---")
    pref_explicita = registrar_preferencia(client, test_user_email, 1, 5)
    logger.info("Preferencia explícita registrada: Libro #%s, Rating: %s", pref_explicita.get("idLibro", 1), pref_explicita.get("rating"))
    pref_implicita = registrar_preferencia(client, test_user_email, 7)
    logger.info("Preferencia implícita registrada: Libro #%s, Rating: %s", pref_implicita.get("idLibro", 7), pref_implicita.get("rating"))

    logger.info("\n================================================================")
    logger.info("  FLUJO DE EJECUCIÓN COMPLETADO SATISFACTORIAMENTE              ")
    logger.info("================================================================")


if __name__ == "__main__":
    main()
