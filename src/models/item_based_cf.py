"""
Modelo 1: Filtrado Colaborativo Basado en Ítems (Item-Based Collaborative Filtering).

Implementa los pasos definidos en la Fase 4 (Modelado):
1. Datos de entrada: Tabla Preferencia (idUsuario, idLibro, rating).
2. Preprocesamiento e imputación implícita: Compras con rating nulo (None) se imputan con 3.0.
3. Construcción de la matriz de utilidad: Filas = usuarios, Columnas = 100 libros (1..100), Valores = ratings.
4. Cálculo de similitud: Similitud del Coseno entre columnas (libros) generando una matriz fija de 100x100.
5. Generación de puntajes (Scoring): Producto punto entre los ratings de los libros adquiridos por el usuario
   y los vectores de similitud correspondientes en la matriz 100x100.
6. Filtrado Post-Modelo: Exclusión de los libros ya adquiridos previamente por el usuario y retorno del Top-k.
"""

import math
from typing import Any, Dict, List, Optional, Tuple

CATALOGO_IDS: List[int] = list(range(1, 101))
IMPLICIT_RATING_IMPUTATION: float = 3.0


class ItemBasedCFModel:
    """Modelo de Filtrado Colaborativo Basado en Ítems con matriz estática 100x100."""

    def __init__(self, implicit_rating: float = IMPLICIT_RATING_IMPUTATION) -> None:
        self.implicit_rating = float(implicit_rating)
        # Matriz de utilidad: {id_usuario: {id_libro (1..100): rating_imputado}}
        self.utility_matrix: Dict[int, Dict[int, float]] = {}
        # Historial original para trazabilidad: {id_usuario: {id_libro: rating_original (int | None)}}
        self.raw_user_history: Dict[int, Dict[int, Optional[int]]] = {}
        # Matriz de similitud del coseno 100x100: {id_libro_i: {id_libro_j: sim_ij}}
        self.similarity_matrix: Dict[int, Dict[int, float]] = {
            i: {j: (1.0 if i == j else 0.0) for j in CATALOGO_IDS}
            for i in CATALOGO_IDS
        }

    def preprocess_preferences(
        self, preferences: List[Dict[str, Any]]
    ) -> Tuple[Dict[int, Dict[int, float]], Dict[int, Dict[int, Optional[int]]]]:
        """
        Paso 1 y Paso 2: Extrae (idUsuario, idLibro, rating) e imputa rating=3.0
        cuando el registro de compra carece de calificación explícita (rating is None).
        """
        utility: Dict[int, Dict[int, float]] = {}
        raw_history: Dict[int, Dict[int, Optional[int]]] = {}

        for row in preferences:
            user_id = int(row["idUsuario"])
            book_id = int(row["idLibro"])
            if book_id < 1 or book_id > 100:
                continue

            raw_rating = row.get("rating")
            imputed_rating = (
                float(raw_rating) if raw_rating is not None else self.implicit_rating
            )

            if user_id not in utility:
                utility[user_id] = {}
                raw_history[user_id] = {}

            # Si ya había una interacción para el mismo (usuario, libro), priorizar rating explícito
            if book_id in raw_history[user_id] and raw_history[user_id][book_id] is not None and raw_rating is None:
                continue

            utility[user_id][book_id] = imputed_rating
            raw_history[user_id][book_id] = int(raw_rating) if raw_rating is not None else None

        return utility, raw_history

    def build_utility_matrix(
        self, preferences: List[Dict[str, Any]]
    ) -> Dict[int, Dict[int, float]]:
        """
        Paso 3: Pivota los datos preprocesados para construir la matriz de utilidad
        Usuarios x 100 Libros.
        """
        self.utility_matrix, self.raw_user_history = self.preprocess_preferences(preferences)
        return self.utility_matrix

    @staticmethod
    def _cosine_similarity_vectors(
        col_i: Dict[int, float],
        col_j: Dict[int, float],
        norm_i: float,
        norm_j: float,
    ) -> float:
        """Calcula cos(theta) = (v_i . v_j) / (||v_i|| * ||v_j||) entre dos libros."""
        if norm_i == 0.0 or norm_j == 0.0:
            return 0.0

        # Producto punto sobre los usuarios en común que interactuaron con ambos libros
        if len(col_i) <= len(col_j):
            dot_product = sum(val * col_j.get(u, 0.0) for u, val in col_i.items())
        else:
            dot_product = sum(val * col_i.get(u, 0.0) for u, val in col_j.items())

        if dot_product == 0.0:
            return 0.0

        return round(dot_product / (norm_i * norm_j), 6)

    def compute_similarity_matrix(self) -> Dict[int, Dict[int, float]]:
        """
        Paso 4: Aplica Similitud del Coseno entre las 100 columnas (libros) de la matriz
        de utilidad para obtener la matriz simétrica estática de 100x100.
        """
        # Invertir a vista por columnas: {id_libro: {id_usuario: rating}}
        item_columns: Dict[int, Dict[int, float]] = {book_id: {} for book_id in CATALOGO_IDS}
        for user_id, items in self.utility_matrix.items():
            for book_id, rating in items.items():
                if 1 <= book_id <= 100 and rating > 0.0:
                    item_columns[book_id][user_id] = rating

        # Precalcular normas euclidianas ||v_i|| para cada uno de los 100 libros
        norms: Dict[int, float] = {
            book_id: math.sqrt(sum(r * r for r in user_ratings.values()))
            for book_id, user_ratings in item_columns.items()
        }

        sim_matrix: Dict[int, Dict[int, float]] = {i: {} for i in CATALOGO_IDS}
        for idx_i, book_i in enumerate(CATALOGO_IDS):
            sim_matrix[book_i][book_i] = 1.0
            for book_j in CATALOGO_IDS[idx_i + 1:]:
                sim_val = self._cosine_similarity_vectors(
                    item_columns[book_i],
                    item_columns[book_j],
                    norms[book_i],
                    norms[book_j],
                )
                sim_matrix[book_i][book_j] = sim_val
                sim_matrix[book_j][book_i] = sim_val

        self.similarity_matrix = sim_matrix
        return self.similarity_matrix

    def fit(self, preferences: List[Dict[str, Any]]) -> "ItemBasedCFModel":
        """Ejecuta el pipeline de entrenamiento del Modelo 1 (Pasos 1 a 4)."""
        self.build_utility_matrix(preferences)
        self.compute_similarity_matrix()
        return self

    def has_user_history(self, user_id: int) -> bool:
        """Indica si el usuario posee compras registradas en la matriz de utilidad."""
        return bool(self.utility_matrix.get(int(user_id)))

    def score_and_recommend(
        self,
        user_id: int,
        books_catalog: Dict[int, Dict[str, Any]],
        k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Paso 5 (Scoring) y Paso 6 (Filtrado Post-Modelo):
        - Multiplica los ratings de los libros adquiridos por el usuario por los vectores
          de similitud correspondientes en la matriz 100x100.
        - Filtra del ranking final los libros ya comprados previamente por el usuario.
        - Retorna el Top-k ordenado descendentemente por puntaje predicho.
        """
        user_id = int(user_id)
        purchased_items = self.utility_matrix.get(user_id, {})
        if not purchased_items:
            return []

        candidates: List[Dict[str, Any]] = []
        for candidate_id in CATALOGO_IDS:
            # Paso 6: Filtrado Post-Modelo (excluir artículos ya comprados por el usuario)
            if candidate_id in purchased_items:
                continue
            if candidate_id not in books_catalog:
                continue

            # Paso 5: Generación de puntajes (Scoring)
            # score(u, j) = sum_{i in comprados(u)} rating(u, i) * sim(i, j)
            raw_score = 0.0
            sim_sum = 0.0
            contribuciones: List[Dict[str, Any]] = []

            for purchased_id, user_rating in purchased_items.items():
                sim_ij = self.similarity_matrix[purchased_id][candidate_id]
                if sim_ij > 0.0:
                    contribution = user_rating * sim_ij
                    raw_score += contribution
                    sim_sum += abs(sim_ij)
                    contribuciones.append({
                        "idLibroComprado": purchased_id,
                        "ratingAplicado": user_rating,
                        "similitudCoseno": round(sim_ij, 4),
                        "aportePuntaje": round(contribution, 4),
                    })

            # Ordenar contribuciones para explicabilidad del modelo
            contribuciones.sort(key=lambda c: c["aportePuntaje"], reverse=True)
            weighted_average = round(raw_score / sim_sum, 4) if sim_sum > 0.0 else 0.0

            book_info = dict(books_catalog[candidate_id])
            book_info["score_colaborativo"] = round(raw_score, 4)
            book_info["rating_estimado_ponderado"] = weighted_average
            book_info["libros_similares_influyentes"] = contribuciones[:3]
            candidates.append(book_info)

        # Ordenar descendentemente por el puntaje del producto punto (y desempate por idLibro ascendente)
        candidates.sort(
            key=lambda item: (item["score_colaborativo"], item.get("promedio_rating", 0.0), -item["id_libro"]),
            reverse=True,
        )
        return candidates[: max(1, int(k))]

    def get_similar_items(
        self,
        book_id: int,
        books_catalog: Dict[int, Dict[str, Any]],
        k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Devuelve los k libros más cercanos a book_id según la matriz de similitud 100x100."""
        book_id = int(book_id)
        if book_id not in self.similarity_matrix:
            raise ValueError(f"El idLibro {book_id} está fuera del rango del catálogo (1..100).")

        row_sims = self.similarity_matrix[book_id]
        similar_list: List[Dict[str, Any]] = []
        for other_id, sim_val in row_sims.items():
            if other_id == book_id or other_id not in books_catalog:
                continue
            item = dict(books_catalog[other_id])
            item["similitud_coseno"] = round(sim_val, 4)
            similar_list.append(item)

        similar_list.sort(
            key=lambda x: (x["similitud_coseno"], x.get("volumen_ventas", 0), -x["id_libro"]),
            reverse=True,
        )
        return similar_list[: max(1, int(k))]
