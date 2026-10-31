"""Endpoints de cálculo · deterministas, NO llaman al modelo (ADR-002).

POST /calculos/decimos     décimo tercero o décimo cuarto, según «tipo»
POST /calculos/vacaciones  días y valor de vacaciones (anuales o proporcionales)
POST /calculos/horas       horas suplementarias y extraordinarias
POST /calculos/liquidacion estimación con motivo y saldos informados

Si la entrada es inválida, FastAPI responde 422 antes de calcular. Los parámetros
(salario básico, divisores, días) se leen de config/parametros.yaml.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas import (EntradaDecimoCuarto, EntradaDecimoTercero, EntradaVacaciones, ResultadoCalculo,
                         SolicitudDecimos, EntradaHoras, EntradaLiquidacion)
from app.tools.horas import calcular_horas
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


@router.post("/horas", response_model=ResultadoCalculo, responses=ERRORES)
def horas(entrada: EntradaHoras) -> ResultadoCalculo:
    return calcular_horas(entrada)


@router.post("/liquidacion", response_model=ResultadoCalculo, responses=ERRORES)
def liquidacion(entrada: EntradaLiquidacion) -> ResultadoCalculo:
    try:
        return estimar_liquidacion(entrada)
    except ValueError as e:
        raise HTTPException(422, str(e))
