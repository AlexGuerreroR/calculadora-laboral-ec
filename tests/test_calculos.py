from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.schemas import (
    EntradaDecimoCuarto,
    EntradaDecimoTercero,
    EntradaVacaciones,
)
from app.tools.decimos import (
    calcular_decimo_cuarto,
    calcular_decimo_tercero,
)
from app.tools.vacaciones import calcular_vacaciones


@pytest.mark.parametrize("montos, esperado", [
    ([600] * 12, 600),
    ([500] * 6, 250),
    ([700] * 9 + [850] * 3, 737.50),
])
def test_decimo_tercero_referencia(montos, esperado):
    resultado = calcular_decimo_tercero(
        EntradaDecimoTercero(remuneraciones=montos)
    )
    assert resultado.total == pytest.approx(esperado, abs=0.01)


@pytest.mark.parametrize("meses, region, esperado", [
    (12, "sierra_amazonia", 482),
    (6, "costa_galapagos", 241),
])
def test_decimo_cuarto_referencia(meses, region, esperado):
    resultado = calcular_decimo_cuarto(
        EntradaDecimoCuarto(meses_trabajados=meses, region=region)
    )
    assert resultado.total == pytest.approx(esperado, abs=0.01)


@pytest.mark.parametrize("sueldo, ingreso, corte, dias, valor", [
    (600, "2025-10-01", "2026-10-01", 15, 300),
    (900, "2019-03-01", "2026-03-01", 17, 510),
    (700, "2026-06-01", "2026-09-30", 5, 116.67),
    (600, "2026-06-01", "2026-06-30", 1.25, 25),
    (600, "2026-06-01", "2026-06-15", 0, 0),
])
def test_vacaciones(sueldo, ingreso, corte, dias, valor):
    resultado = calcular_vacaciones(EntradaVacaciones(
        remuneracion_mensual=sueldo,
        fecha_ingreso=ingreso,
        fecha_corte=corte,
    ))
    assert resultado.dias == pytest.approx(dias)
    assert resultado.total == pytest.approx(valor, abs=0.01)


@pytest.mark.parametrize("montos", [
    [], [0], [-1], [600] * 13,
    [float("nan")], [float("inf")], [float("-inf")],
    [100001],
])
def test_remuneraciones_invalidas(montos):
    with pytest.raises(ValidationError):
        EntradaDecimoTercero(remuneraciones=montos)


@pytest.mark.parametrize("sueldo", [
    0, -1, 100001, float("nan"), float("inf"), float("-inf"),
])
def test_sueldo_vacaciones_invalido(sueldo):
    with pytest.raises(ValidationError):
        EntradaVacaciones(
            remuneracion_mensual=sueldo,
            fecha_ingreso="2025-01-01",
        )


@pytest.mark.parametrize("meses", [0, -1, 13, 1.5])
def test_meses_invalidos(meses):
    with pytest.raises(ValidationError):
        EntradaDecimoCuarto(
            meses_trabajados=meses,
            region="sierra_amazonia",
        )


def test_fechas_invalidas():
    with pytest.raises(ValidationError):
        EntradaVacaciones(
            remuneracion_mensual=600,
            fecha_ingreso="2026-06-02",
            fecha_corte="2026-06-01",
        )


def test_fecha_futura():
    futuro = date.today() + timedelta(days=1)
    with pytest.raises(ValidationError):
        EntradaVacaciones(
            remuneracion_mensual=600,
            fecha_ingreso=futuro,
        )


def test_campo_no_permitido():
    with pytest.raises(ValidationError):
        EntradaDecimoTercero(
            remuneraciones=[600],
            campo_desconocido=True,
        )


def test_region_invalida():
    with pytest.raises(ValidationError):
        EntradaDecimoCuarto(meses_trabajados=12, region="otra")
