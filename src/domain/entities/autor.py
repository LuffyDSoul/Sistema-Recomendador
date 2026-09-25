"""
Entidad de Dominio: Autor
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Autor:
    id_autor: Optional[int]
    nombre: str

    def __post_init__(self):
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre del autor no puede estar vacío.")
        self.nombre = self.nombre.strip()
