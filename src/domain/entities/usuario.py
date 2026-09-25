"""
Entidad de Dominio / Aggregate Root: Usuario
Aplica invariante de Onboarding: máximo 3 géneros favoritos (multiplicidad 0..3).
"""

from dataclasses import dataclass, field
from typing import List, Optional
from src.domain.value_objects.email import Email
from src.domain.exceptions import MultiplicidadGenerosExcedidaException


@dataclass
class Usuario:
    id_usuario: Optional[int]
    nombre: str
    email: Email
    password: str
    generos_favoritos_ids: List[int] = field(default_factory=list)

    def __post_init__(self):
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre del usuario no puede estar vacío.")
        self.validar_generos_favoritos()

    def validar_generos_favoritos(self) -> None:
        """Invariante: Multiplicidad 0..3 para preferencias de género."""
        if len(self.generos_favoritos_ids) > 3:
            raise MultiplicidadGenerosExcedidaException(
                self.id_usuario or 0, len(self.generos_favoritos_ids)
            )

    def agregar_genero_favorito(self, id_genero: int) -> None:
        if id_genero in self.generos_favoritos_ids:
            return
        if len(self.generos_favoritos_ids) >= 3:
            raise MultiplicidadGenerosExcedidaException(
                self.id_usuario or 0, len(self.generos_favoritos_ids) + 1
            )
        self.generos_favoritos_ids.append(id_genero)

    def remover_genero_favorito(self, id_genero: int) -> None:
        if id_genero in self.generos_favoritos_ids:
            self.generos_favoritos_ids.remove(id_genero)
