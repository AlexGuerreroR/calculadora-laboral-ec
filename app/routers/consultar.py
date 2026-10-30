"""POST /consultar · El usuario escribe su caso con sus palabras y responde el agente.

Observación de la revisión: «que el usuario pueda escribir lo que necesita» (por ejemplo,
«si me despidieron sin visto bueno y trabajé 3 años, cuánto recibo»). El formulario guiado
sigue existiendo; esta es la otra puerta de entrada.

Flujo:
  1. Pydantic valida la pregunta (vacía o demasiado larga: 422, no se llama al modelo).
  2. Límite de solicitudes por minuto (el mismo de /explicar: protege la cuota gratuita).
  3. El agente corre su ciclo (app/services/agent.py). Los montos salen de las herramientas;
     las citas se verifican contra lo recuperado.
  4. Si el agente quiere derivar al Ministerio o generar el PDF, la respuesta queda
     «pendiente_confirmacion» con un id de sesión y la descripción de lo que se hará; el usuario
     confirma o rechaza en POST /consultar/confirmar.
  5. Si la consulta tiene cálculos, la sesión se guarda 15 minutos para descargar el resumen PDF
     (POST /consultar/resumen). El PDF se arma con datos del servidor, nunca del navegador.
"""
from __future__ import annotations

import threading
import time
from typing import Callable

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.config import ErrorConfiguracion
from app.routers import explicar as compartido
from app.services import agent
from app.services.llm import ClienteLLM, ErrorLLM
from app.services.resumen import generar_pdf

router = APIRouter(tags=["consulta libre con agente"])

AVISO = ("Respuesta generada con inteligencia artificial. Los montos los calcula el sistema y el artículo "
         "citado se muestra abajo. Es una orientación, no asesoría legal.")
SESION_TTL_S = 15 * 60
MAX_SESIONES = 200


class SolicitudConsulta(BaseModel):
    pregunta: str = Field(min_length=3, max_length=600)


class SolicitudConfirmar(BaseModel):
    sesion: str = Field(min_length=32, max_length=32)
    aprobar: bool


class SolicitudResumen(BaseModel):
    sesion: str = Field(min_length=32, max_length=32)


class RespuestaConsulta(BaseModel):
    estado: str
    respuesta: str
    fuentes: list[dict]
    calculos: list[dict]
    pasos: list[str]
    sesion: str | None = None
    pendiente: dict | None = None
    puede_descargar: bool = False   # hay cálculos: se ofrece el botón del resumen PDF
    aviso: str = AVISO


# ---------------------------------------------------------------- sesiones pendientes (memoria)
class Sesiones:
    """Guarda por 15 minutos las consultas que esperan confirmación o que tienen cálculos
    (para el PDF). En memoria: si el servidor se reinicia, el usuario vuelve a preguntar.
    El navegador solo recibe el id; el historial y los cálculos nunca salen del servidor."""

    def __init__(self):
        self._datos: dict[str, list] = {}   # clave → [hora, pendiente | None, ctx]
        self._candado = threading.Lock()

    def guardar(self, pendiente: agent.Pendiente | None, ctx: agent.Contexto, clave: str | None = None) -> str:
        with self._candado:
            ahora = time.monotonic()
            self._datos = {k: v for k, v in self._datos.items() if ahora - v[0] < SESION_TTL_S}
            if len(self._datos) >= MAX_SESIONES:
                self._datos.pop(next(iter(self._datos)))
            clave = clave or agent.nueva_sesion()
            self._datos[clave] = [ahora, pendiente, ctx]
            return clave

    def _vigente(self, clave: str):
        v = self._datos.get(clave)
        if v is None or time.monotonic() - v[0] >= SESION_TTL_S:
            self._datos.pop(clave, None)
            return None
        return v

    def tomar_pendiente(self, clave: str):
        """La acción pendiente se usa una sola vez: confirmar dos veces no la repite."""
        with self._candado:
            v = self._vigente(clave)
            if v is None or v[1] is None:
                return None
            pendiente, v[1] = v[1], None
            return pendiente, v[2]

    def contexto(self, clave: str) -> agent.Contexto | None:
        with self._candado:
            v = self._vigente(clave)
            return v[2] if v else None


