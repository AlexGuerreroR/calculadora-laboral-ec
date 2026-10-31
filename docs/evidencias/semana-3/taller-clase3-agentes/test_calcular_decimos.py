# tests/test_calcular_decimos.py · generado en el taller · Grupo 7
import pytest
from decimal import Decimal
from pydantic import ValidationError
from app.tools.calcular_decimos import calcular_decimos, CalcularDecimosIn


def test_caso_conocido():
    datos = CalcularDecimosIn(meses_trabajados=6, region="costa_galapagos")
    resultado = calcular_decimos(datos)
    assert resultado["valor"] == pytest.approx(241 )


def test_rechaza_valores_fuera_de_limite():
    with pytest.raises(ValidationError):
        CalcularDecimosIn(meses_trabajados=13, region="costa_galapagos")


def test_es_determinista():
    datos = CalcularDecimosIn(meses_trabajados=6, region="costa_galapagos")
    assert calcular_decimos(datos) == calcular_decimos(datos)
