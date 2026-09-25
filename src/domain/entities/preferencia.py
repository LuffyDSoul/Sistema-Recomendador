"""
Entidad de Dominio: Preferencia
Conecta Usuario y Libro con un Rating (explícito 1-5 o implícito None) y fecha.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional
from src.domain.value_objects.rating import Rating


@dataclass
class Preferencia:
    id_preferencia: Optional[int]
    id_usuario: int
    id_libro: int
    rating: Rating
    fecha: date

    def __post_init__(self):
        if not self.id_usuario or self.id_usuario <= 0:
            raise ValueError("id_usuario debe ser un identificador válido mayor a 0.")
        if not (1 <= self.id_libro <= 100):
            raise ValueError(f"id_libro fuera de catálogo (1-100): {self.id_libro}")
