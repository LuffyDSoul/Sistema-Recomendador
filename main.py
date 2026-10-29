"""Punto de entrada del sistema recomendador híbrido conectado a Supabase (Fase 4: Modelado)."""

import logging
import sys

from src.api.server import run_server
from src.infrastructure.config import AppConfig
from src.infrastructure.supabase.client import SupabaseClient
from src.models.hybrid_pipeline import HybridRecommenderPipeline
from src.supabase_operations import cargar_datos

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    if "--serve" in sys.argv or "--api" in sys.argv:
        run_server()
        return

    logger.info("================================================================")
    logger.info("  INICIANDO SISTEMA RECOMENDADOR HÍBRIDO (FASE 4: MODELADO)     ")
    logger.info("================================================================")

    # 1. Carga de Configuración y Cliente Supabase
    config = AppConfig.load()
    client = SupabaseClient(config.supabase_url, config.supabase_key)

    logger.info("\n--- [PASO 1: Verificación de Catálogo y Entrenamiento del Pipeline] ---")
    cargar_datos(client)
    pipeline = HybridRecommenderPipeline(client=client).fit()

    # 2. Demostración Modelo 1: Filtrado Colaborativo Basado en Ítems (Item-Based CF)
    logger.info("\n--- [PASO 2: Modelo 1 - Filtrado Colaborativo Basado en Ítems (100x100)] ---")
    recurrent_email = "pabloleal@gmail.com"
    res_cf = pipeline.recommend(email=recurrent_email, k=5)
    print(f"\n=== [{res_cf['modelo_aplicado']}] ===")
    print(f"Usuario: {res_cf['usuario']['nombre']} (idUsuario={res_cf['usuario']['idUsuario']}, {recurrent_email})")
    print(
        f"Compras previas: {res_cf['historial_compras_usuario']['total_libros_comprados']} "
        f"(Explícitas: {res_cf['historial_compras_usuario']['compras_con_rating_explicito']}, "
        f"Imputadas con 3.0: {res_cf['historial_compras_usuario']['compras_imputadas_con_3']})"
    )
    for idx, libro in enumerate(res_cf["recomendaciones"], start=1):
        print(
            f"  {idx}. [{libro['id_libro']}] {libro['titulo']} ({libro['autor']}) "
            f"| Score CF: {libro['score_colaborativo']:.4f} | Precio: ${libro['precio']:.2f}"
        )

    # 3. Demostración Modelo 2 (Caso A): Cold Start con géneros seleccionados en Onboarding
    logger.info("\n--- [PASO 3: Modelo 2 (Caso A) - Cold Start Con Géneros de Onboarding] ---")
    cold_start_email = "emilianolanaro@gmail.com"
    res_cs_a = pipeline.recommend(email=cold_start_email, genre_ids=[1, 2], k=5)
    print(f"\n=== [{res_cs_a['modelo_aplicado']} - {res_cs_a['estrategia']}] ===")
    print(f"Usuario: {res_cs_a['usuario']['nombre']} (idUsuario={res_cs_a['usuario']['idUsuario']}, {cold_start_email})")
    print(f"Géneros aplicados: {res_cs_a['parametros']['generos_aplicados']}")
    for idx, libro in enumerate(res_cs_a["recomendaciones"], start=1):
        print(
            f"  {idx}. [{libro['id_libro']}] {libro['titulo']} | Géneros: {', '.join(libro['generos'])} "
            f"| Promedio Rating: {libro['promedio_rating']:.2f} | Ventas: {libro['volumen_ventas']}"
        )

    # 4. Demostración Modelo 2 (Caso B): Cold Start sin géneros (Popularidad Global)
    logger.info("\n--- [PASO 4: Modelo 2 (Caso B) - Cold Start Sin Géneros (Popularidad Global)] ---")
    res_cs_b = pipeline.recommend(email=cold_start_email, genre_ids=[], k=5)
    print(f"\n=== [{res_cs_b['modelo_aplicado']} - {res_cs_b['estrategia']}] ===")
    for idx, libro in enumerate(res_cs_b["recomendaciones"], start=1):
        print(
            f"  {idx}. [{libro['id_libro']}] {libro['titulo']} "
            f"| Ventas: {libro['volumen_ventas']} | Promedio Rating: {libro['promedio_rating']:.2f}"
        )

    logger.info("\n================================================================")
    logger.info("  PARA INICIAR LA API REST EJECUTA: py api.py                   ")
    logger.info("================================================================")


if __name__ == "__main__":
    main()
