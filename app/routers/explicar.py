"""POST /explicar · El modelo explica en lenguaje sencillo un resultado calculado por el código.

Flujo (el orden lo decide el código, no el modelo · ADR-002):
  1. FastAPI valida la forma de la entrada con Pydantic (ResultadoCalculo). Si es inválida: 422.
  2. Límites del backend: tamaño máximo de la entrada y solicitudes por minuto (429 propio).
  3. El backend NO confía en el resultado que envía el cliente (el navegador no es confiable):
     lo RECALCULA desde `entradas` con las mismas herramientas de cálculo. Si el total enviado
     no coincide, responde 422. El desglose, el total y el fundamento que se usan son los del
     servidor (el fundamento sale de config/parametros.yaml).
  4. Recién entonces se crea el cliente del modelo: si falta la configuración (.env), el
     usuario recibe un 503 claro, no un 500.
  5. El RAG recupera artículos; el modelo explica con citas que el servidor verifica.
"""
from __future__ import annotations

import logging
import os
import threading
import time
from collections import defaultdict, deque
from functools import lru_cache
from typing import Callable

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, ValidationError

from app.config import ErrorConfiguracion
from app.schemas import (EntradaDecimoCuarto, EntradaDecimoTercero, EntradaVacaciones,
                         ResultadoCalculo, ExplicacionRAG, FuenteRAG, EntradaHoras, EntradaLiquidacion)
from app.services import rag
from app.services.llm import ClienteLLM, ProveedorNoDisponible, SalidaInvalida
from app.tools.decimos import calcular_decimo_cuarto, calcular_decimo_tercero
from app.tools.vacaciones import calcular_vacaciones
from app.tools.horas import calcular_horas
from app.tools.liquidacion import estimar_liquidacion
from app.tools.parametros import cargar_parametros

router = APIRouter(tags=["explicación con IA"])
log = logging.getLogger("api")

AVISO_IA = ("Explicación generada con inteligencia artificial a partir de un cálculo hecho por el sistema. "
            "Es una orientación: el valor oficial lo determina el empleador conforme a la ley. "
            "Ante un conflicto laboral, acuda al Ministerio del Trabajo.")
SIN_EXPLICACION = "La explicación no está disponible por ahora. El cálculo de arriba sigue siendo válido."
TOLERANCIA = 0.01  # indicador del caso 07: ±0,01 USD


def _entero(nombre: str, defecto: int) -> int:
    valor = os.getenv(nombre, "").strip()
    return int(valor) if valor else defecto


MAX_INPUT_CHARS = _entero("MAX_INPUT_CHARS", 2000)
RATE_LIMIT_POR_MINUTO = _entero("RATE_LIMIT_POR_MINUTO", 4)

# Cada tipo de cálculo con su esquema de entrada y su herramienta (las mismas de /calculos).
CALCULOS = {
    "decimo_tercero": (EntradaDecimoTercero, calcular_decimo_tercero),
    "decimo_cuarto": (EntradaDecimoCuarto, calcular_decimo_cuarto),
    "vacaciones": (EntradaVacaciones, calcular_vacaciones),
    "horas_extra": (EntradaHoras, calcular_horas),
    "liquidacion": (EntradaLiquidacion, estimar_liquidacion),
}


class RespuestaExplicar(BaseModel):
    explicacion: ExplicacionRAG | None
    fundamento: str            # lo pone el servidor, desde la configuración
    total: float               # el monto recalculado por el servidor
    aviso: str
    mensaje: str
    proveedor: str | None = None
    fuentes: list[FuenteRAG] = Field(default_factory=list)


# ---------------------------------------------------------------- cliente del modelo (perezoso)
@lru_cache
def _crear_llm() -> ClienteLLM:
    return ClienteLLM()


def obtener_llm() -> Callable[[], ClienteLLM]:
    """Devuelve una FÁBRICA, no el cliente: así el cliente se crea después de las validaciones
    y un .env incompleto no rompe la solicitud con un 500. En las pruebas se reemplaza."""
    return _crear_llm


