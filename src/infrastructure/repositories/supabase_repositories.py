"""
Implementaciones de Repositorios en Supabase (Infraestructura)
Mapean datos relacionales hacia y desde Entidades de Dominio.
"""

from typing import List, Optional
from datetime import datetime, date
from src.domain.entities.autor import Autor
from src.domain.entities.editorial import Editorial
from src.domain.entities.genero import Genero
from src.domain.entities.libro import Libro
from src.domain.entities.usuario import Usuario
from src.domain.entities.preferencia import Preferencia
from src.domain.value_objects.email import Email
from src.domain.value_objects.rating import Rating
from src.domain.repositories.contracts import (
    IGeneroRepository,
    IEditorialRepository,
    IAutorRepository,
    ILibroRepository,
    IUsuarioRepository,
    IPreferenciaRepository
)
from src.infrastructure.supabase.client import SupabaseClient


class SupabaseGeneroRepository(IGeneroRepository):
    def __init__(self, client: SupabaseClient):
        self.client = client

    def save_bulk(self, generos: List[Genero]) -> List[Genero]:
        data = [{"nombre": g.nombre} for g in generos]
        self.client.insert("Genero", data, upsert=True)
        return self.get_all()

    def get_all(self) -> List[Genero]:
        rows = self.client.select("Genero", "select=idGenero,nombre&order=idGenero.asc")
        return [Genero(id_genero=r["idGenero"], nombre=r["nombre"]) for r in rows]

    def get_by_nombre(self, nombre: str) -> Optional[Genero]:
        rows = self.client.select("Genero", f"select=idGenero,nombre&nombre=eq.{nombre}")
        if rows:
            return Genero(id_genero=rows[0]["idGenero"], nombre=rows[0]["nombre"])
        return None


class SupabaseEditorialRepository(IEditorialRepository):
    def __init__(self, client: SupabaseClient):
        self.client = client

    def save_bulk(self, editoriales: List[Editorial]) -> List[Editorial]:
        data = [{"nombre": e.nombre} for e in editoriales]
        self.client.insert("Editorial", data, upsert=True)
        return self.get_all()

    def get_all(self) -> List[Editorial]:
        rows = self.client.select("Editorial", "select=idEditorial,nombre&order=idEditorial.asc")
        return [Editorial(id_editorial=r["idEditorial"], nombre=r["nombre"]) for r in rows]


class SupabaseAutorRepository(IAutorRepository):
    def __init__(self, client: SupabaseClient):
        self.client = client

    def save_bulk(self, autores: List[Autor]) -> List[Autor]:
        data = [{"nombre": a.nombre} for a in autores]
        self.client.insert("Autor", data, upsert=True)
        return self.get_all()

    def get_all(self) -> List[Autor]:
        rows = self.client.select("Autor", "select=idAutor,nombre&order=idAutor.asc")
        return [Autor(id_autor=r["idAutor"], nombre=r["nombre"]) for r in rows]


class SupabaseLibroRepository(ILibroRepository):
    def __init__(self, client: SupabaseClient):
        self.client = client

    def save_bulk(self, libros: List[Libro]) -> None:
        libros_payload = []
        genero_libro_payload = []

        for l in libros:
            libros_payload.append({
                "idLibro": l.id_libro,
                "titulo": l.titulo,
                "descripcion": l.descripcion,
                "nroPaginas": l.nro_paginas,
                "precio": l.precio,
                "idAutor": l.id_autor,
                "idEditorial": l.id_editorial
            })
            for gid in l.generos_ids:
                genero_libro_payload.append({
                    "idGenero": gid,
                    "idLibro": l.id_libro
                })

        # Insertar libros en lotes
        batch_size = 50
        for i in range(0, len(libros_payload), batch_size):
            self.client.insert("Libro", libros_payload[i:i + batch_size], upsert=True)

        # Insertar relaciones GeneroLibro
        for i in range(0, len(genero_libro_payload), batch_size):
            self.client.insert("GeneroLibro", genero_libro_payload[i:i + batch_size], upsert=True)

    def get_by_id(self, id_libro: int) -> Optional[Libro]:
        rows = self.client.select("Libro", f"select=*&idLibro=eq.{id_libro}")
        if not rows:
            return None
        r = rows[0]
        gl_rows = self.client.select("GeneroLibro", f"select=idGenero&idLibro=eq.{id_libro}")
        g_ids = [gl["idGenero"] for gl in gl_rows]

        return Libro(
            id_libro=r["idLibro"],
            titulo=r["titulo"],
            descripcion=r.get("descripcion", ""),
            nro_paginas=r["nroPaginas"],
            precio=float(r["precio"]),
            id_autor=r["idAutor"],
            id_editorial=r["idEditorial"],
            generos_ids=g_ids
        )

    def get_all(self) -> List[Libro]:
        rows = self.client.select("Libro", "select=*&order=idLibro.asc&limit=105")
        return [
            Libro(
                id_libro=r["idLibro"],
                titulo=r["titulo"],
                descripcion=r.get("descripcion", ""),
                nro_paginas=r["nroPaginas"],
                precio=float(r["precio"]),
                id_autor=r["idAutor"],
                id_editorial=r["idEditorial"]
            )
            for r in rows
        ]

    def count(self) -> int:
        rows = self.client.select("Libro", "select=idLibro")
        return len(rows)

    def get_by_generos(self, generos_ids: List[int], limit: int = 10) -> List[Libro]:
        if not generos_ids:
            return self.get_all()[:limit]

        ids_str = ",".join(str(gid) for gid in generos_ids)
        rows = self.client.select(
            "GeneroLibro",
            f"select=idLibro,Libro(*)&idGenero=in.({ids_str})&limit={limit * 2}"
        )

        libros_dict = {}
        for r in rows:
            book_data = r.get("Libro")
            if book_data and book_data["idLibro"] not in libros_dict:
                libros_dict[book_data["idLibro"]] = Libro(
                    id_libro=book_data["idLibro"],
                    titulo=book_data["titulo"],
                    descripcion=book_data.get("descripcion", ""),
                    nro_paginas=book_data["nroPaginas"],
                    precio=float(book_data["precio"]),
                    id_autor=book_data["idAutor"],
                    id_editorial=book_data["idEditorial"]
                )

        return list(libros_dict.values())[:limit]


