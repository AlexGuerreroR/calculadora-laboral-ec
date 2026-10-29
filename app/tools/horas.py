"""Herramienta: valor de las horas suplementarias y extraordinarias (Art. 55).

Caso de referencia C08 (revisado por contador): USD 800, 10 h al 50 % y 4 h al 100 % = USD 76,67.
Valor de la hora = sueldo / 240, sin redondeo intermedio; cada rubro se redondea al final.
"""
from __future__ import annotations

from app.schemas import EntradaHorasExtra, ResultadoCalculo
from app.tools.parametros import cargar_parametros, dec, redondear


def calcular_horas_extra(entrada: EntradaHorasExtra) -> ResultadoCalculo:
    p = cargar_parametros()["horas"]
    sueldo = dec(entrada.remuneracion_mensual)
    hora = sueldo / dec(p["divisor_hora_ordinaria"])
    factor_s = dec(1) + dec(p["recargo_suplementaria"])
    factor_e = dec(1) + dec(p["recargo_extraordinaria"])
    supl = redondear(hora * dec(entrada.horas_suplementarias) * factor_s)
    extra = redondear(hora * dec(entrada.horas_extraordinarias) * factor_e)
    total = supl + extra
    return ResultadoCalculo(
        tipo="horas_extra",
        entradas=entrada.model_dump(),
        desglose=[
            f"Valor de la hora: {sueldo} / {p['divisor_hora_ordinaria']} = {redondear(hora)}",
            f"Suplementarias: {entrada.horas_suplementarias} h x hora x {factor_s} = {supl}",
            f"Extraordinarias: {entrada.horas_extraordinarias} h x hora x {factor_e} = {extra}",
            f"Total: {supl} + {extra} = {total}",
        ],
        total=float(total),
        fundamento=p["fuente"],
    )
