"""
Value Object: Email
Garantiza inmutabilidad y validación de formato.
"""

from dataclasses import dataclass
from src.domain.exceptions import EmailInvalidoException


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if not self.value or "@" not in self.value or "." not in self.value.split("@")[-1]:
            raise EmailInvalidoException(self.value)

    def __str__(self) -> str:
        return self.value
