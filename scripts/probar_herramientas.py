"""Diagnóstico: ¿cada proveedor acepta llamadas a herramientas (function calling)?

    py scripts/probar_herramientas.py

Hace UNA llamada por proveedor (principal y respaldo) con las herramientas del agente y una
pregunta fija, sin pasar por los reintentos ni el respaldo. Muestra si el modelo pidió una
herramienta o el error exacto del proveedor (por ejemplo, un 400 por el esquema). No envía
datos personales.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from app.services import agent  # noqa: E402
from app.services.llm import ClienteLLM, cargar_prompt  # noqa: E402

PREGUNTA = ("<pregunta>Me despidieron sin visto bueno, ganaba 1000 y trabajé del 1 de agosto de 2020 "
            "al 31 de agosto de 2026 en la Sierra</pregunta>")


def main() -> None:
    llm = ClienteLLM()
    mensajes = [{"role": "system", "content": cargar_prompt(agent.PROMPT_AGENTE)},
                {"role": "user", "content": PREGUNTA}]
    for p in llm.proveedores:
        try:
            r = llm._clientes[p.nombre].chat.completions.create(
                model=p.modelo, messages=mensajes, tools=agent.definiciones(), tool_choice="auto",
                max_tokens=llm.config.max_tokens)
            m = r.choices[0].message
            pedidas = [t.function.name for t in (m.tool_calls or [])]
            print(f"✓ {p.nombre} ({p.modelo}): " + (f"pidió {pedidas}" if pedidas else "respondió con texto"))
        except Exception as e:  # se muestra el error tal como lo devuelve el proveedor
            print(f"✗ {p.nombre} ({p.modelo}): {type(e).__name__} {getattr(e, 'status_code', '')} "
                  f"{str(getattr(e, 'message', e))[:500]}")


if __name__ == "__main__":
    main()
