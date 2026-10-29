"""
Servidor de API REST para el Sistema Recomendador Híbrido de Libros (Fase 4: Modelado).

Implementado sobre http.server (librería estándar de Python) para garantizar ejecución
inmediata sin dependencias externas adicionales, exponiendo endpoints JSON con soporte CORS.
"""

import json
import logging
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

from src.infrastructure.config import AppConfig
from src.infrastructure.supabase.client import SupabaseClient
from src.models.hybrid_pipeline import HybridRecommenderPipeline

logger = logging.getLogger(__name__)


def _parse_genre_list(raw_value: Any) -> List[int]:
    """Convierte un parámetro de géneros (lista JSON o string separado por comas) en List[int]."""
    if raw_value is None or raw_value == "" or raw_value == []:
        return []
    if isinstance(raw_value, list):
        result: List[int] = []
        for item in raw_value:
            if isinstance(item, str) and "," in item:
                result.extend(int(x.strip()) for x in item.split(",") if x.strip())
            elif str(item).strip():
                result.append(int(str(item).strip()))
        return result
    if isinstance(raw_value, (int, float)):
        return [int(raw_value)]
    if isinstance(raw_value, str):
        cleaned = raw_value.strip().strip("[]")
        if not cleaned:
            return []
        return [int(x.strip()) for x in cleaned.split(",") if x.strip()]
    raise ValueError("Formato inválido para 'generos'. Use un arreglo de enteros como [1, 2] o '1,2'.")


