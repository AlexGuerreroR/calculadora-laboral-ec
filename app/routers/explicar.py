"""POST /explicar · El modelo explica en lenguaje sencillo un resultado YA calculado por el código.

Flujo (el orden lo decide el código, no el modelo · ADR-002):
  1. FastAPI valida la entrada con Pydantic (ResultadoCalculo). Si es inválida: 422 y el
     modelo nunca se llama.
  2. Límites del backend: tamaño máximo de la entrada y solicitudes por minuto (429 propio).
  3. llm.py llama al modelo con el prompt versionado, reintentos y respaldo.
  4. El modelo devuelve JSON con el esquema Explicacion.
  5. El CÓDIGO agrega el fundamento (la norma) desde el resultado del cálculo; el modelo
     nunca la escribe (aviso del docente del 22/10: si se la pide, la puede inventar).
"""
from __future__ import annotations

import os
import threading
import time
from collections import defaultdict, deque
from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from app.schemas import Explicacion, ResultadoCalculo
from app.services.llm import ClienteLLM, ProveedorNoDisponible, SalidaInvalida, cargar_prompt

router = APIRouter(tags=["explicación con IA"])

PROMPT = os.getenv("PROMPT_VERSION", "system_v3")  # la versión ganadora de docs/05-prompts.md
AVISO_IA = ("Explicación generada con inteligencia artificial a partir de un cálculo hecho por el sistema. "
            "Es una orientación: el valor oficial lo determina el empleador conforme a la ley. "
            "Ante un conflicto laboral, acuda al Ministerio del Trabajo.")
SIN_EXPLICACION = "La explicación no está disponible por ahora. El cálculo de arriba sigue siendo válido."


def _entero(nombre: str, defecto: int) -> int:
    valor = os.getenv(nombre, "").strip()
    return int(valor) if valor else defecto


MAX_INPUT_CHARS = _entero("MAX_INPUT_CHARS", 2000)
RATE_LIMIT_POR_MINUTO = _entero("RATE_LIMIT_POR_MINUTO", 4)


class RespuestaExplicar(BaseModel):
    explicacion: Explicacion | None
    fundamento: str            # lo pone el código, no el modelo
    total: float               # el monto calculado por el código, sin cambios
    aviso: str
    mensaje: str
    proveedor: str | None = None


@lru_cache
def obtener_llm() -> ClienteLLM:
    return ClienteLLM()


class LimitadorPorMinuto:
    """Ventana deslizante de 60 s por cliente. Protege la cuota gratuita (OWASP LLM10)."""

    def __init__(self, limite: int, ventana_s: float = 60.0):
        self.limite, self.ventana_s = limite, ventana_s
        self._registros: dict[str, deque] = defaultdict(deque)
        self._candado = threading.Lock()

    def permitir(self, clave: str) -> int | None:
        """None si puede pasar; si no, los segundos que debe esperar."""
        ahora = time.monotonic()
        with self._candado:
            cola = self._registros[clave]
            while cola and ahora - cola[0] > self.ventana_s:
                cola.popleft()
            if len(cola) >= self.limite:
                return max(1, int(self.ventana_s - (ahora - cola[0])) + 1)
            cola.append(ahora)
            return None


limitador = LimitadorPorMinuto(RATE_LIMIT_POR_MINUTO)


def _cliente(request: Request) -> str:
    return request.client.host if request.client else "desconocido"


@router.post(
    "/explicar",
    response_model=RespuestaExplicar,
    responses={422: {"description": "Entrada no válida (no se llama al modelo)"},
               429: {"description": "Límite de solicitudes por minuto alcanzado"},
               503: {"description": "Ningún proveedor de IA respondió"}},
)
def explicar(resultado: ResultadoCalculo, request: Request, llm: ClienteLLM = Depends(obtener_llm)):
    datos = resultado.model_dump_json()
    if len(datos) > MAX_INPUT_CHARS:
        raise HTTPException(422, f"La entrada supera el máximo de {MAX_INPUT_CHARS} caracteres.")

    espera = limitador.permitir(_cliente(request))
    if espera is not None:
        raise HTTPException(429, f"Hizo demasiadas solicitudes. Espere {espera} segundos e intente de nuevo.",
                            headers={"Retry-After": str(espera)})

    try:
        r = llm.generar_json(cargar_prompt(PROMPT), f"<resultado>{datos}</resultado>", Explicacion)
    except ProveedorNoDisponible as e:
        raise HTTPException(503, e.mensaje_usuario, headers={"Retry-After": "60"})
    except SalidaInvalida:
        # No es un error HTTP: el servicio decidió no mostrar una explicación dudosa.
        return RespuestaExplicar(explicacion=None, fundamento=resultado.fundamento, total=resultado.total,
                                 aviso=AVISO_IA, mensaje=SIN_EXPLICACION)

    exp: Explicacion = r.datos
    mensaje = "Explicación generada." if exp.estado == "ok" else "El asistente no tiene datos suficientes para explicar este resultado."
    return RespuestaExplicar(explicacion=exp, fundamento=resultado.fundamento, total=resultado.total,
                             aviso=AVISO_IA, mensaje=mensaje, proveedor=r.proveedor)
