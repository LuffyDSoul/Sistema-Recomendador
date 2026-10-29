"""
Modelo 2: Filtrado Basado en Contenido y Popularidad (Cold Start).

Implementa los pasos definidos en la Fase 4 (Modelado):
1. Verificación de estado: Se activa cuando el idUsuario no posee registros en Preferencia.
2. Extracción de perfiles (Onboarding): El endpoint de la API REST recibe dinámicamente un arreglo
   con hasta 3 IDs de géneros de interés seleccionados por el cliente (multiplicidad 0..3),
   eliminando la necesidad de realizar una consulta adicional a la base de datos.
3. Generación del ranking (Caso A - Con géneros): Filtra los libros asociados a esos géneros
   (GeneroLibro) y los ordena descendentemente por su promedio de calificaciones globales y
   volumen de ventas.
4. Generación del ranking (Caso B - Sin géneros): Si el usuario omitió la selección, genera un
   ranking global ordenando el catálogo completo por los libros más vendidos y mejor valorados
   de toda la plataforma.
"""

from typing import Any, Dict, List, Optional, Set, Tuple

IMPLICIT_RATING_IMPUTATION: float = 3.0
MAX_ONBOARDING_GENRES: int = 3


class ColdStartModel:
    """Modelo de contingencia basado en contenido (géneros de onboarding) y popularidad global."""

    def __init__(self, implicit_rating: float = IMPLICIT_RATING_IMPUTATION) -> None:
        self.implicit_rating = float(implicit_rating)
        # Métricas globales por libro: {id_libro: {"volumen_ventas": int, "promedio_rating": float, ...}}
        self.book_metrics: Dict[int, Dict[str, Any]] = {}
        # Relación género -> conjunto de idLibro
        self.genre_to_books: Dict[int, Set[int]] = {}
        # Mapa de idGenero -> nombre y orden posicional (1..12) -> idGenero real en DB
        self.genres_by_id: Dict[int, str] = {}
        self.positional_genre_map: Dict[int, int] = {}

    def fit(
        self,
        preferences: List[Dict[str, Any]],
        genero_libro_rows: List[Dict[str, Any]],
        generos_rows: List[Dict[str, Any]],
        all_book_ids: List[int],
    ) -> "ColdStartModel":
        """Calcula las métricas globales de ventas y calificaciones e indexa GeneroLibro."""
        # 1. Indexar catálogo de géneros (y mapa posicional 1..N por si en DB los IDs arrancan en otro número)
        sorted_genres = sorted(generos_rows, key=lambda g: int(g["idGenero"]))
        self.genres_by_id = {int(g["idGenero"]): str(g["nombre"]) for g in sorted_genres}
        self.positional_genre_map = {
            idx: int(g["idGenero"]) for idx, g in enumerate(sorted_genres, start=1)
        }

        # 2. Indexar relación N:M GeneroLibro
        self.genre_to_books = {gid: set() for gid in self.genres_by_id}
        for rel in genero_libro_rows:
            gid = int(rel["idGenero"])
            bid = int(rel["idLibro"])
            self.genre_to_books.setdefault(gid, set()).add(bid)

        # 3. Calcular volumen de ventas y promedio de calificaciones globales por libro
        sales_count: Dict[int, int] = {bid: 0 for bid in all_book_ids}
        rating_sum_imputed: Dict[int, float] = {bid: 0.0 for bid in all_book_ids}
        explicit_ratings: Dict[int, List[int]] = {bid: [] for bid in all_book_ids}

        for pref in preferences:
            bid = int(pref["idLibro"])
            if bid not in sales_count:
                continue
            raw_r = pref.get("rating")
            imputed_r = float(raw_r) if raw_r is not None else self.implicit_rating
            sales_count[bid] += 1
            rating_sum_imputed[bid] += imputed_r
            if raw_r is not None:
                explicit_ratings[bid].append(int(raw_r))

        self.book_metrics = {}
        for bid in all_book_ids:
            vol = sales_count[bid]
            avg_global = round(rating_sum_imputed[bid] / vol, 4) if vol > 0 else 0.0
            exp_list = explicit_ratings[bid]
            avg_explicit = round(sum(exp_list) / len(exp_list), 4) if exp_list else 0.0
            self.book_metrics[bid] = {
                "volumen_ventas": vol,
                "promedio_rating": avg_global,
                "promedio_rating_explicito": avg_explicit,
                "cantidad_ratings_explicitos": len(exp_list),
            }

        return self

    def resolve_genre_ids(self, raw_genre_ids: Optional[List[int]]) -> List[int]:
        """
        Valida y normaliza el arreglo de hasta 3 IDs de géneros enviados por HTTP.
        Soporta tanto el idGenero exacto de Supabase como el índice 1..12 del listado de géneros.
        """
        if not raw_genre_ids:
            return []

        if len(raw_genre_ids) > MAX_ONBOARDING_GENRES:
            raise ValueError(
                f"Regla de Negocio: Solo se permiten hasta {MAX_ONBOARDING_GENRES} géneros de interés (multiplicidad 0..3)."
            )

        resolved: List[int] = []
        for gid in raw_genre_ids:
            gid_int = int(gid)
            if gid_int in self.genres_by_id:
                actual_id = gid_int
            elif gid_int in self.positional_genre_map:
                actual_id = self.positional_genre_map[gid_int]
            else:
                valid_ids = list(self.genres_by_id.keys())
                raise ValueError(
                    f"El idGenero '{gid}' no existe. IDs válidos en BD: {valid_ids} (o posiciones 1..{len(valid_ids)})."
                )
            if actual_id not in resolved:
                resolved.append(actual_id)

        return resolved

    def recommend(
        self,
        books_catalog: Dict[int, Dict[str, Any]],
        genre_ids: Optional[List[int]] = None,
        k: int = 5,
    ) -> Tuple[str, List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Genera el ranking Top-k para usuarios en estado Cold Start:
        - Caso A (Con géneros): Filtra por GeneroLibro y ordena descendentemente por
          promedio de calificaciones globales y volumen de ventas.
        - Caso B (Sin géneros): Ordena el catálogo completo por los libros más vendidos
          y mejor valorados de toda la plataforma.
        """
        resolved_genres = self.resolve_genre_ids(genre_ids)
        selected_genres_meta = [
            {"idGenero": gid, "nombre": self.genres_by_id.get(gid, "")}
            for gid in resolved_genres
        ]

        if resolved_genres:
            # Caso A - Con géneros de onboarding (1..3 géneros recibidos en la llamada HTTP)
            sub_case = "Caso A - Con géneros (Filtrado por Contenido + Calificación Global y Ventas)"
            matching_book_ids: Set[int] = set()
            book_genre_matches: Dict[int, int] = {}
            for gid in resolved_genres:
                for bid in self.genre_to_books.get(gid, set()):
                    matching_book_ids.add(bid)
                    book_genre_matches[bid] = book_genre_matches.get(bid, 0) + 1

            candidates: List[Dict[str, Any]] = []
            for bid in matching_book_ids:
                if bid not in books_catalog:
                    continue
                metrics = self.book_metrics.get(bid, {})
                item = dict(books_catalog[bid])
                item["promedio_rating"] = metrics.get("promedio_rating", 0.0)
                item["volumen_ventas"] = metrics.get("volumen_ventas", 0)
                item["coincidencias_genero"] = book_genre_matches.get(bid, 1)
                candidates.append(item)

            # Ordenar descendentemente por promedio de calificaciones globales y volumen de ventas
            candidates.sort(
                key=lambda x: (
                    x["promedio_rating"],
                    x["volumen_ventas"],
                    x["coincidencias_genero"],
                    -x["id_libro"],
                ),
                reverse=True,
            )
        else:
            # Caso B - Sin géneros (Popularidad global: más vendidos y mejor valorados del catálogo)
            sub_case = "Caso B - Sin géneros (Popularidad Global: Más Vendidos y Mejor Valorados)"
            candidates = []
            for bid, book_data in books_catalog.items():
                metrics = self.book_metrics.get(bid, {})
                item = dict(book_data)
                item["volumen_ventas"] = metrics.get("volumen_ventas", 0)
                item["promedio_rating"] = metrics.get("promedio_rating", 0.0)
                candidates.append(item)

            # Ordenar descendentemente por volumen de ventas y promedio de calificaciones globales
            candidates.sort(
                key=lambda x: (
                    x["volumen_ventas"],
                    x["promedio_rating"],
                    -x["id_libro"],
                ),
                reverse=True,
            )

        return sub_case, candidates[: max(1, int(k))], selected_genres_meta
