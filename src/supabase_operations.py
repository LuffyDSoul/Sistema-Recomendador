"""Operaciones de la aplicación directamente sobre Supabase."""

import logging
from datetime import date
from typing import Any, Dict, List, Optional

from src.infrastructure.data.seed_data import (
    CATALOGO_100_LIBROS,
    USUARIOS_DATA,
    USUARIOS_GENEROS_NOMBRES,
)
from src.infrastructure.supabase.client import SupabaseClient

logger = logging.getLogger(__name__)


def _insertar_catalogo(client: SupabaseClient) -> None:
    generos = [
        "Ciencia Ficción", "Fantasía Épica", "Novela Policial", "Terror y Suspenso",
        "Desarrollo Personal", "Divulgación Científica", "Historia Universal",
        "Filosofía", "Realismo Mágico", "Distopía", "Biografía y Memorias",
        "Tecnología y Software",
    ]
    editoriales = [
        "Penguin Random House", "Editorial Planeta", "Minotauro", "Alianza Editorial",
        "Fondo de Cultura Económica", "Anagrama", "O'Reilly Media", "Tusquets Editores",
        "Editorial Sudamericana",
    ]
    autores = [
        "Isaac Asimov", "J.R.R. Tolkien", "Agatha Christie", "Stephen King", "James Clear",
        "Carl Sagan", "Yuval Noah Harari", "Friedrich Nietzsche", "Gabriel García Márquez",
        "George Orwell", "Walter Isaacson", "Robert C. Martin", "Arthur C. Clarke",
        "Brandon Sanderson", "Arthur Conan Doyle", "H.P. Lovecraft", "Jorge Luis Borges",
        "Martin Fowler",
    ]

    client.insert("Genero", [{"nombre": nombre} for nombre in generos], upsert=True)
    client.insert("Editorial", [{"nombre": nombre} for nombre in editoriales], upsert=True)
    client.insert("Autor", [{"nombre": nombre} for nombre in autores], upsert=True)

    genero_rows = client.select("Genero", "select=idGenero,nombre")
    editorial_rows = client.select("Editorial", "select=idEditorial,nombre")
    autor_rows = client.select("Autor", "select=idAutor,nombre")
    genero_ids = {row["nombre"]: row["idGenero"] for row in genero_rows}
    editorial_ids = {row["nombre"]: row["idEditorial"] for row in editorial_rows}
    autor_ids = {row["nombre"]: row["idAutor"] for row in autor_rows}

    libros = []
    relaciones_genero = []
    for id_libro, item in enumerate(CATALOGO_100_LIBROS, start=1):
        titulo, autor, editorial, nombres_generos, paginas, precio, descripcion = item
        libros.append({
            "idLibro": id_libro,
            "titulo": titulo,
            "descripcion": descripcion,
            "nroPaginas": paginas,
            "precio": precio,
            "idAutor": autor_ids[autor],
            "idEditorial": editorial_ids[editorial],
        })
        relaciones_genero.extend(
            {"idGenero": genero_ids[nombre], "idLibro": id_libro}
            for nombre in nombres_generos
            if nombre in genero_ids
        )

    for inicio in range(0, len(libros), 50):
        client.insert("Libro", libros[inicio:inicio + 50], upsert=True)
    for inicio in range(0, len(relaciones_genero), 50):
        client.insert("GeneroLibro", relaciones_genero[inicio:inicio + 50], upsert=True)

    usuarios = [
        {"nombre": usuario["nombre"], "email": usuario["email"], "password": usuario["password"]}
        for usuario in USUARIOS_DATA
    ]
    client.insert("Usuario", usuarios, upsert=True)
    usuario_rows = client.select("Usuario", "select=idUsuario,email")
    usuario_ids = {row["email"]: row["idUsuario"] for row in usuario_rows}

    relaciones_usuario = []
    for email, nombres_generos in USUARIOS_GENEROS_NOMBRES.items():
        if email not in usuario_ids:
            continue
        relaciones_usuario.extend(
            {"idUsuario": usuario_ids[email], "idGenero": genero_ids[nombre]}
            for nombre in nombres_generos
            if nombre in genero_ids
        )
    if relaciones_usuario:
        client.insert("UsuarioGenero", relaciones_usuario, upsert=True)


