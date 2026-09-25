"""
Caso de Uso: Carga de Datos Semilla del Sistema Recomendador
Carga los 12 géneros, 9 editoriales, 18 autores, 100 libros exactos y 20 usuarios con preferencias.
"""

import logging
from typing import Dict, Any, List
from src.domain.entities.genero import Genero
from src.domain.entities.editorial import Editorial
from src.domain.entities.autor import Autor
from src.domain.entities.libro import Libro
from src.domain.entities.usuario import Usuario
from src.domain.value_objects.email import Email
from src.domain.repositories.contracts import (
    IGeneroRepository,
    IEditorialRepository,
    IAutorRepository,
    ILibroRepository,
    IUsuarioRepository
)

logger = logging.getLogger(__name__)


class SeedDataUseCase:
    def __init__(
        self,
        genero_repo: IGeneroRepository,
        editorial_repo: IEditorialRepository,
        autor_repo: IAutorRepository,
        libro_repo: ILibroRepository,
        usuario_repo: IUsuarioRepository
    ):
        self.genero_repo = genero_repo
        self.editorial_repo = editorial_repo
        self.autor_repo = autor_repo
        self.libro_repo = libro_repo
        self.usuario_repo = usuario_repo

    def execute(self, force_reload: bool = False) -> None:
        logger.info("Ejecutando Caso de Uso: Cargar Catálogo de 100 Libros y Datos Semilla...")
        
        # 1. Comprobar si ya existe el catálogo de 100 libros
        total_libros = self.libro_repo.count()
        if total_libros >= 100 and not force_reload:
            logger.info(f"El catálogo ya cuenta con {total_libros} libros en Supabase. Omitiendo seed.")
            return

        # 2. Cargar Géneros
        generos_nombres = [
            "Ciencia Ficción", "Fantasía Épica", "Novela Policial", "Terror y Suspenso",
            "Desarrollo Personal", "Divulgación Científica", "Historia Universal",
            "Filosofía", "Realismo Mágico", "Distopía", "Biografía y Memorias", "Tecnología y Software"
        ]
        generos_entidades = [Genero(id_genero=None, nombre=n) for n in generos_nombres]
        self.genero_repo.save_bulk(generos_entidades)
        generos_db = {g.nombre: g.id_genero for g in self.genero_repo.get_all()}

        # 3. Cargar Editoriales
        editoriales_nombres = [
            "Penguin Random House", "Editorial Planeta", "Minotauro", "Alianza Editorial",
            "Fondo de Cultura Económica", "Anagrama", "O'Reilly Media", "Tusquets Editores", "Editorial Sudamericana"
        ]
        editoriales_entidades = [Editorial(id_editorial=None, nombre=n) for n in editoriales_nombres]
        self.editorial_repo.save_bulk(editoriales_entidades)
        editoriales_db = {e.nombre: e.id_editorial for e in self.editorial_repo.get_all()}

        # 4. Cargar Autores
        autores_nombres = [
            "Isaac Asimov", "J.R.R. Tolkien", "Agatha Christie", "Stephen King", "James Clear",
            "Carl Sagan", "Yuval Noah Harari", "Friedrich Nietzsche", "Gabriel García Márquez",
            "George Orwell", "Walter Isaacson", "Robert C. Martin", "Arthur C. Clarke",
            "Brandon Sanderson", "Arthur Conan Doyle", "H.P. Lovecraft", "Jorge Luis Borges", "Martin Fowler"
        ]
        autores_entidades = [Autor(id_autor=None, nombre=n) for n in autores_nombres]
        self.autor_repo.save_bulk(autores_entidades)
        autores_db = {a.nombre: a.id_autor for a in self.autor_repo.get_all()}

        # 5. Cargar los 100 libros exactos del catálogo
        from src.infrastructure.data.seed_data import CATALOGO_100_LIBROS
        
        libros_a_guardar: List[Libro] = []
        for idx, item in enumerate(CATALOGO_100_LIBROS, start=1):
            titulo, autor_nom, edit_nom, lista_generos, pags, precio, desc = item
            
            g_ids = [generos_db[gn] for gn in lista_generos if gn in generos_db]
            
            libro = Libro(
                id_libro=idx,
                titulo=titulo,
                descripcion=desc,
                nro_paginas=pags,
                precio=precio,
                id_autor=autores_db[autor_nom],
                id_editorial=editoriales_db[edit_nom],
                generos_ids=g_ids
            )
            libros_a_guardar.append(libro)

        self.libro_repo.save_bulk(libros_a_guardar)
        logger.info(f"Catálogo cerrado de {len(libros_a_guardar)} libros guardado exitosamente.")

        # 6. Cargar Usuarios
        from src.infrastructure.data.seed_data import USUARIOS_DATA, USUARIOS_GENEROS_NOMBRES
        usuarios_entidades = [
            Usuario(id_usuario=None, nombre=u["nombre"], email=Email(u["email"]), password=u["password"])
            for u in USUARIOS_DATA
        ]
        self.usuario_repo.save_bulk(usuarios_entidades)
        usuarios_db = {str(u.email): u for u in self.usuario_repo.get_all()}

        # 7. Asignar Preferencias de Géneros (Onboarding 0..3)
        for email_str, g_nombres in USUARIOS_GENEROS_NOMBRES.items():
            if email_str in usuarios_db:
                u = usuarios_db[email_str]
                g_ids = [generos_db[gn] for gn in g_nombres if gn in generos_db]
                u.generos_favoritos_ids = g_ids
                self.usuario_repo.save_preferencias_generos(u)

        logger.info("Caso de uso SeedDataUseCase finalizado exitosamente con principios DDD.")
