"""Horas adicionales en Python: hora sin redondear, redondeo por rubro final."""
from app.schemas import EntradaHoras, ResultadoCalculo
from app.tools.parametros import cargar_parametros, dec, redondear


def rubros_horas(sueldo, suplementarias, extraordinarias):
    p = cargar_parametros()["horas"]
    hora = dec(sueldo) / dec(p["divisor_hora_ordinaria"])
    suplementarias = redondear(hora * dec(suplementarias) * (dec(1) + dec(p["recargo_suplementaria"])))
    extraordinarias = redondear(hora * dec(extraordinarias) * (dec(1) + dec(p["recargo_extraordinaria"])))
    return hora, suplementarias, extraordinarias


def calcular_horas(entrada: EntradaHoras) -> ResultadoCalculo:
    p = cargar_parametros()["horas"]
    hora, suplementarias, extraordinarias = rubros_horas(
        entrada.remuneracion_mensual, entrada.horas_suplementarias, entrada.horas_extraordinarias)
    total = suplementarias + extraordinarias
    return ResultadoCalculo(
        tipo="horas_extra", entradas=entrada.model_dump(mode="json"), total=float(total),
        fundamento=p["fuente"], desglose=[
            f"Hora ordinaria sin redondeo intermedio: {entrada.remuneracion_mensual} / {p['divisor_hora_ordinaria']} = {hora}",
            f"Suplementarias: {entrada.horas_suplementarias} horas con recargo {dec(p['recargo_suplementaria']) * 100}% = {suplementarias}",
            f"Extraordinarias: {entrada.horas_extraordinarias} horas con recargo {dec(p['recargo_extraordinaria']) * 100}% = {extraordinarias}",
            f"Total de rubros redondeados: {suplementarias} + {extraordinarias} = {total}",
            "Alcance: sueldo mensual y jornada completa. Las horas las informa el usuario; no se determina si su distribución diaria o semanal fue legal.",
        ])
