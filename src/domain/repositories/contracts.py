"""
Interfaces / Contratos de Repositorios (Domain Layer)
Definen las operaciones requeridas por la lógica de negocio sin depender de la persistencia.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.autor import Autor
from src.domain.entities.editorial import Editorial
from src.domain.entities.genero import Genero
from src.domain.entities.libro import Libro
from src.domain.entities.usuario import Usuario
from src.domain.entities.preferencia import Preferencia


class IGeneroRepository(ABC):
    @abstractmethod
    def save_bulk(self, generos: List[Genero]) -> List[Genero]:
        pass

    @abstractmethod
    def get_all(self) -> List[Genero]:
        pass

    @abstractmethod
    def get_by_nombre(self, nombre: str) -> Optional[Genero]:
        pass


class IEditorialRepository(ABC):
    @abstractmethod
    def save_bulk(self, editoriales: List[Editorial]) -> List[Editorial]:
        pass

    @abstractmethod
    def get_all(self) -> List[Editorial]:
        pass


class IAutorRepository(ABC):
    @abstractmethod
    def save_bulk(self, autores: List[Autor]) -> List[Autor]:
        pass

    @abstractmethod
    def get_all(self) -> List[Autor]:
        pass


class ILibroRepository(ABC):
    @abstractmethod
    def save_bulk(self, libros: List[Libro]) -> None:
        pass

    @abstractmethod
    def get_by_id(self, id_libro: int) -> Optional[Libro]:
        pass

    @abstractmethod
    def get_all(self) -> List[Libro]:
        pass

    @abstractmethod
    def count(self) -> int:
        pass

    @abstractmethod
    def get_by_generos(self, generos_ids: List[int], limit: int = 10) -> List[Libro]:
        pass


class IUsuarioRepository(ABC):
    @abstractmethod
    def save_bulk(self, usuarios: List[Usuario]) -> List[Usuario]:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[Usuario]:
        pass

    @abstractmethod
    def get_all(self) -> List[Usuario]:
        pass

    @abstractmethod
    def save_preferencias_generos(self, usuario: Usuario) -> None:
        pass


class IPreferenciaRepository(ABC):
    @abstractmethod
    def save(self, preferencia: Preferencia) -> Preferencia:
        pass

    @abstractmethod
    def get_by_usuario(self, id_usuario: int) -> List[Preferencia]:
        pass
