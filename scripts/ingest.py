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
import json
import hashlib
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from app.services import retriever  # noqa: E402

retriever.cargar_entorno()  # respeta EMBEDDING_MODEL y CHROMA_PATH del .env
from app.services.normativa import cortar  # noqa: E402

CORPUS = json.loads((RAIZ / "config/corpus.json").read_text(encoding="utf-8"))
PDF = RAIZ / CORPUS["archivo"]
URL = CORPUS["url"]
VERSION = CORPUS["version"]


def leer_pdf(ruta: Path) -> str:
    import pymupdf  # se importa aquí para que las pruebas no lo necesiten

    with pymupdf.open(ruta) as doc:
        return "\n".join(pagina.get_text() for pagina in doc)


def main() -> None:
    # Comprobar todos los destinos antes de descargar, leer o reconstruir.
    retriever.ruta_indice()
    pdf = retriever.validar_ruta_copia(PDF)
    if not pdf.exists():
        # El PDF no se sube al repositorio (restricción de redistribución, ver data/raw/README.md).
        print(f"No está {pdf.name}: se descarga de la fuente oficial…")
        pdf.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(URL, pdf)

    if hashlib.sha256(pdf.read_bytes()).hexdigest() != CORPUS["sha256"]:
        sys.exit("El PDF no coincide con la edición registrada: revisar origen y actualizar el manifiesto antes de indexar.")
    fragmentos = cortar(leer_pdf(pdf), fuente=URL, version=VERSION)
    for f in fragmentos:
        f.metadatos.update({k: CORPUS[k] for k in ("fecha_publicacion", "fecha_corte_normativa", "fecha_consulta", "alcance_vigencia")})
        f.metadatos["estado_vigencia_fuente"] = "vigente según edición" if f.metadatos["vigente"] else "derogado según edición"
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
