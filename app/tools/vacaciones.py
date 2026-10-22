"""Herramienta: días y valor de vacaciones de un año completo de servicio.

Art. 69: 15 días; desde el año 6, un día más por cada año excedente de 5 (máximo 15 adicionales).
Art. 71: el pago es la veinticuatroava parte de lo percibido en el año; los días
adicionales se pagan a razón de remuneración / 30 por día.
"""
from __future__ import annotations

from datetime import date

from app.schemas import EntradaVacaciones, ResultadoCalculo
from app.tools.parametros import cargar_parametros, dec, redondear


def anios_completos(desde: date, hasta: date) -> int:
    anios = hasta.year - desde.year
    if (hasta.month, hasta.day) < (desde.month, desde.day):
        anios -= 1
    return anios


def calcular_vacaciones(entrada: EntradaVacaciones) -> ResultadoCalculo:
    params = cargar_parametros()
    p = params["vacaciones"]
    corte = entrada.fecha_corte or date.today()
    anios = anios_completos(entrada.fecha_ingreso, corte)
    if anios < 1:
        raise ValueError("Aún no cumple un año de servicio; el valor proporcional se calcula en la liquidación.")

    adicionales = min(max(0, anios - (p["dia_adicional_desde_anio"] - 1)), p["max_dias_adicionales"])
    dias = p["dias_base"] + adicionales

    sueldo = dec(entrada.remuneracion_mensual)
    valor_base = redondear(sueldo * dec(12) / dec(p["divisor_valor"]))
    valor_adicional = redondear(sueldo / dec(params["calendario"]["dias_mes"]) * dec(adicionales))
    total = valor_base + valor_adicional

    return ResultadoCalculo(
        tipo="vacaciones",
        entradas={**entrada.model_dump(mode="json"), "anios_completos": anios},
        desglose=[
            f"Años completos de servicio: {anios}",
            f"Días: {p['dias_base']} base + {adicionales} adicionales = {dias}",
            f"Valor base: {sueldo} x 12 / {p['divisor_valor']} = {valor_base}",
            f"Valor de días adicionales: {sueldo} / {params['calendario']['dias_mes']} x {adicionales} = {valor_adicional}",
            f"Total: {valor_base} + {valor_adicional} = {total}",
        ],
        total=float(total),
        dias=dias,
        fundamento=p["fuente"],
    )