def cargar_datos(client: SupabaseClient, force_reload: bool = False) -> None:
    """Carga el catálogo y los usuarios si todavía no hay 100 libros."""
    total_libros = len(client.select("Libro", "select=idLibro"))
    if total_libros >= 100 and not force_reload:
        logger.info("El catálogo ya cuenta con %s libros. Se omite la carga.", total_libros)
        return
    _insertar_catalogo(client)
    logger.info("Catálogo y usuarios cargados en Supabase.")


def buscar_usuario(client: SupabaseClient, email: str) -> Optional[Dict[str, Any]]:
    rows = client.select("Usuario", f"select=*&email=eq.{email}")
    if not rows:
        return None
    usuario = rows[0]
    generos = client.select(
        "UsuarioGenero",
        f"select=idGenero&idUsuario=eq.{usuario['idUsuario']}",
    )
    usuario["generos_favoritos_ids"] = [row["idGenero"] for row in generos]
    return usuario


def recomendar(client: SupabaseClient, email: str, limit: int = 5) -> List[Dict[str, Any]]:
    usuario = buscar_usuario(client, email)
    if not usuario:
        raise ValueError(f"No se encontró un usuario con el email '{email}'.")

    generos = client.select("Genero", "select=idGenero,nombre")
    nombres_generos = {row["idGenero"]: row["nombre"] for row in generos}
    favoritos = usuario["generos_favoritos_ids"]

    if favoritos:
        ids = ",".join(str(id_genero) for id_genero in favoritos)
        relaciones = client.select(
            "GeneroLibro",
            f"select=idLibro,Libro(*)&idGenero=in.({ids})&limit={limit * 2}",
        )
        libros_por_id = {
            row["Libro"]["idLibro"]: row["Libro"]
            for row in relaciones
            if row.get("Libro")
        }
        libros = list(libros_por_id.values())[:limit]
    else:
        libros = client.select("Libro", f"select=*&order=idLibro.asc&limit={limit}")

    resultado = []
    for libro in libros:
        relaciones = client.select(
            "GeneroLibro",
            f"select=idGenero&idLibro=eq.{libro['idLibro']}",
        )
        resultado.append({
            "id_libro": libro["idLibro"],
            "titulo": libro["titulo"],
            "descripcion": libro.get("descripcion", ""),
            "nro_paginas": libro["nroPaginas"],
            "precio": float(libro["precio"]),
            "generos": [nombres_generos.get(row["idGenero"], "General") for row in relaciones],
        })
    return resultado


def registrar_preferencia(
    client: SupabaseClient,
    email: str,
    id_libro: int,
    rating: Optional[int] = None,
) -> Dict[str, Any]:
    usuario = buscar_usuario(client, email)
    if not usuario:
        raise ValueError(f"Usuario con email '{email}' no encontrado.")
    libros = client.select("Libro", f"select=idLibro&idLibro=eq.{id_libro}")
    if not libros:
        raise ValueError(f"Libro con id '{id_libro}' no existe en el catálogo.")
    if rating is not None and (not isinstance(rating, int) or not 1 <= rating <= 5):
        raise ValueError("El rating debe ser un entero entre 1 y 5, o None.")

    respuesta = client.insert("Preferencia", [{
        "idUsuario": usuario["idUsuario"],
        "idLibro": id_libro,
        "rating": rating,
        "fecha": str(date.today()),
    }], upsert=True)
    return respuesta[0] if respuesta else {
        "idLibro": id_libro,
        "rating": rating,
    }