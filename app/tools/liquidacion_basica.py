"""Estimación orientativa con los parámetros y fuentes del proyecto."""
from calendar import monthrange
from datetime import date
from decimal import Decimal

from app.schemas import EntradaLiquidacionBasica, ResultadoCalculo
from app.tools.liquidacion import antiguedad, rubros_terminacion
from app.tools.parametros import cargar_parametros, dec, redondear


def sugerir_vacaciones(ingreso: date, salida: date) -> Decimal:
    if not ingreso <= salida <= date.today():
        raise ValueError("revise las fechas de ingreso y salida")
    p = cargar_parametros()
    anios, fraccion = antiguedad(ingreso, salida)
    # En el aniversario exacto se muestra el período que acaba de completarse.
    anio = ingreso.year + (anios if fraccion else max(0, anios - 1))
    inicio = ingreso.replace(year=anio, day=min(ingreso.day, monthrange(anio, ingreso.month)[1]))
    dias_anio = p["calendario"]["dias_anio"]
    dias = min((salida - inicio).days, dias_anio)
    return redondear(dec(p["vacaciones"]["dias_base"]) * dec(dias) / dec(dias_anio))


def _dias_decimo(ingreso, salida, mes_inicio, mensualiza, calendario):
    if mensualiza:
        inicio = salida.replace(day=1)
    else:
        inicio = date(salida.year - int(salida.month < mes_inicio), mes_inicio, 1)
    inicio = max(inicio, ingreso)
    dias_mes = calendario["dias_mes"]
    fin = dias_mes if salida.day == monthrange(salida.year, salida.month)[1] else salida.day
    meses = (salida.year - inicio.year) * 12 + salida.month - inicio.month
    return meses * dias_mes + min(fin, dias_mes) - min(inicio.day, dias_mes) + 1


def estimar_liquidacion_basica(entrada: EntradaLiquidacionBasica) -> ResultadoCalculo:
    p = cargar_parametros()
    calendario = p["calendario"]
    sbu = p["salario_basico_unificado"]
    ingreso, salida = entrada.fecha_ingreso, entrada.fecha_salida
    if salida.year != sbu["anio"]:
        raise ValueError(f"El cálculo básico tiene salario básico verificado para salidas de {sbu['anio']}.")

    sueldo = entrada.remuneracion_mensual
    mes_13 = int(p["decimo_tercero"]["periodo_inicio"].split("-")[1])
    mes_14 = p["decimo_cuarto"]["regiones"][entrada.region]["mes_inicio"]
    dias_13 = _dias_decimo(ingreso, salida, mes_13, entrada.mensualiza_decimo_tercero, calendario)
    dias_14 = _dias_decimo(ingreso, salida, mes_14, entrada.mensualiza_decimo_cuarto, calendario)
    decimo_13 = redondear(sueldo * dias_13 / calendario["dias_mes"] / p["decimo_tercero"]["divisor"])
    decimo_14 = redondear(dec(sbu["valor"]) * dias_14 / calendario["dias_anio"])

    dias_vacaciones = entrada.dias_vacaciones_pendientes
    origen_vacaciones = "saldo informado"
    if dias_vacaciones is None:
        dias_vacaciones = sugerir_vacaciones(ingreso, salida)
        origen_vacaciones = "sugerencia del último período de servicio"
    vacaciones = redondear(sueldo * dias_vacaciones / calendario["dias_mes"])
    anios, fraccion = antiguedad(ingreso, salida)
    regla = p["liquidacion"]
    _, indemnizacion, desahucio = rubros_terminacion(entrada.motivo_salida, sueldo, anios, fraccion, regla)
    total = sum((decimo_13, decimo_14, vacaciones, indemnizacion, desahucio))
    desglose = [
        f"Décimo tercero estimado ({dias_13} días): USD {decimo_13}",
        f"Décimo cuarto estimado ({dias_14} días): USD {decimo_14}",
        f"Vacaciones estimadas ({dias_vacaciones} días, {origen_vacaciones}): USD {vacaciones}",
        f"Indemnización por despido intempestivo: USD {indemnizacion}",
        f"Bonificación por desahucio ({anios} años completos): USD {desahucio}",
        "Supuestos: remuneración fija; si recibe un décimo cada mes, se presume pagado hasta el mes anterior; "
        "si lo acumula, se estima el período vigente hasta la salida.",
        "El total excluye salarios y horas pendientes, vacaciones de períodos anteriores o adicionales por "
        "antigüedad que no se hayan informado en el saldo, descuentos y situaciones especiales.",
        "Monto referencial. Revise los valores definitivos en su acta de finiquito.",
    ]
    return ResultadoCalculo(tipo="liquidacion", entradas=entrada.model_dump(mode="json"),
                            desglose=desglose, total=float(total),
                            fundamento=regla["fuente"] + "; " + regla["fuente_saldos"] + "; " + calendario["fuente"])
