"""
Entidad de Dominio: Genero
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Genero:
    id_genero: Optional[int]
    nombre: str

    def __post_init__(self):
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre del género no puede estar vacío.")
        self.nombre = self.nombre.strip()