def obtener_recuperador():
    return rag.recuperar_calculo


# ---------------------------------------------------------------- límite por minuto
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


# ---------------------------------------------------------------- recálculo en el servidor
def recalcular(resultado: ResultadoCalculo) -> ResultadoCalculo:
    """Vuelve a calcular desde `entradas`. Lo que mande el cliente en total, desglose o
    fundamento no se usa: solo se comprueba que el total coincida."""
    esquema, calcular = CALCULOS[resultado.tipo]
    datos = {k: v for k, v in resultado.entradas.items() if k in esquema.model_fields}
    try:
        servidor = calcular(esquema(**datos))
    except ValidationError as e:
        campos = ", ".join(".".join(map(str, x["loc"])) for x in e.errors())
        raise HTTPException(422, f"Las entradas del cálculo no son válidas ({campos}).")
    except ValueError as e:
        raise HTTPException(422, str(e))
    if abs(servidor.total - resultado.total) > TOLERANCIA:
        raise HTTPException(422, "El resultado enviado no coincide con el cálculo del sistema. "
                                 "Vuelva a calcular antes de pedir la explicación.")
    return servidor


@router.post(
    "/explicar",
    response_model=RespuestaExplicar,
    responses={422: {"description": "Entrada no válida o resultado manipulado (no se llama al modelo)"},
               429: {"description": "Límite de solicitudes por minuto alcanzado"},
               503: {"description": "Servicio de IA no configurado o ningún proveedor respondió"}},
)
def explicar(resultado: ResultadoCalculo, request: Request,
             fabrica_llm: Callable[[], ClienteLLM] = Depends(obtener_llm),
             recuperar=Depends(obtener_recuperador)):
    limite = (cargar_parametros()["limites"]["explicar_liquidacion_caracteres"]
              if resultado.tipo == "liquidacion" else MAX_INPUT_CHARS)
    if len(resultado.model_dump_json()) > limite:
        raise HTTPException(422, f"La entrada supera el máximo de {limite} caracteres.")

    espera = limitador.permitir(_cliente(request))
    if espera is not None:
        raise HTTPException(429, f"Hizo demasiadas solicitudes. Espere {espera} segundos e intente de nuevo.",
                            headers={"Retry-After": str(espera)})

    confiable = recalcular(resultado)  # desde aquí solo se usan datos del servidor

    try:
        fuentes = recuperar(confiable)
    except Exception:
        log.exception("No se pudo consultar el índice normativo")
        raise HTTPException(503, "La base normativa no está disponible. El cálculo sigue visible; "
                                 "revise la ingesta local antes de solicitar una explicación.")
    if not fuentes:
        return RespuestaExplicar(explicacion=None, fundamento=confiable.fundamento,
                                 total=confiable.total, aviso=AVISO_IA, mensaje=rag.SIN_RESPALDO)

    try:
        llm = fabrica_llm()
    except ErrorConfiguracion as e:
        log.error("configuración del servicio de IA incompleta: %s", e)
        raise HTTPException(503, "El servicio de explicación no está configurado. El cálculo sigue siendo válido.")

    try:
        r, usadas = rag.explicar_calculo(llm, confiable, fuentes)
    except ProveedorNoDisponible as e:
        raise HTTPException(503, e.mensaje_usuario, headers={"Retry-After": "60"})
    except SalidaInvalida:
        # No es un error HTTP: el servicio decidió no mostrar una explicación dudosa.
        return RespuestaExplicar(explicacion=None, fundamento=confiable.fundamento, total=confiable.total,
                                 aviso=AVISO_IA, mensaje=SIN_EXPLICACION)

    exp: ExplicacionRAG = r.datos
    mensaje = ("Explicación generada." if exp.estado == "ok"
               else "El asistente no tiene datos suficientes para explicar este resultado.")
    return RespuestaExplicar(explicacion=exp, fundamento=confiable.fundamento, total=confiable.total,
                             aviso=AVISO_IA, mensaje=mensaje, proveedor=r.proveedor, fuentes=usadas)
