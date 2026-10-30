"""Ingesta reproducible del Código del Trabajo (semana 3).

    py scripts/ingest.py

Pasos (clase del 27/10, «Tres pasos para que su sistema encuentre»):
  1. Leer el PDF de data/raw/ (si falta, se descarga de la URL oficial).
  2. Cortar por artículo y etiquetar (app/services/normativa.py).
  3. Ponerle dirección a cada fragmento con el modelo de embeddings y guardarlo en ChromaDB.

Se corre una vez, y otra vez si cambia el documento o el modelo de embeddings
(en ese caso se reconstruye la colección completa).
"""
import sys
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from app.services import retriever  # noqa: E402

retriever.cargar_entorno()  # respeta EMBEDDING_MODEL y CHROMA_PATH del .env
from app.services.normativa import cortar  # noqa: E402

PDF = RAIZ / "data/raw/CODIGO_DEL_TRABAJO.pdf"
URL = "https://www.trabajo.gob.ec/wp-content/uploads/downloads/2024/01/CODIGO_DEL_TRABAJO.pdf"
VERSION = "Codificación 2005-017, última reforma RO 309-S 2023-05-12"


def leer_pdf(ruta: Path) -> str:
    import pymupdf  # se importa aquí para que las pruebas no lo necesiten

    with pymupdf.open(ruta) as doc:
        return "\n".join(pagina.get_text() for pagina in doc)


def main() -> None:
    if not PDF.exists():
        # El PDF no se sube al repositorio (restricción de redistribución, ver data/raw/README.md).
        print(f"No está {PDF.name}: se descarga de la fuente oficial…")
        PDF.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(URL, PDF)

    fragmentos = cortar(leer_pdf(PDF), fuente=URL, version=VERSION)
    vigentes = sum(f.metadatos["vigente"] for f in fragmentos)
    print(f"1) Corte: {len(fragmentos)} artículos detectados ({vigentes} vigentes, "
          f"{len(fragmentos) - vigentes} derogados)")
    if not fragmentos:
        sys.exit("No se detectó ningún artículo: revise el patrón de corte antes de seguir.")

    print(f"2) Embeddings con {retriever.modelo_embeddings()} (la primera vez se descarga el modelo)…")
    total = retriever.reconstruir(fragmentos)
    print(f"3) Guardado en {retriever.ruta_indice()}: colección «{retriever.COLECCION}» con {total} fragmentos")

    print("\nPrueba rápida · «Me botaron sin aviso»:")
    for i, r in enumerate(retriever.buscar("Me botaron sin aviso"), 1):
        print(f"   {i}. Art. {r['articulo']:<22} distancia {r['distancia']:.3f}  [{r['tema']}]")


if __name__ == "__main__":
    main()
