"""
Entidad de Dominio: Editorial
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Editorial:
    id_editorial: Optional[int]
    nombre: str

    def __post_init__(self):
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre de la editorial no puede estar vacío.")
        self.nombre = self.nombre.strip()
