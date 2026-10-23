"""NIVEL 2 · Salida en JSON validada con esquema (caso 07: explicación de un resultado ya calculado).

    python scripts/probar_json.py            # usa la entrada 1 de eval/entradas_prompts.csv (caso C01)
    python scripts/probar_json.py 6          # usa la entrada 6 (vacaciones, caso C06)
"""
import csv
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from app.schemas import Explicacion  # noqa: E402
from app.services.llm import ClienteLLM, ErrorLLM, cargar_prompt  # noqa: E402

num = sys.argv[1] if len(sys.argv) > 1 else "1"
entradas = {e["id"]: e for e in csv.DictReader(open(RAIZ / "eval/entradas_prompts.csv", encoding="utf-8"))}
entrada = entradas[num]["entrada"]
try:
    r = ClienteLLM().generar_json(cargar_prompt("system_v3"), entrada, Explicacion)
except ErrorLLM as e:
    sys.exit(f"✗ {e.mensaje_usuario}")
print(r.datos.model_dump_json(indent=2))
print(f"Proveedor: {r.proveedor} · {r.modelo} · {r.latencia_ms} ms · tokens {r.tokens_entrada}+{r.tokens_salida} · intentos {r.intentos}")
