"""
Pipeline Híbrido de Procesamiento y Generación de Recomendaciones (Fase 4: Modelado).

Ensambla secuencialmente las transformaciones de datos y coordina la selección
dinámica entre:
- Modelo 1: Filtrado Colaborativo Basado en Ítems (Item-Based CF con matriz 100x100).
- Modelo 2: Filtrado Basado en Contenido y Popularidad (Cold Start: Caso A y Caso B).
"""

import logging
from typing import Any, Dict, List, Optional

from src.infrastructure.supabase.client import SupabaseClient
from src.models.cold_start import ColdStartModel, IMPLICIT_RATING_IMPUTATION
from src.models.item_based_cf import CATALOGO_IDS, ItemBasedCFModel

logger = logging.getLogger(__name__)


class HybridRecommenderPipeline:
    """
    Pipeline de ensamblado de transformaciones que integra el Modelo 1 (Item-Based CF)
    y el Modelo 2 (Cold Start: Contenido + Popularidad) sobre el catálogo fijo de 100 libros.
    """

    def __init__(
        self,
        client: SupabaseClient,
        implicit_rating: float = IMPLICIT_RATING_IMPUTATION,
    ) -> None:
        self.client = client
        self.implicit_rating = float(implicit_rating)
        self.cf_model = ItemBasedCFModel(implicit_rating=self.implicit_rating)
        self.cold_start_model = ColdStartModel(implicit_rating=self.implicit_rating)

        self.books_catalog: Dict[int, Dict[str, Any]] = {}
        self.users_by_id: Dict[int, Dict[str, Any]] = {}
        self.users_by_email: Dict[str, Dict[str, Any]] = {}
        self.genres_list: List[Dict[str, Any]] = []
        self.total_preferences_loaded: int = 0
        self.is_trained: bool = False

    def fit(self) -> "HybridRecommenderPipeline":
        """
        Ejecuta el pipeline completo de extracción, preprocesamiento, imputación
        de feedback implícito (rating nulo -> 3.0), matriz de utilidad y matriz
        de similitud del coseno 100x100.
        """
        logger.info("Ejecutando pipeline de entrenamiento híbrido desde Supabase...")

        # 1. Extracción de tablas desde Supabase
        libros_rows = self.client.select("Libro", "select=*&order=idLibro.asc")
        autores_rows = self.client.select("Autor", "select=idAutor,nombre")
        editoriales_rows = self.client.select("Editorial", "select=idEditorial,nombre")
        generos_rows = self.client.select("Genero", "select=idGenero,nombre&order=idGenero.asc")
        genero_libro_rows = self.client.select("GeneroLibro", "select=idGenero,idLibro")
        usuarios_rows = self.client.select("Usuario", "select=idUsuario,nombre,email&order=idUsuario.asc")
        preferencias_rows = self.client.select(
            "Preferencia",
            "select=idPreferencia,idUsuario,idLibro,rating,fecha&order=idPreferencia.asc",
        )

        autores_map = {int(r["idAutor"]): r["nombre"] for r in autores_rows}
        editoriales_map = {int(r["idEditorial"]): r["nombre"] for r in editoriales_rows}
        generos_map = {int(r["idGenero"]): r["nombre"] for r in generos_rows}

        # Mapear géneros por libro
        libro_generos_ids: Dict[int, List[int]] = {}
        libro_generos_nombres: Dict[int, List[str]] = {}
        for rel in genero_libro_rows:
            bid = int(rel["idLibro"])
            gid = int(rel["idGenero"])
            libro_generos_ids.setdefault(bid, []).append(gid)
            if gid in generos_map:
                libro_generos_nombres.setdefault(bid, []).append(generos_map[gid])

        # 2. Entrenar Modelo 1 (Item-Based CF: Imputación rating=3.0 + Matriz Utilidad + Similitud 100x100)
        self.cf_model.fit(preferencias_rows)

        # 3. Entrenar Modelo 2 (Cold Start: Métricas globales de ventas y calificaciones + índice GeneroLibro)
        self.cold_start_model.fit(
            preferences=preferencias_rows,
            genero_libro_rows=genero_libro_rows,
            generos_rows=generos_rows,
            all_book_ids=CATALOGO_IDS,
        )

        # 4. Construir catálogo enriquecido de los 100 libros
        self.books_catalog = {}
        for libro in libros_rows:
            bid = int(libro["idLibro"])
            metrics = self.cold_start_model.book_metrics.get(bid, {})
            self.books_catalog[bid] = {
                "id_libro": bid,
                "titulo": libro["titulo"],
                "autor": autores_map.get(int(libro["idAutor"]), "Desconocido"),
                "editorial": editoriales_map.get(int(libro["idEditorial"]), "Desconocida"),
                "descripcion": libro.get("descripcion", ""),
                "nro_paginas": int(libro["nroPaginas"]),
                "precio": float(libro["precio"]),
                "generos_ids": libro_generos_ids.get(bid, []),
                "generos": libro_generos_nombres.get(bid, []),
                "promedio_rating": metrics.get("promedio_rating", 0.0),
                "volumen_ventas": metrics.get("volumen_ventas", 0),
            }

        # 5. Indexar usuarios
        self.users_by_id = {}
        self.users_by_email = {}
        for u in usuarios_rows:
            uid = int(u["idUsuario"])
            user_obj = {
                "idUsuario": uid,
                "nombre": u["nombre"],
                "email": u["email"],
                "cantidad_compras": len(self.cf_model.utility_matrix.get(uid, {})),
                "es_cold_start": not self.cf_model.has_user_history(uid),
            }
            self.users_by_id[uid] = user_obj
            self.users_by_email[u["email"].strip().lower()] = user_obj

        sorted_genres = sorted(generos_rows, key=lambda g: int(g["idGenero"]))
        self.genres_list = [
            {
                "posicion": idx,
                "idGenero": int(g["idGenero"]),
                "nombre": g["nombre"],
            }
            for idx, g in enumerate(sorted_genres, start=1)
        ]
        self.total_preferences_loaded = len(preferencias_rows)
        self.is_trained = True

        logger.info(
            "Pipeline entrenado: %s libros, %s usuarios, %s preferencias, matriz similitud 100x100 lista.",
            len(self.books_catalog),
            len(self.users_by_id),
            self.total_preferences_loaded,
        )
        return self

    def _ensure_trained(self) -> None:
        if not self.is_trained:
            self.fit()

    def resolve_user(
        self,
        user_id: Optional[int] = None,
        email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Localiza un usuario por idUsuario o por email."""
        self._ensure_trained()
        if user_id is not None:
            uid = int(user_id)
            if uid in self.users_by_id:
                return self.users_by_id[uid]
            raise ValueError(
                f"No existe el usuario con idUsuario={uid}. Consulte GET /api/usuarios para ver los IDs disponibles."
            )
        if email:
            key = email.strip().lower()
            if key in self.users_by_email:
                return self.users_by_email[key]
            raise ValueError(
                f"No existe el usuario con email='{email}'. Consulte GET /api/usuarios para ver los usuarios disponibles."
            )
        raise ValueError("Debe proporcionar 'id_usuario' (idUsuario) o 'email'.")

    def get_user_purchase_details(self, user_id: int) -> List[Dict[str, Any]]:
        """Devuelve el historial de compras del usuario mostrando el rating real y el imputado (3.0)."""
        self._ensure_trained()
        uid = int(user_id)
        imputed_map = self.cf_model.utility_matrix.get(uid, {})
        raw_map = self.cf_model.raw_user_history.get(uid, {})

        history: List[Dict[str, Any]] = []
        for bid, imputed_val in imputed_map.items():
            raw_val = raw_map.get(bid)
            book = self.books_catalog.get(bid, {})
            history.append({
                "idLibro": bid,
                "titulo": book.get("titulo", f"Libro #{bid}"),
                "generos": book.get("generos", []),
                "ratingOriginal": raw_val,
                "ratingPreprocesado": imputed_val,
                "fueImputado": raw_val is None,
            })
        history.sort(key=lambda x: (x["ratingPreprocesado"], x["idLibro"]), reverse=True)
        return history

    def recommend(
        self,
        user_id: Optional[int] = None,
        email: Optional[str] = None,
        genre_ids: Optional[List[int]] = None,
        k: int = 5,
    ) -> Dict[str, Any]:
        """
        Orquestador Híbrido (Fase 4):
        1. Verifica si el idUsuario posee registros en la tabla Preferencia.
        2. Si posee compras -> ejecuta Modelo 1: Filtrado Colaborativo Basado en Ítems (Item-Based CF).
        3. Si NO posee compras -> ejecuta Modelo 2: Filtrado Basado en Contenido y Popularidad (Cold Start)
           utilizando el arreglo de hasta 3 IDs de géneros recibido por HTTP (Caso A) o popularidad global (Caso B).
        """
        self._ensure_trained()
        user = self.resolve_user(user_id=user_id, email=email)
        uid = user["idUsuario"]

        if self.cf_model.has_user_history(uid):
            # Activar Modelo 1: Filtrado Colaborativo Basado en Ítems
            recomendaciones = self.cf_model.score_and_recommend(
                user_id=uid,
                books_catalog=self.books_catalog,
                k=k,
            )
            compras = self.get_user_purchase_details(uid)
            return {
                "usuario": user,
                "modelo_aplicado": "Modelo 1: Filtrado Colaborativo Basado en Ítems (Item-Based CF)",
                "estrategia": "Similitud del Coseno sobre Matriz Estática 100x100 + Imputación Implícita (rating NULL -> 3.0)",
                "parametros": {
                    "k": int(k),
                    "imputacion_rating_nulo": self.implicit_rating,
                    "dimension_matriz_similitud": "100x100",
                },
                "historial_compras_usuario": {
                    "total_libros_comprados": len(compras),
                    "compras_con_rating_explicito": sum(1 for c in compras if not c["fueImputado"]),
                    "compras_imputadas_con_3": sum(1 for c in compras if c["fueImputado"]),
                    "detalle": compras,
                },
                "total_recomendaciones": len(recomendaciones),
                "recomendaciones": recomendaciones,
            }

        # Activar Modelo 2: Filtrado Basado en Contenido y Popularidad (Cold Start)
        sub_case, recomendaciones, generos_aplicados = self.cold_start_model.recommend(
            books_catalog=self.books_catalog,
            genre_ids=genre_ids,
            k=k,
        )
        return {
            "usuario": user,
            "modelo_aplicado": "Modelo 2: Filtrado Basado en Contenido y Popularidad (Cold Start)",
            "estrategia": sub_case,
            "parametros": {
                "k": int(k),
                "generos_recibidos_http": genre_ids or [],
                "generos_aplicados": generos_aplicados,
            },
            "historial_compras_usuario": {
                "total_libros_comprados": 0,
                "estado": "Usuario sin compras registradas en Preferencia (Cold Start activo)",
            },
            "total_recomendaciones": len(recomendaciones),
            "recomendaciones": recomendaciones,
        }

    def recommend_collaborative_only(
        self,
        user_id: Optional[int] = None,
        email: Optional[str] = None,
        k: int = 5,
    ) -> Dict[str, Any]:
        """Ejecuta explícitamente el Modelo 1 (Item-Based CF) para un usuario con compras."""
        self._ensure_trained()
        user = self.resolve_user(user_id=user_id, email=email)
        uid = user["idUsuario"]

        if not self.cf_model.has_user_history(uid):
            raise ValueError(
                f"El usuario {uid} ({user['email']}) no posee compras en 'Preferencia'. "
                "El Modelo 1 (Item-Based CF) requiere historial; utilice el endpoint híbrido (/api/recomendaciones) "
                "o el de Cold Start (/api/modelo/cold-start)."
            )

        recomendaciones = self.cf_model.score_and_recommend(
            user_id=uid,
            books_catalog=self.books_catalog,
            k=k,
        )
        compras = self.get_user_purchase_details(uid)
        return {
            "usuario": user,
            "modelo_aplicado": "Modelo 1: Filtrado Colaborativo Basado en Ítems (Item-Based CF)",
            "parametros": {
                "k": int(k),
                "imputacion_rating_nulo": self.implicit_rating,
                "dimension_matriz_similitud": "100x100",
            },
            "historial_compras_usuario": {
                "total_libros_comprados": len(compras),
                "compras_con_rating_explicito": sum(1 for c in compras if not c["fueImputado"]),
                "compras_imputadas_con_3": sum(1 for c in compras if c["fueImputado"]),
                "detalle": compras,
            },
            "total_recomendaciones": len(recomendaciones),
            "recomendaciones": recomendaciones,
        }

    def recommend_cold_start_only(
        self,
        genre_ids: Optional[List[int]] = None,
        k: int = 5,
        user_id: Optional[int] = None,
        email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Ejecuta explícitamente el Modelo 2 (Cold Start: Caso A con géneros o Caso B sin géneros).
        Puede invocarse pasando opcionalmente un usuario o directamente la lista de hasta 3 IDs de géneros.
        """
        self._ensure_trained()
        user_info = None
        if user_id is not None or email is not None:
            user_info = self.resolve_user(user_id=user_id, email=email)

        sub_case, recomendaciones, generos_aplicados = self.cold_start_model.recommend(
            books_catalog=self.books_catalog,
            genre_ids=genre_ids,
            k=k,
        )
        return {
            "usuario": user_info,
            "modelo_aplicado": "Modelo 2: Filtrado Basado en Contenido y Popularidad (Cold Start)",
            "estrategia": sub_case,
            "parametros": {
                "k": int(k),
                "generos_recibidos_http": genre_ids or [],
                "generos_aplicados": generos_aplicados,
            },
            "total_recomendaciones": len(recomendaciones),
            "recomendaciones": recomendaciones,
        }

    def get_similarity_info(
        self,
        book_id: Optional[int] = None,
        k: int = 5,
    ) -> Dict[str, Any]:
        """Devuelve metadatos de la matriz 100x100 o el Top-k de libros más similares a un idLibro."""
        self._ensure_trained()
        if book_id is not None:
            bid = int(book_id)
            if bid not in self.books_catalog:
                raise ValueError(f"El libro con idLibro={bid} no existe en el catálogo (1..100).")
            similares = self.cf_model.get_similar_items(
                book_id=bid,
                books_catalog=self.books_catalog,
                k=k,
            )
            return {
                "dimension_matriz": "100x100",
                "metrica": "Similitud del Coseno (Item-Based CF)",
                "libro_base": self.books_catalog[bid],
                "top_k_similares": similares,
            }

        # Resumen general de la matriz 100x100
        non_zero_pairs = 0
        for i in CATALOGO_IDS:
            for j in CATALOGO_IDS:
                if i != j and self.cf_model.similarity_matrix[i][j] > 0.0:
                    non_zero_pairs += 1

        sample_ids = CATALOGO_IDS[:5]
        muestra_5x5 = {
            str(i): {str(j): self.cf_model.similarity_matrix[i][j] for j in sample_ids}
            for i in sample_ids
        }
        return {
            "dimension_matriz": "100x100",
            "total_celdas": 100 * 100,
            "pares_distintos_con_similitud_positiva": non_zero_pairs,
            "imputacion_feedback_implicito": self.implicit_rating,
            "usuarios_en_matriz_utilidad": len(self.cf_model.utility_matrix),
            "muestra_submatriz_5x5_libros_1_a_5": muestra_5x5,
        }
