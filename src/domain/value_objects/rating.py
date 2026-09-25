"""
Value Object: Rating
Representa feedback explícito (1-5) o implícito (None / click / vista).
"""

from dataclasses import dataclass
from typing import Optional
from src.domain.exceptions import RatingInvalidoException


@dataclass(frozen=True)
class Rating:
    value: Optional[int]

    def __post_init__(self):
        if self.value is not None:
            if not isinstance(self.value, int) or not (1 <= self.value <= 5):
                raise RatingInvalidoException(self.value)

    @property
    def es_implicito(self) -> bool:
        return self.value is None

    @property
    def es_explicito(self) -> bool:
        return self.value is not None

    def __int__(self) -> int:
        return self.value or 0

    def __str__(self) -> str:
        return f"{self.value} estrellas" if self.value is not None else "Interacción implícita"
