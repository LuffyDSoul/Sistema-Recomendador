"""
Entidad de Dominio / Aggregate Root: Libro
Aplica invariantes de negocio: catálogo fijo (id 1 a 100), páginas y precio positivo.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from src.domain.exceptions import CatalogoLimiteExcedidoException


@dataclass
class Libro:
    id_libro: int
    titulo: str
    descripcion: str
    nro_paginas: int
    precio: float
    id_autor: int
    id_editorial: int
    generos_ids: List[int] = field(default_factory=list)

    def __post_init__(self):
        # Invariante 1: Catálogo fijo de exactamente 100 libros
        if not (1 <= self.id_libro <= 100):
            raise CatalogoLimiteExcedidoException(self.id_libro)

        # Invariante 2: Validación de páginas
        if self.nro_paginas <= 0:
            raise ValueError(f"El número de páginas debe ser mayor a 0. Recibido: {self.nro_paginas}")

        # Invariante 3: Validación de precio
        if self.precio < 0:
            raise ValueError(f"El precio no puede ser negativo. Recibido: {self.precio}")

        if not self.titulo or not self.titulo.strip():
            raise ValueError("El título del libro no puede estar vacío.")

    def asociar_genero(self, id_genero: int) -> None:
        if id_genero not in self.generos_ids:
            self.generos_ids.append(id_genero)
