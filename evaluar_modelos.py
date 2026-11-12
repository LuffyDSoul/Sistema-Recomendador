"""
Fase 5: Evaluación Offline mediante Validación Cruzada (Leave-2-Out).
Compara el Sistema Recomendador (Modelo 1 y Modelo 2) contra el Carrusel Aleatorio actual.
"""

import random
import statistics
from typing import Any, Dict, List, Set, Tuple
import matplotlib.pyplot as plt

from src.infrastructure.config import AppConfig
from src.infrastructure.supabase.client import SupabaseClient
from src.models.item_based_cf import CATALOGO_IDS, ItemBasedCFModel
from src.models.cold_start import ColdStartModel

# Configuración del experimento
K_CARRUSEL = 5
CANTIDAD_OCULTA_TEST = 2
N_FOLDS = 5  # 5 repeticiones de validación cruzada con distintas particiones


def partir_train_test_por_usuario(
    preferencias: List[Dict[str, Any]],
    n_ocultos: int,
    seed: int,
) -> Tuple[List[Dict[str, Any]], Dict[int, Set[int]], Dict[int, Set[int]]]:
    """
    Para cada usuario con historial suficiente, oculta 'n_ocultos' libros (Test)
    y deja el resto para entrenar la matriz 100x100 (Train).
    """
    rng = random.Random(seed)
    prefs_por_usuario: Dict[int, List[Dict[str, Any]]] = {}
    for row in preferencias:
        uid = int(row["idUsuario"])
        prefs_por_usuario.setdefault(uid, []).append(row)

    train_rows: List[Dict[str, Any]] = []
    train_items_by_user: Dict[int, Set[int]] = {}
    test_items_by_user: Dict[int, Set[int]] = {}

    for uid, rows in prefs_por_usuario.items():
        # Si el usuario tiene menos de 4 compras, no le ocultamos compras
        if len(rows) <= n_ocultos + 1:
            train_rows.extend(rows)
            train_items_by_user[uid] = {int(r["idLibro"]) for r in rows}
            continue

        # Elegir preferentemente libros bien valorados (rating >= 3 o implícitos) para ocultar en Test
        filas_copia = list(rows)
        rng.shuffle(filas_copia)
        test_seleccion = filas_copia[:n_ocultos]
        train_seleccion = filas_copia[n_ocultos:]

        train_rows.extend(train_seleccion)
        train_items_by_user[uid] = {int(r["idLibro"]) for r in train_seleccion}
        test_items_by_user[uid] = {int(r["idLibro"]) for r in test_seleccion}

    return train_rows, train_items_by_user, test_items_by_user


def calcular_metricas_usuario(recommended_ids: List[int], test_ids: Set[int], k: int) -> Tuple[float, float, float]:
    """Calcula Precision@K, Recall@K y HitRate@K para un usuario."""
    top_k = recommended_ids[:k]
    aciertos = len(set(top_k).intersection(test_ids))
    precision = aciertos / float(k)
    recall = aciertos / float(len(test_ids)) if test_ids else 0.0
    hit_rate = 1.0 if aciertos > 0 else 0.0
    return precision, recall, hit_rate