class SupabaseUsuarioRepository(IUsuarioRepository):
    def __init__(self, client: SupabaseClient):
        self.client = client

    def save_bulk(self, usuarios: List[Usuario]) -> List[Usuario]:
        data = [
            {"nombre": u.nombre, "email": str(u.email), "password": u.password}
            for u in usuarios
        ]
        self.client.insert("Usuario", data, upsert=True)
        return self.get_all()

    def get_by_email(self, email: str) -> Optional[Usuario]:
        rows = self.client.select("Usuario", f"select=*&email=eq.{email}")
        if not rows:
            return None
        r = rows[0]
        # Recuperar géneros favoritos
        ug_rows = self.client.select("UsuarioGenero", f"select=idGenero&idUsuario=eq.{r['idUsuario']}")
        g_ids = [ug["idGenero"] for ug in ug_rows]

        return Usuario(
            id_usuario=r["idUsuario"],
            nombre=r["nombre"],
            email=Email(r["email"]),
            password=r["password"],
            generos_favoritos_ids=g_ids
        )

    def get_all(self) -> List[Usuario]:
        rows = self.client.select("Usuario", "select=*&order=idUsuario.asc")
        return [
            Usuario(
                id_usuario=r["idUsuario"],
                nombre=r["nombre"],
                email=Email(r["email"]),
                password=r["password"]
            )
            for r in rows
        ]

    def save_preferencias_generos(self, usuario: Usuario) -> None:
        usuario.validar_generos_favoritos()
        if not usuario.id_usuario:
            raise ValueError("El usuario debe tener un idUsuario asignado para registrar preferencias.")

        # Limpiar anteriores y registrar las nuevas
        self.client.delete("UsuarioGenero", f"idUsuario=eq.{usuario.id_usuario}")
        payload = [
            {"idUsuario": usuario.id_usuario, "idGenero": gid}
            for gid in usuario.generos_favoritos_ids
        ]
        if payload:
            self.client.insert("UsuarioGenero", payload, upsert=True)


class SupabasePreferenciaRepository(IPreferenciaRepository):
    def __init__(self, client: SupabaseClient):
        self.client = client

    def save(self, preferencia: Preferencia) -> Preferencia:
        payload = [{
            "idUsuario": preferencia.id_usuario,
            "idLibro": preferencia.id_libro,
            "rating": preferencia.rating.value,
            "fecha": str(preferencia.fecha)
        }]
        res = self.client.insert("Preferencia", payload, upsert=True)
        if res:
            preferencia.id_preferencia = res[0].get("idPreferencia")
        return preferencia

    def get_by_usuario(self, id_usuario: int) -> List[Preferencia]:
        rows = self.client.select("Preferencia", f"select=*&idUsuario=eq.{id_usuario}")
        return [
            Preferencia(
                id_preferencia=r["idPreferencia"],
                id_usuario=r["idUsuario"],
                id_libro=r["idLibro"],
                rating=Rating(r["rating"]),
                fecha=datetime.strptime(r["fecha"], "%Y-%m-%d").date() if isinstance(r["fecha"], str) else r["fecha"]
            )
            for r in rows
        ]
