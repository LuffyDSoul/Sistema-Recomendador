"""
Caso de Uso: Recomendación para Usuarios Nuevos (Cold Start)
Resuelve el arranque en frío apoyándose en los géneros de interés elegidos en el onboarding (0..3).
"""

import logging
from typing import List
from src.domain.repositories.contracts import ILibroRepository, IUsuarioRepository, IGeneroRepository
from src.application.dtos import LibroRecomendadoDTO

logger = logging.getLogger(__name__)


class ColdStartRecommendationUseCase:
    def __init__(
        self,
        libro_repo: ILibroRepository,
        usuario_repo: IUsuarioRepository,
        genero_repo: IGeneroRepository
    ):
        self.libro_repo = libro_repo
        self.usuario_repo = usuario_repo
        self.genero_repo = genero_repo

    def execute(self, email_usuario: str, limit: int = 5) -> List[LibroRecomendadoDTO]:
        logger.info(f"Generando recomendaciones de Cold Start para el usuario '{email_usuario}'...")
        
        usuario = self.usuario_repo.get_by_email(email_usuario)
        if not usuario:
            raise ValueError(f"No se encontró un usuario con el email '{email_usuario}'.")

        generos_todos = {g.id_genero: g.nombre for g in self.genero_repo.get_all()}

        # 1. Si el usuario seleccionó géneros en onboarding (hasta 3), recomendar libros de esos géneros
        if usuario.generos_favoritos_ids:
            logger.info(f"Usuario cuenta con {len(usuario.generos_favoritos_ids)} géneros favoritos.")
            libros = self.libro_repo.get_by_generos(usuario.generos_favoritos_ids, limit=limit)
        else:
            # 2. Si no seleccionó géneros, recomendar catálogo base
            logger.info("El usuario no tiene géneros en onboarding. Recomendando catálogo general.")
            libros = self.libro_repo.get_all()[:limit]

        # 3. Mapear a DTOs para la capa de presentación
        resultado: List[LibroRecomendadoDTO] = []
        for l in libros:
            nombres_generos = [generos_todos.get(gid, "General") for gid in l.generos_ids]
            dto = LibroRecomendadoDTO(
                id_libro=l.id_libro,
                titulo=l.titulo,
                descripcion=l.descripcion,
                nro_paginas=l.nro_paginas,
                precio=l.precio,
                generos=nombres_generos
            )
            resultado.append(dto)

        return resultado
