"""Herramienta: días y valor de vacaciones de un año completo de servicio.

Art. 69: 15 días; desde el año 6, un día más por cada año excedente de 5 (máximo 15 adicionales).
Art. 71: el pago es la veinticuatroava parte de lo percibido en el año; los días
adicionales se pagan a razón de remuneración / 30 por día.
"""
from __future__ import annotations

from datetime import date, timedelta

from app.schemas import (EntradaVacaciones, ResultadoCalculo,
                         EntradaDiasVacaciones, ResultadoDiasVacaciones)
from app.tools.parametros import cargar_parametros, dec, redondear


def anios_completos(desde: date, hasta: date) -> int:
    anios = hasta.year - desde.year
    if (hasta.month, hasta.day) < (desde.month, desde.day):
        anios -= 1
    return anios

def meses_completos(desde: date, hasta: date) -> int:
    """Incluye el día de corte y descarta fracciones de mes."""
    fin = hasta + timedelta(days=1)
    meses = (fin.year - desde.year) * 12 + fin.month - desde.month
    if fin.day < desde.day:
        meses -= 1
    return max(0, meses)


def calcular_dias_vacaciones(entrada: EntradaDiasVacaciones) -> ResultadoDiasVacaciones:
    """Días por período anual con años declarados; no calcula un saldo acumulado."""
    p = cargar_parametros()["vacaciones"]
    adicionales = min(max(0, entrada.anios_servicio - (p["dia_adicional_desde_anio"] - 1)),
                       p["max_dias_adicionales"])
    return ResultadoDiasVacaciones(anios_servicio=entrada.anios_servicio,
        dias_base=p["dias_base"], dias_adicionales=adicionales,
        dias_anuales=p["dias_base"] + adicionales, fundamento=p["fuente"])


def calcular_vacaciones(entrada: EntradaVacaciones) -> ResultadoCalculo:
    params = cargar_parametros()
    p = params["vacaciones"]
    corte = entrada.fecha_corte or date.today()
    anios = anios_completos(entrada.fecha_ingreso, corte)
    
    # MVP: remuneración fija y meses completos.
    # Con un año o más, este cálculo representa un período anual,
    # no el saldo acumulado de todos los años de servicio.
    meses = meses_completos(entrada.fecha_ingreso, corte) if anios < 1 else 12

    adicionales = calcular_dias_vacaciones(EntradaDiasVacaciones(anios_servicio=anios)).dias_adicionales
    dias_base = dec(p["dias_base"]) * dec(meses) / dec(12)
    dias = dias_base + dec(adicionales)

    sueldo = dec(entrada.remuneracion_mensual)
    valor_base = redondear(sueldo * dec(meses) / dec(p["divisor_valor"]))
    valor_adicional = redondear(
        sueldo / dec(params["calendario"]["dias_mes"]) * dec(adicionales)
    )
    total = valor_base + valor_adicional

    return ResultadoCalculo(
        tipo="vacaciones",
        entradas={**entrada.model_dump(mode="json"), "anios_completos": anios},
        desglose=[
            f"Años completos de servicio: {anios}",
            f"Días: {dias_base} base proporcional + {adicionales} adicionales = {dias}",
            f"Valor base: {sueldo} x {meses} / {p['divisor_valor']} = {valor_base}",
            f"Valor de días adicionales: {sueldo} / {params['calendario']['dias_mes']} x {adicionales} = {valor_adicional}",
            f"Total: {valor_base} + {valor_adicional} = {total}",
        ],
        total=float(total),
        dias=float(dias),
        fundamento=p["fuente"],
    )
