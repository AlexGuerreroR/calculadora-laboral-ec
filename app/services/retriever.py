"""Consulta a la base vectorial (ChromaDB) con el Código del Trabajo.

Reglas de la clase del 27/10 (bases vectoriales):
- Un modelo de embeddings que entienda español, elegido por su nombre
  (nunca el que trae ChromaDB por defecto, que está entrenado en inglés).
- El mismo modelo para guardar y para buscar; si se cambia, se reconstruye el índice.
- Distancia coseno; prefijo «passage: » al guardar y «query: » al buscar (modelos E5).
- El filtro por etiquetas (vigente, tema) se aplica antes del top-k.
- Búsqueda híbrida: si la pregunta nombra un artículo («Art. 188»), ese artículo se
  trae por coincidencia exacta, porque el significado no distingue números.

chromadb y sentence-transformers se importan dentro de las funciones: así las pruebas
del resto de la aplicación no los necesitan.
"""
from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path

COLECCION = "normativa"
MODELO_POR_DEFECTO = "intfloat/multilingual-e5-small"
_RAIZ = Path(__file__).resolve().parents[2]
_CITA = re.compile(r"\b(?:art(?:[íi]culo)?\.?)\s*(\d+(?:\.\d+)?)", re.IGNORECASE)


def cargar_entorno(ruta: Path | None = None) -> None:
    """Lee el .env de la raíz del proyecto. La usan los scripts (ingest.py, run_eval.py), que no
    pasan por app/config.py: sin esto, ignorarían EMBEDDING_MODEL y CHROMA_PATH del .env y
    usarían los valores por defecto. Una variable ya definida en la terminal tiene prioridad."""
    from dotenv import load_dotenv

    load_dotenv(ruta or _RAIZ / ".env", override=False)


def modelo_embeddings() -> str:
    return os.getenv("EMBEDDING_MODEL", "").strip() or MODELO_POR_DEFECTO


def ruta_indice() -> Path:
    ruta = Path(os.getenv("CHROMA_PATH", "").strip() or "./data/chroma")
    return ruta if ruta.is_absolute() else _RAIZ / ruta


def articulos_citados(pregunta: str) -> list[str]:
    """Números de artículo escritos en la pregunta: «art. 188», «artículo 69»."""
    return list(dict.fromkeys(_CITA.findall(pregunta)))


@lru_cache(maxsize=1)
def _modelo():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(modelo_embeddings())


def _cliente():
    import chromadb

    return chromadb.PersistentClient(path=str(ruta_indice()))


def _vectores(textos: list[str], prefijo: str) -> list[list[float]]:
    return _modelo().encode([prefijo + t for t in textos], normalize_embeddings=True).tolist()


def reconstruir(fragmentos) -> int:
    """Borra la colección y la vuelve a crear con todos los fragmentos."""
    cliente = _cliente()
    if COLECCION in [c.name if hasattr(c, "name") else c for c in cliente.list_collections()]:
        cliente.delete_collection(COLECCION)
    col = cliente.create_collection(
        COLECCION,
        configuration={"hnsw": {"space": "cosine"}},
        metadata={"modelo_embeddings": modelo_embeddings()},
    )
    for i in range(0, len(fragmentos), 64):  # por lotes, para no saturar la memoria
        lote = fragmentos[i:i + 64]
        col.add(ids=[f.id for f in lote], documents=[f.texto for f in lote],
                metadatas=[f.metadatos for f in lote],
                embeddings=_vectores([f.texto for f in lote], "passage: "))
    return col.count()


@lru_cache(maxsize=1)
def _coleccion():
    col = _cliente().get_collection(COLECCION)
    guardado = (col.metadata or {}).get("modelo_embeddings")
    if guardado and guardado != modelo_embeddings():
        raise RuntimeError(
            f"El índice se construyó con {guardado} y ahora se busca con {modelo_embeddings()}. "
            "Vuelva a correr scripts/ingest.py.")
    return col


def _filtro(tema: str | None, solo_vigentes: bool) -> dict | None:
    condiciones = ([{"vigente": True}] if solo_vigentes else []) + ([{"tema": tema}] if tema else [])
    if not condiciones:
        return None
    return condiciones[0] if len(condiciones) == 1 else {"$and": condiciones}


def buscar(pregunta: str, k: int = 5, tema: str | None = None, solo_vigentes: bool = True) -> list[dict]:
    """Devuelve los k fragmentos más cercanos: artículo, distancia, texto y etiquetas."""
    col = _coleccion()
    filtro = _filtro(tema, solo_vigentes)
    r = col.query(query_embeddings=_vectores([pregunta], "query: "), n_results=k, where=filtro)
    hallados = [
        {"articulo": m["articulo"], "distancia": d, "texto": t, "tema": m["tema"],
         "capitulo": m.get("capitulo", ""), "origen": "significado"}
        for t, m, d in zip(r["documents"][0], r["metadatas"][0], r["distances"][0])
    ]
    # Búsqueda híbrida: el artículo nombrado en la pregunta va primero.
    exactos = []
    for numero in articulos_citados(pregunta):
        cond = {"articulo": numero}
        g = col.get(where={"$and": [cond, filtro]} if filtro else cond)
        exactos += [{"articulo": m["articulo"], "distancia": 0.0, "texto": t, "tema": m["tema"],
                     "capitulo": m.get("capitulo", ""), "origen": "exacta"}
                    for t, m in zip(g["documents"], g["metadatas"])]
    vistos = {e["articulo"] for e in exactos}
    return (exactos + [h for h in hallados if h["articulo"] not in vistos])[:k]
