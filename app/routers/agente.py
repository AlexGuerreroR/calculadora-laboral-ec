"""Consulta al agente con historial construido exclusivamente por el servidor."""
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from app.routers.resumen import preparar_para_usuario

from app.config import ErrorConfiguracion
from app.schemas import ConsultaAgente, RespuestaAgente
from app.services.agente import controlar_alcance, ejecutar_agente
from app.services.llm import ProveedorNoDisponible, SalidaInvalida
from app.routers.explicar import LimitadorPorMinuto, obtener_llm, recalcular
from app.tools.parametros import cargar_parametros

router = APIRouter(tags=["agente laboral"])
limitador = LimitadorPorMinuto(cargar_parametros()["agente"]["solicitudes_por_minuto"])


@router.post("/agente", response_model=RespuestaAgente)
def consultar(consulta: ConsultaAgente, request: Request, response: Response, fabrica_llm=Depends(obtener_llm)):
    cfg = cargar_parametros()["agente"]
    if len(consulta.mensaje) > cfg["max_caracteres_mensaje"] or len(consulta.model_dump_json()) > cfg["max_caracteres_entrada"]:
        raise HTTPException(422, "La consulta supera el tamaño permitido.")
    espera = limitador.permitir(request.client.host if request.client else "desconocido")
    if espera is not None:
        raise HTTPException(429, "Hizo demasiadas consultas. Espere e intente nuevamente.", headers={"Retry-After": str(espera)})
    bloqueo = controlar_alcance(consulta.mensaje, consulta.calculo is not None)
    if bloqueo:
        return RespuestaAgente(estado=bloqueo[0], mensaje=bloqueo[1])
    if consulta.calculo:
        consulta = consulta.model_copy(update={"calculo": recalcular(consulta.calculo)})
    try:
        cliente = fabrica_llm()
        resultado = ejecutar_agente(consulta, cliente)
        if resultado.calculo_para_resumen is not None:
            resultado.resumen_pdf = preparar_para_usuario(resultado.calculo_para_resumen, request, response)
        return resultado
    except ErrorConfiguracion:
        raise HTTPException(503, "Configure el proveedor del agente en el backend. Los formularios de cálculo siguen disponibles.")
    except ProveedorNoDisponible as e:
        raise HTTPException(503, e.mensaje_usuario, headers={"Retry-After": "60"})
    except SalidaInvalida:
        return RespuestaAgente(estado="abstencion", mensaje="No se obtuvo una respuesta verificable. Intente reformular su consulta.")
    except HTTPException:
        raise
    except Exception:
        # No mostrar datos del proveedor, rutas locales ni claves en la interfaz.
        raise HTTPException(503, "No se pudo completar la consulta. Revise la disponibilidad del proveedor y de la base normativa.")