class RecommenderRequestHandler(BaseHTTPRequestHandler):
    """Controlador HTTP REST que atiende las peticiones hacia el pipeline híbrido."""

    pipeline: HybridRecommenderPipeline

    def _send_json(self, status_code: int, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> Dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", "0") or "0")
        if content_length <= 0:
            return {}
        raw_body = self.rfile.read(content_length).decode("utf-8")
        if not raw_body.strip():
            return {}
        try:
            data = json.loads(raw_body)
            if not isinstance(data, dict):
                raise ValueError("El cuerpo JSON debe ser un objeto clave-valor.")
            return data
        except json.JSONDecodeError as exc:
            raise ValueError(f"JSON malformado en el cuerpo de la petición: {exc}") from exc

    @staticmethod
    def _extract_common_params(
        query_params: Dict[str, List[str]],
        body_params: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Optional[int], Optional[str], List[int], int]:
        """Extrae (user_id, email, genre_ids, k) tanto de query params como de body JSON."""
        body = body_params or {}

        raw_uid = (
            body.get("idUsuario")
            if "idUsuario" in body
            else body.get("id_usuario")
            if "id_usuario" in body
            else (query_params.get("id_usuario") or query_params.get("idUsuario") or [None])[0]
        )
        user_id = int(raw_uid) if raw_uid is not None and str(raw_uid).strip() != "" else None

        raw_email = (
            body.get("email")
            if "email" in body
            else (query_params.get("email") or [None])[0]
        )
        email = str(raw_email).strip() if raw_email else None

        if "generos" in body:
            genre_ids = _parse_genre_list(body.get("generos"))
        elif "generos_ids" in body:
            genre_ids = _parse_genre_list(body.get("generos_ids"))
        elif "generos" in query_params:
            genre_ids = _parse_genre_list(query_params.get("generos"))
        elif "generos_ids" in query_params:
            genre_ids = _parse_genre_list(query_params.get("generos_ids"))
        else:
            genre_ids = []

        raw_k = (
            body.get("k")
            if "k" in body
            else body.get("limit")
            if "limit" in body
            else (query_params.get("k") or query_params.get("limit") or ["5"])[0]
        )
        k = int(raw_k) if raw_k is not None else 5
        if k < 1 or k > 100:
            raise ValueError("El parámetro 'k' debe ser un entero entre 1 y 100.")

        return user_id, email, genre_ids, k

    def do_OPTIONS(self) -> None:
        self._send_json(200, {"ok": True})

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query_params = parse_qs(parsed.query)

        try:
            if path in ("/", "/api", "/api/health", "/health"):
                self.pipeline._ensure_trained()
                self._send_json(200, {
                    "ok": True,
                    "servicio": "API REST - Sistema Recomendador Híbrido de Libros (Fase 4)",
                    "estado_modelo": {
                        "entrenado": self.pipeline.is_trained,
                        "libros_en_catalogo": len(self.pipeline.books_catalog),
                        "usuarios_registrados": len(self.pipeline.users_by_id),
                        "preferencias_procesadas": self.pipeline.total_preferences_loaded,
                        "dimension_matriz_similitud": "100x100",
                        "imputacion_rating_implicito": self.pipeline.implicit_rating,
                    },
                    "endpoints_disponibles": [
                        "GET  /api/health",
                        "GET  /api/recomendaciones?id_usuario=<id>&k=5&generos=1,2",
                        "POST /api/recomendaciones",
                        "GET  /api/modelo/colaborativo?id_usuario=<id>&k=5",
                        "POST /api/modelo/colaborativo",
                        "GET  /api/modelo/cold-start?generos=1,2&k=5",
                        "POST /api/modelo/cold-start",
                        "GET  /api/modelo/matriz-similitud?id_libro=1&k=5",
                        "POST /api/preferencias",
                        "POST /api/modelo/reentrenar",
                        "GET  /api/usuarios",
                        "GET  /api/generos",
                        "GET  /api/libros",
                    ],
                })
                return

            if path in ("/api/recomendaciones", "/recomendaciones"):
                user_id, email, genre_ids, k = self._extract_common_params(query_params)
                result = self.pipeline.recommend(
                    user_id=user_id,
                    email=email,
                    genre_ids=genre_ids,
                    k=k,
                )
                self._send_json(200, {"ok": True, **result})
                return

            if path in ("/api/modelo/colaborativo", "/modelo/colaborativo"):
                user_id, email, _, k = self._extract_common_params(query_params)
                result = self.pipeline.recommend_collaborative_only(
                    user_id=user_id,
                    email=email,
                    k=k,
                )
                self._send_json(200, {"ok": True, **result})
                return

            if path in ("/api/modelo/cold-start", "/modelo/cold-start"):
                user_id, email, genre_ids, k = self._extract_common_params(query_params)
                result = self.pipeline.recommend_cold_start_only(
                    genre_ids=genre_ids,
                    k=k,
                    user_id=user_id,
                    email=email,
                )
                self._send_json(200, {"ok": True, **result})
                return

            if path in ("/api/modelo/matriz-similitud", "/modelo/matriz-similitud"):
                raw_book = (query_params.get("id_libro") or query_params.get("idLibro") or [None])[0]
                raw_k = (query_params.get("k") or ["5"])[0]
                book_id = int(raw_book) if raw_book is not None else None
                k = int(raw_k) if raw_k is not None else 5
                result = self.pipeline.get_similarity_info(book_id=book_id, k=k)
                self._send_json(200, {"ok": True, **result})
                return

            if path in ("/api/usuarios", "/usuarios"):
                self.pipeline._ensure_trained()
                usuarios = list(self.pipeline.users_by_id.values())
                self._send_json(200, {
                    "ok": True,
                    "total_usuarios": len(usuarios),
                    "usuarios_con_compras_colaborativo": [u for u in usuarios if not u["es_cold_start"]],
                    "usuarios_sin_compras_cold_start": [u for u in usuarios if u["es_cold_start"]],
                    "usuarios": usuarios,
                })
                return

            if path in ("/api/generos", "/generos"):
                self.pipeline._ensure_trained()
                self._send_json(200, {
                    "ok": True,
                    "total_generos": len(self.pipeline.genres_list),
                    "nota": "En los endpoints puede enviar tanto 'idGenero' real como 'posicion' (1..12).",
                    "generos": self.pipeline.genres_list,
                })
                return

            if path in ("/api/libros", "/libros"):
                self.pipeline._ensure_trained()
                libros = list(self.pipeline.books_catalog.values())
                self._send_json(200, {
                    "ok": True,
                    "total_libros": len(libros),
                    "libros": libros,
                })
                return

            self._send_json(404, {
                "ok": False,
                "error": f"Ruta '{path}' no encontrada. Consulte GET /api/health para ver los endpoints disponibles.",
            })
        except ValueError as exc:
            self._send_json(400, {"ok": False, "error": str(exc)})
        except Exception as exc:
            logger.exception("Error inesperado en GET %s", path)
            self._send_json(500, {"ok": False, "error": f"Error interno del servidor: {exc}"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query_params = parse_qs(parsed.query)

        try:
            body_params = self._read_json_body()

            if path in ("/api/recomendaciones", "/recomendaciones"):
                user_id, email, genre_ids, k = self._extract_common_params(query_params, body_params)
                result = self.pipeline.recommend(
                    user_id=user_id,
                    email=email,
                    genre_ids=genre_ids,
                    k=k,
                )
                self._send_json(200, {"ok": True, **result})
                return

            if path in ("/api/modelo/colaborativo", "/modelo/colaborativo"):
                user_id, email, _, k = self._extract_common_params(query_params, body_params)
                result = self.pipeline.recommend_collaborative_only(
                    user_id=user_id,
                    email=email,
                    k=k,
                )
                self._send_json(200, {"ok": True, **result})
                return

            if path in ("/api/modelo/cold-start", "/modelo/cold-start"):
                user_id, email, genre_ids, k = self._extract_common_params(query_params, body_params)
                result = self.pipeline.recommend_cold_start_only(
                    genre_ids=genre_ids,
                    k=k,
                    user_id=user_id,
                    email=email,
                )
                self._send_json(200, {"ok": True, **result})
                return

            if path in ("/api/preferencias", "/preferencias"):
                user_id, email, _, _ = self._extract_common_params(query_params, body_params)
                user = self.pipeline.resolve_user(user_id=user_id, email=email)
                raw_book = body_params.get("idLibro", body_params.get("id_libro"))
                if raw_book is None:
                    raise ValueError("El campo 'idLibro' (1..100) es obligatorio.")
                book_id = int(raw_book)
                if book_id not in self.pipeline.books_catalog:
                    raise ValueError(f"El libro con idLibro={book_id} no existe en el catálogo (1..100).")

                raw_rating = body_params.get("rating")
                if raw_rating is not None:
                    rating_val = int(raw_rating)
                    if not (1 <= rating_val <= 5):
                        raise ValueError("El campo 'rating' debe ser un entero entre 1 y 5, o null.")
                else:
                    rating_val = None

                inserted = self.pipeline.client.insert("Preferencia", [{
                    "idUsuario": user["idUsuario"],
                    "idLibro": book_id,
                    "rating": rating_val,
                    "fecha": str(date.today()),
                }])
                # Reentrenar el pipeline en memoria para reflejar la nueva compra
                self.pipeline.fit()
                self._send_json(201, {
                    "ok": True,
                    "mensaje": "Preferencia registrada y matriz 100x100 actualizada.",
                    "preferencia_insertada": inserted[0] if inserted else {
                        "idUsuario": user["idUsuario"],
                        "idLibro": book_id,
                        "rating": rating_val,
                    },
                    "rating_aplicado_en_modelo": rating_val if rating_val is not None else self.pipeline.implicit_rating,
                })
                return

            if path in ("/api/modelo/reentrenar", "/modelo/reentrenar"):
                self.pipeline.fit()
                self._send_json(200, {
                    "ok": True,
                    "mensaje": "Pipeline reentrenado exitosamente desde Supabase.",
                    "libros_en_catalogo": len(self.pipeline.books_catalog),
                    "usuarios_registrados": len(self.pipeline.users_by_id),
                    "preferencias_procesadas": self.pipeline.total_preferences_loaded,
                    "dimension_matriz_similitud": "100x100",
                })
                return

            self._send_json(404, {
                "ok": False,
                "error": f"Ruta POST '{path}' no encontrada. Consulte GET /api/health.",
            })
        except ValueError as exc:
            self._send_json(400, {"ok": False, "error": str(exc)})
        except Exception as exc:
            logger.exception("Error inesperado en POST %s", path)
            self._send_json(500, {"ok": False, "error": f"Error interno del servidor: {exc}"})

    def log_message(self, format: str, *args: Any) -> None:
        logger.info("%s - %s", self.address_string(), format % args)


def create_server(host: str = "127.0.0.1", port: int = 8000) -> ThreadingHTTPServer:
    """Inicializa el pipeline híbrido con Supabase y crea el servidor HTTP REST."""
    config = AppConfig.load()
    client = SupabaseClient(config.supabase_url, config.supabase_key)
    pipeline = HybridRecommenderPipeline(client=client).fit()
    RecommenderRequestHandler.pipeline = pipeline
    return ThreadingHTTPServer((host, port), RecommenderRequestHandler)


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Inicia y mantiene en ejecución el servidor de la API REST."""
    server = create_server(host=host, port=port)
    logger.info("================================================================")
    logger.info("  SERVIDOR API REST INICIADO EN http://%s:%s", host, port)
    logger.info("  Health Check: http://%s:%s/api/health", host, port)
    logger.info("================================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Deteniendo servidor API REST...")
    finally:
        server.server_close()
