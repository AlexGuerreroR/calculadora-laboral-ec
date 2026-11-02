# eval/evaluar.py · Grupo 7 · corre en CI: python eval/evaluar.py
import json, sys
from app.flujo import procesar
from app.rag import buscar            # su recuperador

METAS = {
    "rag_acierto_top5": 0.9,
    "rag_con_cita": 0.8,
    "agente_tareas": 0.79,
    "flujo_max_revision": 0.3,
    "flujo_errores_silenciosos": 0,
}


def leer(ruta):
    return [json.loads(l) for l in open(ruta, encoding="utf-8") if l.strip()]


def evaluar_rag(preguntas, k=5):
    """Cada pregunta trae la fuente correcta; cuenta si aparece en los primeros k."""
    aciertos = sum(p["fuente"] in [f.id for f in buscar(p["pregunta"], k=k)]
                   for p in preguntas if p.get("fuente"))
    con_fuente = [p for p in preguntas if p.get("fuente")]
    return aciertos / max(1, len(con_fuente))


def evaluar_flujo(casos):
    auto = rev = silenciosos = 0
    for c in casos:
        r = procesar(c)                  # devuelve {"destino": ..., "resultado": ...}
        if r["destino"] == "revision":
            rev += 1
        else:
            auto += 1
            if r["resultado"] != c["esperado"]["resultado"]:
                silenciosos += 1           # salió automático y mal
    return {"revision": rev / len(casos), "silenciosos": silenciosos}


if __name__ == "__main__":
    rag = evaluar_rag(leer("eval/preguntas_rag.jsonl"))   # 20 preguntas, 3 sin respuesta
    flujo = evaluar_flujo(leer("eval/casos_flujo.jsonl")) # 20 casos
    print(f"RAG acierto top-5: {rag:.0%}  ·  flujo a revisión: {flujo['revision']:.0%}  ·  errores silenciosos: {flujo['silenciosos']}")
    ok = (rag >= METAS["rag_acierto_top5"] and flujo["silenciosos"] == 0
          and flujo["revision"] <= METAS["flujo_max_revision"])
    sys.exit(0 if ok else 1)             # en CI, falla el build si no se cumplen las metas
