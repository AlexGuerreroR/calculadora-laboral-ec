"""Agente de la Calculadora Laboral EC (semana 3 · ADR-004).

Un agente es el modelo dentro de un ciclo (clase del 28/10):
    el modelo PIDE una herramienta → el SERVIDOR la ejecuta → el resultado vuelve al modelo
    → … hasta que el modelo responde con texto o se llega al tope de vueltas.

Reglas de diseño (lo que se defiende ante el tribunal):
  1. Lista cerrada (PERMITIDAS). Si el modelo pide otra cosa, no se ejecuta.
  2. Tope de vueltas (agente.max_iteraciones en config/parametros.yaml).
  3. Confirmación humana para lo que tiene efecto fuera de la conversación
     (REQUIEREN_OK = derivar al Ministerio): el ciclo se pausa hasta que el usuario acepte.
  4. Cada herramienta valida sus argumentos con Pydantic ANTES de ejecutarse;
     si faltan datos, el error vuelve al modelo para que se los pida al usuario.
  5. Lo que el agente lee (pregunta, fragmentos del Código) es dato NO confiable:
     va entre etiquetas y nunca cambia las reglas (OWASP, riesgos de agentes).
  6. El modelo no calcula ni inventa artículos: al final el código VERIFICA que
     cada artículo citado haya sido recuperado y que cada monto venga de una herramienta.
     Si no pasa, el sistema se abstiene.
"""
from __future__ import annotations

import json
import logging
import re
import uuid
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Callable, Literal

from pydantic import BaseModel, Field, ValidationError

from app.schemas import (EntradaDecimoCuarto, EntradaDecimoTercero, EntradaHorasExtra, EntradaLiquidacion,
                         EntradaVacaciones, Estricto)
from app.services.llm import cargar_prompt
from app.tools.decimos import calcular_decimo_cuarto, calcular_decimo_tercero
from app.tools.horas import calcular_horas_extra
from app.tools.liquidacion import estimar_liquidacion
from app.tools.parametros import cargar_parametros
from app.tools.vacaciones import calcular_vacaciones

log = logging.getLogger("agente")

ABSTENCION = ("No encontré en el Código del Trabajo una fuente que responda su pregunta con seguridad. "
              "Puede reformularla o usar el formulario de cálculo. Si se trata de un conflicto con su "
              "empleador, acuda al Ministerio del Trabajo.")
TOPE = ("La consulta necesitó más pasos de los permitidos. Escríbala de forma más concreta "
        "(por ejemplo: sueldo, fecha de ingreso, fecha de salida y motivo).")
NO_PERMITIDA = "Herramienta no permitida. Use solo las herramientas de la lista."


class BaseNoDisponible(Exception):
    """La base vectorial no responde: falta correr scripts/ingest.py o cambió el modelo."""


# ---------------------------------------------------------------- esquemas de herramientas nuevas
class EntradaConsulta(Estricto):
    pregunta: str = Field(min_length=3, max_length=300,
                          description="Qué buscar en el Código del Trabajo, en palabras del usuario")
    tema: Literal["jornada", "vacaciones", "remuneracion", "decimos", "despido"] | None = Field(
        default=None, description="Tema, si se conoce, para buscar solo en esa parte del Código")


class EntradaDerivacion(Estricto):
    motivo: str = Field(min_length=3, max_length=300,
                        description="Por qué el caso necesita asesoría humana (conflicto, disputa, litigio)")


# ---------------------------------------------------------------- catálogo (lista cerrada)
@dataclass(frozen=True)
class Herramienta:
    esquema: type[BaseModel]
    funcion: Callable
    descripcion: str
    nivel: Literal["libre", "con_confirmacion"]


def _calculo(funcion):
    """Adapta una herramienta de cálculo: devuelve el resultado del código como dict."""
    return lambda entrada, ctx: funcion(entrada).model_dump(mode="json")


