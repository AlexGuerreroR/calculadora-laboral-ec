"""Endpoints de cálculo · deterministas, NO llaman al modelo (ADR-002).

POST /calculos/decimos     décimo tercero o décimo cuarto, según «tipo»
POST /calculos/vacaciones  días y valor de vacaciones (anuales o proporcionales)
POST /calculos/horas-extra  horas suplementarias (50 %) y extraordinarias (100 %) de un mes
POST /calculos/liquidacion  liquidación (finiquito) estimada al terminar la relación laboral

Si la entrada es inválida, FastAPI responde 422 antes de calcular. Los parámetros
(salario básico, divisores, días) se leen de config/parametros.yaml.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas import (EntradaDecimoCuarto, EntradaDecimoTercero, EntradaHorasExtra, EntradaLiquidacion,
                         EntradaVacaciones, ResultadoCalculo, SolicitudDecimos)
from app.tools.horas import calcular_horas_extra
from app.tools.liquidacion import estimar_liquidacion
from app.tools.decimos import calcular_decimo_cuarto, calcular_decimo_tercero
from app.tools.vacaciones import calcular_vacaciones

router = APIRouter(prefix="/calculos", tags=["cálculos (sin IA)"])
ERRORES = {422: {"description": "Entrada no válida: faltan datos o tienen valores no permitidos"}}


@router.post("/decimos", response_model=ResultadoCalculo, responses=ERRORES)
def decimos(solicitud: SolicitudDecimos) -> ResultadoCalculo:
    if solicitud.tipo == "decimo_tercero":
        return calcular_decimo_tercero(EntradaDecimoTercero(remuneraciones=solicitud.remuneraciones))
    return calcular_decimo_cuarto(EntradaDecimoCuarto(meses_trabajados=solicitud.meses_trabajados,
                                                      region=solicitud.region))


@router.post("/vacaciones", response_model=ResultadoCalculo, responses=ERRORES)
def vacaciones(entrada: EntradaVacaciones) -> ResultadoCalculo:
    try:
        return calcular_vacaciones(entrada)
    except ValueError as e:  # por ejemplo, menos de un mes completo de servicio
        raise HTTPException(422, str(e))


@router.post("/horas-extra", response_model=ResultadoCalculo, responses=ERRORES)
def horas_extra(entrada: EntradaHorasExtra) -> ResultadoCalculo:
    return calcular_horas_extra(entrada)


@router.post("/liquidacion", response_model=ResultadoCalculo, responses=ERRORES)
def liquidacion(entrada: EntradaLiquidacion) -> ResultadoCalculo:
    """Liquidación o finiquito estimado: los mismos cálculos que usa el agente (casos C09 y C10)."""
    return estimar_liquidacion(entrada)
