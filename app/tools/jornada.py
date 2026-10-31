"""Compara horas declaradas con jornada general; no determina recargos ni dinero."""
from app.schemas import EntradaJornada, ResultadoJornada
from app.tools.parametros import cargar_parametros, dec


def analizar_jornada(entrada: EntradaJornada) -> ResultadoJornada:
    p = cargar_parametros()["jornada"]
    referencia = dec(p["horas_maximas_diarias_generales"])
    exceso = max(dec(0), entrada.horas_diarias - referencia)
    return ResultadoJornada(horas_declaradas=float(entrada.horas_diarias),
        referencia_diaria=float(referencia), exceso_sobre_referencia=float(exceso),
        fundamento=p["fuente"])
