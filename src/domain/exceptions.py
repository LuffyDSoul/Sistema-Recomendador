"""
Excepciones del Dominio
Define los errores de negocio independientes de la infraestructura o base de datos.
"""

class DomainException(Exception):
    """Excepción base del dominio."""
    pass


class CatalogoLimiteExcedidoException(DomainException):
    """Lanzada cuando se intenta registrar un libro fuera del rango permitido (1 a 100)."""
    def __init__(self, id_libro: int):
        super().__init__(
            f"Violación de Invariante de Dominio: El catálogo cuenta con exactamente 100 libros fijos. "
            f"El id {id_libro} es inválido."
        )


class MultiplicidadGenerosExcedidaException(DomainException):
    """Lanzada cuando un usuario intenta asociar más de 3 géneros en Onboarding (regla 0..3)."""
    def __init__(self, id_usuario: int, cantidad: int):
        super().__init__(
            f"Violación de Invariante de Dominio: El usuario {id_usuario} intentó seleccionar {cantidad} "
            f"géneros. La regla de negocio estipula un máximo de 3 (multiplicidad 0..3)."
        )


class RatingInvalidoException(DomainException):
    """Lanzada cuando una calificación explícita no está en el rango de 1 a 5."""
    def __init__(self, rating: int):
        super().__init__(
            f"Violación de Invariante de Dominio: El rating explícito debe estar entre 1 y 5. Valor recibido: {rating}."
        )


class EmailInvalidoException(DomainException):
    """Lanzada cuando un email no cumple con el formato requerido."""
    def __init__(self, email: str):
        super().__init__(f"El email '{email}' no tiene un formato válido.")
