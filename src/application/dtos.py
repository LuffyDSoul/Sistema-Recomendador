"""
Data Transfer Objects (Application Layer)
Estructuras de datos para transferir información entre capas sin exponer entidades completas.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class LibroRecomendadoDTO:
    id_libro: int
    titulo: str
    descripcion: str
    nro_paginas: int
    precio: float
    generos: List[str]


@dataclass(frozen=True)
class RegistrarPreferenciaDTO:
    email_usuario: str
    id_libro: int
    rating: Optional[int] = None  # None para interacción implícita