def _consultar(entrada: EntradaConsulta, ctx: "Contexto") -> dict:
    p = cargar_parametros()["agente"]
    try:
        hallados = ctx.buscador(entrada.pregunta, k=p["fragmentos_por_consulta"], tema=entrada.tema)
    except Exception as e:  # índice no construido, modelo de embeddings distinto, etc.
        raise BaseNoDisponible() from e
    for h in hallados:
        ctx.fuentes.setdefault(h["articulo"], h)
    # Cada fragmento va etiquetado: es texto para leer, no instrucciones.
    return {"fragmentos": [
        {"articulo": h["articulo"], "capitulo": h.get("capitulo", ""),
         "texto": f"<fragmento>{h['texto'][:p['max_caracteres_fragmento']]}</fragmento>"}
        for h in hallados]}


def _derivar(entrada: EntradaDerivacion, ctx: "Contexto") -> dict:
    d = cargar_parametros()["agente"]["derivacion"]
    return {"destino": d["destino"], "sitio": d["sitio"], "mensaje": d["mensaje"]}


HERRAMIENTAS: dict[str, Herramienta] = {
    "consultar_articulo": Herramienta(
        EntradaConsulta, _consultar,
        "Busca artículos del Código del Trabajo. Úsala antes de explicar cualquier norma.", "libre"),
    "calcular_decimo_tercero": Herramienta(
        EntradaDecimoTercero, _calculo(calcular_decimo_tercero),
        "Calcula el décimo tercero con las remuneraciones de cada mes del período.", "libre"),
    "calcular_decimo_cuarto": Herramienta(
        EntradaDecimoCuarto, _calculo(calcular_decimo_cuarto),
        "Calcula el décimo cuarto con los meses trabajados y la región.", "libre"),
    "calcular_vacaciones": Herramienta(
        EntradaVacaciones, _calculo(calcular_vacaciones),
        "Calcula días y valor de vacaciones de un período.", "libre"),
    "calcular_horas_extra": Herramienta(
        EntradaHorasExtra, _calculo(calcular_horas_extra),
        "Calcula el valor de horas suplementarias (50 %) y extraordinarias (100 %) de un mes.", "libre"),
    "estimar_liquidacion": Herramienta(
        EntradaLiquidacion, _calculo(estimar_liquidacion),
        "Estima la liquidación al terminar la relación laboral (despido, desahucio o acuerdo).", "libre"),
    "derivar_al_ministerio": Herramienta(
        EntradaDerivacion, _derivar,
        "Deriva el caso al Ministerio del Trabajo cuando hay conflicto o se pide un dictamen legal. "
        "Requiere que el usuario confirme.", "con_confirmacion"),
}
PERMITIDAS = frozenset(HERRAMIENTAS)
REQUIEREN_OK = frozenset(n for n, h in HERRAMIENTAS.items() if h.nivel == "con_confirmacion")


def _simplificar(esquema):
    """Quita «title» y «additionalProperties» de lo que ve el modelo: algunos proveedores
    (Gemini) los rechazan. La validación estricta sigue en el servidor con Pydantic."""
    if isinstance(esquema, dict):
        return {k: _simplificar(v) for k, v in esquema.items() if k not in ("title", "additionalProperties")}
    if isinstance(esquema, list):
        return [_simplificar(v) for v in esquema]
    return esquema


def definiciones() -> list[dict]:
    """Lo que el modelo ve de cada herramienta: nombre, descripción y esquema de argumentos."""
    return [{"type": "function", "function": {
        "name": nombre, "description": h.descripcion,
        "parameters": _simplificar(h.esquema.model_json_schema())}}
        for nombre, h in HERRAMIENTAS.items()]


# ---------------------------------------------------------------- estado de una consulta
@dataclass
class Contexto:
    buscador: Callable
    fuentes: dict[str, dict] = field(default_factory=dict)   # artículos recuperados en ESTA consulta
    calculos: list[dict] = field(default_factory=list)       # resultados de las herramientas de cálculo
    pasos: list[str] = field(default_factory=list)           # herramientas usadas, en orden


@dataclass
class Pendiente:
    """Una acción que espera la confirmación del usuario."""
    id_llamada: str
    herramienta: str
    argumentos: dict