def ejecutar_evaluacion() -> None:
    config = AppConfig.load()
    client = SupabaseClient(config.supabase_url, config.supabase_key)

    print("Extrayendo datos desde Supabase para la evaluación offline...")
    libros_rows = client.select("Libro", "select=*&order=idLibro.asc")
    generos_rows = client.select("Genero", "select=idGenero,nombre&order=idGenero.asc")
    genero_libro_rows = client.select("GeneroLibro", "select=idGenero,idLibro")
    usuario_genero_rows = client.select("UsuarioGenero", "select=idUsuario,idGenero")
    preferencias_rows = client.select("Preferencia", "select=idPreferencia,idUsuario,idLibro,rating")
    if not preferencias_rows:
        raise RuntimeError(
            "La tabla 'Preferencia' está vacía en Supabase. "
            "Ejecuta primero el script de carga con --reset-preferencias."
        )

    books_catalog = {
        int(l["idLibro"]): {"id_libro": int(l["idLibro"]), "titulo": l["titulo"]}
        for l in libros_rows
    }

    generos_por_usuario: Dict[int, List[int]] = {}
    for ug in usuario_genero_rows:
        generos_por_usuario.setdefault(int(ug["idUsuario"]), []).append(int(ug["idGenero"]))

    modelos_nombres = [
        "Modelo 1: Item-Based CF",
        "Modelo 2A: Cold Start (Géneros)",
        "Modelo 2B: Popularidad Global",
        "Carrusel Aleatorio (Actual)",
    ]

    historial_folds: Dict[str, Dict[str, List[float]]] = {
        m: {"precision": [], "recall": [], "hit_rate": []} for m in modelos_nombres
    }

    # Ejecutar Validación Cruzada en N_FOLDS particiones
    for fold in range(N_FOLDS):
        seed_fold = 100 + fold * 17
        rng_azar = random.Random(seed_fold)

        train_rows, train_by_user, test_by_user = partir_train_test_por_usuario(
            preferencias_rows, n_ocultos=CANTIDAD_OCULTA_TEST, seed=seed_fold
        )

        # Entrenar Modelo 1 y Modelo 2 solo con Train
        cf_model = ItemBasedCFModel(implicit_rating=3.0).fit(train_rows)
        cs_model = ColdStartModel(implicit_rating=3.0).fit(
            preferences=train_rows,
            genero_libro_rows=genero_libro_rows,
            generos_rows=generos_rows,
            all_book_ids=CATALOGO_IDS,
        )

        # Actualizar métricas en el catálogo temporal
        catalogo_fold = {}
        for bid, data in books_catalog.items():
            m = cs_model.book_metrics.get(bid, {})
            catalogo_fold[bid] = {
                **data,
                "promedio_rating": m.get("promedio_rating", 0.0),
                "volumen_ventas": m.get("volumen_ventas", 0),
            }

        metricas_usuarios = {m: {"p": [], "r": [], "hr": []} for m in modelos_nombres}

        for uid, test_set in test_by_user.items():
            comprados_train = train_by_user.get(uid, set())
            candidatos_disponibles = [bid for bid in CATALOGO_IDS if bid not in comprados_train]

            # 1. Modelo 1: Item-Based CF
            recs_cf = cf_model.score_and_recommend(user_id=uid, books_catalog=catalogo_fold, k=K_CARRUSEL)
            ids_cf = [r["id_libro"] for r in recs_cf]

            # 2. Modelo 2A: Cold Start con Géneros (filtrando los ya comprados en train para comparar justo)
            user_genres = generos_por_usuario.get(uid, [])[:3]
            _, recs_cs_a, _ = cs_model.recommend(books_catalog=catalogo_fold, genre_ids=user_genres, k=100)
            ids_cs_a = [r["id_libro"] for r in recs_cs_a if r["id_libro"] not in comprados_train][:K_CARRUSEL]

            # 3. Modelo 2B: Popularidad Global (sin géneros)
            _, recs_cs_b, _ = cs_model.recommend(books_catalog=catalogo_fold, genre_ids=None, k=100)
            ids_cs_b = [r["id_libro"] for r in recs_cs_b if r["id_libro"] not in comprados_train][:K_CARRUSEL]

            # 4. Línea Base Aleatoria (Carrusel actual del comitente)
            ids_azar = rng_azar.sample(candidatos_disponibles, min(K_CARRUSEL, len(candidatos_disponibles)))

            for nombre_m, lista_ids in [
                ("Modelo 1: Item-Based CF", ids_cf),
                ("Modelo 2A: Cold Start (Géneros)", ids_cs_a),
                ("Modelo 2B: Popularidad Global", ids_cs_b),
                ("Carrusel Aleatorio (Actual)", ids_azar),
            ]:
                p, r, hr = calcular_metricas_usuario(lista_ids, test_set, k=K_CARRUSEL)
                metricas_usuarios[nombre_m]["p"].append(p)
                metricas_usuarios[nombre_m]["r"].append(r)
                metricas_usuarios[nombre_m]["hr"].append(hr)

        for nombre_m in modelos_nombres:
            historial_folds[nombre_m]["precision"].append(statistics.mean(metricas_usuarios[nombre_m]["p"]))
            historial_folds[nombre_m]["recall"].append(statistics.mean(metricas_usuarios[nombre_m]["r"]))
            historial_folds[nombre_m]["hit_rate"].append(statistics.mean(metricas_usuarios[nombre_m]["hr"]))

    # Imprimir Tabla de Validación Cruzada
    print("\n=== Resultados de Validación Cruzada Offline (Top-5, 5 Folds) ===")
    print(f"{'Modelo':<34} | {'Precision@5 Mean':<16} | {'Precision@5 Std':<15} | {'Recall@5 Mean':<14} | {'HitRate@5 Mean':<14}")
    print("-" * 105)

    resumen: Dict[str, Dict[str, float]] = {}
    for nombre_m in modelos_nombres:
        p_mean = statistics.mean(historial_folds[nombre_m]["precision"])
        p_std = statistics.stdev(historial_folds[nombre_m]["precision"])
        r_mean = statistics.mean(historial_folds[nombre_m]["recall"])
        r_std = statistics.stdev(historial_folds[nombre_m]["recall"])
        hr_mean = statistics.mean(historial_folds[nombre_m]["hit_rate"])
        hr_std = statistics.stdev(historial_folds[nombre_m]["hit_rate"])
        resumen[nombre_m] = {
            "p_mean": p_mean, "p_std": p_std,
            "r_mean": r_mean, "r_std": r_std,
            "hr_mean": hr_mean, "hr_std": hr_std,
        }
        print(f"{nombre_m:<34} | {p_mean:<16.3f} | {p_std:<15.3f} | {r_mean:<14.3f} | {hr_mean:<14.3f}")

    # Generar Gráficos estilo TP1
    colores = ["#4169E1", "#63B8FF", "#82E0AA", "#E74C3C"]
    etiquetas_cortas = ["Item-Based CF", "Cold Start (Géneros)", "Popularidad Global", "Aleatorio (Actual)"]

    # Gráfico 1: Recall@5
    plt.figure(figsize=(8, 5))
    r_means = [resumen[m]["r_mean"] for m in modelos_nombres]
    r_stds = [resumen[m]["r_std"] for m in modelos_nombres]
    bars = plt.bar(etiquetas_cortas, r_means, yerr=r_stds, capsize=6, color=colores, edgecolor="black", alpha=0.9)
    for bar, val in zip(bars, r_means):
        plt.text(bar.get_x() + bar.get_width() / 2, val + 0.015, f"{val:.3f}", ha="center", fontweight="bold")
    plt.title(f"Validación Cruzada - Recall@{K_CARRUSEL} (Recuperación de Compras Ocultas)", fontweight="bold")
    plt.ylabel(f"Recall@{K_CARRUSEL}")
    plt.xticks(rotation=15)
    plt.ylim(0, max(r_means) + 0.15)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("validacion_cruzada_recall.png", dpi=150)
    plt.show()

    # Gráfico 2: Hit Rate@5 (Tasa de Acierto en el Carrusel)
    plt.figure(figsize=(8, 5))
    hr_means = [resumen[m]["hr_mean"] for m in modelos_nombres]
    hr_stds = [resumen[m]["hr_std"] for m in modelos_nombres]
    bars2 = plt.bar(etiquetas_cortas, hr_means, yerr=hr_stds, capsize=6, color=colores, edgecolor="black", alpha=0.9)
    for bar, val in zip(bars2, hr_means):
        plt.text(bar.get_x() + bar.get_width() / 2, val + 0.02, f"{val:.3f}", ha="center", fontweight="bold")
    plt.title(f"Validación Cruzada - Hit Rate@{K_CARRUSEL} (Tasa de Acierto por Usuario)", fontweight="bold")
    plt.ylabel(f"Hit Rate@{K_CARRUSEL}")
    plt.xticks(rotation=15)
    plt.ylim(0, min(1.05, max(hr_means) + 0.20))
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("validacion_cruzada_hitrate.png", dpi=150)
    plt.show()


if __name__ == "__main__":
    ejecutar_evaluacion()