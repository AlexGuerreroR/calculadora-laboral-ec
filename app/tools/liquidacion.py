"""Herramienta: estimación de la liquidación al terminar la relación laboral.

Criterios de los casos de referencia C09 y C10 (semana 1, revisados por contador):
- Despido intempestivo (Art. 188): hasta 3 años, 3 remuneraciones; más de 3, una por año.
  La fracción de año cuenta como año completo. Tope: 25 remuneraciones.
- Bonificación por desahucio (Art. 185): 25 % del último sueldo por cada año COMPLETO.
  Se paga en el desahucio, en la terminación por acuerdo y también en el despido (Art. 188,
  «sin perjuicio de pagar las bonificaciones… del artículo 185»).
- Proporcionales pendientes, con meses completos y sueldo fijo: décimo tercero desde el 1 de
  diciembre, décimo cuarto desde el inicio del período de la región, vacaciones desde el último
  aniversario (sin días adicionales). Se asume que lo anterior ya fue pagado.
No calcula el sueldo del último mes ni dictamina si el despido fue legal: eso lo decide la
autoridad (se deriva al Ministerio del Trabajo).
"""
from __future__ import annotations

from datetime import date, timedelta

from app.schemas import EntradaLiquidacion, ResultadoCalculo
from app.tools.parametros import cargar_parametros, dec, redondear
from app.tools.vacaciones import anios_completos, meses_completos

INICIO_DECIMO_CUARTO = {"costa_galapagos": 3, "sierra_amazonia": 8}  # mes en que empieza el período


def _inicio_periodo(salida: date, mes_inicio: int) -> date:
    anio = salida.year if salida.month >= mes_inicio else salida.year - 1
    return date(anio, mes_inicio, 1)


def _ultimo_aniversario(ingreso: date, anios: int) -> date:
    try:
        return ingreso.replace(year=ingreso.year + anios)
    except ValueError:  # 29 de febrero
        return ingreso.replace(year=ingreso.year + anios, day=28)


def estimar_liquidacion(entrada: EntradaLiquidacion) -> ResultadoCalculo:
    params = cargar_parametros()
    p = params["liquidacion"]
    sueldo = dec(entrada.remuneracion_mensual)
    ingreso, salida = entrada.fecha_ingreso, entrada.fecha_salida
    anios = anios_completos(ingreso, salida + timedelta(days=1))  # el último día trabajado cuenta
    hay_fraccion = salida + timedelta(days=1) > _ultimo_aniversario(ingreso, anios)  # basta un día de más
    desglose, total = [f"Tiempo de servicio: {anios} años completos{' y una fracción' if hay_fraccion else ''}"], dec(0)

    if entrada.motivo == "despido_intempestivo":
        indemnizables = anios + (1 if hay_fraccion else 0)
        meses = min(max(indemnizables, 0), p["despido_tope_remuneraciones"])
        if indemnizables <= 3:
            meses = p["despido_minimo_remuneraciones"]
        despido = redondear(sueldo * dec(meses))
        desglose.append(f"Indemnización por despido (Art. 188): {sueldo} x {meses} remuneraciones = {despido}")
        total += despido

    desahucio = redondear(dec(p["desahucio_porcentaje_por_anio"]) * sueldo * dec(anios))
    desglose.append(f"Bonificación por desahucio (Art. 185): {dec(p['desahucio_porcentaje_por_anio']) * 100:.0f} % x {sueldo} x {anios} años = {desahucio}")
    total += desahucio

    if entrada.decimos_mensualizados:
        desglose.append("Décimos: se recibían cada mes, no hay valores pendientes")
    else:
        inicio13 = max(ingreso, _inicio_periodo(salida, 12))
        m13 = meses_completos(inicio13, salida)
        d13 = redondear(sueldo * dec(m13) / dec(12))
        inicio14 = max(ingreso, _inicio_periodo(salida, INICIO_DECIMO_CUARTO[entrada.region]))
        m14 = meses_completos(inicio14, salida)
        sbu = dec(params["salario_basico_unificado"]["valor"])
        d14 = redondear(sbu * dec(m14) / dec(12))
        desglose += [f"Décimo tercero proporcional (Art. 111): {sueldo} x {m13} meses / 12 = {d13}",
                     f"Décimo cuarto proporcional (Art. 113): {sbu} x {m14} meses / 12 = {d14}"]
        total += d13 + d14

    mvac = meses_completos(max(ingreso, _ultimo_aniversario(ingreso, anios)), salida)
    vac = redondear(sueldo * dec(mvac) / dec(params["vacaciones"]["divisor_valor"]))
    desglose.append(f"Vacaciones proporcionales no gozadas (Art. 71): {sueldo} x {mvac} meses / 24 = {vac}")
    total += vac
    desglose.append(f"Total estimado: {redondear(total)}")

    return ResultadoCalculo(
        tipo="liquidacion",
        entradas=entrada.model_dump(mode="json"),
        desglose=desglose,
        total=float(redondear(total)),
        fundamento=p["fuente_estimacion"],
    )
