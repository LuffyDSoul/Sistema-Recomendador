"""
Punto de Entrada Principal (Presentation / Orchestration Layer)
Arquitectura Orientada al Dominio (Domain-Driven Design - DDD)
Proyecto: Sistema Recomendador Híbrido de Libros con Supabase
"""

import logging
from src.infrastructure.config import AppConfig
from src.infrastructure.supabase.client import SupabaseClient
from src.infrastructure.repositories.supabase_repositories import (
    SupabaseGeneroRepository,
    SupabaseEditorialRepository,
    SupabaseAutorRepository,
    SupabaseLibroRepository,
    SupabaseUsuarioRepository,
    SupabasePreferenciaRepository
)
from src.application.use_cases.seed_data_use_case import SeedDataUseCase
from src.application.use_cases.cold_start_recommendation_use_case import ColdStartRecommendationUseCase
from src.application.use_cases.registrar_preferencia_use_case import RegistrarPreferenciaUseCase
from src.application.dtos import RegistrarPreferenciaDTO

# Configuración de Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def main():
    logger.info("================================================================")
    logger.info("  INICIANDO SISTEMA RECOMENDADOR HÍBRIDO (ARQUITECTURA DDD)    ")
    logger.info("================================================================")

    # 1. Carga de Configuración (Infrastructure)
    config = AppConfig.load()
    client = SupabaseClient(config.supabase_url, config.supabase_key)

    # 2. Inyección de Dependencias: Repositorios (Infrastructure -> Domain Contracts)
    genero_repo = SupabaseGeneroRepository(client)
    editorial_repo = SupabaseEditorialRepository(client)
    autor_repo = SupabaseAutorRepository(client)
    libro_repo = SupabaseLibroRepository(client)
    usuario_repo = SupabaseUsuarioRepository(client)
    preferencia_repo = SupabasePreferenciaRepository(client)

    # 3. Inyección de Dependencias: Casos de Uso (Application Layer)
    seed_use_case = SeedDataUseCase(
        genero_repo=genero_repo,
        editorial_repo=editorial_repo,
        autor_repo=autor_repo,
        libro_repo=libro_repo,
        usuario_repo=usuario_repo
    )

    cold_start_use_case = ColdStartRecommendationUseCase(
        libro_repo=libro_repo,
        usuario_repo=usuario_repo,
        genero_repo=genero_repo
    )

    registrar_preferencia_use_case = RegistrarPreferenciaUseCase(
        preferencia_repo=preferencia_repo,
        usuario_repo=usuario_repo,
        libro_repo=libro_repo
    )

    # 4. Ejecución del Caso de Uso: Carga de Datos Semilla
    logger.info("\n--- [PASO 1: Verificación / Carga de Catálogo y Datos Semilla] ---")
    seed_use_case.execute(force_reload=False)

    # 5. Ejecución del Caso de Uso: Recomendación Cold Start
    logger.info("\n--- [PASO 2: Demostración de Recomendación Cold Start] ---")
    test_user_email = "pabloleal@gmail.com"
    recomendaciones = cold_start_use_case.execute(test_user_email, limit=5)

    print(f"\n=== [RECOMENDACIONES COLD START] Para '{test_user_email}' ===")
    for idx, libro_dto in enumerate(recomendaciones, start=1):
        print(f"  {idx}. [{libro_dto.id_libro}] {libro_dto.titulo}")
        print(f"     Páginas: {libro_dto.nro_paginas} | Precio: ${libro_dto.precio:.2f}")
        print(f"     Descripción: {libro_dto.descripcion}")
        print()

    # 6. Ejecución del Caso de Uso: Registrar Feedback (Explícito e Implícito)
    logger.info("--- [PASO 3: Demostración de Registro de Preferencia (Rating / Click)] ---")
    # Calificación explícita de 5 estrellas
    pref_explicita = registrar_preferencia_use_case.execute(
        RegistrarPreferenciaDTO(email_usuario=test_user_email, id_libro=1, rating=5)
    )
    logger.info(f"Preferencia explícita registrada: Libro #{pref_explicita.id_libro}, Rating: {pref_explicita.rating}")

    # Interacción implícita (click / vista, rating es None)
    pref_implicita = registrar_preferencia_use_case.execute(
        RegistrarPreferenciaDTO(email_usuario=test_user_email, id_libro=7, rating=None)
    )
    logger.info(f"Interacción implícita registrada: Libro #{pref_implicita.id_libro}, Rating: {pref_implicita.rating}")

    logger.info("\n================================================================")
    logger.info("  FLUJO DE EJECUCIÓN DDD COMPLETADO SATISFACTORIAMENTE          ")
    logger.info("================================================================")


if __name__ == "__main__":
    main()