sesiones = Sesiones()


def obtener_buscador() -> Callable:
    """El buscador real del RAG. Se importa aquí para que las pruebas no necesiten ChromaDB."""
    from app.services.retriever import buscar

    return buscar


def _salida(r: agent.RespuestaAgente, sesion: str | None = None) -> RespuestaConsulta:
    pendiente = ({"herramienta": r.pendiente.herramienta, "argumentos": r.pendiente.argumentos}
                 if r.pendiente else None)
    return RespuestaConsulta(estado=r.estado, respuesta=r.respuesta, fuentes=r.fuentes, calculos=r.calculos,
                             pasos=r.pasos, sesion=sesion, pendiente=pendiente,
                             puede_descargar=bool(sesion and r.calculos and r.estado in ("ok", "resumen_listo")))


@router.post(
    "/consultar",
    response_model=RespuestaConsulta,
    responses={422: {"description": "Pregunta vacía o demasiado larga (no se llama al modelo)"},
               429: {"description": "Límite de solicitudes por minuto alcanzado"},
               503: {"description": "Modelo o base de conocimiento no disponible"}},
)
def consultar(solicitud: SolicitudConsulta, request: Request,
              fabrica_llm: Callable[[], ClienteLLM] = Depends(compartido.obtener_llm),
              buscador: Callable = Depends(obtener_buscador)):
    espera = compartido.limitador.permitir(compartido._cliente(request))
    if espera is not None:
        raise HTTPException(429, f"Hizo demasiadas solicitudes. Espere {espera} segundos e intente de nuevo.",
                            headers={"Retry-After": str(espera)})
    try:
        llm = fabrica_llm()
    except ErrorConfiguracion:
        raise HTTPException(503, "El asistente no está configurado. Puede usar el formulario de cálculo.")
    try:
        r, _, ctx = agent.iniciar(llm, solicitud.pregunta.strip(), buscador)
    except ErrorLLM as e:
        raise HTTPException(503, e.mensaje_usuario, headers={"Retry-After": "60"})
    except agent.BaseNoDisponible:
        raise HTTPException(503, "La base de normativa no está disponible. Puede usar el formulario de cálculo.")
    guardar = r.estado == "pendiente_confirmacion" or (r.estado == "ok" and r.calculos)
    sesion = sesiones.guardar(r.pendiente, ctx) if guardar else None
    return _salida(r, sesion)


@router.post("/consultar/confirmar", response_model=RespuestaConsulta,
             responses={404: {"description": "La sesión no existe, ya se usó o expiró"}})
def confirmar(solicitud: SolicitudConfirmar):
    guardado = sesiones.tomar_pendiente(solicitud.sesion)
    if guardado is None:
        raise HTTPException(404, "La consulta ya no está disponible. Vuelva a escribir su pregunta.")
    pendiente, ctx = guardado
    r = agent.confirmar(pendiente, solicitud.aprobar, ctx)
    return _salida(r, solicitud.sesion if r.calculos else None)


@router.post("/consultar/resumen", response_class=Response,
             responses={200: {"content": {"application/pdf": {}}, "description": "Resumen PDF"},
                        404: {"description": "La sesión no existe, expiró o no tiene cálculos"}})
def resumen(solicitud: SolicitudResumen):
    """Descarga el PDF. Pulsar «Descargar resumen PDF» es la confirmación del usuario."""
    ctx = sesiones.contexto(solicitud.sesion)
    if ctx is None or not ctx.calculos:
        raise HTTPException(404, "No hay un cálculo disponible para el resumen. Vuelva a consultar.")
    pdf = generar_pdf(ctx.calculos, agent.fuentes_del_resumen(ctx), ctx.respuesta_final)
    return Response(pdf, media_type="application/pdf",
                    headers={"Content-Disposition": 'attachment; filename="resumen-calculadora-laboral.pdf"'})
