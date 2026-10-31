"""Evaluación del RAG con el conjunto de referencia (eval/preguntas.csv).

    py eval/run_eval.py

Por ahora mide la primera métrica de la guía, «Recuperación correcta» (hit@5): de las
preguntas con fuente esperada, ¿en cuántas aparece el artículo esperado entre los 5
recuperados? Objetivo mínimo: 85 %.

También muestra la distancia del mejor resultado en las preguntas que deben abstenerse:
sirve para elegir el umbral de silencio (si nada queda lo bastante cerca, no hay fuente).
Los resultados se guardan en eval/resultados_recuperacion.json para docs/07-evaluacion.md.
"""
import csv
import json
import re
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from app.services import retriever  # noqa: E402

retriever.cargar_entorno()  # respeta EMBEDDING_MODEL y CHROMA_PATH del .env

K = 5


def esperados(fuente: str) -> list[str]:
    """«Código del Trabajo, Art. 188; Art. 71» → ["188", "71"]"""
    return re.findall(r"Art\.\s*(\d+(?:\.\d+)?)", fuente)


def main() -> None:
    # Validar índice, entrada y salida antes de consultar o escribir resultados.
    retriever.ruta_indice()
    entrada = retriever.validar_ruta_copia(RAIZ / "eval/preguntas.csv")
    destino = retriever.validar_ruta_copia(RAIZ / "eval/resultados_recuperacion.json")
    with entrada.open(encoding="utf-8") as archivo:
        preguntas = list(csv.DictReader(archivo))
    filas, aciertos, con_fuente = [], 0, 0
    print(f"Modelo de embeddings: {retriever.modelo_embeddings()} · top-{K}\n")
    for p in preguntas:
        hits = retriever.buscar(p["pregunta"], k=K)
        arts = [h["articulo"] for h in hits]
        esp = esperados(p["fuente_esperada"])
        fila = {"id": p["id"], "tipo": p["tipo"], "esperado": esp, "recuperados": arts,
                "distancias": [round(h["distancia"], 3) for h in hits]}
        if esp:
            con_fuente += 1
            puestos = [arts.index(a) + 1 for a in esp if a in arts]
            fila["acierto"] = bool(puestos)
            fila["puesto"] = min(puestos) if puestos else None
            aciertos += fila["acierto"]
            marca = f"✓ puesto {fila['puesto']}" if puestos else "✗ no recuperado"
        else:
            marca = f"(debe {p['comportamiento_esperado']}) mejor distancia {fila['distancias'][0] if hits else '—'}"
        print(f"{p['id']}  {marca:<45} esperado {esp or '—'}  recuperados {arts}")
        filas.append(fila)

    tasa = aciertos / con_fuente if con_fuente else 0
    print(f"\nRecuperación correcta (hit@{K}): {aciertos}/{con_fuente} = {tasa:.0%}  (objetivo ≥ 85 %)")
    salida = {"fecha": date.today().isoformat(), "modelo": retriever.modelo_embeddings(), "k": K,
              "hit_at_k": round(tasa, 3), "aciertos": aciertos, "total_con_fuente": con_fuente,
              "detalle": filas}
    destino.write_text(
        json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Detalle guardado en eval/resultados_recuperacion.json")


if __name__ == "__main__":
    main()
