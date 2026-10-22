"""Herramienta: cálculo del décimo tercero y del décimo cuarto.

Determinista: mismas entradas, mismo resultado. No llama al modelo.
"""
from __future__ import annotations

from app.schemas import EntradaDecimoCuarto, EntradaDecimoTercero, ResultadoCalculo
from app.tools.parametros import cargar_parametros, dec, redondear


def calcular_decimo_tercero(entrada: EntradaDecimoTercero) -> ResultadoCalculo:
    """Art. 111: la doceava parte de lo percibido en el período."""
    p = cargar_parametros()["decimo_tercero"]
    divisor = dec(p["divisor"])
    suma = sum((dec(m) for m in entrada.remuneraciones), dec(0))
    total = redondear(suma / divisor)
    return ResultadoCalculo(
        tipo="decimo_tercero",
        entradas=entrada.model_dump(),
        desglose=[
            f"Suma de {len(entrada.remuneraciones)} remuneraciones: {redondear(suma)}",
            f"Doceava parte: {redondear(suma)} / {divisor} = {total}",
        ],
        total=float(total),
        fundamento=p["fuente"],
    )


def calcular_decimo_cuarto(entrada: EntradaDecimoCuarto) -> ResultadoCalculo:
    """Art. 113: un salario básico unificado por año completo, proporcional a los meses."""
    params = cargar_parametros()
    sbu = dec(params["salario_basico_unificado"]["valor"])
    meses = dec(entrada.meses_trabajados)
    total = redondear(sbu * meses / dec(12))
    return ResultadoCalculo(
        tipo="decimo_cuarto",
        entradas=entrada.model_dump(),
        desglose=[
            f"Salario básico unificado {params['anio_vigencia']}: {sbu}",
            f"Proporción: {sbu} x {entrada.meses_trabajados} / 12 = {total}",
            f"Período de la región: {params['decimo_cuarto']['regiones'][entrada.region]['periodo']}",
        ],
        total=float(total),
        fundamento=params["decimo_cuarto"]["fuente"],
    )