@dataclass
class RespuestaAgente:
    estado: Literal["ok", "falta", "abstencion", "pendiente_confirmacion", "derivado", "tope", "rechazado"]
    respuesta: str
    fuentes: list[dict]
    calculos: list[dict]
    pasos: list[str]
    pendiente: Pendiente | None = None
    proveedor: str | None = None


# ---------------------------------------------------------------- verificaciones del final
_CITA = re.compile(r"\bart(?:[íi]culos?|s?\.)\s*((?:\d+(?:\.\d+)?)(?:\s*(?:,|y|e)\s*\d+(?:\.\d+)?)*)", re.I)
_MONTO = re.compile(r"(?:USD|\$|US\$)\s*(\d[\d.,]*\d|\d)|(\d[\d.,]*\d)\s*(?:USD|dólares)", re.I)


def articulos_en(texto: str) -> set[str]:
    """«arts. 185 y 188», «Art. 71», «artículo 111» → {"185", "188", "71", "111"}."""
    return {n for grupo in _CITA.findall(texto) for n in re.findall(r"\d+(?:\.\d+)?", grupo)}


def _a_decimal(numero: str) -> Decimal | None:
    """Acepta 9331.84 · 9,331.84 · 9.331,84 · 9331,84."""
    n = numero.strip(".,")
    if "," in n and "." in n:
        n = n.replace(".", "").replace(",", ".") if n.rfind(",") > n.rfind(".") else n.replace(",", "")
    elif "," in n:
        n = n.replace(",", ".") if len(n.split(",")[-1]) == 2 else n.replace(",", "")
    try:
        return Decimal(n).quantize(Decimal("0.01"))
    except InvalidOperation:
        return None


def montos_en(texto: str) -> set[Decimal]:
    return {d for a, b in _MONTO.findall(texto) if (d := _a_decimal(a or b)) is not None}


def verificar(texto: str, ctx: Contexto) -> str | None:
    """Devuelve el motivo para abstenerse, o None si la respuesta pasa."""
    citados = articulos_en(texto)
    permitidos = set(ctx.fuentes) | {a for c in ctx.calculos for a in articulos_en(c["fundamento"])}
    if not citados:
        return "sin_cita"
    if citados - permitidos:
        return f"cita_no_recuperada:{sorted(citados - permitidos)}"
    # Todo monto del texto debe salir de una herramienta (el modelo no calcula).
    conocidos = set()
    for c in ctx.calculos:
        conocidos.add(Decimal(str(c["total"])).quantize(Decimal("0.01")))
        for linea in c["desglose"]:
            conocidos |= {d for n in re.findall(r"\d[\d.,]*\d|\d", linea) if (d := _a_decimal(n)) is not None}
    if montos_en(texto) - conocidos:
        return "monto_no_calculado"
    return None


# ---------------------------------------------------------------- el ciclo
def _mensaje_asistente(m) -> dict:
    """Se reconstruye a mano: solo los campos estándar (algunos proveedores agregan otros)."""
    return {"role": "assistant", "content": m.content or "",
            "tool_calls": [{"id": t.id, "type": "function",
                            "function": {"name": t.function.name, "arguments": t.function.arguments}}
                           for t in m.tool_calls]}


def _ejecutar(nombre: str, argumentos: str | dict, ctx: Contexto) -> dict:
    if nombre not in PERMITIDAS:
        log.warning("herramienta fuera de la lista: %s", nombre)
        return {"error": NO_PERMITIDA}
    h = HERRAMIENTAS[nombre]
    try:
        datos = json.loads(argumentos) if isinstance(argumentos, str) else argumentos
        entrada = h.esquema.model_validate(datos)
    except (json.JSONDecodeError, ValidationError) as e:
        faltan = [".".join(map(str, x["loc"])) + ": " + x["msg"] for x in e.errors()] \
            if isinstance(e, ValidationError) else ["argumentos no son JSON"]
        return {"error": "Datos inválidos o incompletos. Pídale al usuario: " + "; ".join(faltan)}
    try:
        salida = h.funcion(entrada, ctx)
    except ValueError as e:
        return {"error": str(e)}
    ctx.pasos.append(nombre)
    if nombre.startswith(("calcular_", "estimar_")):
        ctx.calculos.append(salida)
    return salida


