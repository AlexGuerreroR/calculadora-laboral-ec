"""Revisar -> confirmar -> descargar. No existe descarga por GET ni aprobación del modelo."""
import hashlib
import re
import secrets

from fastapi import APIRouter, HTTPException, Request, Response

from app.routers.explicar import LimitadorPorMinuto, recalcular
from app.schemas import ConfirmacionResumen, SolicitudResumen, TokenResumen, VistaPreviaResumen
from app.services import rag, resumen
from app.tools import resumen as herramienta
from app.tools.parametros import cargar_parametros

router = APIRouter(prefix="/resumen", tags=["resumen PDF con confirmación"])
limitador = LimitadorPorMinuto(cargar_parametros()["resumen"]["solicitudes_por_minuto"])
COOKIE = "resumen_sesion"


def _propietario(request, response=None):
    sesion = request.cookies.get(COOKIE, "")
    if not re.fullmatch(r"[A-Za-z0-9_-]{32,128}", sesion):
        if response is None:
            raise HTTPException(404, "La solicitud no existe, venció o pertenece a otra sesión. Prepare una nueva vista previa.")
        sesion = secrets.token_urlsafe(32)
    if response is not None:
        response.set_cookie(COOKIE, sesion, httponly=True, secure=request.url.scheme == "https",
                            samesite="strict", max_age=cargar_parametros()["resumen"]["vigencia_segundos"])
    return hashlib.sha256(sesion.encode()).hexdigest()


def preparar_para_usuario(calculo, request, response):
    if len(calculo.model_dump_json()) > cargar_parametros()["resumen"]["max_caracteres_entrada"]:
        raise HTTPException(422, "El cálculo supera el tamaño permitido para el resumen.")
    espera = limitador.permitir(request.client.host if request.client else "desconocido")
    if espera is not None:
        raise HTTPException(429, "Espere antes de preparar otro resumen.", headers={"Retry-After": str(espera)})
    confiable = recalcular(calculo)
    propietario = _propietario(request, response)
    aviso = ""
    try:
        fuentes = rag.recuperar_calculo(confiable)
    except Exception:
        fuentes = []
    if not fuentes:
        aviso = "No se recuperaron fragmentos normativos. El fundamento indicado procede de la configuración del cálculo y requiere comprobación."
    try:
        vista = resumen.almacen.preparar(confiable, fuentes, propietario, aviso)
    except resumen.DemasiadosPendientes:
        raise HTTPException(429, "Hay demasiados resúmenes pendientes. Confirme, cancele o espere a que venzan.")
    response.headers["Cache-Control"] = "no-store"
    return vista


@router.post("/preparar", response_model=VistaPreviaResumen)
def preparar(datos: SolicitudResumen, request: Request, response: Response):
    return preparar_para_usuario(datos.calculo, request, response)


def _consumir(datos, request):
    propietario = _propietario(request)
    try:
        return resumen.almacen.consumir(datos.token, propietario)
    except resumen.SolicitudNoDisponible:
        raise HTTPException(404, "La solicitud no existe, venció o ya fue utilizada. Prepare una nueva vista previa.")


@router.post("/confirmar")
def confirmar(datos: ConfirmacionResumen, request: Request):
    pendiente = _consumir(datos, request)
    try:
        pdf = herramienta.generar_resumen(pendiente)
    except Exception:
        raise HTTPException(503, "No se pudo generar el PDF. Prepare otra vista previa y confirme nuevamente.")
    return Response(pdf, media_type="application/pdf", headers={
        "Content-Disposition": f'attachment; filename="{pendiente.nombre_archivo}"',
        "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})


@router.post("/cancelar")
def cancelar(datos: TokenResumen, request: Request):
    _consumir(datos, request)
    return Response(status_code=204, headers={"Cache-Control": "no-store"})
