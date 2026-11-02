"""Estimación de saldos e indemnizaciones, con los criterios explícitos del caso 07.

No decide el motivo legal de salida ni reconstruye pagos/vacaciones desconocidos.
El usuario informa saldos y confirma el supuesto. Desahucio por años completos,
según la referencia del grupo, pendiente de contraste normativo actualizado.
"""
from calendar import monthrange
from decimal import Decimal

from app.schemas import EntradaLiquidacion, ResultadoCalculo
from app.tools.horas import rubros_horas
from app.tools.parametros import cargar_parametros, dec, redondear


def antiguedad(ingreso, salida):
    def aniversario(anio):
        return ingreso.replace(year=anio, day=min(ingreso.day, monthrange(anio, ingreso.month)[1]))
    anios = salida.year - ingreso.year
    if salida < aniversario(salida.year):
        anios -= 1
    return anios, salida > aniversario(ingreso.year + anios)


def estimar_liquidacion(entrada: EntradaLiquidacion) -> ResultadoCalculo:
    p = cargar_parametros()
    regla = p["liquidacion"]
    anios, fraccion = antiguedad(entrada.fecha_ingreso, entrada.fecha_salida)
    sueldo = entrada.remuneracion_mensual
    cero = Decimal("0.00")
    indemnizacion = cero
    anios_indemnizables = 0
    if entrada.motivo_salida == "despido_intempestivo":
        anios_indemnizables = min(max(regla["despido_minimo_remuneraciones"], anios + int(fraccion)),
                                 regla["despido_tope_remuneraciones"])
        indemnizacion = redondear(sueldo * dec(anios_indemnizables))
    desahucio = redondear(sueldo * dec(regla["desahucio_porcentaje_por_anio"]) * dec(anios))
    decimo_tercero = redondear(entrada.base_acumulada_decimo_tercero / dec(p["decimo_tercero"]["divisor"]))
    decimo_cuarto = redondear(dec(p["salario_basico_unificado"]["valor"]) * entrada.dias_decimo_cuarto_pendientes
                             / dec(p["calendario"]["dias_anio"]))
    vacaciones_base = redondear(sueldo / dec(p["calendario"]["dias_mes"]) * entrada.dias_vacaciones_base_pendientes)
    vacaciones_adicionales = redondear(sueldo / dec(p["calendario"]["dias_mes"]) * entrada.dias_vacaciones_adicionales_pendientes)
    _, suplementarias, extraordinarias = rubros_horas(
        sueldo, entrada.horas_suplementarias_pendientes, entrada.horas_extraordinarias_pendientes)
    rubros = [
        ("Salario pendiente informado", redondear(entrada.salario_pendiente)),
        ("Indemnización por despido intempestivo", indemnizacion),
        ("Bonificación por desahucio", desahucio),
        ("Décimo tercero pendiente", decimo_tercero),
        ("Décimo cuarto pendiente", decimo_cuarto),
        ("Vacaciones base pendientes", vacaciones_base),
        ("Vacaciones adicionales pendientes", vacaciones_adicionales),
        ("Horas suplementarias pendientes", suplementarias),
        ("Horas extraordinarias pendientes", extraordinarias),
    ]
    bruto = sum((valor for _, valor in rubros), cero)
    descuentos = redondear(entrada.descuentos_confirmados)
    if descuentos > bruto:
        raise ValueError("los descuentos superan los rubros calculados; revise los saldos confirmados")
    total = bruto - descuentos
    desglose = [f"Años completos de servicio: {anios}; fracción adicional: {'sí' if fraccion else 'no'}",
                f"Remuneraciones indemnizables según motivo informado: {anios_indemnizables}"]
    desglose += [f"{nombre}: {valor}" for nombre, valor in rubros]
    desglose += [
        f"Desahucio: {sueldo} x {regla['desahucio_porcentaje_por_anio']} x {anios} años completos = {desahucio}",
        f"Décimo tercero: base informada {entrada.base_acumulada_decimo_tercero} / {p['decimo_tercero']['divisor']} = {decimo_tercero}",
        f"Décimo cuarto: SBU {p['salario_basico_unificado']['valor']} x {entrada.dias_decimo_cuarto_pendientes} días / {p['calendario']['dias_anio']} = {decimo_cuarto}",
        f"Total bruto: {bruto}; descuentos confirmados: {descuentos}; total neto estimado: {total}",
        "Criterios: remuneración fija para vacaciones; saldos de días informados por el usuario; no se agrega nuevamente lo ya pagado.",
        "La bonificación por desahucio se estima con años completos de servicio. Revise las fracciones de año y las condiciones particulares antes de utilizar el resultado.",
    ]
    if anios >= p["vacaciones"]["dia_adicional_desde_anio"] and entrada.dias_vacaciones_adicionales_pendientes == 0:
        desglose.append("Se informó saldo cero de vacaciones adicionales pese a la antigüedad. Confirme que fueron gozadas o pagadas; no se presume que no existe el derecho.")
    return ResultadoCalculo(tipo="liquidacion", entradas=entrada.model_dump(mode="json"),
                            desglose=desglose, total=float(total),
                            fundamento=regla["fuente"] + "; " + regla["fuente_saldos"])