def _respuesta(estado, texto, ctx: Contexto, **extra) -> RespuestaAgente:
    fuentes = [{"articulo": a, "capitulo": f.get("capitulo", ""), "texto": f["texto"]}
               for a, f in ctx.fuentes.items()]
    return RespuestaAgente(estado, texto, fuentes, ctx.calculos, ctx.pasos, **extra)


def ciclo(llm, mensajes: list[dict], ctx: Contexto, max_iter: int | None = None) -> RespuestaAgente:
    """Corre el ciclo desde `mensajes`. Se usa al empezar y al reanudar tras una confirmación."""
    max_iter = max_iter or cargar_parametros()["agente"]["max_iteraciones"]
    system, herramientas, proveedor = cargar_prompt("agente_v1"), definiciones(), None
    for _ in range(max_iter):
        r = llm.generar_con_herramientas(system, mensajes, herramientas)
        m, proveedor = r.datos, r.proveedor
        if not getattr(m, "tool_calls", None):
            texto = (m.content or "").strip()
            if texto.startswith("SIN_FUENTE"):
                return _respuesta("abstencion", ABSTENCION, ctx, proveedor=proveedor)
            if texto.startswith("FALTA:"):
                # El modelo pide un dato al usuario. No puede traer montos ni citas sin verificar.
                if montos_en(texto) or articulos_en(texto) - set(ctx.fuentes):
                    return _respuesta("abstencion", ABSTENCION, ctx, proveedor=proveedor)
                return _respuesta("falta", texto.removeprefix("FALTA:").strip(), ctx, proveedor=proveedor)
            motivo = verificar(texto, ctx)
            if motivo:
                log.info("abstención por verificación: %s", motivo)
                return _respuesta("abstencion", ABSTENCION, ctx, proveedor=proveedor)
            return _respuesta("ok", texto, ctx, proveedor=proveedor)

        mensajes.append(_mensaje_asistente(m))
        for t in m.tool_calls:
            if t.function.name in REQUIEREN_OK:
                # Se pausa: el servidor NO ejecuta hasta que el usuario confirme.
                try:
                    args = json.loads(t.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                return _respuesta("pendiente_confirmacion",
                                  "Su caso parece necesitar asesoría humana. ¿Desea que lo derivemos al "
                                  "Ministerio del Trabajo?", ctx,
                                  pendiente=Pendiente(t.id, t.function.name, args), proveedor=proveedor)
            salida = _ejecutar(t.function.name, t.function.arguments, ctx)
            mensajes.append({"role": "tool", "tool_call_id": t.id,
                             "content": json.dumps(salida, ensure_ascii=False)})
    return _respuesta("tope", TOPE, ctx, proveedor=proveedor)


def iniciar(llm, pregunta: str, buscador: Callable) -> tuple[RespuestaAgente, list[dict], Contexto]:
    ctx = Contexto(buscador=buscador)
    mensajes = [{"role": "user", "content": f"<pregunta>{pregunta}</pregunta>"}]
    return ciclo(llm, mensajes, ctx), mensajes, ctx


def confirmar(pendiente: Pendiente, aprobado: bool, ctx: Contexto) -> RespuestaAgente:
    """La decisión del usuario. Si acepta, se ejecuta la derivación; si no, no se hace nada."""
    if not aprobado:
        return _respuesta("rechazado", "No se derivó el caso. Puede seguir consultando.", ctx)
    salida = _ejecutar(pendiente.herramienta, pendiente.argumentos, ctx)
    if "error" in salida:
        return _respuesta("abstencion", ABSTENCION, ctx)
    return _respuesta("derivado", f"{salida['mensaje']} Sitio oficial: {salida['sitio']}", ctx)


def nueva_sesion() -> str:
    return uuid.uuid4().hex
