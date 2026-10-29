"""Pruebas de las herramientas de horas extra y liquidación (semana 3).

Los casos C08, C09 y C10 son los de docs/evidencias/semana-1 (B4_Resolución de casos.xlsx),
revisados por un contador. Indicador del caso 07: coincidir con ±0,01 USD.
"""
from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas import EntradaHorasExtra, EntradaLiquidacion
from app.tools.horas import calcular_horas_extra
from app.tools.liquidacion import estimar_liquidacion


def liquidacion(sueldo, ingreso, salida, motivo="despido_intempestivo", region="sierra_amazonia", **kw):
    return estimar_liquidacion(EntradaLiquidacion(
        remuneracion_mensual=sueldo, fecha_ingreso=date(*ingreso), fecha_salida=date(*salida),
        motivo=motivo, region=region, **kw))


# ---------------------------------------------------------------- casos de referencia
def test_c08_horas_extra():
    r = calcular_horas_extra(EntradaHorasExtra(remuneracion_mensual=800, horas_suplementarias=10,
                                               horas_extraordinarias=4))
    assert r.total == pytest.approx(76.67, abs=0.01)


def test_c09_renuncia_con_desahucio():
    assert liquidacion(700, (2024, 6, 1), (2026, 9, 30), motivo="desahucio").total == pytest.approx(1130.33, abs=0.01)


def test_c10_despido_intempestivo():
    assert liquidacion(1000, (2020, 8, 1), (2026, 8, 31)).total == pytest.approx(9331.84, abs=0.01)


# ---------------------------------------------------------------- bordes del Art. 188
def _remuneraciones(r):
    return next(l for l in r.desglose if "Indemnización" in l or "indemnización" in l)


def test_tres_anios_exactos_son_tres_remuneraciones():
    r = liquidacion(600, (2023, 10, 1), (2026, 9, 30), region="costa_galapagos")
    assert "3 remuneraciones" in _remuneraciones(r)


def test_la_fraccion_de_anio_cuenta_como_anio_completo():
    r = liquidacion(600, (2023, 10, 1), (2026, 10, 15), region="costa_galapagos")
    assert "4 remuneraciones" in _remuneraciones(r)


def test_tope_de_25_remuneraciones():
    r = liquidacion(600, (1995, 1, 1), (2026, 6, 30), region="costa_galapagos")
    assert "25 remuneraciones" in _remuneraciones(r)


def test_con_decimos_mensualizados_no_hay_decimos_pendientes():
    con = liquidacion(1000, (2020, 8, 1), (2026, 8, 31), decimos_mensualizados=True)
    sin = liquidacion(1000, (2020, 8, 1), (2026, 8, 31))
    assert con.total < sin.total


# ---------------------------------------------------------------- entradas inválidas
@pytest.mark.parametrize("datos", [
    {"remuneracion_mensual": 800},                                             # ninguna hora
    {"remuneracion_mensual": 800, "horas_suplementarias": 60},                 # más de 48 al mes
    {"remuneracion_mensual": -1, "horas_suplementarias": 2},                   # sueldo negativo
    {"remuneracion_mensual": 800, "horas_suplementarias": 2, "extra": "x"},    # campo no permitido
])
def test_horas_invalidas_se_rechazan(datos):
    with pytest.raises(ValidationError):
        EntradaHorasExtra(**datos)


@pytest.mark.parametrize("cambio", [
    {"fecha_salida": date(2019, 1, 1)},          # salida antes del ingreso
    {"fecha_salida": date(2999, 1, 1)},          # salida en el futuro
    {"motivo": "renuncia_sin_aviso"},            # motivo fuera de la lista
    {"region": "galapagos"},                     # región inexistente
])
def test_liquidacion_invalida_se_rechaza(cambio):
    datos = {"remuneracion_mensual": 1000, "fecha_ingreso": date(2020, 8, 1), "fecha_salida": date(2026, 8, 31),
             "motivo": "despido_intempestivo", "region": "sierra_amazonia", **cambio}
    with pytest.raises(ValidationError):
        EntradaLiquidacion(**datos)
