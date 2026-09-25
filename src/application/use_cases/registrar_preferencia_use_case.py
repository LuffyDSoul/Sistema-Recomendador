"""
Caso de Uso: Registrar Preferencia o Interacción
Permite capturar calificaciones explícitas (1 a 5) o interacciones implícitas (rating = None).
"""

from datetime import date
from src.domain.entities.preferencia import Preferencia
from src.domain.value_objects.rating import Rating
from src.domain.repositories.contracts import IPreferenciaRepository, IUsuarioRepository, ILibroRepository
from src.application.dtos import RegistrarPreferenciaDTO


class RegistrarPreferenciaUseCase:
    def __init__(
        self,
        preferencia_repo: IPreferenciaRepository,
        usuario_repo: IUsuarioRepository,
        libro_repo: ILibroRepository
    ):
        self.preferencia_repo = preferencia_repo
        self.usuario_repo = usuario_repo
        self.libro_repo = libro_repo

    def execute(self, dto: RegistrarPreferenciaDTO) -> Preferencia:
        usuario = self.usuario_repo.get_by_email(dto.email_usuario)
        if not usuario or not usuario.id_usuario:
            raise ValueError(f"Usuario con email '{dto.email_usuario}' no encontrado.")

        libro = self.libro_repo.get_by_id(dto.id_libro)
        if not libro:
            raise ValueError(f"Libro con id '{dto.id_libro}' no existe en el catálogo.")

        # Construcción de la entidad de dominio con su Value Object Rating
        preferencia = Preferencia(
            id_preferencia=None,
            id_usuario=usuario.id_usuario,
            id_libro=dto.id_libro,
            rating=Rating(dto.rating),
            fecha=date.today()
        )

        return self.preferencia_repo.save(preferencia)
